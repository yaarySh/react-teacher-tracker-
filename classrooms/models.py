from django.db import models


class Classroom(models.Model):
    grade_letter = models.CharField(
        max_length=1, null=True
    )  # Supports letters like א, ב, etc.
    class_number = models.IntegerField(null=True)  # Supports numbers like 1, 2, etc.
    building_name = models.CharField(max_length=100)
    floor_number = models.IntegerField()

    class Meta:
        unique_together = (
            "grade_letter",
            "class_number",
        )  # Ensures unique combinations

    def __str__(self):
        return f"{self.grade_letter}{self.class_number}"
