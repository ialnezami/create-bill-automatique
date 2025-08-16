from mongoengine import Document, StringField, EmailField, DateTimeField, BooleanField, ListField, ReferenceField
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(Document):
    username = StringField(required=True, unique=True, max_length=50)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    first_name = StringField(required=True, max_length=50)
    last_name = StringField(required=True, max_length=50)
    company_name = StringField(max_length=100)
    role = StringField(choices=['admin', 'user'], default='user')
    is_active = BooleanField(default=True)
    is_verified = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Company settings
    company_address = StringField(max_length=200)
    company_phone = StringField(max_length=20)
    company_website = StringField(max_length=100)
    company_logo = StringField(max_length=200)
    
    # Invoice settings
    default_currency = StringField(default='EUR', max_length=3)
    default_tax_rate = StringField(default='20.0')
    invoice_prefix = StringField(default='INV', max_length=10)
    next_invoice_number = StringField(default='0001')
    
    # Payment settings
    stripe_enabled = BooleanField(default=False)
    paypal_enabled = BooleanField(default=False)
    
    # Localization settings
    preferred_language = StringField(default='en', max_length=5)
    timezone = StringField(default='UTC', max_length=50)
    
    meta = {
        'collection': 'users',
        'indexes': [
            'username',
            'email',
            'company_name'
        ]
    }
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company_name': self.company_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'company_address': self.company_address,
            'company_phone': self.company_phone,
            'company_website': self.company_website,
            'company_logo': self.company_logo,
            'default_currency': self.default_currency,
            'default_tax_rate': self.default_tax_rate,
            'invoice_prefix': self.invoice_prefix,
            'next_invoice_number': self.next_invoice_number,
            'stripe_enabled': self.stripe_enabled,
            'paypal_enabled': self.paypal_enabled,
            'preferred_language': self.preferred_language,
            'timezone': self.timezone
        }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
