import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from finance.models import Invoice
from tenants.models import Lease
from django.utils import timezone


class Command(BaseCommand):
    help = 'Sends email reminders for overdue invoices and expiring leases.'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        sent_count = 0

        # ---- 1. Overdue Invoice Reminders ----
        overdue_invoices = Invoice.objects.filter(status='overdue')
        self.stdout.write(f"Found {overdue_invoices.count()} overdue invoices.")

        for invoice in overdue_invoices:
            tenant = invoice.tenant
            if not tenant.email:
                self.stdout.write(self.style.WARNING(
                    f"  [!] {tenant.full_name} has no email, skipping invoice {invoice.invoice_number}."
                ))
                continue

            days_overdue = (today - invoice.due_date).days
            subject = f"[RAPPEL] Facture {invoice.invoice_number} en retard - YOU IMMO"
            message = (
                f"Bonjour {tenant.full_name},\n\n"
                f"Nous vous rappelons que votre facture N° {invoice.invoice_number} "
                f"d'un montant de {invoice.amount} FCFA, émise le {invoice.issue_date.strftime('%d/%m/%Y')}, "
                f"est en retard de {days_overdue} jour(s).\n\n"
                f"Date d'échéance initiale : {invoice.due_date.strftime('%d/%m/%Y')}\n"
                f"Boutique concernée : {invoice.shop.shop_number} - {invoice.shop.name}\n\n"
                f"Merci de bien vouloir régulariser votre situation dans les plus brefs délais.\n\n"
                f"Cordialement,\n"
                f"La Direction du Centre Commercial YOU IMMO\n"
                f"\"Une autre idée de l'immobilier\""
            )

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@youimmo.com',
                    [tenant.email],
                    fail_silently=False,
                )
                sent_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  [OK] Rappel envoye a {tenant.email} pour facture {invoice.invoice_number}"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"  [ERREUR] Erreur envoi a {tenant.email}: {e}"
                ))

        # ---- 2. Expiring Lease Reminders (to admin) ----
        expiring_leases = []
        for lease in Lease.objects.filter(status='active'):
            if lease.is_expiring_soon:
                expiring_leases.append(lease)

        if expiring_leases:
            self.stdout.write(f"Found {len(expiring_leases)} leases expiring within 30 days.")
            
            lease_details = ""
            for lease in expiring_leases:
                lease_details += (
                    f"  - {lease.tenant.full_name} - Boutique {lease.shop.shop_number} "
                    f"(expire le {lease.end_date.strftime('%d/%m/%Y')}, "
                    f"{lease.days_remaining} jours restants)\n"
                )

            admin_subject = f"[ALERTE] {len(expiring_leases)} bail(s) expirant bientôt - YOU IMMO"
            admin_message = (
                f"Bonjour Administrateur,\n\n"
                f"Les baux suivants arrivent à expiration dans les 30 prochains jours :\n\n"
                f"{lease_details}\n"
                f"Veuillez prendre les dispositions nécessaires pour le renouvellement "
                f"ou la libération des emplacements concernés.\n\n"
                f"Cordialement,\n"
                f"Système de Gestion YOU IMMO"
            )

            try:
                send_mail(
                    admin_subject,
                    admin_message,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@youimmo.com',
                    ['admin@youimmo.com'],
                    fail_silently=False,
                )
                sent_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  [OK] Alerte baux envoyee a l'admin"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"  [ERREUR] Erreur envoi alerte admin: {e}"
                ))

        self.stdout.write(self.style.SUCCESS(f"\nTermine. {sent_count} email(s) envoye(s)."))
