from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from classes.models import Class
from .models import Teacher
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(["POST"])
@permission_classes([AllowAny])
def register_teacher(request):
    username = request.data.get("username")
    password = request.data.get("password")
    confirmPassword = request.data.get("confirmPassword")

    # Ensure username, password, and name are provided
    if not username or not password or not confirmPassword:
        return Response(
            {"error": "Username, password and confirm password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if password != confirmPassword:
        return Response(
            {"error": "Password and confirm password do not match"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Create a new teacher user with the provided name
        teacher = Teacher.objects.create_user(
            username=username,
            password=password,
            # Storing the name in the first_name field
        )

        # Generate JWT token
        refresh = RefreshToken.for_user(teacher)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_teacher_by_id(request, teacher_id):
    try:
        # Retrieve the teacher using the provided teacher_id
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return Response(
            {"error": "Teacher not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Prepare the response data with the teacher's details
    teacher_data = {
        "id": teacher.id,
        "username": teacher.username,
        "first_name": teacher.first_name,
        "email": teacher.email,
        "monthly_hours": teacher.monthly_hours,
    }

    return Response(teacher_data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    teacher.delete()
    return Response(
        {"message": "Teacher deleted successfully."}, status=status.HTTP_204_NO_CONTENT
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_attendance(request, class_id):
    try:
        # Get the class instance
        class_instance = Class.objects.get(id=class_id)

        # Check if the logged-in user is the teacher of the class
        if class_instance.teacher != request.user:
            return Response(
                {"error": "You are not authorized to update this class."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the current and new attendance status
        new_attended_status = request.data.get("attended")
        current_attended_status = class_instance.attended

        # Update the attendance status
        class_instance.attended = new_attended_status
        class_instance.save()

        teacher = class_instance.teacher
        if new_attended_status and not current_attended_status:
            # Increment monthly hours if marking as attended
            teacher.monthly_hours += 1
        elif not new_attended_status and current_attended_status:
            # Decrement monthly hours if changing from attended to not attended
            teacher.monthly_hours -= 1

        teacher.save()

        return Response(
            {"message": "Attendance status updated and teacher hours adjusted."},
            status=status.HTTP_200_OK,
        )

    except Class.DoesNotExist:
        return Response({"error": "Class not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
