# GenerationTask (was BaseTask)
import warnings
from django.apps import apps
from .helper import FileWriter

class GenerationTask:
    """
    Handles the generation of a specific type of API component.
    """

    def __init__(self, app_name, task_type, force=False):
        self.app_name = app_name
        self.type = task_type
        self.force = force
        self.models = self._get_valid_models()  # only models with fields

    def run(self):
        """Execute the generation based on the task type."""
        # App‑level tasks (generate once)
        if self.type in ('permissions', 'pagination', 'importbase'):
            writer = FileWriter(self.app_name, self.type, force=self.force)
            writer.write()
            return

        # Router generation (app‑level, single file)
        if self.type == 'routers':
            writer = FileWriter(self.app_name, self.type, force=self.force)
            writer.write()
            return

        # Per‑model tasks: serializers, viewsets
        if self.type in ('serializers', 'viewsets'):
            if not self.models:
                warnings.warn(f"No models with fields in app '{self.app_name}'. Skipping '{self.type}'.")
                return
            for model in self.models:
                writer = FileWriter(
                    self.app_name,
                    self.type,
                    model_name=model.__name__,
                    force=self.force
                )
                writer.write()
            return

        # Unknown task type – ignore
        warnings.warn(f"Unknown task type '{self.type}' – skipping.")

    def _get_valid_models(self):
        """Return models that have at least one field."""
        try:
            app_config = apps.get_app_config(self.app_name)
        except LookupError:
            warnings.warn(f"App '{self.app_name}' not found in INSTALLED_APPS.")
            return []

        valid = []
        for model in app_config.get_models():
            if model._meta.get_fields():
                valid.append(model)
            else:
                warnings.warn(f"Model '{model.__name__}' has no fields. Skipping API generation for it.")
        return valid