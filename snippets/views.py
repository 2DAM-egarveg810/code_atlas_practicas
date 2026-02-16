from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from accounts.models import UserProfile
from snippets.models import Snippet
from . import forms


# Create your views here.

def index(request):
    snippets_list = Snippet.objects.all().order_by("-pub_date")
    context = {"snippets_list": snippets_list}
    return render(request, "snippets/index.html", context)


def new_snippet(request):
    if request.method == "POST":
        form = forms.CreateSnippet(request.POST)
        if form.is_valid():
            newsnippet = form.save(commit=False)
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            newsnippet.author = profile
            newsnippet.save()
            return redirect('snippets:index')
    else:
        form = forms.CreateSnippet()
    return render(request, 'snippets/create_snippet.html', {'form': form})


def snippet_detail(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    return render(request, 'snippets/snippet_detail.html', {'snippet': snippet})


def map_snippet(request):
    return None
