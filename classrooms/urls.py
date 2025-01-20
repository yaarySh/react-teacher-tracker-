from django.urls import path
from .views import (
    create_classroom,
    delete_classroom,
    list_classrooms,
    get_classroom_by_grade_and_number,
)

urlpatterns = [
    path("add/", create_classroom, name="create_classroom"),
    path("list/", list_classrooms, name="list_classrooms"),
    path(
        "get/<str:grade_letter>/<int:class_number>/",
        get_classroom_by_grade_and_number,
        name="get_classroom_by_grade_and_number",
    ),
    path("delete/<int:classroom_id>/", delete_classroom, name="delete_classroom"),
]
