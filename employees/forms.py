from django import forms
from django.contrib.auth.models import User
from .models import Employee

class EmployeeForm(forms.ModelForm):
    create_user_account = forms.BooleanField(
        required=False, 
        initial=False, 
        label="Créer un compte d'accès pour cet employé",
        widget=forms.CheckboxInput(attrs={'id': 'id_create_user_account', 'class': 'form-checkbox', 'onchange': 'toggleUserFields()'})
    )
    username = forms.CharField(
        required=False, 
        max_length=150, 
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'id': 'id_username_field', 'class': 'form-control', 'placeholder': "Nom d'utilisateur pour l'accès"})
    )
    password = forms.CharField(
        required=False, 
        widget=forms.PasswordInput(render_value=False, attrs={'id': 'id_password_field', 'class': 'form-control', 'placeholder': "Mot de passe d'accès"}),
        label="Mot de passe"
    )

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'department', 
            'position', 'hire_date', 'contract_type', 'salary', 'status', 
            'address', 'is_accountant', 'is_maintenance', 'is_secretary', 'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Poste occupé'}),
            'custom_hire_date_widget_placeholder': forms.TextInput(), # Just safety placeholder
            'contract_type': forms.Select(attrs={'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salaire (FCFA)'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse physique'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes complémentaires'}),
            'is_accountant': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_maintenance': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_secretary': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set hire_date input type to date
        self.fields['hire_date'].widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        
        # Si l'employé a déjà un compte d'accès utilisateur
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['create_user_account'].initial = True
            self.fields['create_user_account'].widget.attrs['disabled'] = 'disabled'
            self.fields['create_user_account'].help_text = f"Compte lié : {self.instance.user.username}"
            self.fields['username'].widget.attrs['disabled'] = 'disabled'
            self.fields['username'].initial = self.instance.user.username
            self.fields['password'].help_text = "Laissez vide pour conserver le mot de passe actuel"
            self.fields['password'].label = "Nouveau mot de passe"

    def clean(self):
        cleaned_data = super().clean()
        create_account = cleaned_data.get('create_user_account')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        # Si l'employé n'a pas encore de compte utilisateur et qu'on demande la création
        if create_account and not (self.instance and self.instance.pk and self.instance.user):
            if not username:
                self.add_error('username', "Le nom d'utilisateur est requis pour la création du compte.")
            elif User.objects.filter(username=username).exists():
                self.add_error('username', "Ce nom d'utilisateur est déjà utilisé par un autre utilisateur.")
            
            if not password:
                self.add_error('password', "Le mot de passe est requis pour la création du compte.")
        
        return cleaned_data
