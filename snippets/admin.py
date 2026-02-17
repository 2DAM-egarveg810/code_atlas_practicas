from django.contrib.gis import admin
from snippets.models import Snippet


# Register your models here.

# admin.site.register(Snippet)


@admin.register(Snippet)
class MarkerAdmin(admin.GISModelAdmin):
    list_display = ("title", "point")
