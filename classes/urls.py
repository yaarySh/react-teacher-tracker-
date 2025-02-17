from django.urls import path
from .views import (
    create_class,
    list_classes,
    delete_class,
    monthly_hours,
    update_class,
    get_class_details,
    list_classes_by_teacher,
    list_classes_by_date,
)

urlpatterns = [
    path("create/", create_class, name="create_class"),
    path("list/", list_classes, name="list_classes"),
    path("teacher/", list_classes_by_teacher, name="list_classes_by_teacher"),
    path("date/<str:date>/", list_classes_by_date, name="list_classes_by_date"),
    path("<int:class_id>/", get_class_details, name="get_class_details"),
    path("<int:class_id>/update/", update_class, name="update_class"),
    path("<int:class_id>/delete/", delete_class, name="delete_class"),
    path("monthly-hours/", monthly_hours, name="monthly_hours"),
]
