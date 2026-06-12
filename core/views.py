from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.core.management import call_command
from tenants.models import Shop, Lease, Tenant, Floor, Mall
from maintenance.models import MaintenanceRequest
from parking.models import ParkingSpace, ParkingSubscription
from finance.models import Invoice, Expense
from employees.models import Employee, Department
from django.db.models import Sum, Q, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
import datetime
import json
import os
import io


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get(self, request, *args, **kwargs):
        if hasattr(request.user, 'tenant') and request.user.tenant is not None:
            return redirect('tenant_dashboard')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'dashboard'

        active_mall = self.request.active_mall
        if not active_mall:
            context['no_mall'] = True
            context['monthly_chart_data'] = json.dumps([])
            return context

        # Basic counts & states (filtered by active mall)
        total_shops = Shop.objects.filter(mall=active_mall).count()
        occupied_shops = Shop.objects.filter(mall=active_mall, status='occupied').count()
        context['occupancy_rate'] = round((occupied_shops / total_shops * 100)) if total_shops > 0 else 0
        
        context['total_maintenance'] = MaintenanceRequest.objects.filter(mall=active_mall, status__in=['new', 'in_progress']).count()
        
        active_tenants = Tenant.objects.filter(
            leases__shop__mall=active_mall,
            leases__status='active'
        ).distinct().count()
        context['active_tenants'] = active_tenants

        # Financial Calculations (current month for active mall)
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        monthly_revenue = Invoice.objects.filter(
            shop__mall=active_mall,
            status='paid',
            paid_date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_expenses = Expense.objects.filter(
            mall=active_mall,
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0

        context['monthly_revenue'] = monthly_revenue
        context['monthly_net'] = monthly_revenue - monthly_expenses

        # Recent activities & warnings (filtered by active mall)
        context['recent_requests'] = MaintenanceRequest.objects.filter(mall=active_mall).order_by('-created_at')[:5]
        context['recent_invoices'] = Invoice.objects.filter(shop__mall=active_mall).select_related('tenant').order_by('-issue_date')[:5]
        context['expiring_leases'] = [l for l in Lease.objects.filter(shop__mall=active_mall, status='active').select_related('tenant', 'shop') if l.is_expiring_soon][:5]

        # Monthly income list for visual bar chart
        today = timezone.now().date()
        six_months_ago = (today - datetime.timedelta(days=180)).replace(day=1)

        revenue_by_month = (
            Invoice.objects.filter(shop__mall=active_mall, status='paid', paid_date__gte=six_months_ago)
            .annotate(month=TruncMonth('paid_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        expenses_by_month = (
            Expense.objects.filter(mall=active_mall, date__gte=six_months_ago)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        # Build a dict for quick lookup
        rev_map = {entry['month'].strftime('%b'): int(entry['total']) for entry in revenue_by_month}
        exp_map = {entry['month'].strftime('%b'): int(entry['total']) for entry in expenses_by_month}

        # Generate the last 6 months labels
        monthly_data = []
        for i in range(5, -1, -1):
            month_date = (today - datetime.timedelta(days=i * 30)).replace(day=1)
            label = month_date.strftime('%b')
            monthly_data.append({
                'month': label,
                'revenue': rev_map.get(label, 0),
                'expenses': exp_map.get(label, 0),
            })

        context['monthly_chart_data'] = json.dumps(monthly_data)

        # ── Loyers en retard (alertes urgentes) ──────────────────────────────
        # On détermine les loyers en retard dynamiquement (status='overdue' OU status='pending' avec date dépassée)
        # sans faire d'écriture en base de données pour éviter de bloquer SQLite
        overdue_invoices = Invoice.objects.filter(
            shop__mall=active_mall
        ).filter(
            Q(status='overdue') | Q(status='pending', due_date__lt=today)
        ).select_related('tenant', 'shop').order_by('due_date')

        # Charger jusqu'à 11 factures pour optimiser le nombre de requêtes SQL
        overdue_list = list(overdue_invoices[:11])
        if len(overdue_list) <= 10:
            context['overdue_invoices_list'] = overdue_list
            context['total_overdue_count'] = len(overdue_list)
            context['total_overdue_amount'] = sum(inv.amount for inv in overdue_list)
        else:
            context['overdue_invoices_list'] = overdue_list[:10]
            stats = overdue_invoices.aggregate(count=Count('id'), total=Sum('amount'))
            context['total_overdue_count'] = stats['count'] or 0
            context['total_overdue_amount'] = stats['total'] or 0

        # ── Masse salariale (infos rapides) ──────────────────────────────────
        emp_stats = Employee.objects.filter(mall=active_mall, status='active').aggregate(
            count=Count('id'),
            total=Sum('salary')
        )
        context['active_employees_count'] = emp_stats['count'] or 0
        context['total_salary_monthly'] = emp_stats['total'] or 0

        # ── Vérifier si loyers et salaires déjà générés ce mois ──────────────
        context['invoices_generated_this_month'] = Invoice.objects.filter(
            shop__mall=active_mall,
            invoice_type='rent',
            issue_date__year=today.year,
            issue_date__month=today.month,
        ).exists()
        context['salaries_paid_this_month'] = Expense.objects.filter(
            mall=active_mall,
            category='salary',
            date__year=today.year,
            date__month=today.month,
        ).exists()

        return context


class SwitchMallView(LoginRequiredMixin, View):
    """View to switch active shopping center in session."""
    def post(self, request):
        mall_id = request.POST.get('mall_id')
        if mall_id:
            if Mall.objects.filter(id=mall_id).exists():
                request.session['active_mall_id'] = int(mall_id)
                messages.success(request, "Centre commercial changé avec succès.")
        
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('dashboard')


class CustomLogoutView(View):
    """Custom logout view supporting both GET and POST requests to avoid 405 errors."""
    def get(self, request):
        logout(request)
        return redirect('login')

    def post(self, request):
        logout(request)
        return redirect('login')


BACKUP_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data_backup.json')


class ResetDatabaseView(LoginRequiredMixin, View):
    """Sauvegarde les données actuelles puis efface toutes les entrées opérationnelles."""
    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Permission refusée.")
            return redirect('dashboard')
        try:
            # ── 1. Sauvegarde automatique avant effacement ────────────────
            buf = io.StringIO()
            call_command(
                'dumpdata',
                '--natural-foreign',
                '--natural-primary',
                '--exclude=contenttypes',
                '--exclude=auth.permission',
                '--exclude=sessions',
                '--indent=2',
                stdout=buf,
            )
            with open(BACKUP_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(buf.getvalue())

            # ── 2. Effacement des données opérationnelles ─────────────────
            Lease.objects.all().delete()
            Tenant.objects.all().delete()
            Shop.objects.all().delete()
            Floor.objects.all().delete()
            Mall.objects.all().delete()
            Employee.objects.all().delete()
            Department.objects.all().delete()
            MaintenanceRequest.objects.all().delete()
            Expense.objects.all().delete()
            Invoice.objects.all().delete()
            ParkingSubscription.objects.all().delete()
            ParkingSpace.objects.all().delete()

            # Supprimer tous les autres utilisateurs sauf l'utilisateur actuel
            User = request.user.__class__
            User.objects.exclude(pk=request.user.pk).delete()

            messages.success(
                request,
                "✅ Base remise à zéro. Une sauvegarde de vos données a été créée automatiquement "
                "— utilisez le bouton \"Restaurer mes données\" pour les récupérer."
            )
        except Exception as e:
            messages.error(request, f"Erreur lors de la remise à zéro : {str(e)}")
        return redirect('dashboard')


class RestoreBackupView(LoginRequiredMixin, View):
    """Recharge la dernière sauvegarde créée avant une remise à zéro."""
    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Permission refusée.")
            return redirect('dashboard')

        if not os.path.exists(BACKUP_FILE_PATH):
            messages.error(
                request,
                "❌ Aucune sauvegarde disponible. La sauvegarde est créée automatiquement "
                "lors d'une remise à zéro."
            )
            return redirect('dashboard')

        try:
            # Vider d'abord les données actuelles pour éviter les conflits de clés
            Lease.objects.all().delete()
            Tenant.objects.all().delete()
            Shop.objects.all().delete()
            Floor.objects.all().delete()
            Mall.objects.all().delete()
            Employee.objects.all().delete()
            Department.objects.all().delete()
            MaintenanceRequest.objects.all().delete()
            Expense.objects.all().delete()
            Invoice.objects.all().delete()
            ParkingSubscription.objects.all().delete()
            ParkingSpace.objects.all().delete()
            from django.contrib.auth.models import User as AuthUser
            AuthUser.objects.exclude(pk=request.user.pk).delete()

            # Recharger la sauvegarde
            call_command('loaddata', BACKUP_FILE_PATH, verbosity=0)

            messages.success(
                request,
                "✅ Vos données ont été restaurées avec succès ! "
                "Reconnectez-vous si votre compte a été réinitialisé."
            )
        except Exception as e:
            messages.error(request, f"Erreur lors de la restauration : {str(e)}")
        return redirect('dashboard')


class RestoreDatabaseView(LoginRequiredMixin, View):
    """Charge les données de démonstration via la commande seed_data."""
    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Permission refusée.")
            return redirect('dashboard')
        try:
            call_command('seed_data')
            messages.success(
                request,
                "✅ Données de démonstration chargées."
            )
        except Exception as e:
            messages.error(request, f"Erreur lors de la restauration démo : {str(e)}")
        return redirect('dashboard')


class MarkNotificationReadView(LoginRequiredMixin, View):
    """Mark a single notification as read and redirect to appropriate page or referer."""
    def get(self, request, pk):
        from core.models import Notification
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('dashboard')


class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    """Mark all unread notifications of the logged in user as read."""
    def post(self, request):
        from core.models import Notification
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, "Toutes les notifications ont été marquées comme lues.")
        
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('dashboard')

