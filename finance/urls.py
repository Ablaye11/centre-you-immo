from django.urls import path
from . import views
from .invoice_pdf import InvoicePDFView

urlpatterns = [
    path('', views.FinanceOverviewView.as_view(), name='finance_overview'),
    path('factures/creer/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('factures/<int:pk>/payer/', views.MarkInvoicePaidView.as_view(), name='mark_invoice_paid'),
    path('factures/generer/', views.GenerateMonthlyInvoicesView.as_view(), name='generate_monthly_invoices'),
    path('depenses/creer/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('factures/<int:invoice_id>/pdf/', InvoicePDFView.as_view(), name='invoice_pdf'),
    path('factures/<int:pk>/supprimer/', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    path('depenses/<int:pk>/supprimer/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
    path('export/factures/', views.ExportInvoicesExcelView.as_view(), name='export_invoices_excel'),
    path('export/locataires/', views.ExportTenantsExcelView.as_view(), name='export_tenants_excel'),
    path('rapports/', views.ReportOverviewView.as_view(), name='report_overview'),
    path('rapports/export/', views.ExportReportExcelView.as_view(), name='export_report_excel'),
    path('charges/repartition/', views.DistributeChargesView.as_view(), name='distribute_charges'),
    path('salaires/generer/', views.GenerateMonthlySalariesView.as_view(), name='generate_monthly_salaries'),
]
