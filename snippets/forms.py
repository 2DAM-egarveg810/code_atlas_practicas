from django import forms
from . import models


class CreateSnippet(forms.ModelForm):
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = models.Snippet
        fields = ['title', 'description', 'source_code', 'language', 'latitude', 'longitude']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter snippet title'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter snippet description'}),
            'source_code': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Paste your code here'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
        }
