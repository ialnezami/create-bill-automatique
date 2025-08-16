from mongoengine import Document, StringField, EmailField, DateTimeField, BooleanField, ReferenceField, ListField
from datetime import datetime

class Client(Document):
    user = ReferenceField('User', required=True)
    company_name = StringField(required=True, max_length=100)
    contact_person = StringField(max_length=100)
    email = EmailField(required=True)
    phone = StringField(max_length=20)
    
    # Billing address
    billing_address = StringField(required=True, max_length=200)
    billing_city = StringField(required=True, max_length=50)
    billing_state = StringField(max_length=50)
    billing_zip_code = StringField(max_length=20)
    billing_country = StringField(required=True, max_length=50)
    
    # Shipping address (optional, defaults to billing)
    shipping_address = StringField(max_length=200)
    shipping_city = StringField(max_length=50)
    shipping_state = StringField(max_length=50)
    shipping_zip_code = StringField(max_length=20)
    shipping_country = StringField(max_length=50)
    
    # Additional information
    tax_id = StringField(max_length=50)
    notes = StringField(max_length=500)
    tags = ListField(StringField(max_length=50))
    
    # Status
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'clients',
        'indexes': [
            'user',
            'company_name',
            'email',
            'tags'
        ]
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user.id),
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'billing_address': self.billing_address,
            'billing_city': self.billing_city,
            'billing_state': self.billing_state,
            'billing_zip_code': self.billing_zip_code,
            'billing_country': self.billing_country,
            'shipping_address': self.shipping_address,
            'shipping_city': self.shipping_city,
            'shipping_state': self.shipping_state,
            'shipping_zip_code': self.shipping_zip_code,
            'shipping_country': self.shipping_country,
            'tax_id': self.tax_id,
            'notes': self.notes,
            'tags': self.tags,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
