from mongoengine import Document, StringField, DateTimeField, BooleanField, ReferenceField, ListField, DecimalField, IntField, EnumField
from datetime import datetime
from decimal import Decimal

class InvoiceItem(EmbeddedDocument):
    description = StringField(required=True, max_length=200)
    quantity = DecimalField(required=True, precision=2)
    unit_price = DecimalField(required=True, precision=2)
    tax_rate = DecimalField(default=0.0, precision=2)
    discount_rate = DecimalField(default=0.0, precision=2)
    
    @property
    def subtotal(self):
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self):
        return self.subtotal * (self.discount_rate / 100)
    
    @property
    def tax_amount(self):
        return (self.subtotal - self.discount_amount) * (self.tax_rate / 100)
    
    @property
    def total(self):
        return self.subtotal - self.discount_amount + self.tax_amount

class Invoice(Document):
    # Basic information
    invoice_number = StringField(required=True, unique=True)
    user = ReferenceField('User', required=True)
    client = ReferenceField('Client', required=True)
    
    # Dates
    issue_date = DateTimeField(required=True, default=datetime.utcnow)
    due_date = DateTimeField(required=True)
    sent_date = DateTimeField()
    paid_date = DateTimeField()
    
    # Status
    status = EnumField('InvoiceStatus', choices=['draft', 'sent', 'paid', 'overdue', 'cancelled'], default='draft')
    
    # Financial information
    currency = StringField(required=True, max_length=3, default='EUR')
    subtotal = DecimalField(required=True, precision=2, default=0.0)
    tax_total = DecimalField(required=True, precision=2, default=0.0)
    discount_total = DecimalField(required=True, precision=2, default=0.0)
    total_amount = DecimalField(required=True, precision=2, default=0.0)
    paid_amount = DecimalField(required=True, precision=2, default=0.0)
    balance_due = DecimalField(required=True, precision=2, default=0.0)
    
    # Items
    items = ListField(EmbeddedDocumentField(InvoiceItem), required=True)
    
    # Additional charges
    shipping_fee = DecimalField(default=0.0, precision=2)
    handling_fee = DecimalField(default=0.0, precision=2)
    
    # Notes and terms
    notes = StringField(max_length=500)
    terms_conditions = StringField(max_length=500)
    
    # Payment information
    payment_method = StringField(max_length=50)
    payment_reference = StringField(max_length=100)
    
    # Files
    pdf_path = StringField(max_length=200)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'invoices',
        'indexes': [
            'invoice_number',
            'user',
            'client',
            'status',
            'issue_date',
            'due_date'
        ]
    }
    
    def calculate_totals(self):
        """Calculate all totals based on items"""
        self.subtotal = sum(item.subtotal for item in self.items)
        self.discount_total = sum(item.discount_amount for item in self.items)
        self.tax_total = sum(item.tax_amount for item in self.items)
        
        # Add additional fees
        self.total_amount = (self.subtotal - self.discount_total + 
                           self.tax_total + self.shipping_fee + self.handling_fee)
        
        # Calculate balance due
        self.balance_due = self.total_amount - self.paid_amount
    
    def mark_as_sent(self):
        """Mark invoice as sent"""
        self.status = 'sent'
        self.sent_date = datetime.utcnow()
    
    def mark_as_paid(self, amount=None):
        """Mark invoice as paid"""
        if amount:
            self.paid_amount = amount
        else:
            self.paid_amount = self.total_amount
        
        self.balance_due = self.total_amount - self.paid_amount
        self.status = 'paid'
        self.paid_date = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'invoice_number': self.invoice_number,
            'user_id': str(self.user.id),
            'client_id': str(self.client.id),
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'sent_date': self.sent_date.isoformat() if self.sent_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'status': self.status,
            'currency': self.currency,
            'subtotal': float(self.subtotal),
            'tax_total': float(self.tax_total),
            'discount_total': float(self.discount_total),
            'total_amount': float(self.total_amount),
            'paid_amount': float(self.paid_amount),
            'balance_due': float(self.balance_due),
            'items': [{
                'description': item.description,
                'quantity': float(item.quantity),
                'unit_price': float(item.unit_price),
                'tax_rate': float(item.tax_rate),
                'discount_rate': float(item.discount_rate),
                'subtotal': float(item.subtotal),
                'discount_amount': float(item.discount_amount),
                'tax_amount': float(item.tax_amount),
                'total': float(item.total)
            } for item in self.items],
            'shipping_fee': float(self.shipping_fee),
            'handling_fee': float(self.handling_fee),
            'notes': self.notes,
            'terms_conditions': self.terms_conditions,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'pdf_path': self.pdf_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
