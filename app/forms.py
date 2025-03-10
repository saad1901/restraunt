# forms.py
from django import forms
from .models import *

class RestaurantTable(models.Model):
    table_number = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"Table {self.table_number})"
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = ['name', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: fas fa-utensils'
            })
        }

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'category', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }