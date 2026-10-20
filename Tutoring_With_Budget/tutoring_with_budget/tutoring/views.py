from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ApplicationForm, RegisterForm, RequestForm
from .models import Application, TutoringRequest, get_role


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        login(request, form.save())
        return redirect("request_list")
    return render(request, "tutoring/form.html", {"form": form, "title": "Register"})


def request_list(request):
    reqs = TutoringRequest.objects.filter(status=TutoringRequest.OPEN)
    subject = request.GET.get("subject", "").strip()
    if subject:
        reqs = reqs.filter(subject__icontains=subject)
    return render(
        request, "tutoring/request_list.html", {"requests": reqs, "subject": subject}
    )


@login_required
def request_create(request):
    if get_role(request.user) != "student":
        raise PermissionDenied("Only students can post requests.")
    form = RequestForm(request.POST or None)
    if form.is_valid():
        tr = form.save(commit=False)
        tr.student = request.user
        tr.save()
        return redirect("request_detail", pk=tr.pk)
    return render(
        request, "tutoring/form.html", {"form": form, "title": "New tutoring request"}
    )


def request_detail(request, pk):
    tr = get_object_or_404(TutoringRequest, pk=pk)
    user = request.user
    is_owner = user.is_authenticated and user == tr.student
    can_apply = (
        user.is_authenticated
        and get_role(user) == "tutor"
        and tr.status == TutoringRequest.OPEN
        and not tr.applications.filter(tutor=user).exists()
    )
    return render(
        request,
        "tutoring/request_detail.html",
        {"tr": tr, "is_owner": is_owner, "can_apply": can_apply, "app_form": ApplicationForm()},
    )


@login_required
@require_POST
def apply(request, pk):
    tr = get_object_or_404(TutoringRequest, pk=pk)
    form = ApplicationForm(request.POST)
    if form.is_valid():
        try:
            tr.apply(request.user, form.cleaned_data["message"])
            messages.success(request, "Application sent.")
        except ValidationError as e:
            messages.error(request, e.messages[0])
    return redirect("request_detail", pk=pk)


@login_required
@require_POST
def accept(request, pk, app_pk):
    app = get_object_or_404(Application, pk=app_pk, tutoring_request_id=pk)
    tr = app.tutoring_request
    if tr.student != request.user:
        raise PermissionDenied
    try:
        tr.accept(app)
        messages.success(request, f"{app.tutor.username} accepted.")
    except ValidationError as e:
        messages.error(request, e.messages[0])
    return redirect("request_detail", pk=pk)
