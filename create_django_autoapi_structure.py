#!/usr/bin/env python3
"""
create_django_autoapi_structure.py
Creates the folder and file skeleton for the django-autoapi package.
"""

import os

# Define the structure as a nested dictionary:
# key = path (relative), value = list of files (or subdirs with their own files)
STRUCTURE = {
    "django_autoapi": {
        "__init__.py": "",
        "management": {
            "__init__.py": "",
            "commands": {
                "__init__.py": "",
                "generate_api.py": "# Django management command to generate APIs\n",
                "clean_api.py": "# Optional: remove generated files\n",
            },
        },
        "core": {
            "__init__.py": "",
            "generator.py": "# ApiGenerator class\n",
            "task.py": "# GenerationTask (was BaseTask)\n",
            "helper.py": "# FileWriter (was BaseHelper)\n",
            "utils.py": "# helper functions (get_project_urls_path, get_custom_apps)\n",
        },
        "templates": {
            "permissions.txt": "# DjangoRestFramework permissions template\n",
            "pagination.txt": "# Pagination template\n",
            "importbase.txt": "# Base import template\n",
            "serializers.txt": "# Serializer templates\n",
            "viewsets.txt": "# ViewSet templates\n",
            "routers.txt": "# Router registration template\n",
        },
    }
}

def create_structure(base_path, struct):
    """Recursively create directories and files."""
    for name, content in struct.items():
        full_path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # It's a directory
            os.makedirs(full_path, exist_ok=True)
            create_structure(full_path, content)
        else:
            # It's a file – write content (or empty string)
            with open(full_path, 'w', encoding='utf-8') as f:
                if content:
                    f.write(content)
            print(f"Created file: {full_path}")

if __name__ == "__main__":
    # Create the structure in the current working directory
    create_structure(".", STRUCTURE)
    print("\n django_autoapi folder structure created successfully.")