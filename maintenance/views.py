from django.views.generic import ListView, CreateView, UpdateView
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
        return MaintenanceRequest.objects.select_related('reported_by').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'maintenance'
        return context


class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRequest
    template_name = 'maintenance/maintenance_form.html'
    fields = ['title', 'description', 'zone', 'priority', 'status', 'assigned_to', 'estimated_cost', 'actual_cost']
    success_url = reverse_lazy('maintenance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'maintenance'
        context['title'] = "Signaler une anomalie"
        return context

    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        messages.success(self.request, "La demande d'intervention a été créée avec succès.")
        return super().form_valid(form)


class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceRequest
    template_name = 'maintenance/maintenance_form.html'
    fields = ['title', 'description', 'zone', 'priority', 'status', 'assigned_to', 'estimated_cost', 'actual_cost', 'notes']
    success_url = reverse_lazy('maintenance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'maintenance'
        context['title'] = "Mettre à jour l'intervention"
        return context

    def form_valid(self, form):
        messages.success(self.request, "La demande de maintenance a été mise à jour.")
        return super().form_valid(form)
