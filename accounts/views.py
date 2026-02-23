from django.contrib import messages
from django.contrib.auth import forms, logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm

from accounts.models import UserProfile
from snippets.models import Snippet
from django.db.models import Count
from django.core.paginator import Paginator


# Create your views here.
def index(request):
    return None


def login_user(request):
    """
    Procesa el inicio de sesion de usuarios.

    @return:
        - redirect('snippets:index') si las credenciales son validas.
        - redirect("accounts:login") con mensaje de error si fallan.
        - render() del template login_user.html para peticiones GET.
    """
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
    """
    Procesa el registro de nuevos usuarios.

    @return:
        - redirect('snippets:index') tras registro exitoso.
        - render() del template register_user.html con formulario (y errores si los hay).
    """
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


@login_required
def profile(request):
    """
    Muestra el perfil del usuario autenticado con sus snippets publicados.
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)

    snippets = Snippet.objects.filter(
        author=user_profile
    ).order_by('-pub_date')

    context = {
        "user_profile": user_profile,
        "snippets_list": snippets,
        "page_title": f"Perfil de {request.user.username}"
    }
    return render(request, 'accounts/my_profile.html', context)


def profile_username(request, username):
    """
    Muestra el perfil público de un usuario por su nombre de usuario.
    """
    target_profile = get_object_or_404(UserProfile, user__username=username)
    if request.user.is_authenticated and request.user == target_profile.user:
        return redirect('accounts:profile')

    snippets = Snippet.objects.filter(author=target_profile)

    snippets = snippets.order_by('-pub_date')

    language_filter = request.GET.get('lang')
    if language_filter:
        snippets = snippets.filter(language__iexact=language_filter)

    context = {
        'target_profile': target_profile,
        'snippets_list': snippets,
        'page_title': f'Perfil de {target_profile.user.username}',
        'is_own_profile': False,
        'language_filter': language_filter,
        'available_languages': Snippet.objects.filter(author=target_profile)
        .values_list('language', flat=True)
        .distinct()
    }

    return render(request, 'accounts/public_profile.html', context)


def logout_user(request):
    """
        Cierra la sesion del usuario actual y redirige a la pagina principal.

        @return:
            redirect("snippets:index") tras cerrar sesion.
        """
    logout(request)
    return redirect("snippets:index")
    # return render(request, 'accounts/logout_user.html')
