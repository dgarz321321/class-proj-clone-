from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Application, Profile, TutoringRequest


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

    def save(self, commit=True):
        user = super().save(commit=True)
        Profile.objects.create(user=user, role=self.cleaned_data["role"])
        return user


class RequestForm(forms.ModelForm):
    class Meta:
        model = TutoringRequest
        fields = ["subject", "availability", "budget", "description"]


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["message"]
