from django.db import models
from tenants.models import Tenant, Shop


class Invoice(models.Model):
    """Represents an invoice/facture for a tenant."""
    STATUS_CHOICES = [
        ('paid', 'Payée'),
        ('pending', 'En attente'),
        ('overdue', 'En retard'),
        ('cancelled', 'Annulée'),
    ]

    TYPE_CHOICES = [
        ('rent', 'Loyer'),
        ('charges', 'Charges'),
        ('parking', 'Parking'),
        ('penalty', 'Pénalité'),
        ('other', 'Autre'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, verbose_name='N° Facture')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='invoices', verbose_name='Locataire')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='invoices', verbose_name='Boutique')
    invoice_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='rent', verbose_name='Type')
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Montant (FCFA)')
    issue_date = models.DateField(verbose_name='Date d\'émission')
    due_date = models.DateField(verbose_name='Date d\'échéance')
    paid_date = models.DateField(null=True, blank=True, verbose_name='Date de paiement')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Statut')
    description = models.TextField(blank=True, verbose_name='Description')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'

    def __str__(self):
        return f"Facture {self.invoice_number} - {self.tenant}"


class Expense(models.Model):
    """Represents an expense/dépense of the shopping center."""
    CATEGORY_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('salary', 'Salaires'),
        ('energy', 'Énergie & Eau'),
        ('security', 'Sécurité'),
        ('cleaning', 'Nettoyage'),
        ('insurance', 'Assurance'),
        ('taxes', 'Taxes & Impôts'),
        ('marketing', 'Marketing'),
        ('equipment', 'Équipement'),
        ('other', 'Autre'),
    ]

    mall = models.ForeignKey('tenants.Mall', on_delete=models.CASCADE, related_name='expenses', verbose_name='Centre Commercial', null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name='Titre')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Catégorie')
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Montant (FCFA)')
    date = models.DateField(verbose_name='Date')
    description = models.TextField(blank=True, verbose_name='Description')
    supplier = models.CharField(max_length=200, blank=True, verbose_name='Fournisseur')
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True, verbose_name='Reçu')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Dépense'
        verbose_name_plural = 'Dépenses'

    def __str__(self):
        return f"{self.title} - {self.amount} FCFA"


class Payment(models.Model):
    """Represents a payment/paiement received."""
    METHOD_CHOICES = [
        ('cash', 'Espèces'),
        ('bank_transfer', 'Virement bancaire'),
        ('check', 'Chèque'),
        ('mobile_money', 'Mobile Money'),
        ('other', 'Autre'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name='Facture')
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Montant (FCFA)')
    payment_date = models.DateField(verbose_name='Date de paiement')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash', verbose_name='Mode de paiement')
    reference = models.CharField(max_length=100, blank=True, verbose_name='Référence')
    notes = models.TextField(blank=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'

    def __str__(self):
        return f"Paiement {self.amount} FCFA - {self.invoice.invoice_number}"
