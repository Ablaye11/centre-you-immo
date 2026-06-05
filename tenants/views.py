from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import Tenant, Shop, Lease, Floor, Mall
from .forms import ShopForm, TenantForm, FloorForm, MallForm
from finance.models import Invoice, Payment


def _generate_invoice_number():
    """Generate a unique sequential invoice number like FAC-2024-0042."""
    today = timezone.now()
    prefix = f"FAC-{today.year}-"
    last = Invoice.objects.filter(invoice_number__startswith=prefix).order_by('-invoice_number').first()
    if last:
        try:
            seq = int(last.invoice_number.split('-')[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


class TenantListView(LoginRequiredMixin, ListView):
    model = Tenant
    template_name = 'tenants/tenant_list.html'
    context_object_name = 'tenants'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'tenants'
        active_mall = self.request.active_mall
        context['shops'] = Shop.objects.filter(mall=active_mall) if active_mall else Shop.objects.all()
        return context

    def get_queryset(self):
        active_mall = self.request.active_mall
        # Tenants that have at least one lease in the active mall
        if active_mall:
            queryset = Tenant.objects.filter(leases__shop__mall=active_mall).distinct().prefetch_related('leases')
        else:
            queryset = Tenant.objects.prefetch_related('leases')
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['active_mall'] = self.request.active_mall
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'tenants'
        context['title'] = "Nouveau locataire"
        context['is_new'] = True
        return context

    @transaction.atomic
    def form_valid(self, form):
        tenant = form.save()
        shop = form.cleaned_data.get('shop')
        monthly_rent = form.cleaned_data.get('monthly_rent')
        deposit = form.cleaned_data.get('deposit')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        initial_payment = form.cleaned_data.get('initial_payment', 'none')
        payment_method = form.cleaned_data.get('payment_method', 'cash')

        lease = None
        if shop and monthly_rent and start_date and end_date:
            lease = Lease.objects.create(
                shop=shop,
                tenant=tenant,
                start_date=start_date,
                end_date=end_date,
                monthly_rent=monthly_rent,
                deposit=deposit or 0,
                status='active',
            )
            # Mark shop as occupied
            shop.status = 'occupied'
            shop.save(update_fields=['status'])

            today = timezone.now().date()

            def _make_invoice(inv_type, amount, description, paid=False):
                inv = Invoice.objects.create(
                    invoice_number=_generate_invoice_number(),
                    tenant=tenant,
                    shop=shop,
                    invoice_type=inv_type,
                    amount=amount,
                    issue_date=today,
                    due_date=today,
                    status='paid' if paid else 'pending',
                    paid_date=today if paid else None,
                    description=description,
                )
                if paid:
                    Payment.objects.create(
                        invoice=inv,
                        amount=amount,
                        payment_date=today,
                        method=payment_method,
                        notes=f"Paiement initial à la signature du bail",
                    )
                return inv

            # Generate invoices based on initial_payment choice
            if initial_payment in ('deposit', 'both') and deposit:
                _make_invoice('charges', deposit, f"Caution - Bail {shop}", paid=True)
            elif deposit:
                _make_invoice('charges', deposit, f"Caution - Bail {shop}", paid=False)

            if initial_payment in ('rent', 'both') and monthly_rent:
                _make_invoice('rent', monthly_rent, f"Premier loyer - {start_date.strftime('%B %Y')}", paid=True)
            else:
                _make_invoice('rent', monthly_rent, f"Loyer - {start_date.strftime('%B %Y')}", paid=False)

            messages.success(self.request, f"✅ Locataire '{tenant.full_name}' créé, bail signé pour {shop.name}, factures générées.")
        else:
            messages.success(self.request, f"✅ Locataire '{tenant.full_name}' créé avec succès.")

        return redirect(self.success_url)


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


class TenantDeleteView(LoginRequiredMixin, DeleteView):
    model = Tenant
    template_name = 'tenants/tenant_confirm_delete.html'
    success_url = reverse_lazy('tenant_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'tenants'
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Le locataire '{self.object.full_name}' a été supprimé.")
        return super().form_valid(form)


class ShopListView(LoginRequiredMixin, TemplateView):
    """Visual map of all shops showing occupied vs available."""
    template_name = 'tenants/shop_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'tenants'

        active_mall = self.request.active_mall
        if active_mall:
            all_shops = Shop.objects.filter(mall=active_mall).order_by('floor', 'shop_number')
        else:
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




class ShopCreateView(LoginRequiredMixin, CreateView):
    """Create a new shop/boutique."""
    model = Shop
    template_name = 'tenants/shop_form.html'
    form_class = ShopForm
    success_url = reverse_lazy('shop_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['active_mall'] = self.request.active_mall
        return kwargs

    def form_valid(self, form):
        if self.request.active_mall:
            form.instance.mall = self.request.active_mall
        return super().form_valid(form)

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['active_mall'] = self.request.active_mall
        return kwargs
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

    def get_queryset(self):
        active_mall = self.request.active_mall
        if active_mall:
            return Floor.objects.filter(mall=active_mall)
        return Floor.objects.all()

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
        if self.request.active_mall:
            form.instance.mall = self.request.active_mall
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


# ---- Mall (Centre Commercial) CRUD Views ----

class MallListView(LoginRequiredMixin, ListView):
    model = Mall
    template_name = 'tenants/mall_list.html'
    context_object_name = 'malls'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'malls'
        return context


class MallCreateView(LoginRequiredMixin, CreateView):
    model = Mall
    form_class = MallForm
    template_name = 'tenants/mall_form.html'
    success_url = reverse_lazy('mall_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'malls'
        context['title'] = "Ajouter un Centre Commercial"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"✅ Centre commercial '{form.instance.name}' créé avec succès.")
        return super().form_valid(form)


class MallUpdateView(LoginRequiredMixin, UpdateView):
    model = Mall
    form_class = MallForm
    template_name = 'tenants/mall_form.html'
    success_url = reverse_lazy('mall_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'malls'
        context['title'] = f"Modifier - {self.object.name}"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Centre commercial '{form.instance.name}' mis à jour.")
        return super().form_valid(form)


class MallDeleteView(LoginRequiredMixin, DeleteView):
    model = Mall
    template_name = 'tenants/mall_confirm_delete.html'
    success_url = reverse_lazy('mall_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'malls'
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Centre commercial '{self.object.name}' supprimé.")
        return super().form_valid(form)


class LeasePrintView(LoginRequiredMixin, DetailView):
    model = Lease
    template_name = 'tenants/lease_print.html'
    context_object_name = 'lease'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'tenants'
        context['today'] = timezone.now().date()
        return context


class AddLeaseView(LoginRequiredMixin, View):
    """Assign a new shop (bail) to an existing tenant."""

    def get(self, request, pk):
        tenant = Tenant.objects.get(pk=pk)
        active_mall = request.active_mall
        if active_mall:
            available_shops = Shop.objects.filter(mall=active_mall, status='available')
        else:
            available_shops = Shop.objects.filter(status='available')
        return render(request, 'tenants/add_lease.html', {
            'tenant': tenant,
            'available_shops': available_shops,
            'active_menu': 'tenants',
            'today': timezone.now().date().isoformat(),
        })

    @transaction.atomic
    def post(self, request, pk):
        tenant = Tenant.objects.get(pk=pk)
        active_mall = request.active_mall

        shop_id = request.POST.get('shop')
        monthly_rent = request.POST.get('monthly_rent')
        deposit = request.POST.get('deposit') or 0
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        initial_payment = request.POST.get('initial_payment', 'none')
        payment_method = request.POST.get('payment_method', 'cash')

        if not (shop_id and monthly_rent and start_date and end_date):
            messages.error(request, "Veuillez remplir tous les champs obligatoires : boutique, loyer, dates de début et de fin.")
            if active_mall:
                available_shops = Shop.objects.filter(mall=active_mall, status='available')
            else:
                available_shops = Shop.objects.filter(status='available')
            return render(request, 'tenants/add_lease.html', {
                'tenant': tenant,
                'available_shops': available_shops,
                'active_menu': 'tenants',
                'today': timezone.now().date().isoformat(),
            })

        try:
            shop = Shop.objects.get(pk=shop_id)
        except Shop.DoesNotExist:
            messages.error(request, "Boutique introuvable.")
            return redirect('tenant_detail', pk=pk)

        from datetime import date
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)

        lease = Lease.objects.create(
            shop=shop,
            tenant=tenant,
            start_date=start_date,
            end_date=end_date,
            monthly_rent=monthly_rent,
            deposit=deposit or 0,
            status='active',
        )
        shop.status = 'occupied'
        shop.save(update_fields=['status'])

        today = timezone.now().date()

        def _make_invoice(inv_type, amount, description, paid=False):
            inv = Invoice.objects.create(
                invoice_number=_generate_invoice_number(),
                tenant=tenant,
                shop=shop,
                invoice_type=inv_type,
                amount=amount,
                issue_date=today,
                due_date=today,
                status='paid' if paid else 'pending',
                paid_date=today if paid else None,
                description=description,
            )
            if paid:
                Payment.objects.create(
                    invoice=inv,
                    amount=amount,
                    payment_date=today,
                    method=payment_method,
                    notes="Paiement initial à la signature du bail",
                )
            return inv

        deposit_val = float(deposit) if deposit else 0
        rent_val = float(monthly_rent)

        if initial_payment in ('deposit', 'both') and deposit_val:
            _make_invoice('charges', deposit_val, f"Caution - Bail {shop}", paid=True)
        elif deposit_val:
            _make_invoice('charges', deposit_val, f"Caution - Bail {shop}", paid=False)

        if initial_payment in ('rent', 'both'):
            _make_invoice('rent', rent_val, f"Premier loyer - {start_date.strftime('%B %Y')}", paid=True)
        else:
            _make_invoice('rent', rent_val, f"Loyer - {start_date.strftime('%B %Y')}", paid=False)

        messages.success(request, f"✅ Bail pour la boutique {shop.shop_number} ({shop.name}) ajouté avec succès à {tenant.full_name}. Factures générées.")
        return redirect('tenant_detail', pk=pk)

