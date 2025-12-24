from django.urls import path

from . import views

app_name = "lessons"

urlpatterns = [
    path(
        "lessons/",
        views.LessonViewSet.as_view({"get": "list", "post": "create"}),
        name="lesson-list-create",
    ),
    path(
        "lessons/<int:pk>/",
        views.LessonViewSet.as_view(
            {
                "get": "retrieve",
            }
        ),
        name="lesson-detail",
    ),
    path(
        "lessons/<int:pk>/start/",
        views.LessonViewSet.as_view({"post": "start"}),
        name="lesson-start",
    ),
    path(
        "lessons/<int:pk>/complete/",
        views.LessonViewSet.as_view({"post": "complete"}),
        name="lesson-complete",
    ),
    path(
        "lessons/<int:pk>/cancel/",
        views.LessonViewSet.as_view({"post": "cancel"}),
        name="lesson-cancel",
    ),
]
