from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Employee


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'employees'
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        active_mall = self.request.active_mall
        if active_mall:
            queryset = queryset.filter(mall=active_mall)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(position__icontains=query)
            )
        return queryset


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    template_name = 'employees/employee_form.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'department', 'position', 'hire_date', 'contract_type', 'salary', 'status', 'address']
    success_url = reverse_lazy('employee_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'employees'
        context['title'] = "Nouvel Employé"
        return context

    def form_valid(self, form):
        if self.request.active_mall:
            form.instance.mall = self.request.active_mall
        messages.success(self.request, "L'employé a été enregistré avec succès.")
        return super().form_valid(form)


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    template_name = 'employees/employee_form.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'department', 'position', 'hire_date', 'contract_type', 'salary', 'status', 'address']
    success_url = reverse_lazy('employee_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'employees'
        context['title'] = "Modifier les Informations de l'Employé"
        return context

    def form_valid(self, form):
        messages.success(self.request, "La fiche de l'employé a été mise à jour.")
        return super().form_valid(form)


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'employees'
        return context

    def form_valid(self, form):
        messages.success(self.request, f"L'employé '{self.object.full_name}' a été supprimé.")
        return super().form_valid(form)

