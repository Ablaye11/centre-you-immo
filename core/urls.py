from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import tenant_portal

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('switch-mall/', views.SwitchMallView.as_view(), name='switch_mall'),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('db/reset/', views.ResetDatabaseView.as_view(), name='reset_database'),
    path('db/restore/', views.RestoreDatabaseView.as_view(), name='restore_database'),
    path('db/restore-backup/', views.RestoreBackupView.as_view(), name='restore_backup'),
    path('locataire/', tenant_portal.TenantDashboardView.as_view(), name='tenant_dashboard'),
    path('locataire/maintenance/signaler/', tenant_portal.TenantMaintenanceCreateView.as_view(), name='tenant_maintenance_create'),
    path('notifications/<int:pk>/lire/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('notifications/tout-lire/', views.MarkAllNotificationsReadView.as_view(), name='mark_all_notifications_read'),
]
