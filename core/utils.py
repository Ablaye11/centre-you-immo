from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin(AccessMixin):
    """Verify that the current user has one of the allowed roles."""
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Superuser has access to everything
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
            
        # Check profile and role
        if hasattr(request.user, 'profile'):
            role = request.user.profile.role
            if role in self.allowed_roles:
                return super().dispatch(request, *args, **kwargs)
                
        raise PermissionDenied("Vous n'avez pas l'autorisation d'accéder à cette page.")
