import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from io import BytesIO

class InvoiceService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='NormalRight',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT
        ))
    
    def generate_invoice_number(self, user):
        """Generate unique invoice number for user"""
        prefix = user.invoice_prefix
        next_number = user.next_invoice_number
        
        # Check if invoice number already exists
        while True:
            invoice_number = f"{prefix}-{next_number}"
            from ..models import Invoice
            if not Invoice.objects(invoice_number=invoice_number).first():
                break
            next_number = str(int(next_number) + 1).zfill(4)
        
        return invoice_number
    
    def generate_invoice_pdf(self, invoice):
        """Generate PDF for invoice"""
        try:
            # Create buffer for PDF
            buffer = BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # Add company header
            story.extend(self._create_company_header(invoice))
            
            # Add invoice details
            story.extend(self._create_invoice_details(invoice))
            
            # Add client information
            story.extend(self._create_client_section(invoice))
            
            # Add invoice items table
            story.extend(self._create_items_table(invoice))
            
            # Add totals section
            story.extend(self._create_totals_section(invoice))
            
            # Add notes and terms
            story.extend(self._create_notes_section(invoice))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF content
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
    
    def _create_company_header(self, invoice):
        """Create company header section"""
        story = []
        
        # Company name
        if invoice.user.company_name:
            story.append(Paragraph(invoice.user.company_name, self.styles['InvoiceTitle']))
        
        # Company details
        company_details = []
        if invoice.user.company_address:
            company_details.append(invoice.user.company_address)
        if invoice.user.company_phone:
            company_details.append(f"Phone: {invoice.user.company_phone}")
        if invoice.user.company_website:
            company_details.append(f"Website: {invoice.user.company_website}")
        
        for detail in company_details:
            story.append(Paragraph(detail, self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_invoice_details(self, invoice):
        """Create invoice details section"""
        story = []
        
        # Invoice title and number
        story.append(Paragraph("INVOICE", self.styles['SectionTitle']))
        story.append(Paragraph(f"Invoice Number: {invoice.invoice_number}", self.styles['Normal']))
        story.append(Paragraph(f"Issue Date: {invoice.issue_date.strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(Paragraph(f"Due Date: {invoice.due_date.strftime('%B %d, %Y')}", self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_client_section(self, invoice):
        """Create client information section"""
        story = []
        
        story.append(Paragraph("Bill To:", self.styles['SectionTitle']))
        
        if invoice.client.contact_person:
            story.append(Paragraph(invoice.client.contact_person, self.styles['Normal']))
        
        story.append(Paragraph(invoice.client.company_name, self.styles['Normal']))
        story.append(Paragraph(invoice.client.billing_address, self.styles['Normal']))
        
        city_state_zip = []
        if invoice.client.billing_city:
            city_state_zip.append(invoice.client.billing_city)
        if invoice.client.billing_state:
            city_state_zip.append(invoice.client.billing_state)
        if invoice.client.billing_zip_code:
            city_state_zip.append(invoice.client.billing_zip_code)
        
        if city_state_zip:
            story.append(Paragraph(", ".join(city_state_zip), self.styles['Normal']))
        
        if invoice.client.billing_country:
            story.append(Paragraph(invoice.client.billing_country, self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_items_table(self, invoice):
        """Create invoice items table"""
        story = []
        
        story.append(Paragraph("Items:", self.styles['SectionTitle']))
        
        # Table headers
        headers = ['Description', 'Qty', 'Unit Price', 'Tax %', 'Discount %', 'Total']
        
        # Table data
        data = [headers]
        for item in invoice.items:
            data.append([
                item.description,
                str(item.quantity),
                f"{item.unit_price:.2f}",
                f"{item.tax_rate:.1f}%",
                f"{item.discount_rate:.1f}%",
                f"{item.total:.2f}"
            ])
        
        # Create table
        table = Table(data, colWidths=[2.5*inch, 0.5*inch, 1*inch, 0.7*inch, 0.7*inch, 1*inch])
        
        # Style table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        return story
    
    def _create_totals_section(self, invoice):
        """Create totals section"""
        story = []
        
        # Totals table
        totals_data = [
            ['Subtotal:', f"{invoice.subtotal:.2f}"],
            ['Tax Total:', f"{invoice.tax_total:.2f}"],
            ['Discount Total:', f"{invoice.discount_total:.2f}"]
        ]
        
        if invoice.shipping_fee > 0:
            totals_data.append(['Shipping Fee:', f"{invoice.shipping_fee:.2f}"])
        
        if invoice.handling_fee > 0:
            totals_data.append(['Handling Fee:', f"{invoice.handling_fee:.2f}"])
        
        totals_data.append(['Total Amount:', f"{invoice.total_amount:.2f}"])
        totals_data.append(['Paid Amount:', f"{invoice.paid_amount:.2f}"])
        totals_data.append(['Balance Due:', f"{invoice.balance_due:.2f}"])
        
        # Create totals table
        table = Table(totals_data, colWidths=[2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        return story
    
    def _create_notes_section(self, invoice):
        """Create notes and terms section"""
        story = []
        
        if invoice.notes:
            story.append(Paragraph("Notes:", self.styles['SectionTitle']))
            story.append(Paragraph(invoice.notes, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        if invoice.terms_conditions:
            story.append(Paragraph("Terms & Conditions:", self.styles['SectionTitle']))
            story.append(Paragraph(invoice.terms_conditions, self.styles['Normal']))
        
        return story
    
    def send_invoice_email(self, invoice):
        """Send invoice by email"""
        try:
            # This would integrate with your email service
            # For now, return True to simulate success
            print(f"Sending invoice {invoice.invoice_number} to {invoice.client.email}")
            return True
            
        except Exception as e:
            print(f"Error sending invoice email: {e}")
            return False
