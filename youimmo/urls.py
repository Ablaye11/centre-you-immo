"""
URL configuration for youimmo project.
Centre Commercial YOU IMMO
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('locataires/', include('tenants.urls')),
    path('finances/', include('finance.urls')),
    path('employes/', include('employees.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('parking/', include('parking.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
