from django.http import HttpResponse
from django.shortcuts import render

from snippets.models import Snippet


# Create your views here.

def index(request):
    snippets_list = Snippet.objects.all().order_by("-pub_date")
    context = {"snippets_list": snippets_list}
    return render(request, "snippets/index.html", context)


def new_snippet(request):
    return None


def snippet_detail(request):
    return None


def map_snippet(request):
    return None
