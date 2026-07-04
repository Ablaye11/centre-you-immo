from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Mall(models.Model):
    """Represents a property (shopping center, building, house)."""
    PROPERTY_TYPES = [
        ('mall', 'Centre Commercial'),
        ('building', 'Immeuble'),
        ('house', 'Maison / Villa'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nom de la propriété')
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='mall', verbose_name='Type de propriété')
    address = models.TextField(blank=True, verbose_name='Adresse')
    description = models.TextField(blank=True, verbose_name='Description')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Propriété'
        verbose_name_plural = 'Propriétés'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.property_type == 'house':
            # Create a default shop representing the house itself
            Shop.objects.create(
                mall=self,
                name=self.name,
                shop_number=f"MSN-{self.id:04d}",
                category='other',
                surface=0,
                status='available',
                description=f"Unité de location principale pour la maison {self.name}"
            )



class Floor(models.Model):
    """Represents a floor/level in the shopping center."""
    mall = models.ForeignKey(Mall, on_delete=models.CASCADE, related_name='floors', verbose_name='Centre Commercial', null=True, blank=True)
    name = models.CharField(max_length=50, verbose_name='Nom (ex: Rez-de-chaussée, 1er étage)')
    level = models.IntegerField(default=0, verbose_name='Niveau (pour le tri, ex: 0, 1, 2, -1)')
    description = models.TextField(blank=True, verbose_name='Description')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['level', 'name']
        verbose_name = 'Étage'
        verbose_name_plural = 'Étages'

    def __str__(self):
        return self.name


class Shop(models.Model):
    """Represents a shop/boutique in the shopping center."""
    CATEGORY_CHOICES = [
        ('clothing', 'Vêtements & Mode'),
        ('food', 'Restauration'),
        ('electronics', 'Électronique'),
        ('jewelry', 'Bijouterie'),
        ('beauty', 'Beauté & Cosmétiques'),
        ('sports', 'Sport & Loisirs'),
        ('home', 'Maison & Décoration'),
        ('services', 'Services'),
        ('supermarket', 'Supermarché'),
        ('pharmacy', 'Pharmacie'),
        ('bank', 'Banque & Finance'),
        ('telecom', 'Télécommunications'),
        ('other', 'Autre'),
    ]

    FLOOR_CHOICES = [
        ('rdc', 'Rez-de-chaussée'),
        ('1er', '1er étage'),
        ('2eme', '2ème étage'),
        ('3eme', '3ème étage'),
    ]

    STATUS_CHOICES = [
        ('occupied', 'Occupée'),
        ('available', 'Disponible'),
        ('maintenance', 'En maintenance'),
    ]

    mall = models.ForeignKey(Mall, on_delete=models.CASCADE, related_name='shops', verbose_name='Centre Commercial', null=True, blank=True)
    name = models.CharField(max_length=200, verbose_name='Nom de la boutique')
    shop_number = models.CharField(max_length=20, unique=True, verbose_name='Numéro')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Catégorie')
    floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True, related_name='shops', verbose_name='Étage / Niveau')
    surface = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Surface (m²)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='Statut')
    description = models.TextField(blank=True, verbose_name='Description')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['shop_number']
        verbose_name = 'Boutique'
        verbose_name_plural = 'Boutiques'

    def __str__(self):
        return f"{self.shop_number} - {self.name}"


class Tenant(models.Model):
    """Represents a tenant/locataire renting a shop."""
    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Téléphone')
    company_name = models.CharField(max_length=200, blank=True, verbose_name='Raison sociale')
    id_number = models.CharField(max_length=50, blank=True, verbose_name='N° Pièce d\'identité')
    address = models.TextField(blank=True, verbose_name='Adresse personnelle')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenant', verbose_name='Utilisateur de connexion')
    cni_or_passport = models.FileField(upload_to='tenants/documents/', null=True, blank=True, verbose_name='CNI ou Passeport')
    ninea_or_rc = models.FileField(upload_to='tenants/documents/', null=True, blank=True, verbose_name='NINEA ou Reg. Commerce')

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Locataire'
        verbose_name_plural = 'Locataires'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def whatsapp_phone(self):
        """Clean phone number for WhatsApp API link."""
        if not self.phone:
            return ""
        # Remove all spaces, dashes, parentheses and plus sign
        clean = "".join(c for c in self.phone if c.isdigit())
        
        # If it's a standard Senegalese mobile number of 9 digits starting with 7
        # we prefix it with country code 221
        if len(clean) == 9 and clean.startswith('7'):
            clean = "221" + clean
            
        return clean


class Lease(models.Model):
    """Represents a lease/bail between a tenant and a shop."""
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('pending', 'En attente'),
        ('terminated', 'Résilié'),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='leases', verbose_name='Boutique')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leases', verbose_name='Locataire')
    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name='Date de fin')
    monthly_rent = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Loyer mensuel (FCFA)')
    deposit = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='Caution (FCFA)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Statut')
    conditions = models.TextField(blank=True, verbose_name='Conditions particulières')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Bail'
        verbose_name_plural = 'Baux'

    def __str__(self):
        return f"Bail {self.shop.name} - {self.tenant.full_name}"

    @property
    def is_expiring_soon(self):
        """Check if the lease is expiring within 30 days."""
        if self.status != 'active':
            return False
        days_left = (self.end_date - timezone.now().date()).days
        return 0 < days_left <= 30

    @property
    def days_remaining(self):
        """Get the number of days remaining on the lease."""
        return (self.end_date - timezone.now().date()).days
