from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings  # Import settings to use AUTH_USER_MODEL


class Teacher(AbstractUser):  # Now extending AbstractUser
    monthly_hours = models.PositiveIntegerField(default=0)

    REQUIRED_FIELDS = [
        "monthly_hours",
    ]  # Fields that are required for creating a superuser

    def __str__(self):
        return self.username  # Or you can return self.name if that's what you want


class DailyHourEntry(models.Model):
    # Foreign key to Teacher model
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    hours_added = models.PositiveIntegerField()

    class Meta:
        # Ensuring there is only one entry per teacher per day
        unique_together = ("teacher", "date")

    def __str__(self):
        return f"{self.teacher.username} - {self.date}: {self.hours_added} hours"


#################################new
class DailyHours(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )  # Updated to use custom user model
    date = models.DateField()  # Store the specific date
    hours = models.PositiveIntegerField(default=0)  # Store the number of hours worked

    class Meta:
        unique_together = (
            "user",
            "date",
        )  # Prevent duplicate records for the same user and date

    def __str__(self):
        return f"{self.user} - {self.date} - {self.hours} hours"
