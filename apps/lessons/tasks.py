import time

from celery import shared_task
from celery.utils.log import get_task_logger
from .models import Lesson

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def send_lesson_created_notification(self, lesson_id):
    """Уведомление о создании урока"""
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        message = f"Урок создан: '{lesson.title}' {lesson_id}, для студента {lesson.student_id}"
        logger.info(f"[CELERY] {message}")
        time.sleep(5)
        message_success = f"Уведомление по уроку: '{lesson.title}' {lesson_id}, для студента {lesson.student_id} успешно отправлено"
        logger.info(f"[CELERY] {message_success}")
        return {'status': 'success', 'task': 'lesson_created', 'lesson_id': lesson_id}

    except Lesson.DoesNotExist:
        logger.warning(f"Lesson {lesson_id} не найден")
        return {'status': 'skipped', 'reason': 'lesson_not_found'}
    except Exception as exc:
        logger.error(f"Ошибка: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_lesson_started_notification(self, lesson_id):
    """Уведомление о начале урока"""
    try:
        lesson = Lesson.objects.get(id=lesson_id)

        message = f"Урок начался: '{lesson.title}'"
        logger.info(f"[CELERY] {message}")
        time.sleep(5)
        message_success = f"Уведомление о завершении урока: '{lesson.title}' {lesson_id}, для студента {lesson.student_id} успешно отправлено"
        logger.info(f"[CELERY] {message_success}")

        return {'status': 'success', 'task': 'lesson_completed', 'lesson_id': lesson_id}

    except Lesson.DoesNotExist:
        logger.warning(f"Lesson {lesson_id} не найден")
        return {'status': 'skipped', 'reason': 'lesson_not_found'}
    except Exception as exc:
        logger.error(f"Ошибка: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_lesson_completed_notification(self, lesson_id):
    """Уведомление о завершении урока"""
    try:
        lesson = Lesson.objects.get(id=lesson_id)

        message = f"Урок завершен: '{lesson.title}'"
        logger.info(f"[CELERY] {message}")
        time.sleep(5)
        message_success = f"Уведомление о завершении урока: '{lesson.title}' {lesson_id}, для студента {lesson.student_id} успешно отправлено"
        logger.info(f"[CELERY] {message_success}")

        return {'status': 'success', 'task': 'lesson_completed', 'lesson_id': lesson_id}

    except Lesson.DoesNotExist:
        logger.warning(f"Lesson {lesson_id} не найден")
        return {'status': 'skipped', 'reason': 'lesson_not_found'}
    except Exception as exc:
        logger.error(f"Ошибка: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_lesson_cancelled_notification(self, lesson_id):
    """Уведомление об отмене урока"""
    try:
        lesson = Lesson.objects.get(id=lesson_id)

        message = f"Урок отменен: '{lesson.title}'"
        logger.info(f"[CELERY] {message}")
        time.sleep(5)
        message_success = f"Уведомление об отмене урока: '{lesson.title}' {lesson_id}, для студента {lesson.student_id} успешно отправлено"
        logger.info(f"[CELERY] {message_success}")
        return {'status': 'success', 'task': 'lesson_cancelled', 'lesson_id': lesson_id}

    except Lesson.DoesNotExist:
        logger.warning(f"Lesson {lesson_id} не найден")
        return {'status': 'skipped', 'reason': 'lesson_not_found'}
    except Exception as exc:
        logger.error(f"Ошибка: {exc}")
        raise self.retry(exc=exc, countdown=60)
