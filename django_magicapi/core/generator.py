import os
import shutil
from django.core.management import CommandError
from .task import GenerationTask
from .helper import FileWriter
from .utils import get_project_urls_path
from .url_manager import UrlManager

class ApiGenerator:
    TASKS = ['permissions', 'pagination', 'importbase', 'serializers', 'viewsets', 'admin', 'routers']

    def __init__(self, app_name, force=False):
        self.app_name = app_name
        self.force = force
        self.main_urls_path = get_project_urls_path()
        self.url_manager = UrlManager(self.main_urls_path, show_swagger=True)


    def generate(self):
        """Generate all API components and register the router."""
        self._create_api_components()
        self._register_router()

    def clean(self):
        """
        Delete all generated folders and files created by django-magicapi.
        Specifically removes serializers/, viewsets/, routers/, and utilities/.
        Also removes __pycache__ folders and .pyc files.
        """
        app_dir = os.path.join(os.getcwd(), self.app_name)
        if not os.path.exists(app_dir):
            print(f"App directory {app_dir} not found – skipping file deletion.")
            return

        # 1. Delete generated subdirectories entirely
        generated_folders = ['serializers', 'viewsets', 'routers', 'utilities']
        for folder in generated_folders:
            folder_path = os.path.join(app_dir, folder)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print(f"Removed folder: {folder_path}")

        # 2. Delete old monolithic files (from earlier versions)
        for old_file in ['serializers.py', 'viewsets.py']:
            full_path = os.path.join(app_dir, old_file)
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"Removed old file: {full_path}")

        # 3. Clean admin.py markers (keep the file itself)
        admin_path = os.path.join(app_dir, 'admin.py')
        if os.path.exists(admin_path):
            self._clean_admin_markers(admin_path)

        # 4. Remove __pycache__ and .pyc files
        self._clean_pycache(app_dir)

    def _clean_admin_markers(self, admin_path):
        """Remove all DJANGO_MAGICAPI_ADMIN_START/END blocks from admin.py."""
        with open(admin_path, 'r') as f:
            lines = f.readlines()
        new_lines = []
        skip = False
        for line in lines:
            if line.startswith('# DJANGO_MAGICAPI_ADMIN_START:'):
                skip = True
                continue
            if skip and line.startswith('# DJANGO_MAGICAPI_ADMIN_END:'):
                skip = False
                continue
            if not skip:
                new_lines.append(line)
        if len(new_lines) != len(lines):
            with open(admin_path, 'w') as f:
                f.writelines(new_lines)
            print(f"Removed magicapi admin markers from {admin_path}")

    def _clean_pycache(self, app_dir):
        """Recursively delete __pycache__ folders and .pyc files in the app directory."""
        for root, dirs, files in os.walk(app_dir):
            for dir_name in dirs:
                if dir_name == '__pycache__':
                    pycache_path = os.path.join(root, dir_name)
                    shutil.rmtree(pycache_path)
                    print(f"Removed: {pycache_path}")
            for file_name in files:
                if file_name.endswith('.pyc'):
                    pyc_path = os.path.join(root, file_name)
                    os.remove(pyc_path)
                    print(f"Removed: {pyc_path}")

    def unregister(self):
        self.url_manager.load_existing()
        self.url_manager.remove_router(self.app_name)
        self.url_manager.write()

    def _create_api_components(self):
        for task in self.TASKS:
            task_obj = GenerationTask(self.app_name, task, force=self.force)
            task_obj.run()

    def _register_router(self):
        self.url_manager.load_existing()
        self.url_manager.add_router(self.app_name)
        self.url_manager.write()

