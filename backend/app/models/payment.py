from mongoengine import Document, StringField, DateTimeField, BooleanField, ReferenceField, DecimalField, EnumField
from datetime import datetime
from decimal import Decimal

class Payment(Document):
    # Basic information
    payment_id = StringField(required=True, unique=True)
    invoice = ReferenceField('Invoice', required=True)
    user = ReferenceField('User', required=True)
    client = ReferenceField('Client', required=True)
    
    # Payment details
    amount = DecimalField(required=True, precision=2)
    currency = StringField(required=True, max_length=3, default='EUR')
    payment_method = StringField(required=True, max_length=50)  # stripe, paypal, bank_transfer, etc.
    
    # Status
    status = EnumField('PaymentStatus', choices=['pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded'], default='pending')
    
    # Provider information
    provider = StringField(required=True, max_length=50)  # stripe, paypal, etc.
    provider_payment_id = StringField(max_length=100)
    provider_transaction_id = StringField(max_length=100)
    
    # Payment dates
    created_at = DateTimeField(default=datetime.utcnow)
    processed_at = DateTimeField()
    completed_at = DateTimeField()
    
    # Additional information
    description = StringField(max_length=200)
    metadata = StringField(max_length=1000)  # JSON string for additional data
    error_message = StringField(max_length=500)
    
    # Refund information
    refunded_amount = DecimalField(default=0.0, precision=2)
    refund_reason = StringField(max_length=200)
    refunded_at = DateTimeField()
    
    meta = {
        'collection': 'payments',
        'indexes': [
            'payment_id',
            'invoice',
            'user',
            'client',
            'status',
            'provider',
            'created_at'
        ]
    }
    
    def mark_as_processing(self):
        """Mark payment as processing"""
        self.status = 'processing'
        self.processed_at = datetime.utcnow()
    
    def mark_as_completed(self):
        """Mark payment as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        
        # Update invoice status
        if self.invoice:
            self.invoice.mark_as_paid(self.amount)
            self.invoice.save()
    
    def mark_as_failed(self, error_message=None):
        """Mark payment as failed"""
        self.status = 'failed'
        if error_message:
            self.error_message = error_message
    
    def mark_as_refunded(self, amount=None, reason=None):
        """Mark payment as refunded"""
        self.status = 'refunded'
        if amount:
            self.refunded_amount = amount
        if reason:
            self.refund_reason = reason
        self.refunded_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'payment_id': self.payment_id,
            'invoice_id': str(self.invoice.id) if self.invoice else None,
            'user_id': str(self.user.id),
            'client_id': str(self.client.id),
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'provider': self.provider,
            'provider_payment_id': self.provider_payment_id,
            'provider_transaction_id': self.provider_transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'description': self.description,
            'metadata': self.metadata,
            'error_message': self.error_message,
            'refunded_amount': float(self.refunded_amount),
            'refund_reason': self.refund_reason,
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None
        }
    
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
