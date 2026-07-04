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
        'app_name': 'Gestion Immobilière YOU IMMO',
        'app_short_name': 'YOU IMMO',
    }

    if request.user.is_authenticated:
        active_mall = getattr(request, 'active_mall', None)
        context['active_mall'] = active_mall
        context['all_malls'] = getattr(request, 'all_malls', [])

        from core.models import Notification
        unread_notifs = list(Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:11])
        if len(unread_notifs) <= 10:
            context['unread_notifications'] = unread_notifs
            context['unread_notifications_count'] = len(unread_notifs)
        else:
            context['unread_notifications'] = unread_notifs[:10]
            context['unread_notifications_count'] = Notification.objects.filter(user=request.user, is_read=False).count()

        if active_mall:
            context['pending_maintenance'] = MaintenanceRequest.objects.filter(
                mall=active_mall,
                status__in=['new', 'in_progress']
            ).count()
            from django.db.models import Q
            from django.utils import timezone
            context['overdue_invoices'] = Invoice.objects.filter(
                shop__mall=active_mall
            ).filter(
                Q(status='overdue') | Q(status='pending', due_date__lt=timezone.now().date())
            ).count()
        else:
            context['pending_maintenance'] = 0
            context['overdue_invoices'] = 0
    else:
        context['active_mall'] = None
        context['all_malls'] = []
        context['pending_maintenance'] = 0
        context['overdue_invoices'] = 0

    return context
