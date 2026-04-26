# helper functions (get_project_urls_path, get_custom_apps)
import os
from django.apps import apps

def get_project_urls_path():
    """
    Return the absolute path to the main urls.py of the Django project.
    Assumes the current working directory is the project root (where manage.py lives).
    """
    cwd = os.getcwd()
    # Try to find manage.py
    if not os.path.exists(os.path.join(cwd, 'manage.py')):
        raise RuntimeError("manage.py not found in current directory. Are you in the project root?")
    # Find the project module name (the directory containing settings.py)
    for item in os.listdir(cwd):
        if item.endswith('.py'):
            continue
        potential_settings = os.path.join(cwd, item, 'settings.py')
        if os.path.exists(potential_settings):
            project_name = item
            break
    else:
        raise RuntimeError("Could not locate settings.py in any subdirectory.")
    return os.path.join(cwd, project_name, 'urls.py')

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