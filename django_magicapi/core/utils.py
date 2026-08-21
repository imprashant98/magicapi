# helper functions (get_project_urls_path, get_custom_apps)
import os
from django.apps import apps

def get_project_urls_path():
    """
    Return the absolute path to the main urls.py of the Django project.
    Uses settings.ROOT_URLCONF to locate the file safely.
    """
    from django.conf import settings
    import importlib

    try:
        url_module = importlib.import_module(settings.ROOT_URLCONF)
        return os.path.abspath(url_module.__file__)
    except Exception as e:
        raise RuntimeError(f"Could not locate project urls.py using ROOT_URLCONF: {e}")

def get_custom_apps():
    """
    Return a list of app labels for apps that are part of the project
    (i.e., not Django contrib or third‑party packages).
    """
    custom_apps = []
    try:
        project_module_name = _get_project_module_name()
    except RuntimeError:
        return []

    for app_config in apps.get_app_configs():
        app_module_name = app_config.module.__name__
        # If the app's module lives inside the project directory, consider it custom
        # This is a heuristic – adjust as needed.
        app_path = app_config.path
        if os.path.exists(os.path.join(project_module_name, app_module_name)):
            custom_apps.append(app_config.label)
        else:
            # Alternatively, check if the app path is under the project root
            if os.path.commonpath([project_module_name, app_path]) == project_module_name:
                custom_apps.append(app_config.label)
    return custom_apps

def _get_project_module_name():
    """
    Find the project's base directory (where manage.py resides) and return its absolute path.
    """
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, 'manage.py')):
        return cwd
    # Fallback: walk up until we find manage.py
    path = cwd
    while path != '/':
        if os.path.exists(os.path.join(path, 'manage.py')):
            return path
        path = os.path.dirname(path)
    raise RuntimeError("Could not locate manage.py")