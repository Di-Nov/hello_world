from django.apps import AppConfig


class LessonsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.lessons"
    verbose_name = "Уроки и уведомления"

    def ready(self):
        from . import signals
