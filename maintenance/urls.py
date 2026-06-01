from django.urls import path
from . import views

urlpatterns = [
    path('', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('creer/', views.MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('<int:pk>/modifier/', views.MaintenanceUpdateView.as_view(), name='maintenance_update'),
]
