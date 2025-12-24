import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")

app = Celery("core", broker=os.getenv("REDIS_BROKER", "redis://localhost:6379/0"))
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
app.conf.task_default_queue = "default"

app.conf.task_queues = {
    "default": {
        "exchange": "default",
        "routing_key": "default",
    },
}

app.conf.task_routes = {
    "*": {"queue": "default"},
}
