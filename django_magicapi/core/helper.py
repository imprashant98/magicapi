import os
from django.core.management import CommandError
from django.template import Template, Context

class FileWriter:
    """
    Writes a single generated file, handling conflicts and markers.
    """

    def __init__(self, app_name, component_type, model_name=None, subfolder=None, force=False):
        self.app_name = app_name
        self.component_type = component_type
        self.model_name = model_name
        self.subfolder = subfolder
        self.force = force
        self.target_path = self._get_target_path()

    def write(self):
        if self.component_type == 'admin':
            self._write_admin()
            return

        if os.path.exists(self.target_path):
            if not self.force:
                raise CommandError(
                    f"File {self.target_path} already exists.\n"
                    f"Please remove it or use --force to overwrite."
                )

        content = self._render_template()
        dirname = os.path.dirname(self.target_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
            if self.subfolder in ('serializers', 'viewsets'):
                init_path = os.path.join(dirname, '__init__.py')
                if not os.path.exists(init_path):
                    with open(init_path, 'w') as f_init:
                        f_init.write("")

        with open(self.target_path, 'w') as f:
            f.write(content)

    def _write_admin(self):
        admin_path = self.target_path
        model_name = self.model_name
        marker_start = f"# DJANGO_MAGICAPI_ADMIN_START:{model_name}"
        marker_end = f"# DJANGO_MAGICAPI_ADMIN_END:{model_name}"
        registration_block = self._render_admin_template().strip()

        if os.path.exists(admin_path):
            with open(admin_path, 'r') as f:
                content = f.read()
            # If a complete block already exists, skip
            if marker_start in content and marker_end in content:
                return
            # If start marker exists but no end marker, remove the partial block
            if marker_start in content and marker_end not in content:
                lines = content.splitlines(keepends=True)
                new_lines = []
                skip = False
                for line in lines:
                    if line.startswith(marker_start):
                        skip = True
                        continue
                    if skip and line.startswith('# DJANGO_MAGICAPI_ADMIN_START:'):
                        skip = False
                    if not skip:
                        new_lines.append(line)
                content = ''.join(new_lines)
                with open(admin_path, 'w') as f:
                    f.write(content)
            # Append the correct block (no import inside)
            with open(admin_path, 'a') as f:
                f.write(f"\n\n{marker_start}\n")
                f.write(registration_block)
                f.write(f"\n{marker_end}\n")
        else:
            # Create new admin.py with the import once
            with open(admin_path, 'w') as f:
                f.write("# DJANGO_MAGICAPI_GENERATED_ADMIN\n")
                f.write("from django.contrib import admin\n\n")
                f.write(f"{marker_start}\n")
                f.write(registration_block)
                f.write(f"\n{marker_end}\n")

    def _render_admin_template(self):
        template_name = "admin.txt"
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', template_name)
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        with open(template_path, 'r') as f:
            raw = f.read()
        context = Context({'model_name': self.model_name, 'app_name': self.app_name})
        template = Template(raw)
        return template.render(context)

    def _get_target_path(self):
        base = os.path.join(os.getcwd(), self.app_name)
        if self.component_type in ('permissions', 'pagination', 'importbase'):
            folder = os.path.join(base, 'utilities')
            os.makedirs(folder, exist_ok=True)
            return os.path.join(folder, f"{self.component_type}.py")
        if self.component_type == 'routers':
            folder = os.path.join(base, 'routers')
            os.makedirs(folder, exist_ok=True)
            return os.path.join(folder, 'routers.py')
        if self.component_type in ('serializers', 'viewsets') and self.subfolder:
            folder = os.path.join(base, self.subfolder)
            os.makedirs(folder, exist_ok=True)
            init_path = os.path.join(folder, '__init__.py')
            if not os.path.exists(init_path):
                with open(init_path, 'w') as f:
                    f.write("")
            # Professional naming: {model_name}_{component_type}.py
            filename = f"{self.model_name.lower()}_{self.component_type}.py"
            return os.path.join(folder, filename)
        if self.component_type == 'admin':
            return os.path.join(base, 'admin.py')
        return os.path.join(base, f"{self.component_type}.py")

    def _render_template(self):
        template_name = f"{self.component_type}.txt"
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', template_name)
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        with open(template_path, 'r') as f:
            raw = f.read()

        context_data = {
            'app_name': self.app_name,
            'model_name': self.model_name,
            'model_name_lower': self.model_name.lower() if self.model_name else '',
            'model_list_serializers': f"{self.model_name}ListSerializer" if self.model_name else '',
            'model_retrieve_serializers': f"{self.model_name}RetrieveSerializer" if self.model_name else '',
            'model_write_serializers': f"{self.model_name}WriteSerializer" if self.model_name else '',
            'viewset_name': f"{self.model_name}ViewSet" if self.model_name else '',
            'api_endpoint': self.model_name.lower() if self.model_name else '',
        }

        if self.component_type == 'routers':
            from django.apps import apps
            from .task import GenerationTask
            task = GenerationTask(self.app_name, 'routers')
            models = task._get_valid_models()
            context_data['models'] = [{'name': m.__name__, 'endpoint': m.__name__.lower()} for m in models]

        context = Context(context_data)
        template = Template(raw)
        return template.render(context)

    def _should_add_marker(self):
        return True