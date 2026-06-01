"""
Context processors for the core app.
Provides global context variables to all templates.
"""
from tenants.models import Shop
from maintenance.models import MaintenanceRequest
from finance.models import Invoice


def global_context(request):
    """Add global context variables available in all templates."""
    context = {
        'app_name': 'Centre Commercial YOU IMMO',
        'app_short_name': 'YOU IMMO',
    }

    if request.user.is_authenticated:
        context['pending_maintenance'] = MaintenanceRequest.objects.filter(
            status__in=['new', 'in_progress']
        ).count()
        context['overdue_invoices'] = Invoice.objects.filter(
            status='overdue'
        ).count()

    return context
