# FileWriter (was BaseHelper)
import os
from django.core.management import CommandError
from django.template import Template, Context
from django.template.loader import get_template
from django.conf import settings

# We'll use Django's template system – you must ensure django_autoapi/templates
# is added to TEMPLATES['DIRS'] or we can load from file directly.

class FileWriter:
    """
    Writes a single generated file, handling conflicts and markers.
    """

    def __init__(self, app_name, component_type, model_name=None, subfolder=None, force=False):
        self.app_name = app_name
        self.component_type = component_type   # e.g., 'serializers', 'permissions'
        self.model_name = model_name            # None for app‑level tasks
        self.subfolder = subfolder              # None or 'utilities'
        self.force = force
        self.target_path = self._get_target_path()

    def write(self):
        """Generate content and write to file, respecting force and conflict handling."""
        if os.path.exists(self.target_path):
            with open(self.target_path, 'r') as f:
                first_line = f.readline()
            if not first_line.startswith('# DJANGO_AUTOAPI_GENERATED') and not self.force:
                raise CommandError(
                    f"File {self.target_path} already exists and was not created by django-autoapi.\n"
                    f"Manually remove it or use --force to overwrite."
                )
        # Render and write
        content = self._render_template()
        dirname = os.path.dirname(self.target_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        with open(self.target_path, 'w') as f:
            if not self.force and self._should_add_marker():
                f.write("# DJANGO_AUTOAPI_GENERATED\n")
            f.write(content)

    def _get_target_path(self):
        """Determine the absolute file path for the generated file."""
        base = os.path.join(os.getcwd(), self.app_name)
        # App‑level utilities go into app/utilities/
        if self.component_type in ('permissions', 'pagination', 'importbase'):
            folder = os.path.join(base, 'utilities')
            os.makedirs(folder, exist_ok=True)
            return os.path.join(folder, f"{self.component_type}.py")

        # Routers: creates app/routers/routers.py
        if self.component_type == 'routers':
            folder = os.path.join(base, 'routers')
            os.makedirs(folder, exist_ok=True)
            return os.path.join(folder, 'routers.py')

        # Serializers and viewsets go directly in app root
        if self.component_type in ('serializers', 'viewsets'):
            return os.path.join(base, f"{self.component_type}.py")

        # Fallback (should not happen)
        return os.path.join(base, f"{self.component_type}.py")

    def _render_template(self):
        """Render the appropriate template with context."""
        # We use Django's template loader – you must put templates in a folder
        # that is in TEMPLATES['DIRS'] or install them as package data.
        # For simplicity, we read from the package's templates folder.
        template_name = f"{self.component_type}.txt"
        template_path = os.path.join(
            os.path.dirname(__file__), '..', 'templates', template_name
        )
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, 'r') as f:
            raw = f.read()

        context = {
            'app_name': self.app_name,
            'model_name': self.model_name,
            'model_list_serializers': f"{self.model_name}ListSerializer" if self.model_name else '',
            'model_retrieve_serializers': f"{self.model_name}RetrieveSerializer" if self.model_name else '',
            'model_write_serializers': f"{self.model_name}WriteSerializer" if self.model_name else '',
            'viewset_name': f"{self.model_name}ViewSet" if self.model_name else '',
            'api_endpoint': self.model_name.lower() if self.model_name else '',
            # For routers, we need a list of all model names.
            # This will be provided by the GenerationTask for routers separately.
            # We'll handle that in a special hook.
        }

        # For routers template, we need to collect all viewsets.
        if self.component_type == 'routers':
            from django.apps import apps
            from .task import GenerationTask
            task = GenerationTask(self.app_name, 'routers')  # temporary to get models
            models = task._get_valid_models()
            context['models'] = [{'name': m.__name__, 'endpoint': m.__name__.lower()} for m in models]

        # Use Django's Template engine
        template = Template(raw)
        return template.render(Context(context))

    def _should_add_marker(self):
        """Return True if this file type should have the auto‑generated marker."""
        # All files we generate should be marked, except maybe routers if we want?
        return True