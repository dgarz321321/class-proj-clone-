from django.contrib import admin

from .models import Application, Profile, TutoringRequest

admin.site.register([Profile, TutoringRequest, Application])
