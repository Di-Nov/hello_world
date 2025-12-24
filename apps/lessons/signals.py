import logging
import time

from django.core.cache import cache
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Lesson, LessonStatus
from .tasks import (
    send_lesson_cancelled_notification,
    send_lesson_completed_notification,
    send_lesson_created_notification,
    send_lesson_started_notification,
)

logger = logging.getLogger("lessons")


@receiver(pre_save, sender=Lesson)
def cache_old_status_redis(sender, instance, **kwargs):
    """Сохраняем старый статус в Redis с уникальным ключом."""
    if instance.pk:
        try:
            old_lesson = Lesson.objects.get(pk=instance.pk)
            timestamp = int(time.time() * 1000)
            cache_key = f"lesson_old_status_{instance.pk}_{timestamp}"
            cache.set(cache_key, old_lesson.status, timeout=10)
            instance._cache_key = cache_key
        except Lesson.DoesNotExist:
            pass


@receiver(post_save, sender=Lesson)
def lesson_post_save(sender, instance: Lesson, created, **kwargs):
    """Обрабатываем создание урока или изменение статуса и запускаем нужную celery задачу."""
    try:
        logger.info(f"Lesson {instance.id} {'created' if created else 'updated'}")
        if created:
            send_lesson_created_notification.delay(instance.id)
        else:
            cache_key = getattr(instance, "_cache_key", None)
            if cache_key:
                old_status = cache.get(cache_key)
                cache.delete(cache_key)
                if old_status and old_status != instance.status:
                    if instance.status == LessonStatus.COMPLETED:
                        send_lesson_completed_notification.delay(instance.id)
                    elif instance.status == LessonStatus.IN_PROGRESS:
                        send_lesson_started_notification.delay(instance.id)
                    elif instance.status == LessonStatus.CANCELLED:
                        send_lesson_cancelled_notification.delay(instance.id)
    except Lesson.DoesNotExist:
        pass
