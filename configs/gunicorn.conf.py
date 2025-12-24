"""gunicorn WSGI server configuration."""


def max_workers():
    return 1


bind = "0.0.0.0:8000"
timeout = 90
max_requests = 1000
max_requests_jitter = 50
worker_class = "sync"
workers = max_workers()
