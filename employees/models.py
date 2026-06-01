from django.db import models


class Department(models.Model):
    """Represents a department in the shopping center."""
    name = models.CharField(max_length=100, verbose_name='Nom du département')
    description = models.TextField(blank=True, verbose_name='Description')

    class Meta:
        ordering = ['name']
        verbose_name = 'Département'
        verbose_name_plural = 'Départements'

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Represents an employee of the shopping center."""
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('on_leave', 'En congé'),
        ('terminated', 'Licencié'),
    ]

    CONTRACT_CHOICES = [
        ('cdi', 'CDI'),
        ('cdd', 'CDD'),
        ('interim', 'Intérimaire'),
        ('stage', 'Stagiaire'),
    ]

    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Téléphone')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees', verbose_name='Département')
    position = models.CharField(max_length=100, verbose_name='Poste')
    hire_date = models.DateField(verbose_name='Date d\'embauche')
    contract_type = models.CharField(max_length=20, choices=CONTRACT_CHOICES, default='cdi', verbose_name='Type de contrat')
    salary = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Salaire (FCFA)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Statut')
    address = models.TextField(blank=True, verbose_name='Adresse')
    emergency_contact = models.CharField(max_length=100, blank=True, verbose_name='Contact d\'urgence')
    emergency_phone = models.CharField(max_length=20, blank=True, verbose_name='Tél. urgence')
    notes = models.TextField(blank=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
