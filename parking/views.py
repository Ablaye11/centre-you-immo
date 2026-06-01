from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ParkingSpace, ParkingSubscription


class ParkingOverviewView(LoginRequiredMixin, TemplateView):
    template_name = 'parking/parking_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'parking'
        
        # Spaces lists
        context['spaces'] = ParkingSpace.objects.all()
        
        # Stats
        context['total_spaces'] = ParkingSpace.objects.count()
        context['occupied_spaces'] = ParkingSpace.objects.filter(status='occupied').count()
        context['reserved_spaces'] = ParkingSpace.objects.filter(status='reserved').count()
        context['available_spaces'] = ParkingSpace.objects.filter(status='available').count()
        
        # Subscriptions
        context['subscriptions'] = ParkingSubscription.objects.all().order_by('-start_date')
        
        return context
