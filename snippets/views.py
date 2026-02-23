from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import UserProfile
from snippets.models import Snippet
from . import forms
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods
import json
from django.contrib.gis.geos import Point
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.

def index(request):
    """
        Vista principal con paginación de snippets.
    """
    snippets_list = Snippet.objects.select_related('author__user').order_by("-pub_date")

    paginator = Paginator(snippets_list, 9)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        "snippets_list": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": paginator.num_pages > 1,
    }
    return render(request, "snippets/index.html", context)


@login_required
def new_snippet(request):
    """
        Vista para crear un nuevo snippet. Se pueden pasar las coordenadas por GET (?lat=X&lng=Y) desde el mapa.

        @return:
            - redirect('snippets:index') tras creacion exitosa.
            - render() de create_snippet para GET o POST invalido.
        """
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
    """
      Muestra los detalles de un snippet especifico identificado por su pk.
      """
    snippet = get_object_or_404(Snippet, pk=pk)
    return render(request, 'snippets/snippet_detail.html', {'snippet': snippet})


GEOM_FIELD = "point"


@require_GET
def map_snippet(request):
    """
    Renderiza la pagina del mapa para visualizar snippets.
    """
    return render(request, "snippets/mapa_snippets.html", {})


@require_GET
def snippets_geojson(request):
    """
    Endpoint API que retorna los snippets en formato GeoJSON para Leaflet.
    """
    qs = Snippet.objects.filter(point__isnull=False)

    bbox = request.GET.get("bbox")
    if bbox:
        try:
            minx, miny, maxx, maxy = [float(x) for x in bbox.split(",")]
        except Exception:
            return HttpResponseBadRequest("bbox inválido. Formato: minx,miny,maxx,maxy")
        qs = qs.filter(**{f"{GEOM_FIELD}__bboverlaps": (minx, miny, maxx, maxy)})

    geojson_str = serialize(
        "geojson",
        qs,
        geometry_field=GEOM_FIELD,
        fields=['title', 'language', 'description', 'pub_date', 'author', 'cont_visited'],
    )

    return JsonResponse(json.loads(geojson_str), safe=False)


@login_required
@require_http_methods(["POST"])
def update_snippet_location(request, snippet_id):
    """
        Actualiza las coordenadas de un snippet existente via API.

        Codigos de estado posibles:
            - 200: Actualizacion exitosa.
            - 400: Datos invalidos o coordenadas fuera de rango.
            - 403: Permiso denegado (usuario no es autor ni staff).
            - 404: Snippet no encontrado.
            - 500: Error interno del servidor.
        """
    try:
        snippet = get_object_or_404(Snippet, id=snippet_id)
        author_user = snippet.author.user if hasattr(snippet.author, 'user') else None

        if snippet.author.user != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'No autorizado'}, status=403)

        data = json.loads(request.body)
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))

        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return JsonResponse({'error': 'Coordenadas inválidas'}, status=400)

        snippet.point = Point(float(lng), float(lat), srid=4326)
        snippet.save(update_fields=['point', 'pub_update'])

        return JsonResponse({
            'success': True,
            'message': 'Ubicación actualizada',
            'data': {'lat': lat, 'lng': lng}
        })

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        return JsonResponse({'error': f'Datos inválidos: {str(e)}'}, status=400)
    except Exception as e:
        import logging
        logging.error(f'Error updating snippet {snippet_id}: {e}')
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_snippet(request, snippet_id):
    """"
        Elimina un snippet identificado por su ID.

        Codigos de estado posibles:
            - 200: Eliminacion exitosa.
            - 403: Permiso denegado.
            - 404: Snippet no encontrado.
            - 500: Error interno del servidor.
    """
    try:
        snippet = get_object_or_404(Snippet, id=snippet_id)
        if snippet.author.user != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        snippet.delete()
        return JsonResponse({
            'success': True,
            'message': 'Snippet eliminado'
        })

    except Exception as e:
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
