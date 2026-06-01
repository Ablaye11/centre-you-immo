from django.urls import path
from . import views

urlpatterns = [
    path('', views.EmployeeListView.as_view(), name='employee_list'),
    path('creer/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('<int:pk>/modifier/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('<int:pk>/supprimer/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
]
