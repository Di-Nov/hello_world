from rest_framework import serializers

from .models import Lesson, User


class LessonSerializer(serializers.ModelSerializer):
    """Общий сериализатор для всех операций"""
    teacher = serializers.PrimaryKeyRelatedField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'teacher', 'student', 'start_time', 'end_time', 'status', 'created_at']
        read_only_fields = ['created_at']

    def __str__(self):
        """Для совместимости с Swagger"""
        return f"LessonSerializer for {self.Meta.model.__name__}"

    def to_representation(self, instance: Lesson):
        """Преобразование для JSON"""
        data = super().to_representation(instance)
        return data

    def validate(self, data):
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("Время окончания должно быть позже времени начала")

        if 'teacher' in data and self.context['request'].user != data['teacher']:
            raise serializers.ValidationError("Вы можете создавать уроки только за себя как преподаватель")

        return data