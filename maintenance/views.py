from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import MaintenanceRequest


class MaintenanceListView(LoginRequiredMixin, ListView):
    model = MaintenanceRequest
    template_name = 'maintenance/maintenance_list.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        qs = MaintenanceRequest.objects.select_related('reported_by', 'assigned_employee').all()
        active_mall = self.request.active_mall
        if active_mall:
            qs = qs.filter(mall=active_mall)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'maintenance'
        return context


class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRequest
    template_name = 'maintenance/maintenance_form.html'
    fields = ['title', 'description', 'zone', 'priority', 'status', 'assigned_to', 'assigned_employee', 'photo', 'estimated_cost', 'actual_cost']
    success_url = reverse_lazy('maintenance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'maintenance'
        context['title'] = "Signaler une anomalie"
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        active_mall = self.request.active_mall
        from employees.models import Employee
        if active_mall:
            form.fields['assigned_employee'].queryset = Employee.objects.filter(mall=active_mall, status='active', is_maintenance=True)
        else:
            form.fields['assigned_employee'].queryset = Employee.objects.filter(status='active', is_maintenance=True)
        return form

    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        if self.request.active_mall:
            form.instance.mall = self.request.active_mall
        messages.success(self.request, "La demande d'intervention a été créée avec succès.")
        return super().form_valid(form)


class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceRequest
    template_name = 'maintenance/maintenance_form.html'
    fields = ['title', 'description', 'zone', 'priority', 'status', 'assigned_to', 'assigned_employee', 'photo', 'estimated_cost', 'actual_cost', 'notes']
    success_url = reverse_lazy('maintenance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'maintenance'
        context['title'] = "Mettre à jour l'intervention"
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        active_mall = self.request.active_mall
        from employees.models import Employee
        if active_mall:
            form.fields['assigned_employee'].queryset = Employee.objects.filter(mall=active_mall, status='active', is_maintenance=True)
        else:
            form.fields['assigned_employee'].queryset = Employee.objects.filter(status='active', is_maintenance=True)
        return form

    def form_valid(self, form):
        # Check if assignment changed
        request_obj = self.get_object()
        assigned_employee = form.cleaned_data.get('assigned_employee')
        
        if assigned_employee and request_obj.assigned_employee != assigned_employee:
            from django.contrib.auth.models import User
            from django.db.models import Q
            from core.models import Notification
            
            admins = User.objects.filter(Q(is_superuser=True) | Q(profile__role__in=['admin', 'manager', 'maintenance'])).distinct()
            for admin in admins:
                if admin != self.request.user:
                    Notification.objects.create(
                        user=admin,
                        title="Intervention assignée",
                        message=f"L'intervention '{form.instance.title}' a été assignée à {assigned_employee.full_name}.",
                        notif_type='info'
                    )

        messages.success(self.request, "La demande de maintenance a été mise à jour.")
        return super().form_valid(form)


class MaintenanceDeleteView(LoginRequiredMixin, DeleteView):
    model = MaintenanceRequest
    template_name = 'maintenance/maintenance_confirm_delete.html'
    success_url = reverse_lazy('maintenance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'maintenance'
        return context

    def form_valid(self, form):
        messages.success(self.request, f"La demande d'intervention '{self.object.title}' a été supprimée.")
        return super().form_valid(form)

