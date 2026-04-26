# ApiGenerator class
import os
from django.core.management import CommandError
from .task import GenerationTask
from .helper import FileWriter
from .utils import get_project_urls_path

class ApiGenerator:
    """
    Main class for generating DRF API components for a Django app.
    """

    # Tasks are processed in this order.
    # 'permissions', 'pagination', 'importbase' are app‑level (once).
    # 'serializers' and 'viewsets' are per‑model.
    # 'routers' is app‑level (creates a single routers.py).
    TASKS = ['permissions', 'pagination', 'importbase', 'serializers', 'viewsets', 'routers']

    def __init__(self, app_name, force=False):
        self.app_name = app_name
        self.force = force
        self.main_urls_path = get_project_urls_path()
        self._generated_files = set()

    def generate(self):
        """Generate all API components and register the router."""
        self._create_api_components()
        self._record_generated_files()
        self._register_router()

    def clean(self):
        """
        Delete all generated files that were created by this generator.
        If `force` is True, removes the files even without the marker comment.
        """
        for file_path in list(self._generated_files):
            if os.path.exists(file_path):
                should_remove = False
                if self.force:
                    should_remove = True
                else:
                    with open(file_path, 'r') as f:
                        first_line = f.readline()
                    if first_line.startswith('# DJANGO_AUTOAPI_GENERATED'):
                        should_remove = True
                if should_remove:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                else:
                    print(f"Skip (user file, use --force to override): {file_path}")

    def unregister(self):
        """Remove router registration from the project's urls.py."""
        if not os.path.exists(self.main_urls_path):
            return

        with open(self.main_urls_path, 'r') as f:
            lines = f.readlines()

        marker = f"# DJANGO_AUTOAPI_REGISTERED:{self.app_name}\n"
        new_lines = []
        removed = False
        i = 0
        while i < len(lines):
            if lines[i] == marker:
                # skip marker line
                i += 1
                # skip the following urlpatterns.append line if it exists
                if i < len(lines) and 'urlpatterns.append' in lines[i]:
                    i += 1
                removed = True
                continue
            new_lines.append(lines[i])
            i += 1

        if removed:
            # Also remove the import line for this app's router if no other references remain
            import_line = f"from {self.app_name}.routers.routers import router as {self.app_name}_router\n"
            if import_line in new_lines and new_lines.count(import_line) == 1:
                new_lines.remove(import_line)

            with open(self.main_urls_path, 'w') as f:
                f.writelines(new_lines)
            print(f"Unregistered router for '{self.app_name}'")
        else:
            print(f"No registration found for '{self.app_name}'")

    # -------------------------------------------------------------------------
    # Internal methods
    # -------------------------------------------------------------------------
    def _create_api_components(self):
        for task in self.TASKS:
            task_obj = GenerationTask(self.app_name, task, force=self.force)
            task_obj.run()

    def _record_generated_files(self):
        """Collect paths of generated files (based on what FileWriter would create)."""
        app_dir = os.path.join(os.getcwd(), self.app_name)
        # Utility files
        for util in ['permissions', 'pagination', 'importbase']:
            path = os.path.join(app_dir, 'utilities', f"{util}.py")
            if os.path.exists(path):
                self._generated_files.add(path)
        # Serializers, viewsets, routers
        for fname in ['serializers.py', 'viewsets.py', 'routers.py']:
            path = os.path.join(app_dir, fname)
            if os.path.exists(path):
                self._generated_files.add(path)

    def _register_router(self):
        """Idempotent router registration with import and urlpatterns fixes."""
        if not os.path.exists(self.main_urls_path):
            raise FileNotFoundError(f"urls.py not found at {self.main_urls_path}")

        with open(self.main_urls_path, 'r') as f:
            content = f.read()

        marker = f"# DJANGO_AUTOAPI_REGISTERED:{self.app_name}"
        if marker in content:
            return  # already registered

        # Ensure imports
        if 'from django.urls import path' not in content or 'from django.urls import include' not in content:
            content = self._add_imports(content)

        # Ensure urlpatterns exists
        if 'urlpatterns = [' not in content and 'urlpatterns = (' not in content:
            content = content.rstrip() + "\n\nurlpatterns = []\n"

        # Build registration snippet
        snippet = f"""
{marker}
from {self.app_name}.routers.routers import router as {self.app_name}_router
urlpatterns.append(path('api/', include({self.app_name}_router.urls)))
"""
        # Append safely
        with open(self.main_urls_path, 'w') as f:
            f.write(content.rstrip() + '\n' + snippet)

    @staticmethod
    def _add_imports(content):
        lines = content.splitlines()
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('#!') or line.startswith('# -*-'):
                insert_pos = i + 1
            else:
                break
        lines.insert(insert_pos, "from django.urls import path, include")
        return '\n'.join(lines)