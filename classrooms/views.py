from django.shortcuts import render

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Classroom
from .serializers import ClassroomSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_classroom(request):
    serializer = ClassroomSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_classrooms(request):
    classrooms = Classroom.objects.all()
    serializer = ClassroomSerializer(classrooms, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_classroom_by_grade_and_number(request, grade_letter, class_number):
    # Fetch the classroom based on the grade letter and class number
    classroom = get_object_or_404(
        Classroom, grade_letter=grade_letter, class_number=class_number
    )
    serializer = ClassroomSerializer(classroom)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    classroom.delete()
    return Response(
        {"message": "Classroom deleted successfully."},
        status=status.HTTP_204_NO_CONTENT,
    )
