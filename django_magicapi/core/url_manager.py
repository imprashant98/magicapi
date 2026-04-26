import os
import re

class UrlManager:
    MARKER_START = "# BEGIN DJANGO_MAGICAPI_URLS"
    MARKER_END = "# END DJANGO_MAGICAPI_URLS"

    def __init__(self, urls_path, show_swagger=True):
        self.urls_path = urls_path
        self.show_swagger = show_swagger
        self.app_routers = []

    def add_router(self, app_name):
        entry = (app_name, f"{app_name}.routers.routers")
        if entry not in self.app_routers:
            self.app_routers.append(entry)

    def remove_router(self, app_name):
        self.app_routers = [(n, i) for (n, i) in self.app_routers if n != app_name]

    def write(self):
        if not os.path.exists(self.urls_path):
            raise FileNotFoundError(f"urls.py not found at {self.urls_path}")

        with open(self.urls_path, 'r') as f:
            content = f.read()

        # Remove any existing magic block
        new_content = re.sub(
            rf"{self.MARKER_START}.*?{self.MARKER_END}\n?",
            '',
            content,
            flags=re.DOTALL
        )
        new_content = re.sub(r'\n\s*\n+', '\n\n', new_content).strip()

        # No routers and Swagger disabled → only clean the file
        if not self.app_routers and not self.show_swagger:
            with open(self.urls_path, 'w') as f:
                f.write(new_content + '\n')
            return

        block = self._build_block()
        if not new_content.endswith('\n'):
            new_content += '\n'
        final_content = new_content + block

        with open(self.urls_path, 'w') as f:
            f.write(final_content)

    def _build_block(self):
        imports = [
            "from django.urls import path, include",
            "from django.shortcuts import redirect",
            "from django.http import HttpResponse",
            "from rest_framework import routers",
            "from django.conf import settings",
            "from django.conf.urls.static import static",
        ]

        # Smart drf_yasg handling: imports + runtime template availability check
        drf_yasg_imports = [
            "try:",
            "    from drf_yasg.views import get_schema_view",
            "    from drf_yasg import openapi",
            "    from rest_framework import permissions",
            "    from django.template import TemplateDoesNotExist",
            "    DRF_YASG_AVAILABLE = True",
            "except ImportError:",
            "    DRF_YASG_AVAILABLE = False",
            "    def get_schema_view(**kwargs):",
            "        return None",
        ]
        import_lines = "\n".join(imports + drf_yasg_imports)

        router_lines = []
        if self.app_routers:
            router_lines.append("main_router = routers.DefaultRouter()")
            for app_name, _ in self.app_routers:
                router_lines.append(f"from {app_name}.routers.routers import router as {app_name}_router")
                router_lines.append(f"main_router.registry.extend({app_name}_router.registry)")
        else:
            router_lines.append("main_router = routers.DefaultRouter()")

        # This code creates a safe schema_view that never raises TemplateDoesNotExist
        schema_view_code = """def get_safe_swagger_view():
    if not DRF_YASG_AVAILABLE:
        return None
    try:
        # Try to create the schema view – this may fail if drf_yasg templates are not found
        schema_view = get_schema_view(
            openapi.Info(
                title="API",
                default_version='v1',
                description="Auto-generated API",
                terms_of_service="",
                contact=openapi.Contact(email=""),
                license=openapi.License(name="MIT"),
            ),
            public=True,
            permission_classes=[permissions.AllowAny],
        )
        # Test if the Swagger template can be loaded (to catch missing INSTALLED_APPS)
        from django.template import loader
        loader.get_template('drf_yasg/swagger-ui.html')
        return schema_view
    except (TemplateDoesNotExist, Exception):
        # Swagger is not properly configured (e.g., drf_yasg not in INSTALLED_APPS)
        return None

schema_view = get_safe_swagger_view()

def swagger_placeholder(request):
    return HttpResponse(
        "Swagger UI is not available.\\n"
        "Please make sure 'drf_yasg' is installed and added to INSTALLED_APPS. and also check if templates are properly configured.",
        content_type="text/plain",
        status=501,
    )
"""

        url_items = []
        if self.app_routers:
            url_items.append("path('api/v1/', include(main_router.urls))")
        url_items.append("path('api-auth/', include('rest_framework.urls'))")

        if self.show_swagger:
            url_items.append(
                "path('swagger/', schema_view.with_ui('swagger', cache_timeout=0) "
                "if schema_view else swagger_placeholder, name='schema-swagger-ui')"
            )
            url_items.append(
                "path('redoc/', schema_view.with_ui('redoc', cache_timeout=0) "
                "if schema_view else swagger_placeholder, name='schema-redoc')"
            )

        url_items.append("path('', lambda request: redirect('/swagger/'))")

        urlpatterns_lines = [
            "urlpatterns += [",
            "    " + ",\n    ".join(url_items) + ",",
            "]",
            "if settings.DEBUG:",
            "    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)",
            "    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)",
        ]
        urlpatterns_update = "\n".join(urlpatterns_lines)

        block_lines = [
            self.MARKER_START,
            "# Auto-generated by django-magicapi - DO NOT EDIT MANUALLY",
            import_lines,
            "",
            "\n".join(router_lines),
            "",
            schema_view_code,
            "",
            urlpatterns_update,
            self.MARKER_END,
        ]
        return "\n".join(block_lines) + "\n"