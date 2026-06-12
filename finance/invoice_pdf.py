import io
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from .models import Invoice


class InvoicePDFView(LoginRequiredMixin, View):
    """Generates a professional PDF for a given invoice."""

    def get(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setTitle(f"Facture-{invoice.invoice_number}")

        # Document margins and layout setups
        width, height = letter

        # Draw a custom premium gold/orange header
        p.setFillColor(colors.HexColor('#0d1321')) # Deep Blue Dark Theme Accent
        p.rect(0, height - 120, width, 120, fill=True, stroke=False)

        # Header Text
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 16)
        mall_name = invoice.shop.mall.name.upper() if (invoice.shop and invoice.shop.mall) else "YOU-IMMO"
        p.drawString(40, height - 60, mall_name)
        
        p.setFont("Helvetica", 9)
        p.drawString(40, height - 85, "YOU-IMMO - Une autre idée de l'immobilier")
        p.drawString(40, height - 98, "Rond Point Keur Massar, Route de Diaxay | Tél: 76 754 30 30 / 77 873 01 00")

        # Invoice Status Banner
        p.setFillColor(colors.HexColor('#f59e0b')) # Gold Accent
        p.setFont("Helvetica-Bold", 14)
        p.drawRightString(width - 40, height - 60, f"FACTURE : {invoice.invoice_number}")
        
        status_text = invoice.get_status_display().upper()
        p.setFont("Helvetica", 11)
        p.drawRightString(width - 40, height - 85, f"STATUT : {status_text}")

        # Grid separator
        p.setStrokeColor(colors.HexColor('#e2e8f0'))
        p.setLineWidth(1)
        p.line(40, height - 150, width - 40, height - 150)

        # Invoice details (Issuer / Receiver)
        p.setFillColor(colors.HexColor('#1e293b'))
        p.setFont("Helvetica-Bold", 11)
        p.drawString(40, height - 180, "ÉMIS PAR :")
        p.setFont("Helvetica", 10)
        p.drawString(40, height - 200, "YOU-IMMO")
        p.drawString(40, height - 215, "Rond Point Keur Massar, Route de Diaxay")
        p.drawString(40, height - 230, "youimmobtp@gmail.com")

        p.setFont("Helvetica-Bold", 11)
        p.drawString(width / 2 + 40, height - 180, "DESTINATAIRE / LOCATAIRE :")
        p.setFont("Helvetica", 10)
        p.drawString(width / 2 + 40, height - 200, f"{invoice.tenant.full_name}")
        if invoice.tenant.company_name:
            p.drawString(width / 2 + 40, height - 215, f"Entreprise: {invoice.tenant.company_name}")
        p.drawString(width / 2 + 40, height - 230, f"Téléphone: {invoice.tenant.phone}")
        p.drawString(width / 2 + 40, height - 245, f"Emplacement: Boutique {invoice.shop.shop_number}")

        # Item Details Table
        p.line(40, height - 290, width - 40, height - 290)
        
        # Table Header
        p.setFillColor(colors.HexColor('#0d1321'))
        p.rect(40, height - 315, width - 80, 25, fill=True, stroke=False)
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, height - 308, "Description des charges / Loyers")
        p.drawString(width / 2 - 20, height - 308, "Type")
        p.drawRightString(width - 50, height - 308, "Total (FCFA)")

        # Table Row
        p.setFillColor(colors.HexColor('#1e293b'))
        p.setFont("Helvetica", 10)
        desc = invoice.description if invoice.description else f"Paiement au titre de la location de l'emplacement {invoice.shop.shop_number}"
        p.drawString(50, height - 345, desc[:50])
        p.drawString(width / 2 - 20, height - 345, invoice.get_invoice_type_display())
        p.drawRightString(width - 50, height - 345, f"{invoice.amount} FCFA")
        
        p.line(40, height - 365, width - 40, height - 365)

        # Summary Block
        p.setFont("Helvetica-Bold", 11)
        p.drawString(40, height - 400, f"Date d'émission : {invoice.issue_date.strftime('%d/%m/%Y')}")
        p.drawString(40, height - 420, f"Date d'échéance : {invoice.due_date.strftime('%d/%m/%Y')}")
        
        # Total Box
        p.setFillColor(colors.HexColor('#f1f5f9'))
        p.rect(width - 240, height - 440, 200, 60, fill=True, stroke=False)
        p.setFillColor(colors.HexColor('#0f172a'))
        p.setFont("Helvetica", 9)
        p.drawString(width - 230, height - 405, "MONTANT TOTAL NET :")
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(colors.HexColor('#ea580c')) # Orange/Dark Gold
        p.drawString(width - 230, height - 430, f"{invoice.amount} FCFA")

        # Terms and Signatures
        p.setFillColor(colors.HexColor('#64748b'))
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(40, 80, "Merci de régler vos factures avant la date d'échéance indiquée.")
        p.drawString(40, 68, "En cas de retard de paiement, des pénalités légales pourront s'appliquer conformément au bail.")
        
        # Stamp signature line
        p.setFont("Helvetica-Bold", 9)
        p.setFillColor(colors.HexColor('#0d1321'))
        p.drawRightString(width - 60, 100, "Le Directeur de Gestion")
        p.setStrokeColor(colors.HexColor('#94a3b8'))
        p.line(width - 180, 50, width - 40, 50)

        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()

        # Check if the user wants to view inline (for printing or viewing in browser)
        # instead of downloading as an attachment.
        inline = request.GET.get('inline', 'false') == 'true'
        as_attachment = not inline

        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=as_attachment,
            filename=f"facture-{invoice.invoice_number}.pdf"
        )
