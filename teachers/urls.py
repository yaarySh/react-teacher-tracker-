from django.urls import path
from .views import (
    get_teacher_by_id,
    register_teacher,
    update_attendance,
    # Import the submit_attendance view
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("register/", register_teacher, name="register_teacher"),
    path("login/", TokenObtainPairView.as_view(), name="access_token"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("teacher/<int:teacher_id>/", get_teacher_by_id, name="get_teacher_by_id"),
    path("class/<int:class_id>/update/", update_attendance, name="update_attendance"),
]
