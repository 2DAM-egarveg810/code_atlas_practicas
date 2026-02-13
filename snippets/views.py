from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from snippets.models import Snippet


# Create your views here.

def index(request):
    snippets_list = Snippet.objects.all().order_by("-pub_date")
    context = {"snippets_list": snippets_list}
    return render(request, "snippets/index.html", context)


def new_snippet(request):
    return None


def snippet_detail(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    return render(request, 'snippets/snippet_detail.html', {'snippet': snippet})


def map_snippet(request):
    return None
