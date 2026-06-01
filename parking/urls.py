from django.urls import path
from . import views

urlpatterns = [
    path('', views.ParkingOverviewView.as_view(), name='parking_overview'),
]
