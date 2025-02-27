from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import make_aware
from datetime import datetime
from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from django.utils.timezone import now
from classrooms.models import Classroom
from teachers.serializers import TeacherSerializer
from .models import Class
from .serializers import ClassSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_class(request):
    # Extract classroom data from the request body
    classroom_data = request.data.get("classroom", {})
    grade_letter = classroom_data.get("grade_letter")
    class_number = classroom_data.get("class_number")

    # Get the existing classroom instance or return 404
    classroom = get_object_or_404(
        Classroom, grade_letter=grade_letter, class_number=class_number
    )

    # Create a new class instance and populate fields
    class_instance = Class(
        teacher=request.user,  # Set the teacher to the authenticated user
        classroom=classroom,  # Use the existing classroom instance
        period=request.data.get("period"),
        date=request.data.get("date"),
        attended=request.data.get("attended", False),
    )

    # Validate and save the instance
    try:
        class_instance.full_clean()  # Validate the instance
        class_instance.save()
        return Response(
            ClassSerializer(class_instance).data, status=status.HTTP_201_CREATED
        )
    except ValidationError as e:
        return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_classes(request):
    classes = Class.objects.all()
    serializer = ClassSerializer(classes, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_class(request, class_id):
    try:
        class_instance = Class.objects.get(id=class_id)

        # Check if the class belongs to the authenticated teacher
        if class_instance.teacher != request.user:
            return Response(
                {"error": "You are not authorized to delete this class."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check the attendance status before deletion
        current_attended_status = (
            class_instance.attended
        )  # Assuming 'attended' is the field representing attendance

        # Only decrement the teacher's monthly_hours if the class was marked as attended
        teacher = class_instance.teacher
        if current_attended_status:  # If it was attended, decrement monthly_hours
            teacher.monthly_hours -= 1
            teacher.save()

        # Now delete the class
        class_instance.delete()

        return Response(
            {"message": "Class deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
    except Class.DoesNotExist:
        return Response({"error": "Class not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_class(request, class_id):
    try:
        class_instance = Class.objects.get(id=class_id)
        if class_instance.teacher != request.user:
            return Response(
                {"error": "You are not authorized to update this class."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Update the 'attended' field if provided
        attended = request.data.get("attended")
        if attended is not None:
            class_instance.attended = attended

        # Update grade_letter, class_number, and date if provided
        grade_letter = request.data.get("grade_letter")
        class_number = request.data.get("class_number")
        date = request.data.get("date")

        if grade_letter:
            class_instance.classroom.grade_letter = grade_letter
        if class_number:
            class_instance.classroom.class_number = class_number
        if date:
            class_instance.date = date

        # Save the class instance after modifications
        class_instance.save()

        serializer = ClassSerializer(class_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Class.DoesNotExist:
        return Response({"error": "Class not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_class_details(request, class_id):
    try:
        class_instance = Class.objects.get(id=class_id)
        if class_instance.teacher != request.user:
            return Response(
                {"error": "You are not authorized to view this class."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ClassSerializer(class_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Class.DoesNotExist:
        return Response({"error": "Class not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_classes_by_teacher(request):
    teacher = request.user
    classes = Class.objects.filter(teacher=teacher)
    serializer = ClassSerializer(classes, many=True)
    return Response(
        {"data": serializer.data, "teacher": TeacherSerializer(request.user).data}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_classes_by_date(request, date):
    teacher = request.user  # Get the authenticated teacher
    classes = Class.objects.filter(
        date=date, teacher=teacher
    )  # Filter by both date and teacher
    serializer = ClassSerializer(classes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_hours(request):
    teacher = request.user  # Assuming the logged-in user is a Teacher
    classes = (
        Class.objects.filter(teacher=teacher)
        .values("date__year", "date__month")  # Group by year and month
        .annotate(total_hours=Count("id"))  # Count occurrences as total hours
        .order_by("-date__year", "-date__month")  # Order by recent months first
    )

    return Response(list(classes))
