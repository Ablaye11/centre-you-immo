from django import forms
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from tenants.models import Tenant, Lease
from finance.models import Invoice
from maintenance.models import MaintenanceRequest


class TenantRequiredMixin(UserPassesTestMixin):
    """Ensure the user has a Tenant profile linked."""
    def test_func(self):
        return hasattr(self.request.user, 'tenant') and self.request.user.tenant is not None

    def handle_no_permission(self):
        messages.error(self.request, "Accès refusé. Ce compte n'est pas lié à un profil de locataire.")
        return redirect('login')


class TenantDashboardView(LoginRequiredMixin, TenantRequiredMixin, TemplateView):
    template_name = 'tenant_portal/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.user.tenant
        
        # Get leases
        leases = Lease.objects.filter(tenant=tenant).select_related('shop', 'shop__mall')
        
        # Get invoices
        invoices = Invoice.objects.filter(tenant=tenant).select_related('shop').order_by('-issue_date')
        
        # Get maintenance requests
        maintenance_requests = MaintenanceRequest.objects.filter(reported_by=self.request.user).order_by('-created_at')
        
        # Stats
        total_invoiced = sum(inv.amount for inv in invoices)
        total_paid = sum(inv.amount for inv in invoices if inv.status == 'paid')
        total_pending = sum(inv.amount for inv in invoices if inv.status in ['pending', 'overdue'])
        
        context.update({
            'tenant': tenant,
            'leases': leases,
            'invoices': invoices,
            'maintenance_requests': maintenance_requests,
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'app_name': 'YOU IMMO',
        })
        return context


class TenantMaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'description', 'zone', 'priority', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Fuite d\'eau sous le lavabo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Décrivez le problème en détail...'}),
            'zone': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class TenantMaintenanceCreateView(LoginRequiredMixin, TenantRequiredMixin, CreateView):
    model = MaintenanceRequest
    form_class = TenantMaintenanceForm
    template_name = 'tenant_portal/maintenance_form.html'
    success_url = reverse_lazy('tenant_dashboard')

    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        
        # Try to find their active lease and mall
        tenant = self.request.user.tenant
        active_lease = Lease.objects.filter(tenant=tenant, status='active').first()
        if active_lease:
            form.instance.mall = active_lease.shop.mall
            
        messages.success(self.request, "Votre demande de maintenance a bien été enregistrée.")
        response = super().form_valid(form)

        # Notify admins and managers
        from django.contrib.auth.models import User
        from django.db.models import Q
        from core.models import Notification
        
        admins = User.objects.filter(Q(is_superuser=True) | Q(profile__role__in=['admin', 'manager']))
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title="Signalement d'anomalie",
                message=f"Le locataire {tenant.full_name} a signalé un incident : {form.instance.title} ({form.instance.get_zone_display()})",
                notif_type='warning'
            )
            
        return response
