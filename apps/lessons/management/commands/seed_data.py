import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.lessons.models import Lesson

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает тестовых пользователей и уроки'

    def handle(self, *args, **options):
        if User.objects.exists():
            print("Данные уже есть, пропускаем")
            return

        print("Создаем тестовые данные...")

        teachers = []
        students = []

        for i in range(1, 6):
            teacher = User.objects.create_user(
                username=f'teacher_{i}',
                password='123456',
                email=f'teacher{i}@mail.ru',
                first_name=f'Учитель_{i}',
                last_name='Тестовый',
            )
            teachers.append(teacher)
        print(f"Созданы 5 учителей")

        for i in range(1, 6):
            student = User.objects.create_user(
                username=f'student_{i}',
                password='123456',
                email=f'student{i}@mail.ru',
                first_name=f'Ученик_{i}',
                last_name='Тестовый'
            )
            students.append(student)
        print(f"Созданы 5 учеников")


        subjects = ['математике', 'физике', 'химии', 'английскому', 'истории',
                    'биологии', 'географии', 'литературе', 'информатике', 'музыке']

        statuses = ['draft', 'scheduled', 'completed', 'cancelled', 'in_progress']

        for i in range(10):
            teacher = random.choice(teachers)
            student = random.choice(students)

            days = random.randint(-5, 10)
            start = timezone.now() + timedelta(days=days)

            end = start + timedelta(hours=random.randint(1, 2))

            status = random.choice(statuses)

            if status == 'completed':
                start = timezone.now() - timedelta(days=random.randint(1, 10))
                end = start + timedelta(hours=2)

            Lesson.objects.create(
                title=f'Урок по {subjects[i]}',
                teacher=teacher,
                student=student,
                start_time=start,
                end_time=end,
                status=status
            )

        print(f"Создано 10 уроков")
