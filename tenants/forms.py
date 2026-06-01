from django import forms
from .models import Shop, Tenant, Floor

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['shop_number', 'name', 'category', 'floor', 'surface', 'description', 'status']
        widgets = {
            'shop_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: A-01'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la boutique'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'floor': forms.Select(attrs={'class': 'form-control'}),
            'surface': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'En m²'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description...'}),
        }

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['first_name', 'last_name', 'email', 'phone', 'company_name', 'id_number', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ['name', 'level', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Rez-de-chaussée, 1er étage'}),
            'level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pour le tri (ex: 0, 1, 2)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description optionnelle'}),
        }
