from django.db import models
from django.conf import settings
from questions.models import Subject
from datetime import timedelta

User = settings.AUTH_USER_MODEL


class MentorshipSettings(models.Model):
    cost_per_question = models.DecimalField(
        max_digits=10, decimal_places=2, default=10.00, help_text="XamCoins required per question."
    )
    max_cost_30_minutes = models.DecimalField(
        max_digits=10, decimal_places=2, default=50.00, help_text="Maximum XamCoins for a 30-minute mentorship session."
    )
    max_cost_60_minutes = models.DecimalField(
        max_digits=10, decimal_places=2, default=100.00, help_text="Maximum XamCoins for a 60-minute mentorship session."
    )

    def __str__(self):
        return "Mentorship Settings"


class Question(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="mentorship_questions")
    content = models.TextField(help_text="The question content.")
    created_at = models.DateTimeField(auto_now_add=True)
    answered = models.BooleanField(default=False)

    def __str__(self):
        return f"Question by {self.student.email} on {self.subject.name}"


class MentorAvailability(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mentor_availability")
    start_time = models.DateTimeField(help_text="Start time of availability.")
    end_time = models.DateTimeField(help_text="End time of availability.")
    is_booked = models.BooleanField(default=False, help_text="Is this time slot booked?")

    def __str__(self):
        return f"Availability of {self.teacher.email} from {self.start_time} to {self.end_time}"


class MentorshipSession(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mentorship_sessions")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(choices=[(30, "30 minutes"), (60, "60 minutes")])
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Session: {self.student.email} with {self.teacher.email} at {self.start_time}"
