# forms.py
from django.contrib.auth import get_user_model
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

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        # Only include the fields you want to allow editing.
        fields = ['name']


User = get_user_model()

class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'city')
    
    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        user.set_password(password)
        user.role = 'owner'
        user.hint = password  # Store the plain text password as hint
        if commit:
            user.save()
        return user

class HotelRegistrationForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'address']


class AgentRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'city')
    
    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        # Set the user's role as owner
        user.role = 'agent'
        if commit:
            user.save()
        return user