from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Notification
from ..services.notification_service import NotificationService
from ..middleware.auth import auth_required, handle_errors
from datetime import datetime, timedelta

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@auth_required
@handle_errors
def get_notifications():
    """Get user notifications"""
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    # Get notifications
    notifications = Notification.objects(user=current_user_id)
    
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    # Apply pagination
    total = notifications.count()
    notifications = notifications.skip((page - 1) * per_page).limit(per_page)
    
    # Convert to list of dictionaries
    notification_list = [notif.to_dict() for notif in notifications]
    
    return jsonify({
        'notifications': notification_list,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }), 200

@notifications_bp.route('/unread-count', methods=['GET'])
@auth_required
@handle_errors
def get_unread_count():
    """Get count of unread notifications"""
    current_user_id = get_jwt_identity()
    
    unread_count = Notification.objects(user=current_user_id, is_read=False).count()
    
    return jsonify({
        'unread_count': unread_count
    }), 200

@notifications_bp.route('/<notification_id>/read', methods=['PUT'])
@auth_required
@handle_errors
def mark_as_read(notification_id):
    """Mark a notification as read"""
    current_user_id = get_jwt_identity()
    
    notification = Notification.objects(id=notification_id, user=current_user_id).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.mark_as_read()
    
    return jsonify({
        'message': 'Notification marked as read',
        'notification': notification.to_dict()
    }), 200

@notifications_bp.route('/mark-all-read', methods=['PUT'])
@auth_required
@handle_errors
def mark_all_as_read():
    """Mark all notifications as read"""
    current_user_id = get_jwt_identity()
    
    # Update all unread notifications
    result = Notification.objects(user=current_user_id, is_read=False).update(
        is_read=True,
        read_at=datetime.utcnow()
    )
    
    return jsonify({
        'message': f'{result} notifications marked as read'
    }), 200

@notifications_bp.route('/<notification_id>', methods=['DELETE'])
@auth_required
@handle_errors
def delete_notification(notification_id):
    """Delete a notification"""
    current_user_id = get_jwt_identity()
    
    notification = Notification.objects(id=notification_id, user=current_user_id).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.delete()
    
    return jsonify({
        'message': 'Notification deleted successfully'
    }), 200

@notifications_bp.route('/clear-old', methods=['DELETE'])
@auth_required
@handle_errors
def clear_old_notifications():
    """Clear old notifications (admin only)"""
    current_user_id = get_jwt_identity()
    
    # Get user to check if admin
    from ..models import User
    user = User.objects(id=current_user_id).first()
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get days parameter (default 30)
    days = int(request.args.get('days', 30))
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Delete old notifications
    deleted_count = Notification.objects(created_at__lt=cutoff_date).delete()
    
    return jsonify({
        'message': f'{deleted_count} old notifications cleared',
        'cutoff_date': cutoff_date.isoformat()
    }), 200
