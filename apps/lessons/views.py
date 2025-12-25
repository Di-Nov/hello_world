from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Lesson, LessonStatus
from .serializers import LessonSerializer


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления уроками.

    Доступные действия:
    - GET /lessons/ - список уроков (учитель видит свои уроки, студент видит свои уроки)
    - POST /lessons/ - создание нового урока (текущий пользователь становится учителем)
    - GET /lessons/<int:pk>/ - просмотр конкретного урока
    - POST /lessons/<int:pk>/complete/ - завершение урока (только учитель)
    - POST /lessons/<int:pk>/cancel/ - отмена урока (только учитель)
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """При создании урока текущий пользователь становится учителем"""
        serializer.save(teacher=self.request.user)

    @swagger_auto_schema(
        operation_summary="Получить список уроков",
        operation_description="""
        Возвращает список уроков с возможностью фильтрации.
        В качестве теста даем возможно делать запрос всем 
        Тек же нет ограничений на возможность просмотра уроков других студентов и преподавателей.
        """,
        manual_parameters=[
            openapi.Parameter(
                "role",
                openapi.IN_QUERY,
                description="Роль пользователя: 'teacher' или 'student'",
                type=openapi.TYPE_STRING,
                enum=["teacher", "student"],
                default="student",
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Фильтр по статусу урока",
                type=openapi.TYPE_STRING,
                enum=["draft", "scheduled", "completed", "cancelled"],
            ),
            openapi.Parameter(
                "upcoming",
                openapi.IN_QUERY,
                description="Только предстоящие уроки",
                type=openapi.TYPE_BOOLEAN,
                default=False,
            ),
        ],
        responses={
            200: openapi.Response("Успешно", LessonSerializer(many=True)),
            401: openapi.Response("Не авторизован"),
        },
    )
    def list(self, request, *args, **kwargs):
        """GET /api/v1/lessons/ - список уроков"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Создать новый урок",
        operation_description="""
        Создает новый урок. 
        Текущий пользователь автоматически становится преподавателем (для теста).
        """,
        request_body=LessonSerializer,
        responses={
            201: openapi.Response("Урок создан", LessonSerializer),
            400: openapi.Response("Ошибка валидации"),
            401: openapi.Response("Не авторизован"),
        },
    )
    def create(self, request, *args, **kwargs):
        """POST /api/v1/lessons/ - создание урока"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(teacher=request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @swagger_auto_schema(
        operation_summary="Получить детали урока",
        operation_description="Возвращает полную информацию об уроке по ID.",
        responses={
            200: openapi.Response("Успешно", LessonSerializer),
            404: openapi.Response("Урок не найден"),
            401: openapi.Response("Не авторизован"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """GET /api/v1/lessons/{id}/ - детали урока"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Начать урок",
        request_body=no_body,
        responses={
            200: openapi.Response(
                description="Начинаем урок",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Начать урок"
                        ),
                        "lesson": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                                "status": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response("Невозможно отменить урок с текущим статусом"),
            403: openapi.Response("Только преподаватель может начать урок"),
            404: openapi.Response("Урок не найден"),
        },
    )
    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        """Начать урок"""
        lesson = self.get_object()
        if lesson.start_lesson():
            return Response({"status": "Урок начат"})
        else:
            return Response(
                {
                    "error": 'Не удалось начать урок. Урок должен быть в статусе "Запланирован"'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Завершить урок",
        request_body=no_body,
        responses={
            200: openapi.Response(
                description="Урок завершен",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Урок завершен"
                        ),
                        "lesson": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                                "status": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response("Невозможно завершить урок с текущим статусом"),
            403: openapi.Response("Только преподаватель может завершить урок"),
            404: openapi.Response("Урок не найден"),
        },
    )
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Завершить урок"""
        lesson = self.get_object()
        if lesson.complete_lesson():
            return Response({"status": "Урок завершен"})
        else:
            return Response(
                {"error": "Не удалось завершить урок. Урок должен быть в статусе 'В процессе'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Отменить урок",
        request_body=no_body,
        responses={
            200: openapi.Response(
                description="Урок отменен",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Урок отменен"
                        ),
                        "lesson": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                                "status": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response("Невозможно отменить урок с текущим статусом"),
            403: openapi.Response("Только преподаватель может отменить урок"),
            404: openapi.Response("Урок не найден"),
        },
    )
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Отменить урок"""
        lesson = self.get_object()
        if lesson.cancel_lesson():
            return Response({"status": "Урок отменен"})
        else:
            return Response(
                {"error": "Невозможно отменить завершенный или уже отмененный урок"},
                status=status.HTTP_400_BAD_REQUEST,
            )
