from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
from django.contrib import messages
from django.core.management import call_command
from tenants.models import Shop, Lease, Tenant, Floor
from maintenance.models import MaintenanceRequest
from parking.models import ParkingSpace, ParkingSubscription
from finance.models import Invoice, Expense
from employees.models import Employee, Department
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
import datetime
import json


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'dashboard'

        # Basic counts & states
        total_shops = Shop.objects.count()
        occupied_shops = Shop.objects.filter(status='occupied').count()
        context['occupancy_rate'] = round((occupied_shops / total_shops * 100)) if total_shops > 0 else 0
        
        context['total_maintenance'] = MaintenanceRequest.objects.filter(status__in=['new', 'in_progress']).count()
        
        total_parking = ParkingSpace.objects.count()
        available_parking = ParkingSpace.objects.filter(status='available').count()
        context['parking_available'] = available_parking
        context['parking_rate'] = round((available_parking / total_parking * 100)) if total_parking > 0 else 0

        # Financial Calculations (current month)
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        monthly_revenue = Invoice.objects.filter(
            status='paid',
            paid_date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_expenses = Expense.objects.filter(
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0

        context['monthly_revenue'] = monthly_revenue
        context['monthly_net'] = monthly_revenue - monthly_expenses

        # Recent activities & warnings
        context['recent_requests'] = MaintenanceRequest.objects.all().order_by('-created_at')[:5]
        context['recent_invoices'] = Invoice.objects.all().order_by('-issue_date')[:5]
        context['expiring_leases'] = [l for l in Lease.objects.filter(status='active') if l.is_expiring_soon][:5]

        # Monthly income list for visual bar chart (2 queries instead of 12)
        today = timezone.now().date()
        six_months_ago = (today - datetime.timedelta(days=180)).replace(day=1)

        revenue_by_month = (
            Invoice.objects.filter(status='paid', paid_date__gte=six_months_ago)
            .annotate(month=TruncMonth('paid_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        expenses_by_month = (
            Expense.objects.filter(date__gte=six_months_ago)
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
        return context


class CustomLogoutView(View):
    """Custom logout view supporting both GET and POST requests to avoid 405 errors."""
    def get(self, request):
        logout(request)
        return redirect('login')

    def post(self, request):
        logout(request)
        return redirect('login')


class ResetDatabaseView(LoginRequiredMixin, View):
    """Deletes all operational database entries (except the active superuser/user)."""
    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Permission refusée.")
            return redirect('dashboard')
        try:
            # Delete operational models
            Lease.objects.all().delete()
            Tenant.objects.all().delete()
            Shop.objects.all().delete()
            Floor.objects.all().delete()
            Employee.objects.all().delete()
            Department.objects.all().delete()
            MaintenanceRequest.objects.all().delete()
            Expense.objects.all().delete()
            Invoice.objects.all().delete()
            ParkingSubscription.objects.all().delete()
            ParkingSpace.objects.all().delete()
            
            # Delete all other users except current user
            User = request.user.__class__
            User.objects.exclude(pk=request.user.pk).delete()
            
            messages.success(request, "La base de données a été remise à zéro avec succès (les données opérationnelles et autres comptes utilisateurs ont été supprimés).")
        except Exception as e:
            messages.error(request, f"Erreur lors de la remise à zéro : {str(e)}")
        return redirect('dashboard')


class RestoreDatabaseView(LoginRequiredMixin, View):
    """Runs seed_data command to restore database demo entries."""
    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Permission refusée.")
            return redirect('dashboard')
        try:
            call_command('seed_data')
            messages.success(request, "La base de données a été restaurée avec succès. Veuillez vous reconnecter avec les identifiants de test (admin / admin123).")
        except Exception as e:
            messages.error(request, f"Erreur lors de la restauration : {str(e)}")
        return redirect('dashboard')

