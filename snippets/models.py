from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

from accounts.models import UserProfile


# Create your models here.

# Representa un fragmento de código, funciona como si fuese una publicación.
class Snippet(models.Model):
    LENGUAJES_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('typescript', 'TypeScript'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('django', 'Django'),
        ('sql', 'SQL'),
        ('java', 'Java'),
        ('php', 'PHP'),
        ('kotlin', 'Kotlin'),
        ('markdown', 'Markdown'),
    ]

    title = models.CharField(max_length=50)
    source_code = models.TextField()
    description = models.TextField(null=True, blank=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='snippets', default=1, null=True,
                               blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    pub_update = models.DateTimeField(auto_now=True)
    language = models.CharField(
        choices=LENGUAJES_CHOICES,
        max_length=20
    )

    cont_visited = models.IntegerField(default=0)
    latitude = models.FloatField(default=1, null=True, blank=True)
    longitude = models.FloatField(default=1, null=True, blank=True)

    point = models.PointField(default=Point(0, 0), null=True, blank=True)

    def __str__(self):
        return f'{self.title} [{self.language}]'

    def get_language_badge_color(self):
        return {
            'python': 'bg-primary',
            'javascript': 'bg-warning text-dark',
            'typescript': 'bg-info text-dark',
            'html': 'bg-danger',
            'css': 'bg-secondary',
            'django': 'bg-success',
            'sql': 'bg-dark',
            'java': 'bg-danger',
            'php': 'bg-indigo',
            'kotlin': 'bg-purple',
            'markdown': 'bg-light text-dark',
        }.get(self.language, 'bg-primary')
