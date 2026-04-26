from django.core.management.base import BaseCommand
from django_magicapi.core.generator import ApiGenerator
from django_magicapi.core.utils import get_custom_apps

class Command(BaseCommand):
    help = "Remove all auto‑generated API files and router registrations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--app", nargs="+", type=str,
            help="App names to clean (if omitted, all custom apps are used)"
        )
        parser.add_argument(
            "--force", action="store_true",
            help="Force removal even if marker comments are missing (NOT recommended)"
        )

    def handle(self, *args, **options):
        apps_to_clean = options["app"] or get_custom_apps()
        if not apps_to_clean:
            self.stdout.write(self.style.WARNING("No apps specified and no custom apps found."))
            return

        for app_name in apps_to_clean:
            try:
                generator = ApiGenerator(app_name, force=options["force"])
                generator.clean()
                generator.unregister()
                self.stdout.write(self.style.SUCCESS(f"✓ Cleaned '{app_name}'"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed for '{app_name}': {e}"))