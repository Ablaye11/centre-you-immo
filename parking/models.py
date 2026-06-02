from django.db import models
from tenants.models import Tenant


class ParkingSpace(models.Model):
    """Represents a parking space."""
    TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('vip', 'VIP'),
        ('handicap', 'Handicapé'),
        ('reserved', 'Réservé'),
    ]

    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('occupied', 'Occupée'),
        ('reserved', 'Réservée'),
        ('maintenance', 'En maintenance'),
    ]

    mall = models.ForeignKey('tenants.Mall', on_delete=models.CASCADE, related_name='parking_spaces', verbose_name='Centre Commercial', null=True, blank=True)
    space_number = models.CharField(max_length=10, unique=True, verbose_name='N° Place')
    level = models.CharField(max_length=20, verbose_name='Niveau')
    space_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='standard', verbose_name='Type')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='Statut')

    class Meta:
        ordering = ['space_number']
        verbose_name = 'Place de parking'
        verbose_name_plural = 'Places de parking'

    def __str__(self):
        return f"Place {self.space_number} ({self.get_status_display()})"


class ParkingSubscription(models.Model):
    """Represents a parking subscription for a tenant."""
    SUB_TYPE_CHOICES = [
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('annual', 'Annuel'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='parking_subscriptions', verbose_name='Locataire')
    space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Place')
    vehicle_plate = models.CharField(max_length=20, verbose_name='Immatriculation')
    vehicle_type = models.CharField(max_length=50, verbose_name='Type de véhicule')
    subscription_type = models.CharField(max_length=20, choices=SUB_TYPE_CHOICES, default='monthly', verbose_name='Type d\'abonnement')
    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name='Date de fin')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Tarif mensuel (FCFA)')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Abonnement parking'
        verbose_name_plural = 'Abonnements parking'

    def __str__(self):
        return f"Abo. {self.tenant} - Place {self.space.space_number}"
