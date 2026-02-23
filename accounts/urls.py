from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_user, name="login_user"),
    path("logout/", views.logout_user, name="logout_user"),
    path("register/", views.register_user, name="register_user"),
    path("profile/", views.profile, name="profile"),
    path("profile/<str:username>/", views.profile_username, name="public_profile"),
]
