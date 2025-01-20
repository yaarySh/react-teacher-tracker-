# teachers/serializers.py
from rest_framework import serializers
from .models import Teacher


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        # Include first_name, last_name, and other fields you want to serialize
        fields = ["username", "password", "first_name", "last_name", "monthly_hours"]

    def create(self, validated_data):
        # Use the create_user method to create a Teacher user instance (which includes password hashing)
        teacher = Teacher.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            monthly_hours=validated_data.get(
                "monthly_hours", 0
            ),  # Default to 0 if not provided
        )
        return teacher
