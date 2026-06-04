from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from core.models import UserProfile
from tenants.models import Mall

class MallMiddleware:
    """Middleware to select and store the active mall in session."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Query all malls
            request.all_malls = Mall.objects.all()
            
            # Fetch active mall ID from session
            active_mall_id = request.session.get('active_mall_id')
            active_mall = None
            
            if active_mall_id:
                active_mall = Mall.objects.filter(id=active_mall_id).first()
            
            # Default to first mall if none is selected or not active
            if not active_mall:
                active_mall = Mall.objects.first()
                if active_mall:
                    request.session['active_mall_id'] = active_mall.id
            
            request.active_mall = active_mall
        else:
            request.all_malls = []
            request.active_mall = None

        response = self.get_response(request)
        return response


class RolePermissionMiddleware:
    """Middleware to enforce role-based route access controls with user-friendly redirects."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # 1. Enforce user profile existence
            if not hasattr(request.user, 'profile'):
                UserProfile.objects.create(
                    user=request.user,
                    role='admin' if (request.user.is_superuser or request.user.is_staff) else 'employee'
                )

            # 2. Check if user is a tenant
            is_tenant = hasattr(request.user, 'tenant') and request.user.tenant is not None
            path = request.path

            # Allow tenant dashboard, login/logout/admin views, media and static files
            if is_tenant:
                allowed_tenant_prefixes = [
                    '/locataire/',
                    '/logout/',
                    '/media/',
                    '/static/',
                    '/admin/',  # allow admin login pages if needed, middleware will redirect if they shouldn't be here
                ]
                # If tenant tries to access admin-only pages, redirect to their tenant portal
                is_allowed = False
                for prefix in allowed_tenant_prefixes:
                    if path.startswith(prefix) or path == '/':
                        is_allowed = True
                        break
                
                if not is_allowed:
                    return redirect('tenant_dashboard')

            # 3. Check roles for staff users (non-superusers)
            elif not request.user.is_superuser:
                role = request.user.profile.role
                denied = False
                msg = ""

                # Employees (Only admin, manager)
                if path.startswith('/employes/') and role not in ['admin', 'manager']:
                    denied = True
                    msg = "Seuls les Administrateurs et Managers peuvent gérer le personnel."

                # Finances (Admin, manager, accountant)
                elif path.startswith('/finances/') and role not in ['admin', 'manager', 'accountant']:
                    denied = True
                    msg = "Seuls les Administrateurs, Managers et Comptables peuvent accéder aux finances."

                # Maintenance (Admin, manager, maintenance, secretary)
                elif path.startswith('/maintenance/') and role not in ['admin', 'manager', 'maintenance', 'secretary']:
                    denied = True
                    msg = "Seuls les Administrateurs, Managers, Secrétaires et Agents de Maintenance peuvent gérer les demandes de maintenance."

                # Structural parts (shops, floors, malls) (Only admin, manager, secretary)
                elif (path.startswith('/locataires/boutiques/') or 
                      path.startswith('/locataires/etages/') or 
                      path.startswith('/locataires/centres/')) and role not in ['admin', 'manager', 'secretary']:
                    denied = True
                    msg = "Seuls les Administrateurs, Managers et Secrétaires peuvent modifier la structure du centre commercial."

                # General Tenants / Leases list and detail (Admin, manager, accountant, secretary)
                elif path.startswith('/locataires/') and role not in ['admin', 'manager', 'accountant', 'secretary']:
                    denied = True
                    msg = "Seuls les Administrateurs, Managers, Comptables et Secrétaires peuvent accéder aux locataires et contrats de baux."

                if denied:
                    messages.error(request, f"Accès refusé : {msg}")
                    return redirect('dashboard')

        response = self.get_response(request)
        return response
