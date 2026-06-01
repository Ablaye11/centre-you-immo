from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Tenant, Shop, Lease, Floor
from .forms import ShopForm, TenantForm, FloorForm


class TenantListView(LoginRequiredMixin, ListView):
    model = Tenant
    template_name = 'tenants/tenant_list.html'
    context_object_name = 'tenants'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'tenants'
        context['shops'] = Shop.objects.all()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(first_name__icontains=query) | queryset.filter(last_name__icontains=query) | queryset.filter(company_name__icontains=query)
        return queryset


class TenantDetailView(LoginRequiredMixin, DetailView):
    model = Tenant
    template_name = 'tenants/tenant_detail.html'
    context_object_name = 'tenant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'tenants'
        context['leases'] = self.object.leases.all()
        return context


class TenantCreateView(LoginRequiredMixin, CreateView):
    model = Tenant
    template_name = 'tenants/tenant_form.html'
    form_class = TenantForm
    success_url = reverse_lazy('tenant_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'tenants'
        context['title'] = "Nouveau locataire"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Le locataire a été créé avec succès.")
        return super().form_valid(form)


class TenantUpdateView(LoginRequiredMixin, UpdateView):
    model = Tenant
    template_name = 'tenants/tenant_form.html'
    form_class = TenantForm
    success_url = reverse_lazy('tenant_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'tenants'
        context['title'] = "Modifier le locataire"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Les informations du locataire ont ete mises a jour.")
        return super().form_valid(form)


class ShopListView(LoginRequiredMixin, TemplateView):
    """Visual map of all shops showing occupied vs available."""
    template_name = 'tenants/shop_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'tenants'

        all_shops = Shop.objects.all().order_by('floor', 'shop_number')
        context['shops'] = all_shops
    
        # Stats
        total = all_shops.count()
        occupied = all_shops.filter(status='occupied').count()
        available = all_shops.filter(status='available').count()
        maintenance = all_shops.filter(status='maintenance').count()

        context['total_shops'] = total
        context['occupied_shops'] = occupied
        context['available_shops'] = available
        context['maintenance_shops'] = maintenance
        context['occupancy_rate'] = round((occupied / total * 100)) if total > 0 else 0

        # Group by floor
        floors = {}
        for shop in all_shops:
            f = shop.floor.name if shop.floor else 'Non assigné'
            if f not in floors:
                floors[f] = []
            floors[f].append(shop)
        context['floors'] = floors

        return context


from django.views.generic import DeleteView

class ShopCreateView(LoginRequiredMixin, CreateView):
    """Create a new shop/boutique."""
    model = Shop
    template_name = 'tenants/shop_form.html'
    form_class = ShopForm
    success_url = reverse_lazy('shop_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'shops'
        context['title'] = 'Ajouter une Boutique'
        context['is_new'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, f"La boutique '{form.instance.name}' a ete ajoutee avec succes.")
        return super().form_valid(form)


class ShopUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing shop."""
    model = Shop
    template_name = 'tenants/shop_form.html'
    form_class = ShopForm
    success_url = reverse_lazy('shop_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'shops'
        context['title'] = f'Modifier - {self.object.name}'
        context['is_new'] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, f"La boutique '{form.instance.name}' a ete mise a jour.")
        return super().form_valid(form)


class ShopDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a shop."""
    model = Shop
    template_name = 'tenants/shop_confirm_delete.html'
    success_url = reverse_lazy('shop_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'shops'
        return context

    def form_valid(self, form):
        messages.success(self.request, f"La boutique '{self.object.name}' a ete supprimee.")
        return super().form_valid(form)


# ---- Floor Views ----

class FloorListView(LoginRequiredMixin, ListView):
    model = Floor
    template_name = 'tenants/floor_list.html'
    context_object_name = 'floors'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'floors'
        return context

class FloorCreateView(LoginRequiredMixin, CreateView):
    model = Floor
    form_class = FloorForm
    template_name = 'tenants/floor_form.html'
    success_url = reverse_lazy('floor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'floors'
        context['title'] = "Ajouter un Étage"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"L'étage '{form.instance.name}' a été ajouté.")
        return super().form_valid(form)

class FloorUpdateView(LoginRequiredMixin, UpdateView):
    model = Floor
    form_class = FloorForm
    template_name = 'tenants/floor_form.html'
    success_url = reverse_lazy('floor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'floors'
        context['title'] = f"Modifier - {self.object.name}"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"L'étage '{form.instance.name}' a été mis à jour.")
        return super().form_valid(form)

class FloorDeleteView(LoginRequiredMixin, DeleteView):
    model = Floor
    template_name = 'tenants/floor_confirm_delete.html'
    success_url = reverse_lazy('floor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'floors'
        return context

    def form_valid(self, form):
        messages.success(self.request, f"L'étage '{self.object.name}' a été supprimé.")
        return super().form_valid(form)
