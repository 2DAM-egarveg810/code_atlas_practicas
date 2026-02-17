from django.contrib import messages
from django.contrib.auth import forms, logout, login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from accounts.models import UserProfile


# Create your views here.
def index(request):
    return None


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('snippets:index')
        else:
            messages.info(request, "Invalid username or password.")
            return redirect("accounts:login")

    return render(request, 'accounts/login_user.html')


def register_user(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = forms.UserCreationForm(request.POST)
        if form.is_valid():
            newuser = form.save(commit=False)
            newuser.save()
            u = UserProfile.objects.create(user=newuser)
            u.save()
            login(request, newuser)
            return redirect('snippets:index')
    else:
        form = forms.UserCreationForm()

    return render(request, "accounts/register_user.html", {"form": form})


def profile(request):
    return None


def profile_username(request):
    return None


def logout_user(request):
    logout(request)
    return redirect("snippets:index")
    # return render(request, 'accounts/logout_user.html')
