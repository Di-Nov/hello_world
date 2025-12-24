from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import generators, openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from core.settings.base import MEDIA_URL, MEDIA_ROOT


class BothHttpAndHttpsSchemaGenerator(generators.OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = settings.SWAGGER_SCHEMAS
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title='Lesson API',
        default_version='v1',
        description='API для управления уроками',
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(SessionAuthentication, BasicAuthentication),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.lessons.urls', namespace='v1')),

] + static(MEDIA_URL, document_root=MEDIA_ROOT)
