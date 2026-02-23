from django.urls import path

from . import views

app_name = 'snippets'

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new_snippet, name="new_snippet"),
    path("<int:pk>/", views.snippet_detail, name="snippet_detail"),
    path("map/", views.map_snippet, name="map_snippet"),
    path('map/api/geojson/', views.snippets_geojson, name='snippets_geojson'),
    path('api/snippets/<int:snippet_id>/update_location/',
         views.update_snippet_location,
         name='snippet_update_location'),

    path('api/snippets/<int:snippet_id>/delete/',
         views.delete_snippet,
         name='snippet_delete'),
]
