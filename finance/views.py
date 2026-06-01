from django.views.generic import TemplateView, CreateView, View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import Invoice, Expense
from tenants.models import Tenant, Shop
from django.db.models import Sum, Prefetch, Q
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment


class FinanceOverviewView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/finance_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'finance'
        
        # Totals
        context['total_invoiced'] = Invoice.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['total_collected'] = Invoice.objects.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
        context['total_pending'] = Invoice.objects.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
        context['total_overdue'] = Invoice.objects.filter(status='overdue').aggregate(total=Sum('amount'))['total'] or 0
        context['total_expenses'] = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0

        # Balance calculations
        context['net_balance'] = context['total_collected'] - context['total_expenses']

        # Lists with select_related and search filter
        q = self.request.GET.get('q')
        invoices = Invoice.objects.select_related('tenant', 'shop').order_by('-issue_date')
        expenses = Expense.objects.all().order_by('-date')

        if q:
            invoices = invoices.filter(
                Q(invoice_number__icontains=q) |
                Q(tenant__first_name__icontains=q) |
                Q(tenant__last_name__icontains=q) |
                Q(shop__shop_number__icontains=q) |
                Q(shop__name__icontains=q)
            )
            expenses = expenses.filter(
                Q(title__icontains=q) |
                Q(category__icontains=q) |
                Q(supplier__icontains=q)
            )

        context['invoices'] = invoices[:15]
        context['expenses'] = expenses[:15]
        
        return context


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    template_name = 'finance/invoice_form.html'
    fields = ['invoice_number', 'tenant', 'shop', 'invoice_type', 'amount', 'issue_date', 'due_date', 'status', 'description']
    success_url = reverse_lazy('finance_overview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'finance'
        context['title'] = "Emettre une Facture"
        return context

    def form_valid(self, form):
        messages.success(self.request, "La facture a ete emise avec succes.")
        return super().form_valid(form)


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    template_name = 'finance/expense_form.html'
    fields = ['title', 'category', 'amount', 'date', 'supplier', 'description']
    success_url = reverse_lazy('finance_overview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'finance'
        context['title'] = "Enregistrer une Depense"
        return context

    def form_valid(self, form):
        messages.success(self.request, "La depense a ete enregistree avec succes.")
        return super().form_valid(form)


class MarkInvoicePaidView(LoginRequiredMixin, View):
    """Mark an invoice as paid with current date."""

    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        if invoice.status != 'paid':
            invoice.status = 'paid'
            invoice.paid_date = timezone.now().date()
            invoice.save()
            messages.success(request, f"Facture {invoice.invoice_number} marquee comme payee.")
        else:
            messages.info(request, f"Facture {invoice.invoice_number} est deja payee.")
        return redirect('finance_overview')


class ExportInvoicesExcelView(LoginRequiredMixin, View):
    """Export all invoices to an Excel file."""

    def get(self, request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Factures YOU IMMO"

        # Header style
        header_fill = PatternFill(start_color="D2691E", end_color="D2691E", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_align = Alignment(horizontal="center", vertical="center")

        headers = ["N° Facture", "Locataire", "Boutique", "Type", "Montant (FCFA)", "Date Emission", "Date Echeance", "Date Paiement", "Statut"]
        ws.append(headers)

        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align

        # Column widths
        col_widths = [15, 25, 20, 15, 18, 16, 16, 16, 12]
        for i, width in enumerate(col_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

        # Data rows with select_related to avoid N+1 queries
        status_map = {'paid': 'Payee', 'pending': 'En attente', 'overdue': 'En retard', 'cancelled': 'Annulee'}
        for inv in Invoice.objects.select_related('tenant', 'shop').order_by('-issue_date'):
            ws.append([
                inv.invoice_number,
                inv.tenant.full_name,
                f"{inv.shop.shop_number} - {inv.shop.name}",
                inv.get_invoice_type_display(),
                float(inv.amount),
                str(inv.issue_date),
                str(inv.due_date),
                str(inv.paid_date) if inv.paid_date else "-",
                status_map.get(inv.status, inv.status),
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="factures_youimmo.xlsx"'
        wb.save(response)
        return response


class ExportTenantsExcelView(LoginRequiredMixin, View):
    """Export all tenants to an Excel file."""

    def get(self, request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Locataires YOU IMMO"

        header_fill = PatternFill(start_color="D2691E", end_color="D2691E", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_align = Alignment(horizontal="center", vertical="center")

        headers = ["Nom Complet", "Telephone", "Email", "Boutique", "Loyer Mensuel (FCFA)", "Depot Garantie (FCFA)", "Date Debut Bail", "Date Fin Bail", "Statut"]
        ws.append(headers)

        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align

        col_widths = [25, 16, 28, 22, 22, 22, 16, 16, 12]
        for i, width in enumerate(col_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

        from tenants.models import Lease
        active_leases_prefetch = Prefetch(
            'leases',
            queryset=Lease.objects.select_related('shop').filter(status='active'),
            to_attr='active_leases'
        )
        tenants = Tenant.objects.prefetch_related(active_leases_prefetch).order_by('last_name')

        for tenant in tenants:
            lease = tenant.active_leases[0] if tenant.active_leases else None
            ws.append([
                tenant.full_name,
                tenant.phone,
                tenant.email or "-",
                f"{lease.shop.shop_number} - {lease.shop.name}" if lease else "-",
                float(lease.monthly_rent) if lease else "-",
                float(lease.deposit) if lease else "-",
                str(lease.start_date) if lease else "-",
                str(lease.end_date) if lease else "-",
                "Actif" if lease else "Inactif",
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="locataires_youimmo.xlsx"'
        wb.save(response)
        return response


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'finance/invoice_confirm_delete.html'
    success_url = reverse_lazy('finance_overview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'finance'
        return context

    def form_valid(self, form):
        messages.success(self.request, f"La facture '{self.object.invoice_number}' a été supprimée.")
        return super().form_valid(form)


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = 'finance/expense_confirm_delete.html'
    success_url = reverse_lazy('finance_overview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'finance'
        return context

    def form_valid(self, form):
        messages.success(self.request, f"La dépense '{self.object.title}' a été supprimée.")
        return super().form_valid(form)

