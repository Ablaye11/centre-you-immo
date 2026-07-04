from django import forms
from .models import Shop, Tenant, Floor, Mall
from django.utils import timezone

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

    def __init__(self, *args, **kwargs):
        active_mall = kwargs.pop('active_mall', None)
        super().__init__(*args, **kwargs)
        if active_mall:
            self.fields['floor'].queryset = Floor.objects.filter(mall=active_mall)
        else:
            self.fields['floor'].queryset = Floor.objects.all()

class TenantForm(forms.ModelForm):
    # Quick lease addition fields
    shop = forms.ModelChoiceField(
        queryset=Shop.objects.none(),
        required=False,
        label='Boutique / Magasin',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    monthly_rent = forms.DecimalField(
        required=False,
        label='Loyer Mensuel (FCFA)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 250000'})
    )
    deposit = forms.DecimalField(
        required=False,
        label='Caution / Dépôt (FCFA)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 500000'})
    )
    start_date = forms.DateField(
        required=False,
        label='Date de début',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now
    )
    end_date = forms.DateField(
        required=False,
        label='Date de fin',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    initial_payment = forms.ChoiceField(
        choices=[
            ('none', 'Pas de paiement immédiat (Générer factures en attente)'),
            ('rent', 'Payer le premier loyer uniquement'),
            ('deposit', 'Payer la caution uniquement'),
            ('both', 'Payer la caution et le premier loyer'),
        ],
        required=False,
        label='Paiement Initial d\'Entrée',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'Espèces'),
            ('bank_transfer', 'Virement bancaire'),
            ('check', 'Chèque'),
            ('mobile_money', 'Mobile Money'),
        ],
        required=False,
        label='Mode de paiement initial',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Tenant
        fields = ['first_name', 'last_name', 'email', 'phone', 'company_name', 'id_number', 'address', 'user', 'cni_or_passport', 'ninea_or_rc']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'cni_or_passport': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ninea_or_rc': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        active_mall = kwargs.pop('active_mall', None)
        is_edit = kwargs.get('instance') is not None
        super().__init__(*args, **kwargs)
        
        from django.contrib.auth.models import User
        from django.db.models import Q
        
        if is_edit:
            self.fields['user'].queryset = User.objects.filter(Q(tenant__isnull=True) | Q(pk=self.instance.user.pk) if self.instance.user else Q(tenant__isnull=True))
        else:
            self.fields['user'].queryset = User.objects.filter(tenant__isnull=True)
            
        self.fields['user'].required = False
        self.fields['user'].label = 'Compte utilisateur lié (pour le Portail)'
        
        if active_mall:
            self.fields['shop'].queryset = Shop.objects.filter(mall=active_mall, status='available')
        else:
            self.fields['shop'].queryset = Shop.objects.filter(status='available')

        if is_edit:
            if 'shop' in self.fields: self.fields.pop('shop')
            if 'monthly_rent' in self.fields: self.fields.pop('monthly_rent')
            if 'deposit' in self.fields: self.fields.pop('deposit')
            if 'start_date' in self.fields: self.fields.pop('start_date')
            if 'end_date' in self.fields: self.fields.pop('end_date')
            if 'initial_payment' in self.fields: self.fields.pop('initial_payment')
            if 'payment_method' in self.fields: self.fields.pop('payment_method')

class MallForm(forms.ModelForm):
    class Meta:
        model = Mall
        fields = ['name', 'property_type', 'address', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la propriété'}),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description...'}),
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
