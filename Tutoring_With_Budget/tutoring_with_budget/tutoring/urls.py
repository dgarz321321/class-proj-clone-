from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.request_list, name="request_list"),
    path("requests/new/", views.request_create, name="request_create"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path("requests/<int:pk>/apply/", views.apply, name="apply"),
    path("requests/<int:pk>/accept/<int:app_pk>/", views.accept, name="accept"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        LoginView.as_view(
            template_name="tutoring/form.html", extra_context={"title": "Log in"}
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]
