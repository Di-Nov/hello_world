from .base import *

DEBUG = os.getenv('DEBUG', 'True')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', ['localhost', '127.0.0.1', '0.0.0.0'])

DATABASES['default']['HOST'] = 'localhost'

CELERY_BROKER_URL = os.getenv('REDIS_BROKER', 'redis://localhost:6379/0')
REDIS_BROKER = os.getenv('REDIS_BROKER', 'redis://localhost:6379/0')
CACHES['default']['LOCATION'] = 'redis://localhost:6379/1',