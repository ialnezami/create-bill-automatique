from mongoengine import Document, StringField, BooleanField, DateTimeField, DictField, ReferenceField
from datetime import datetime

class Notification(Document):
    """Notification model for user notifications"""
    
    user = ReferenceField('User', required=True)
    title = StringField(required=True, max_length=200)
    message = StringField(required=True, max_length=1000)
    notification_type = StringField(required=True, choices=['info', 'success', 'warning', 'error'])
    data = DictField(default={})  # Additional data for the notification
    is_read = BooleanField(default=False)
    read_at = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'notifications',
        'indexes': [
            'user',
            'is_read',
            'created_at',
            ('user', 'is_read'),
            ('user', 'created_at')
        ],
        'ordering': ['-created_at']
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def to_dict(self):
        """Convert notification to dictionary"""
        return {
            'id': str(self.id),
            'user': str(self.user.id) if self.user else None,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'data': self.data,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        self.save()
    
    def __str__(self):
        return f"Notification({self.title} - {self.notification_type})"
