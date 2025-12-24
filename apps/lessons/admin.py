from django.contrib import admin

from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'teacher',
        'student',
        'start_time',
        'end_time',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'teacher',
        'student',
    )

    search_fields = (
        'title',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    actions = ['mark_as_completed', 'mark_as_cancelled']

    def mark_as_completed(self, request, queryset):
        """Завершение уроков."""
        count = 0
        for lesson in queryset:
            if lesson.complete_lesson():
                count += 1

        self.message_user(
            request,
            f'Успешно завершено {count} уроков.'
        )

    mark_as_completed.short_description = "Завершить выбранные уроки"

    def mark_as_cancelled(self, request, queryset):
        """Отмена уроков."""
        count = 0
        for lesson in queryset:
            if lesson.cancel_lesson():
                count += 1

        self.message_user(
            request,
            f'Успешно отменено {count} уроков.'
        )

    mark_as_cancelled.short_description = "Отменить выбранные уроки"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('teacher', 'student')