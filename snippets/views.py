from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect

from accounts.models import UserProfile
from snippets.models import Snippet
from . import forms
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import json
from django.contrib.gis.geos import Point


# Create your views here.

def index(request):
    snippets_list = Snippet.objects.all().order_by("-pub_date")
    context = {"snippets_list": snippets_list}
    return render(request, "snippets/index.html", context)


@login_required
def new_snippet(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    if request.method == "POST":
        form = forms.CreateSnippet(request.POST)
        if form.is_valid():
            newsnippet = form.save(commit=False)

            profile, created = UserProfile.objects.get_or_create(user=request.user)
            newsnippet.author = profile

            post_lat = form.cleaned_data.get('latitude')
            post_lng = form.cleaned_data.get('longitude')

            if post_lat is not None and post_lng is not None:
                newsnippet.point = Point(float(post_lng), float(post_lat))

            newsnippet.save()

            return redirect('snippets:index')
    else:
        initial_data = {}
        if lat and lng:
            try:
                initial_data['latitude'] = float(lat)
                initial_data['longitude'] = float(lng)
            except (ValueError, TypeError):
                pass
        form = forms.CreateSnippet(initial=initial_data)

    return render(request, 'snippets/create_snippet.html', {
        'form': form,
        'initial_lat': lat,
        'initial_lng': lng,
    })


def snippet_detail(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    return render(request, 'snippets/snippet_detail.html', {'snippet': snippet})


GEOM_FIELD = "point"


@require_GET
def map_snippet(request):
    """
    Página del mapa (HTML).
    """
    return render(request, "snippets/mapa_snippets.html", {})


@require_GET
def snippets_geojson(request):
    """
    Endpoint GeoJSON para Leaflet.
    Opcional: bbox=minx,miny,maxx,maxy
    """
    # Filtrar solo snippets con punto válido
    qs = Snippet.objects.filter(point__isnull=False)

    bbox = request.GET.get("bbox")
    if bbox:
        try:
            minx, miny, maxx, maxy = [float(x) for x in bbox.split(",")]
        except Exception:
            return HttpResponseBadRequest("bbox inválido. Formato: minx,miny,maxx,maxy")
        # GeoDjango: filtro por BBOX
        qs = qs.filter(**{f"{GEOM_FIELD}__bboverlaps": (minx, miny, maxx, maxy)})

    geojson_str = serialize(
        "geojson",
        qs,
        geometry_field=GEOM_FIELD,
        # Incluir campos relevantes en properties
        fields=['title', 'language', 'description', 'pub_date', 'author', 'cont_visited'],
    )

    return JsonResponse(json.loads(geojson_str), safe=False)
