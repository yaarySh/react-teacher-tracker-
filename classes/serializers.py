from rest_framework import serializers
from .models import Class
from classrooms.models import Classroom
from classrooms.serializers import ClassroomSerializer
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer


class ClassSerializer(serializers.ModelSerializer):
    # Teacher field can be updated with teacher ID (no longer read-only)
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())

    # Serialize the classroom fully (using ClassroomSerializer)
    classroom = ClassroomSerializer(read_only=True)

    # Grade letter and class number are sourced from the related classroom
    grade_letter = serializers.CharField(
        source="classroom.grade_letter", read_only=True
    )
    class_number = serializers.IntegerField(
        source="classroom.class_number", read_only=True
    )

    class Meta:
        model = Class
        fields = [
            "id",
            "teacher",
            "classroom",
            "period",
            "date",
            "attended",
            "grade_letter",
            "class_number",
        ]

    def create(self, validated_data):
        # Logic to get the classroom based on grade_letter and class_number
        classroom = Classroom.objects.get(
            grade_letter=validated_data["grade_letter"],
            class_number=validated_data["class_number"],
        )
        validated_data["classroom"] = classroom
        # Save and return the created class
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle updating the teacher's monthly_hours or any other fields if needed
        teacher = validated_data.get("teacher", instance.teacher)
        if "teacher" in validated_data:
            # Example: Increase teacher's monthly_hours when the class is created/updated
            hours = validated_data.get("period", 0)  # Assuming period is in hours
            teacher.monthly_hours += hours
            teacher.save()  # Save the teacher after updating monthly_hours

        # Proceed with the regular update
        return super().update(instance, validated_data)


# class ClassSerializer(serializers.ModelSerializer):
#     teacher = TeacherSerializer()
#     classroom = ClassroomSerializer()

#     class Meta:
#         model = Class
#         fields = ["teacher", "classroom", "period", "date", "attended"]
