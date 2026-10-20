from decimal import Decimal
from django.core.validators import MinValueValidator

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def get_role(user):
    """Return 'student', 'tutor', or None. Superusers/staff are the admin role."""
    profile = getattr(user, "profile", None)
    return profile.role if profile else None


class Profile(models.Model):
    ROLE_CHOICES = [("student", "Student"), ("tutor", "Tutor")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class TutoringRequest(models.Model):
    OPEN, CLOSED = "open", "closed"
    STATUS_CHOICES = [(OPEN, "Open"), (CLOSED, "Closed")]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    subject = models.CharField(max_length=100)
    availability = models.CharField(max_length=200, help_text="e.g. Weekdays after 5pm")
    budget = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Max hourly rate in USD",
    )
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject

    def apply(self, tutor, message=""):
        """Business rules for a tutor applying to this request."""
        if get_role(tutor) != "tutor":
            raise ValidationError("Only tutors can apply.")
        if tutor == self.student:
            raise ValidationError("You can't apply to your own request.")
        if self.status != self.OPEN:
            raise ValidationError("This request is closed.")
        if self.applications.filter(tutor=tutor).exists():
            raise ValidationError("You already applied to this request.")
        return Application.objects.create(
            tutoring_request=self, tutor=tutor, message=message
        )

    def accept(self, application):
        """Accept one application: reject the rest and close the request."""
        if self.status != self.OPEN:
            raise ValidationError("This request is already closed.")
        if application.tutoring_request_id != self.id:
            raise ValidationError("That application doesn't belong to this request.")
        self.applications.exclude(pk=application.pk).update(status=Application.REJECTED)
        application.status = Application.ACCEPTED
        application.save()
        self.status = self.CLOSED
        self.save()


class Application(models.Model):
    PENDING, ACCEPTED, REJECTED = "pending", "accepted", "rejected"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
    ]

    tutoring_request = models.ForeignKey(
        TutoringRequest, on_delete=models.CASCADE, related_name="applications"
    )
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tutoring_request", "tutor"], name="one_application_per_tutor"
            )
        ]

    def __str__(self):
        return f"{self.tutor.username} -> {self.tutoring_request.subject}"
