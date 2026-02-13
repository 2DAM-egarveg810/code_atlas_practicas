from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new_snippet, name="new_snippet"),
    path("<int:pk>/", views.snippet_detail, name="snippet_detail"),
    path("map/", views.map_snippet, name="map_snippet"),
]
