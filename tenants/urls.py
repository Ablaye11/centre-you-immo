from django.urls import path
from . import views

urlpatterns = [
    path('', views.TenantListView.as_view(), name='tenant_list'),
    path('boutiques/', views.ShopListView.as_view(), name='shop_list'),
    path('boutiques/creer/', views.ShopCreateView.as_view(), name='shop_create'),
    path('boutiques/importer/', views.ShopImportView.as_view(), name='shop_import'),
    path('boutiques/importer/modele/', views.ShopImportTemplateView.as_view(), name='shop_import_template'),
    path('boutiques/<int:pk>/modifier/', views.ShopUpdateView.as_view(), name='shop_update'),
    path('boutiques/<int:pk>/supprimer/', views.ShopDeleteView.as_view(), name='shop_delete'),
    path('<int:pk>/', views.TenantDetailView.as_view(), name='tenant_detail'),
    path('creer/', views.TenantCreateView.as_view(), name='tenant_create'),
    path('<int:pk>/modifier/', views.TenantUpdateView.as_view(), name='tenant_update'),
    path('<int:pk>/supprimer/', views.TenantDeleteView.as_view(), name='tenant_delete'),
    path('baux/<int:pk>/imprimer/', views.LeasePrintView.as_view(), name='lease_print'),
    path('<int:pk>/ajouter-bail/', views.AddLeaseView.as_view(), name='add_lease'),

    path('etages/', views.FloorListView.as_view(), name='floor_list'),
    path('etages/creer/', views.FloorCreateView.as_view(), name='floor_create'),
    path('etages/<int:pk>/modifier/', views.FloorUpdateView.as_view(), name='floor_update'),
    path('etages/<int:pk>/supprimer/', views.FloorDeleteView.as_view(), name='floor_delete'),

    # Mall (Centres Commerciaux) CRUD
    path('centres/', views.MallListView.as_view(), name='mall_list'),
    path('centres/creer/', views.MallCreateView.as_view(), name='mall_create'),
    path('centres/<int:pk>/modifier/', views.MallUpdateView.as_view(), name='mall_update'),
    path('centres/<int:pk>/supprimer/', views.MallDeleteView.as_view(), name='mall_delete'),
]
