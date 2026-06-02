import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile
from tenants.models import Shop, Tenant, Lease, Floor
from finance.models import Invoice, Expense, Payment
from employees.models import Employee, Department
from maintenance.models import MaintenanceRequest
from parking.models import ParkingSpace, ParkingSubscription


class Command(BaseCommand):
    help = 'Seeds database with realistic shopping center demo data.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing data...')
        # Clear existing
        User.objects.all().delete()
        Department.objects.all().delete()
        from tenants.models import Mall
        Mall.objects.all().delete()
        Shop.objects.all().delete()
        Floor.objects.all().delete()
        Tenant.objects.all().delete()
        ParkingSpace.objects.all().delete()
        MaintenanceRequest.objects.all().delete()
        Expense.objects.all().delete()

        self.stdout.write('Creating users...')
        # Create Users
        admin_user = User.objects.create_superuser('admin', 'admin@youimmo.com', 'admin123')
        admin_user.first_name = 'Alioune'
        admin_user.last_name = 'Sow'
        admin_user.save()
        UserProfile.objects.create(user=admin_user, role='admin', phone='+221 77 123 45 67')

        manager_user = User.objects.create_user('manager', 'manager@youimmo.com', 'manager123')
        manager_user.first_name = 'Mariama'
        manager_user.last_name = 'Diallo'
        manager_user.save()
        UserProfile.objects.create(user=manager_user, role='manager', phone='+221 77 987 65 43')

        self.stdout.write('Creating malls...')
        mall_dakar = Mall.objects.create(name='Centre Commercial YOU IMMO - Dakar', address='Avenue Cheikh Anta Diop, Dakar', description='Le plus grand centre commercial You Immo de Dakar')
        mall_thies = Mall.objects.create(name='Centre Commercial YOU IMMO - Thiès', address='Avenue Léopold Sédar Senghor, Thiès', description='Centre commercial régional au cœur de Thiès')
        mall_stlouis = Mall.objects.create(name='Centre Commercial YOU IMMO - Saint-Louis', address='Quartier Sindoné, Saint-Louis', description='Centre commercial au charme colonial de Saint-Louis')

        self.stdout.write('Creating departments...')
        # Departments
        dept_sec = Department.objects.create(name='Sécurité', description='Sécurité et gardiennage du centre')
        dept_maint = Department.objects.create(name='Technique & Maintenance', description='Entretien des installations')
        dept_clean = Department.objects.create(name='Nettoyage', description='Propreté du centre commercial')
        dept_admin = Department.objects.create(name='Administration', description='Secrétariat et accueil')

        self.stdout.write('Creating employees...')
        # Employees
        Employee.objects.create(mall=mall_dakar, first_name='Abdou', last_name='Ndiaye', email='abdou@youimmo.com', phone='+221 76 543 21 09', department=dept_sec, position='Agent de Sécurité Chef', hire_date=datetime.date(2024, 1, 15), contract_type='cdi', salary=250000, status='active')
        Employee.objects.create(mall=mall_dakar, first_name='Fatou', last_name='Sarr', email='fatou@youimmo.com', phone='+221 70 876 54 32', department=dept_clean, position='Technicienne de Surface', hire_date=datetime.date(2024, 2, 1), contract_type='cdd', salary=150000, status='active')
        Employee.objects.create(mall=mall_dakar, first_name='Ibrahima', last_name='Diagne', email='ibrahima@youimmo.com', phone='+221 78 456 12 34', department=dept_maint, position='Électricien Principal', hire_date=datetime.date(2023, 11, 1), contract_type='cdi', salary=350000, status='active')
        Employee.objects.create(mall=mall_thies, first_name='Awa', last_name='Faye', email='awa@youimmo.com', phone='+221 77 345 67 89', department=dept_admin, position='Hôtesse d\'accueil', hire_date=datetime.date(2025, 1, 10), contract_type='stage', salary=100000, status='active')
        Employee.objects.create(mall=mall_stlouis, first_name='Cheikh', last_name='Diallo', email='cheikh@youimmo.com', phone='+221 76 111 22 22', department=dept_sec, position='Gardien', hire_date=datetime.date(2024, 6, 1), contract_type='cdi', salary=180000, status='active')

        self.stdout.write('Creating floors...')
        # Floors for Dakar
        floor_rdc_dk = Floor.objects.create(mall=mall_dakar, name='Rez-de-chaussée', level=0, description='Niveau entrée principale - Dakar')
        floor_1er_dk = Floor.objects.create(mall=mall_dakar, name='1er Étage', level=1, description='Premier étage - Dakar')
        floor_2eme_dk = Floor.objects.create(mall=mall_dakar, name='2ème Étage', level=2, description='Deuxième étage - Dakar')
        floor_3eme_dk = Floor.objects.create(mall=mall_dakar, name='3ème Étage', level=3, description='Troisième étage - Dakar')

        # Floors for Thiès
        floor_rdc_th = Floor.objects.create(mall=mall_thies, name='Rez-de-chaussée', level=0, description='Niveau entrée principale - Thiès')
        floor_1er_th = Floor.objects.create(mall=mall_thies, name='1er Étage', level=1, description='Premier étage - Thiès')

        # Floors for Saint-Louis
        floor_rdc_sl = Floor.objects.create(mall=mall_stlouis, name='Rez-de-chaussée', level=0, description='Niveau unique - Saint-Louis')

        self.stdout.write('Creating shops...')
        # Dakar
        shop1 = Shop.objects.create(mall=mall_dakar, name='Samsung Brand Store', shop_number='A01', category='electronics', floor=floor_rdc_dk, surface=120.50, status='occupied', description='Boutique officielle Samsung')
        shop2 = Shop.objects.create(mall=mall_dakar, name='Café Touba & Gourmandises', shop_number='B04', category='food', floor=floor_rdc_dk, surface=45.00, status='occupied', description='Espace café et restauration rapide')
        shop3 = Shop.objects.create(mall=mall_dakar, name='City Mode & Couture', shop_number='C02', category='clothing', floor=floor_1er_dk, surface=85.00, status='occupied')
        shop4 = Shop.objects.create(mall=mall_dakar, name='Espace Vacant 1', shop_number='D12', category='other', floor=floor_2eme_dk, surface=60.00, status='available')
        shop5 = Shop.objects.create(mall=mall_dakar, name='Espace Vacant 2', shop_number='E03', category='other', floor=floor_3eme_dk, surface=200.00, status='available')

        # Thiès
        shop_th1 = Shop.objects.create(mall=mall_thies, name='Auchan Thiès', shop_number='T01', category='food', floor=floor_rdc_th, surface=400.00, status='occupied', description='Supermarché de proximité')
        shop_th2 = Shop.objects.create(mall=mall_thies, name='Beauty & Spa', shop_number='T02', category='other', floor=floor_1er_th, surface=75.00, status='available', description='Salon de beauté')

        # Saint-Louis
        shop_sl1 = Shop.objects.create(mall=mall_stlouis, name='Artisanat du Fleuve', shop_number='SL01', category='clothing', floor=floor_rdc_sl, surface=50.00, status='occupied', description='Boutique d\'artisanat local')
        shop_sl2 = Shop.objects.create(mall=mall_stlouis, name='Restaurant La Caravelle', shop_number='SL02', category='food', floor=floor_rdc_sl, surface=150.00, status='available')

        self.stdout.write('Creating tenants...')
        # Tenants
        tenant1 = Tenant.objects.create(first_name='Moustapha', last_name='Gueye', email='moustapha.gueye@gmail.com', phone='+221 77 654 32 10', company_name='Gueye Electronics SARL', id_number='1234567890123')
        tenant2 = Tenant.objects.create(first_name='Khadidiatou', last_name='Sene', email='khadija.sene@outlook.com', phone='+221 77 111 22 33', company_name='Khadija Café Group', id_number='2345678901234')
        tenant3 = Tenant.objects.create(first_name='Ousmane', last_name='Fall', email='ousmane.fall@gmail.com', phone='+221 76 888 99 00', company_name='City Mode Design', id_number='3456789012345')
        tenant4 = Tenant.objects.create(first_name='Samba', last_name='Sow', email='samba.sow@gmail.com', phone='+221 77 555 44 33', company_name='Auchan Sénégal', id_number='4567890123456')
        tenant5 = Tenant.objects.create(first_name='Fatoumata', last_name='Diallo', email='fatou.diallo@outlook.fr', phone='+221 78 222 33 44', company_name='GIE Artisans du Nord', id_number='5678901234567')

        self.stdout.write('Creating leases...')
        # Leases
        today = datetime.date.today()
        Lease.objects.create(shop=shop1, tenant=tenant1, start_date=today - datetime.timedelta(days=180), end_date=today + datetime.timedelta(days=185), monthly_rent=500000, deposit=1000000, status='active')
        Lease.objects.create(shop=shop2, tenant=tenant2, start_date=today - datetime.timedelta(days=90), end_date=today + datetime.timedelta(days=275), monthly_rent=200000, deposit=400000, status='active')
        Lease.objects.create(shop=shop3, tenant=tenant3, start_date=today - datetime.timedelta(days=340), end_date=today + datetime.timedelta(days=25), monthly_rent=350000, deposit=700000, status='active')
        Lease.objects.create(shop=shop_th1, tenant=tenant4, start_date=today - datetime.timedelta(days=120), end_date=today + datetime.timedelta(days=240), monthly_rent=1200000, deposit=2400000, status='active')
        Lease.objects.create(shop=shop_sl1, tenant=tenant5, start_date=today - datetime.timedelta(days=60), end_date=today + datetime.timedelta(days=300), monthly_rent=150000, deposit=300000, status='active')

        self.stdout.write('Creating parking spaces...')
        # Dakar Parking Spaces
        spaces_dk = []
        for i in range(1, 11):
            spaces_dk.append(ParkingSpace.objects.create(mall=mall_dakar, space_number=f"DK-{i:02d}", level='Sous-sol 1', space_type='standard' if i > 2 else 'vip', status='available'))
        
        # Thiès Parking Spaces
        spaces_th = []
        for i in range(1, 6):
            spaces_th.append(ParkingSpace.objects.create(mall=mall_thies, space_number=f"TH-{i:02d}", level='Niveau 0', space_type='standard', status='available'))

        # Mark some spaces occupied/reserved
        spaces_dk[0].status = 'occupied'
        spaces_dk[0].save()
        spaces_dk[1].status = 'reserved'
        spaces_dk[1].save()

        self.stdout.write('Creating parking subscriptions...')
        ParkingSubscription.objects.create(tenant=tenant1, space=spaces_dk[1], vehicle_plate='DK-4321-A', vehicle_type='Toyota RAV4', subscription_type='monthly', start_date=today - datetime.timedelta(days=30), end_date=today + datetime.timedelta(days=30), monthly_fee=30000, is_active=True)

        self.stdout.write('Creating invoices...')
        # Dakar Invoices
        Invoice.objects.create(invoice_number='FAC-2026-001', tenant=tenant1, shop=shop1, invoice_type='rent', amount=500000, issue_date=today - datetime.timedelta(days=45), due_date=today - datetime.timedelta(days=30), paid_date=today - datetime.timedelta(days=44), status='paid')
        Invoice.objects.create(invoice_number='FAC-2026-002', tenant=tenant2, shop=shop2, invoice_type='rent', amount=200000, issue_date=today - datetime.timedelta(days=45), due_date=today - datetime.timedelta(days=30), paid_date=today - datetime.timedelta(days=40), status='paid')
        Invoice.objects.create(invoice_number='FAC-2026-003', tenant=tenant3, shop=shop3, invoice_type='rent', amount=350000, issue_date=today - datetime.timedelta(days=10), due_date=today + datetime.timedelta(days=5), status='pending')
        Invoice.objects.create(invoice_number='FAC-2026-004', tenant=tenant1, shop=shop1, invoice_type='charges', amount=45000, issue_date=today - datetime.timedelta(days=5), due_date=today + datetime.timedelta(days=10), status='pending')
        Invoice.objects.create(invoice_number='FAC-2026-005', tenant=tenant3, shop=shop3, invoice_type='rent', amount=350000, issue_date=today - datetime.timedelta(days=40), due_date=today - datetime.timedelta(days=25), status='overdue')

        # Thiès Invoice
        Invoice.objects.create(invoice_number='FAC-2026-006', tenant=tenant4, shop=shop_th1, invoice_type='rent', amount=1200000, issue_date=today - datetime.timedelta(days=10), due_date=today + datetime.timedelta(days=5), status='pending')

        self.stdout.write('Creating payments...')
        # Payments for paid invoices
        paid_inv1 = Invoice.objects.get(invoice_number='FAC-2026-001')
        Payment.objects.create(invoice=paid_inv1, amount=500000, payment_date=today - datetime.timedelta(days=44), method='bank_transfer', notes='Paiement loyer Samsung')
        paid_inv2 = Invoice.objects.get(invoice_number='FAC-2026-002')
        Payment.objects.create(invoice=paid_inv2, amount=200000, payment_date=today - datetime.timedelta(days=40), method='cash', notes='Paiement Café Touba')

        self.stdout.write('Creating expenses...')
        # Dakar Expenses
        Expense.objects.create(mall=mall_dakar, title='Achat ampoules LED & Disjoncteurs', category='maintenance', amount=48000, date=today - datetime.timedelta(days=20), supplier='Senelec Materiel')
        Expense.objects.create(mall=mall_dakar, title='Paiement Facture d\'eau SDE', category='energy', amount=120000, date=today - datetime.timedelta(days=15), supplier='SEN\'EAU')
        Expense.objects.create(mall=mall_dakar, title='Rénovation caméra surveillance entrée', category='security', amount=350000, date=today - datetime.timedelta(days=5), supplier='G4S Sénégal')

        # Thiès Expenses
        Expense.objects.create(mall=mall_thies, title='Entretien Climatiseurs', category='maintenance', amount=150000, date=today - datetime.timedelta(days=8), supplier='Clim Froid')

        self.stdout.write('Creating maintenance requests...')
        # Maintenance requests
        MaintenanceRequest.objects.create(mall=mall_dakar, title='Fuite d\'eau toilettes RDC', description='Une fuite d\'eau importante a été signalée dans les toilettes publiques pour hommes près de la cafétéria.', zone='rdc', priority='high', status='in_progress', assigned_to='Plomberie Express', estimated_cost=45000, reported_by=admin_user)
        MaintenanceRequest.objects.create(mall=mall_thies, title='Climatisation centrale en panne', description='La climatisation centrale de la zone Est ne refroidit plus. Température ambiante en hausse.', zone='common', priority='urgent', status='new', reported_by=manager_user)
        MaintenanceRequest.objects.create(mall=mall_dakar, title='Remplacement néons escaliers', description='Plusieurs néons sont grillés dans les escaliers de secours menant au 2ème étage.', zone='elevator', priority='low', status='completed', assigned_to='Service Technique YouImmo', estimated_cost=15000, actual_cost=12000, completed_date=today - datetime.timedelta(days=2), reported_by=admin_user)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with demo data!'))
