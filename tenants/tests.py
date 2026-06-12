from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Mall, Floor, Shop, Tenant, Lease
from finance.models import Invoice, Payment
import io

class ShopImportTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='password123')
        self.client.force_login(self.user)
        self.mall = Mall.objects.create(name="YOU IMMO Test", address="Dakar")
        
    def test_import_template_download(self):
        url = reverse('shop_import_template')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="modele_import_boutiques.xlsx"')

    def test_csv_import_success(self):
        # CSV contents:
        # Étage / Niveau, Boutique - Numéro, Boutique - Nom, Boutique - Catégorie, Boutique - Surface, Description, Locataire - Prénom, Locataire - Nom, Locataire - Téléphone, Locataire - Email, Locataire - Raison Sociale, Locataire - N° Pièce d'identité, Bail - Date de début, Bail - Date de fin, Bail - Loyer Mensuel, Bail - Caution
        csv_data = (
            "Étage / Niveau;Boutique - Numéro;Boutique - Nom;Boutique - Catégorie;Boutique - Surface (m²);Boutique - Description;Locataire - Prénom;Locataire - Nom;Locataire - Téléphone;Locataire - Email;Locataire - Raison Sociale;Locataire - N° Pièce d'identité;Bail - Date de début (AAAA-MM-JJ);Bail - Date de fin (AAAA-MM-JJ);Bail - Loyer Mensuel (FCFA);Bail - Caution (FCFA)\n"
            "Rez-de-chaussée;B-01;Boutique 1;vêtements;15;Boutique test;Mamadou;Diop;771234567;mamadou@email.com;Diop Corp;;2026-01-01;2026-12-31;150000;300000\n"
            "Rez-de-chaussée;B-02;Boutique 2;Restauration;20.5;;;;;;;;;;;\n"
        )
        csv_file = SimpleUploadedFile("import.csv", csv_data.encode('utf-8-sig'), content_type="text/csv")
        
        url = reverse('shop_import')
        response = self.client.post(url, {
            'file': csv_file,
            'overwrite': 'false',
            'initial_invoices': 'paid',
            'mall': self.mall.id
        })
        
        # Should redirect to shop list on success
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('shop_list')))
        
        # Verify Floor
        self.assertEqual(Floor.objects.count(), 1)
        floor = Floor.objects.first()
        self.assertEqual(floor.name, "Rez-de-chaussée")
        
        # Verify Shops
        self.assertEqual(Shop.objects.count(), 2)
        shop1 = Shop.objects.get(shop_number="B-01")
        self.assertEqual(shop1.name, "Boutique 1")
        self.assertEqual(shop1.status, "occupied")
        self.assertEqual(shop1.surface, 15)
        self.assertEqual(shop1.category, "clothing")
        
        shop2 = Shop.objects.get(shop_number="B-02")
        self.assertEqual(shop2.name, "Boutique 2")
        self.assertEqual(shop2.status, "available")
        
        # Verify Tenant
        self.assertEqual(Tenant.objects.count(), 1)
        tenant = Tenant.objects.first()
        self.assertEqual(tenant.first_name, "Mamadou")
        self.assertEqual(tenant.last_name, "Diop")
        
        # Verify Lease
        self.assertEqual(Lease.objects.count(), 1)
        lease = Lease.objects.first()
        self.assertEqual(lease.shop, shop1)
        self.assertEqual(lease.tenant, tenant)
        self.assertEqual(lease.monthly_rent, 150000)
        self.assertEqual(lease.deposit, 300000)
        
        # Verify Invoices (initial invoices were set to 'paid')
        # Total invoices: 1 for rent, 1 for charges (deposit)
        self.assertEqual(Invoice.objects.count(), 2)
        self.assertEqual(Invoice.objects.filter(status='paid').count(), 2)
        self.assertEqual(Payment.objects.count(), 2)

    def test_csv_import_validation_errors(self):
        # Invalid CSV data:
        # Row 1: missing floor name
        # Row 2: invalid date format for start_date
        csv_data = (
            "Étage / Niveau;Boutique - Numéro;Boutique - Nom;Boutique - Catégorie;Boutique - Surface (m²);Boutique - Description;Locataire - Prénom;Locataire - Nom;Locataire - Téléphone;Locataire - Email;Locataire - Raison Sociale;Locataire - N° Pièce d'identité;Bail - Date de début (AAAA-MM-JJ);Bail - Date de fin (AAAA-MM-JJ);Bail - Loyer Mensuel (FCFA);Bail - Caution (FCFA)\n"
            ";B-01;Boutique 1;clothing;15;Boutique test;Mamadou;Diop;771234567;mamadou@email.com;Diop Corp;;2026-01-01;2026-12-31;150000;300000\n"
            "Rez-de-chaussée;B-02;Boutique 2;Restauration;20.5;;Mamadou;Diop;771234567;;;;bad-date;2026-12-31;150000;\n"
        )
        csv_file = SimpleUploadedFile("import_bad.csv", csv_data.encode('utf-8-sig'), content_type="text/csv")
        
        url = reverse('shop_import')
        response = self.client.post(url, {
            'file': csv_file,
            'overwrite': 'false',
            'initial_invoices': 'none',
            'mall': self.mall.id
        })
        
        # No redirect (returns 200 with error page)
        self.assertEqual(response.status_code, 200)
        self.assertIn('errors', response.context)
        self.assertEqual(len(response.context['errors']), 2)
        
        # Ensure no database records were saved (atomic transaction)
        self.assertEqual(Shop.objects.count(), 0)
        self.assertEqual(Floor.objects.count(), 0)
        self.assertEqual(Tenant.objects.count(), 0)
        self.assertEqual(Lease.objects.count(), 0)

