from django.forms import ModelForm
from django import forms
from .models import Page


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = [
            'picture',
            'name',
            'quantity',
            'condition',
            'description',
            'packaging_method',
            'trade_preference',
            'wanted_item_name',
            'wanted_item_details',
            'price',
        ]