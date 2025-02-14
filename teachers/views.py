from datetime import datetime
from django.forms import ValidationError
from django.shortcuts import render

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from classes.models import Class
from .models import DailyHourEntry, Teacher  # Directly import Teacher model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import DailyHours


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


# Endpoint to update monthly hours (based on added hours)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_teacher_monthly_hours(request):
    teacher = request.user  # The logged-in teacher (the one making the request)
    new_hours = request.data.get("added monthly hours")

    if new_hours is None:
        return Response(
            {"error": "Hours are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        new_hours = int(new_hours)  # Ensure the hours are an integer
    except ValueError:
        return Response(
            {"error": "Invalid hours value. It must be an integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Ensure hours added is between 1 and 7
    if not (1 <= new_hours <= 7):
        return Response(
            {"error": "You can only add between 1 and 7 hours in one request."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if the teacher has already added hours for today
    today = request.data.get("date", None)
    if not today:
        today = str(datetime.date.today())

    daily_entry = DailyHourEntry.objects.filter(teacher=teacher, date=today).first()

    # If a daily entry already exists for today, check if we exceed the 7-hour limit
    if daily_entry:
        if daily_entry.hours_added + new_hours > 7:
            return Response(
                {"error": "You cannot add more than 7 hours for today."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Update the existing daily entry with the new hours
        daily_entry.hours_added += new_hours
        daily_entry.save()
    else:
        # If no entry exists for today, create a new daily entry
        DailyHourEntry.objects.create(
            teacher=teacher, date=today, hours_added=new_hours
        )

    # Update the teacher's monthly hours
    teacher.monthly_hours += new_hours
    teacher.save()

    return Response(
        {"message": f"Successfully updated monthly hours to {teacher.monthly_hours}."},
        status=status.HTTP_200_OK,
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_teacher_daily_schedule(request):
    teacher = request.user  # Get the currently logged-in teacher
    today = str(datetime.date.today())  # Get today's date

    # Get all classes taught by the teacher today
    classes_today = Class.objects.filter(teacher=teacher, schedule__date=today)

    # Get the teacher's total hours for today
    daily_entry = DailyHourEntry.objects.filter(teacher=teacher, date=today).first()

    total_hours_today = daily_entry.hours_added if daily_entry else 0

    # Prepare the response data
    class_list = [
        {"class_name": cls.name, "class_time": cls.schedule.time()}
        for cls in classes_today
    ]

    return Response(
        {
            "today_schedule": class_list,
            "total_hours_added": total_hours_today,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_teacher_monthly_hours(request):
    teacher = request.user  # Get the currently logged-in teacher
    current_month = datetime.date.today().month  # Get the current month

    # Get all daily hour entries for the current month
    monthly_entries = DailyHourEntry.objects.filter(
        teacher=teacher, date__month=current_month
    )

    total_hours_this_month = sum(entry.hours_added for entry in monthly_entries)

    return Response(
        {
            "total_hours_this_month": total_hours_this_month,
        },
        status=status.HTTP_200_OK,
    )


############################## New
User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_or_update_daily_hours(request):
    user = request.user  # Get the logged-in user
    date_str = request.data.get("date")  # Expecting 'YYYY-MM-DD'
    hours = request.data.get("hours", 0)  # Number of hours to add (or update)

    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Update or create a record for the given date
    daily_hours, created = DailyHours.objects.get_or_create(user=user, date=date)
    daily_hours.hours += int(hours)  # Add hours to existing or new record
    daily_hours.save()

    return Response(
        {
            "message": "Daily hours updated successfully",
            "user": user.username,
            "date": date,
            "total_hours": daily_hours.hours,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_monthly_hours(request, year, month):
    user = request.user
    start_date = datetime(year, month, 1).date()
    end_date = (
        datetime(year, month + 1, 1).date()
        if month < 12
        else datetime(year + 1, 1, 1).date()
    )

    daily_hours = DailyHours.objects.filter(
        user=user, date__gte=start_date, date__lt=end_date
    )
    total_hours = sum(entry.hours for entry in daily_hours)

    hours_by_date = [
        {"date": entry.date, "hours": entry.hours} for entry in daily_hours
    ]

    return Response(
        {
            "month": f"{start_date.strftime('%B %Y')}",
            "total_hours": total_hours,
            "daily_hours": hours_by_date,
        }
    )
