from django import forms
from django.contrib.auth.models import User
from core.models import UserProfile

class StaffUserForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label="Rôle / Accès",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Téléphone",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'})
    )
    password = forms.CharField(
        required=False,
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )
    confirm_password = forms.CharField(
        required=False,
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse email'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Edit mode
            if hasattr(self.instance, 'profile'):
                self.fields['role'].initial = self.instance.profile.role
                self.fields['phone'].initial = self.instance.profile.phone
            self.fields['username'].disabled = True
            self.fields['username'].required = False
            self.fields['password'].help_text = "Laissez vide pour conserver le mot de passe actuel."
            self.fields['password'].label = "Nouveau mot de passe"
        else:
            # Create mode
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not self.instance.pk:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password or confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")
        
        return cleaned_data
