from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Application, Profile, TutoringRequest


class TutoringTests(TestCase):
    def setUp(self):
        # Create users and their roles before each test.
        self.student = User.objects.create_user(username="student")
        self.tutor = User.objects.create_user(username="tutor")
        self.tutor2 = User.objects.create_user(username="tutor2")

        Profile.objects.create(user=self.student, role="student")
        Profile.objects.create(user=self.tutor, role="tutor")
        Profile.objects.create(user=self.tutor2, role="tutor")

        self.request = TutoringRequest.objects.create(
            student=self.student,
            subject="Math",
            availability="Monday after 5 PM",
            description="Help with algebra",
            budget=20,
        )

    # Happy path: a tutor can apply.
    def test_tutor_can_apply(self):
        application = self.request.apply(self.tutor, "I can help.")

        self.assertEqual(application.status, Application.PENDING)
        self.assertEqual(application.tutor, self.tutor)
        self.assertEqual(self.request.applications.count(), 1)

    # Happy path: accepting one tutor closes the request.
    def test_accept_tutor(self):
        chosen = self.request.apply(self.tutor)
        other = self.request.apply(self.tutor2)

        self.request.accept(chosen)

        self.request.refresh_from_db()
        chosen.refresh_from_db()
        other.refresh_from_db()

        self.assertEqual(self.request.status, TutoringRequest.CLOSED)
        self.assertEqual(chosen.status, Application.ACCEPTED)
        self.assertEqual(other.status, Application.REJECTED)

    # Sad path: a tutor cannot apply twice.
    def test_duplicate_application(self):
        self.request.apply(self.tutor)

        with self.assertRaisesMessage(
            ValidationError, "You already applied to this request."
        ):
            self.request.apply(self.tutor)

        self.assertEqual(self.request.applications.count(), 1)

    # Sad path: students cannot apply as tutors.
    def test_student_cannot_apply(self):
        with self.assertRaisesMessage(
            ValidationError, "Only tutors can apply."
        ):
            self.request.apply(self.student)

        self.assertEqual(self.request.applications.count(), 0)

    # Sad path: a closed request cannot receive applications.
    def test_cannot_apply_to_closed_request(self):
        application = self.request.apply(self.tutor)
        self.request.accept(application)

        with self.assertRaisesMessage(
            ValidationError, "This request is closed."
        ):
            self.request.apply(self.tutor2)

        self.assertEqual(self.request.applications.count(), 1)