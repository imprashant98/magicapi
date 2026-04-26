from django.core.management.base import BaseCommand, CommandError
from django_magicapi.core.generator import ApiGenerator
from django_magicapi.core.utils import get_custom_apps

class Command(BaseCommand):
    help = "Generate or clean DRF API components using django-magicapi"

    def add_arguments(self, parser):
        parser.add_argument(
            "--app", nargs="+", type=str,
            help="App names to process (if omitted, all custom apps are used)"
        )
        parser.add_argument(
            "--clean", action="store_true",
            help="Remove generated files and router registration instead of generating"
        )
        parser.add_argument(
            "--force", action="store_true",
            help="Overwrite user-created files (dangerous - use with caution)"
        )

    def handle(self, *args, **options):
        if options["clean"]:
            self._clean_apps(options["app"], options["force"])
            return

        apps_to_generate = options["app"] or get_custom_apps()
        if not apps_to_generate:
            self.stdout.write(self.style.WARNING("No apps specified and no custom apps found."))
            return

        for app_name in apps_to_generate:
            try:
                generator = ApiGenerator(app_name, force=options["force"])
                generator.generate()
                self.stdout.write(self.style.SUCCESS(f"✓ API generated for '{app_name}'"))
            except CommandError as e:
                self.stderr.write(self.style.ERROR(str(e)))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed for '{app_name}': {e}"))

    def _clean_apps(self, app_names, force):
        apps_to_clean = app_names or get_custom_apps()
        for app_name in apps_to_clean:
            try:
                generator = ApiGenerator(app_name, force=force)
                generator.clean()
                generator.unregister()
                self.stdout.write(self.style.SUCCESS(f"✓ Cleaned '{app_name}'"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to clean '{app_name}': {e}"))