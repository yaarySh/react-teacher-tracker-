import datetime
from django.db import models
from teachers.models import Teacher
from classrooms.models import Classroom


class Class(models.Model):
    CLASS_PERIOD_CHOICES = [(i, f"Period {i}") for i in range(1, 7)]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    period = models.PositiveSmallIntegerField(choices=CLASS_PERIOD_CHOICES, default=1)
    date = models.DateField(
        default=datetime.date.today
    )  # To track when this schedule was created
    attended = models.BooleanField(
        default=False
    )  # Whether the teacher attended this class

    def __str__(self):
        return f"Period {self.period} on {self.date} in {self.classroom} taught by {self.teacher}"
