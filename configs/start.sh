#!/bin/bash

echo "Применяем миграции..."
python manage.py migrate

echo "Собираем статику..."
python manage.py collectstatic --noinput

echo "Создаем суперпользователя..."
python manage.py shell -c "from django.contrib.auth import get_user_model; u, created = get_user_model().objects.get_or_create(username='root', defaults={'email':'admin@example.com'}); u.set_password('root'); u.is_superuser=True; u.is_staff=True; u.save(); print('✅ Готово: root / root')"

echo "Заполняем тестовыми данными..."
python manage.py seed_data

echo "Запускаем Django сервер.."
exec gunicorn -c /app/configs/gunicorn.conf.py core.wsgi:application --bind 0.0.0.0:8000