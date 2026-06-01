from django.db import models
from django.contrib.auth.models import User


class MaintenanceRequest(models.Model):
    """Represents a maintenance request."""
    STATUS_CHOICES = [
        ('new', 'Nouvelle'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Basse'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('urgent', 'Urgente'),
    ]

    ZONE_CHOICES = [
        ('common', 'Parties communes'),
        ('parking', 'Parking'),
        ('rdc', 'Rez-de-chaussée'),
        ('1er', '1er étage'),
        ('2eme', '2ème étage'),
        ('3eme', '3ème étage'),
        ('exterior', 'Extérieur'),
        ('roof', 'Toiture'),
        ('elevator', 'Ascenseur'),
        ('electrical', 'Installation électrique'),
        ('plumbing', 'Plomberie'),
    ]

    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    zone = models.CharField(max_length=50, choices=ZONE_CHOICES, verbose_name='Zone')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='Priorité')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Statut')
    assigned_to = models.CharField(max_length=200, blank=True, verbose_name='Assigné à')
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name='Coût estimé (FCFA)')
    actual_cost = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name='Coût réel (FCFA)')
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Signalé par')
    scheduled_date = models.DateField(null=True, blank=True, verbose_name='Date planifiée')
    completed_date = models.DateField(null=True, blank=True, verbose_name='Date de fin')
    notes = models.TextField(blank=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Demande de maintenance'
        verbose_name_plural = 'Demandes de maintenance'

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"
