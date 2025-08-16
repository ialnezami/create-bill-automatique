import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from ..models import User, Notification

class NotificationService:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.user_rooms: Dict[str, str] = {}  # user_id -> room_name
        
    def create_notification(self, user_id: str, title: str, message: str, 
                          notification_type: str = 'info', data: Optional[Dict] = None) -> Notification:
        """Create a new notification in the database"""
        try:
            notification = Notification(
                user=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                data=data or {},
                is_read=False
            )
            notification.save()
            
            # Send real-time notification
            self.send_notification(user_id, notification)
            
            return notification
            
        except Exception as e:
            current_app.logger.error(f"Error creating notification: {str(e)}")
            return None
    
    def send_notification(self, user_id: str, notification: Notification):
        """Send real-time notification to user"""
        try:
            room_name = self.user_rooms.get(user_id)
            if room_name:
                self.socketio.emit('notification', {
                    'id': str(notification.id),
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.notification_type,
                    'data': notification.data,
                    'created_at': notification.created_at.isoformat(),
                    'is_read': notification.is_read
                }, room=room_name)
                
        except Exception as e:
            current_app.logger.error(f"Error sending real-time notification: {str(e)}")
    
    def send_invoice_notification(self, user_id: str, invoice, action: str):
        """Send invoice-related notifications"""
        notifications = {
            'created': {
                'title': 'New Invoice Created',
                'message': f'Invoice #{invoice.invoice_number} has been created',
                'type': 'success'
            },
            'sent': {
                'title': 'Invoice Sent',
                'message': f'Invoice #{invoice.invoice_number} has been sent to {invoice.client.company_name}',
                'type': 'info'
            },
            'paid': {
                'title': 'Payment Received',
                'message': f'Payment received for invoice #{invoice.invoice_number}',
                'type': 'success'
            },
            'overdue': {
                'title': 'Invoice Overdue',
                'message': f'Invoice #{invoice.invoice_number} is overdue by {invoice.days_overdue} days',
                'type': 'warning'
            }
        }
        
        if action in notifications:
            notif_data = notifications[action]
            self.create_notification(
                user_id=user_id,
                title=notif_data['title'],
                message=notif_data['message'],
                notification_type=notif_data['type'],
                data={'invoice_id': str(invoice.id), 'action': action}
            )
    
    def send_payment_notification(self, user_id: str, payment, action: str):
        """Send payment-related notifications"""
        notifications = {
            'completed': {
                'title': 'Payment Completed',
                'message': f'Payment of {payment.currency} {payment.amount:.2f} received',
                'type': 'success'
            },
            'failed': {
                'title': 'Payment Failed',
                'message': f'Payment attempt failed for invoice #{payment.invoice.invoice_number}',
                'type': 'error'
            },
            'refunded': {
                'title': 'Payment Refunded',
                'message': f'Payment refunded for invoice #{payment.invoice.invoice_number}',
                'type': 'info'
            }
        }
        
        if action in notifications:
            notif_data = notifications[action]
            self.create_notification(
                user_id=user_id,
                title=notif_data['title'],
                message=notif_data['message'],
                notification_type=notif_data['type'],
                data={'payment_id': str(payment.id), 'action': action}
            )
    
    def send_client_notification(self, user_id: str, client, action: str):
        """Send client-related notifications"""
        notifications = {
            'created': {
                'title': 'New Client Added',
                'message': f'Client {client.company_name} has been added',
                'type': 'info'
            },
            'updated': {
                'title': 'Client Updated',
                'message': f'Client {client.company_name} information has been updated',
                'type': 'info'
            }
        }
        
        if action in notifications:
            notif_data = notifications[action]
            self.create_notification(
                user_id=user_id,
                title=notif_data['title'],
                message=notif_data['message'],
                notification_type=notif_data['type'],
                data={'client_id': str(client.id), 'action': action}
            )
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        try:
            notification = Notification.objects(id=notification_id, user=user_id).first()
            if notification:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                notification.save()
                return True
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    def mark_all_as_read(self, user_id: str) -> bool:
        """Mark all notifications as read for a user"""
        try:
            Notification.objects(user=user_id, is_read=False).update(
                is_read=True,
                read_at=datetime.utcnow()
            )
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error marking all notifications as read: {str(e)}")
            return False
    
    def get_user_notifications(self, user_id: str, limit: int = 50, unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user"""
        try:
            query = {'user': user_id}
            if unread_only:
                query['is_read'] = False
                
            notifications = Notification.objects(**query).order_by('-created_at').limit(limit)
            return list(notifications)
            
        except Exception as e:
            current_app.logger.error(f"Error getting user notifications: {str(e)}")
            return []
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        try:
            return Notification.objects(user=user_id, is_read=False).count()
            
        except Exception as e:
            current_app.logger.error(f"Error getting unread count: {str(e)}")
            return 0
    
    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        try:
            notification = Notification.objects(id=notification_id, user=user_id).first()
            if notification:
                notification.delete()
                return True
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error deleting notification: {str(e)}")
            return False
    
    def cleanup_old_notifications(self, days: int = 30) -> int:
        """Clean up old notifications"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted_count = Notification.objects(created_at__lt=cutoff_date).delete()
            return deleted_count
            
        except Exception as e:
            current_app.logger.error(f"Error cleaning up old notifications: {str(e)}")
            return 0

# WebSocket event handlers
def register_socket_events(socketio: SocketIO, notification_service: NotificationService):
    """Register WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        current_app.logger.info(f"Client connected: {request.sid}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        current_app.logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('join')
    def handle_join(data):
        """Join user to their notification room"""
        try:
            user_id = data.get('user_id')
            if user_id:
                room_name = f"user_{user_id}"
                join_room(room_name)
                notification_service.user_rooms[user_id] = room_name
                current_app.logger.info(f"User {user_id} joined room {room_name}")
                
                # Send unread count
                unread_count = notification_service.get_unread_count(user_id)
                emit('unread_count', {'count': unread_count})
                
        except Exception as e:
            current_app.logger.error(f"Error in join handler: {str(e)}")
    
    @socketio.on('leave')
    def handle_leave(data):
        """Leave user from their notification room"""
        try:
            user_id = data.get('user_id')
            if user_id:
                room_name = f"user_{user_id}"
                leave_room(room_name)
                if user_id in notification_service.user_rooms:
                    del notification_service.user_rooms[user_id]
                current_app.logger.info(f"User {user_id} left room {room_name}")
                
        except Exception as e:
            current_app.logger.error(f"Error in leave handler: {str(e)}")
    
    @socketio.on('mark_read')
    def handle_mark_read(data):
        """Mark notification as read"""
        try:
            notification_id = data.get('notification_id')
            user_id = data.get('user_id')
            
            if notification_id and user_id:
                success = notification_service.mark_as_read(notification_id, user_id)
                if success:
                    # Update unread count
                    unread_count = notification_service.get_unread_count(user_id)
                    emit('unread_count', {'count': unread_count})
                    
        except Exception as e:
            current_app.logger.error(f"Error in mark_read handler: {str(e)}")
    
    @socketio.on('mark_all_read')
    def handle_mark_all_read(data):
        """Mark all notifications as read"""
        try:
            user_id = data.get('user_id')
            
            if user_id:
                success = notification_service.mark_all_as_read(user_id)
                if success:
                    emit('unread_count', {'count': 0})
                    
        except Exception as e:
            current_app.logger.error(f"Error in mark_all_read handler: {str(e)}")
