from django.contrib.auth import forms
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from accounts.models import UserProfile


# Create your views here.
def index(request):
    return None


def login_user(request):
    return None


def register_user(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = forms.UserCreationForm(request.POST)
        if form.is_valid():
            newuser = form.save(commit=False)
            newuser.save()
            u = UserProfile.objects.create(user=newuser)
            u.save()
            return redirect('snippets:index')
    else:
        form = forms.UserCreationForm()

    return render(request, "accounts/register_user.html", {"form": form})


def profile(request):
    return None


def profile_username(request):
    return None
