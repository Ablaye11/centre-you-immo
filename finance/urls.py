from django.urls import path
from . import views
from .invoice_pdf import InvoicePDFView

urlpatterns = [
    path('', views.FinanceOverviewView.as_view(), name='finance_overview'),
    path('factures/creer/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('depenses/creer/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('factures/<int:invoice_id>/pdf/', InvoicePDFView.as_view(), name='invoice_pdf'),
    path('factures/<int:pk>/supprimer/', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    path('depenses/<int:pk>/supprimer/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
]
