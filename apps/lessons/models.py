import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger('lesson')

class LessonStatus(models.TextChoices):
    DRAFT = 'draft', 'Черновик'
    SCHEDULED = 'scheduled', 'Запланирован'
    IN_PROGRESS = 'in_progress', 'В процессе'
    COMPLETED = 'completed', 'Завершен'
    CANCELLED = 'cancelled', 'Отменен'


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название урока')
    description = models.TextField(verbose_name='Описание', blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons_taught', verbose_name='Преподаватель',)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons_attended', verbose_name='Студент')
    start_time = models.DateTimeField(verbose_name='Время начала урока')
    end_time = models.DateTimeField(verbose_name='Время окончания')
    status = models.CharField(max_length=20, choices=LessonStatus.choices, default=LessonStatus.DRAFT,verbose_name='Статус урока')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['-start_time']
        # indexes на данный момент избыточны
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='lesson_end_after_start'
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()} ({self.start_time:%d.%m.%Y %H:%M})"

    def clean(self):
        """Валидация модели перед сохранением."""
        super().clean()

        if self.end_time <= self.start_time:
            raise ValidationError({
                'end_time': 'Время окончания должно быть позже времени начала.'
            })

        if self.teacher_id == self.student_id:
            raise ValidationError({
                'teacher': 'Преподаватель и студент не могут быть одним и тем же пользователем.',
                'student': 'Преподаватель и студент не могут быть одним и тем же пользователем.'
            })

    def save(self, *args, **kwargs):
        """Переопределяем save для автоматической валидации."""
        self.full_clean()
        super().save(*args, **kwargs)


    @property
    def is_active(self):
        """Проверяет, активен ли урок в данный момент."""
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == LessonStatus.IN_PROGRESS

    def start_lesson(self):
        """Начинает урок."""
        if self.status == LessonStatus.SCHEDULED:
            self.status = LessonStatus.IN_PROGRESS
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False

    def complete_lesson(self):
        """Завершает урок."""
        if self.status in [LessonStatus.SCHEDULED, LessonStatus.IN_PROGRESS]:
            self.status = LessonStatus.COMPLETED
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False

    def cancel_lesson(self):
        """Отменяет урок."""
        if self.status in [LessonStatus.DRAFT, LessonStatus.SCHEDULED]:
            self.status = LessonStatus.CANCELLED
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False
