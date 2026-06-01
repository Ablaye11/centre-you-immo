from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('db/reset/', views.ResetDatabaseView.as_view(), name='reset_database'),
    path('db/restore/', views.RestoreDatabaseView.as_view(), name='restore_database'),
]
