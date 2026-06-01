from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
from tenants.models import Shop, Lease
from maintenance.models import MaintenanceRequest
from parking.models import ParkingSpace
from finance.models import Invoice, Expense
from django.db.models import Sum
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

        # Monthly income list for visual bar chart
        monthly_data = []
        for i in range(5, -1, -1):
            date = today - datetime.timedelta(days=i*30)
            month_start = date.replace(day=1)
            next_month = (month_start + datetime.timedelta(days=32)).replace(day=1)
            
            rev = Invoice.objects.filter(
                status='paid',
                paid_date__gte=month_start,
                paid_date__lt=next_month
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            exp = Expense.objects.filter(
                date__gte=month_start,
                date__lt=next_month
            ).aggregate(total=Sum('amount'))['total'] or 0

            monthly_data.append({
                'month': month_start.strftime('%b'),
                'revenue': int(rev),
                'expenses': int(exp)
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
