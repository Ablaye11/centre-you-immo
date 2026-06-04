from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.shortcuts import redirect
from .models import Employee
from .forms import EmployeeForm


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
    form_class = EmployeeForm
    success_url = reverse_lazy('employee_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'employees'
        context['title'] = "Nouvel Employé"
        return context

    @transaction.atomic
    def form_valid(self, form):
        employee = form.save(commit=False)
        if self.request.active_mall:
            employee.mall = self.request.active_mall

        create_account = form.cleaned_data.get('create_user_account')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        if create_account and username and password:
            from django.contrib.auth.models import User
            from core.models import UserProfile

            user = User.objects.create_user(
                username=username, 
                password=password, 
                email=employee.email,
                first_name=employee.first_name,
                last_name=employee.last_name
            )
            employee.user = user

            role = 'employee'
            if employee.is_accountant:
                role = 'accountant'
            elif employee.is_maintenance:
                role = 'maintenance'
            elif employee.is_secretary:
                role = 'secretary'

            UserProfile.objects.update_or_create(
                user=user,
                defaults={'role': role, 'phone': employee.phone}
            )

        employee.save()
        messages.success(self.request, "L'employé a été enregistré avec succès.")
        return redirect(self.success_url)


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    template_name = 'employees/employee_form.html'
    form_class = EmployeeForm
    success_url = reverse_lazy('employee_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'employees'
        context['title'] = "Modifier les Informations de l'Employé"
        return context

    @transaction.atomic
    def form_valid(self, form):
        employee = form.save(commit=False)

        password = form.cleaned_data.get('password')
        if employee.user and password:
            employee.user.set_password(password)
            employee.user.save()

        create_account = form.cleaned_data.get('create_user_account')
        username = form.cleaned_data.get('username')
        if create_account and not employee.user and username and password:
            from django.contrib.auth.models import User
            from core.models import UserProfile

            user = User.objects.create_user(
                username=username,
                password=password,
                email=employee.email,
                first_name=employee.first_name,
                last_name=employee.last_name
            )
            employee.user = user

        if employee.user:
            employee.user.email = employee.email
            employee.user.first_name = employee.first_name
            employee.user.last_name = employee.last_name
            employee.user.save()

            role = 'employee'
            if employee.is_accountant:
                role = 'accountant'
            elif employee.is_maintenance:
                role = 'maintenance'
            elif employee.is_secretary:
                role = 'secretary'

            from core.models import UserProfile
            UserProfile.objects.update_or_create(
                user=employee.user,
                defaults={'role': role, 'phone': employee.phone}
            )

        employee.save()
        messages.success(self.request, "La fiche de l'employé a été mise à jour.")
        return redirect(self.success_url)


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
