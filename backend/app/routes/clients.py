from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Client, User

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/', methods=['GET'])
@jwt_required()
def get_clients():
    """Get all clients for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        tags = request.args.get('tags', '')
        
        # Build query
        query = {'user': current_user_id, 'is_active': True}
        
        if search:
            query['$or'] = [
                {'company_name__icontains': search},
                {'contact_person__icontains': search},
                {'email__icontains': search}
            ]
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            query['tags__in'] = tag_list
        
        # Get clients with pagination
        clients = Client.objects(**query).order_by('company_name').skip((page - 1) * per_page).limit(per_page)
        total = Client.objects(**query).count()
        
        client_list = [client.to_dict() for client in clients]
        
        return jsonify({
            'clients': client_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/<client_id>', methods=['GET'])
@jwt_required()
def get_client(client_id):
    """Get specific client by ID"""
    try:
        current_user_id = get_jwt_identity()
        
        client = Client.objects(id=client_id, user=current_user_id).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        return jsonify({
            'client': client.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/', methods=['POST'])
@jwt_required()
def create_client():
    """Create new client"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['company_name', 'email', 'billing_address', 'billing_city', 'billing_country']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Field {field} is required'}), 400
        
        # Get user
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create client
        client = Client(
            user=user,
            company_name=data['company_name'],
            contact_person=data.get('contact_person', ''),
            email=data['email'],
            phone=data.get('phone', ''),
            billing_address=data['billing_address'],
            billing_city=data['billing_city'],
            billing_state=data.get('billing_state', ''),
            billing_zip_code=data.get('billing_zip_code', ''),
            billing_country=data['billing_country'],
            shipping_address=data.get('shipping_address', data['billing_address']),
            shipping_city=data.get('shipping_city', data['billing_city']),
            shipping_state=data.get('shipping_state', data.get('billing_state', '')),
            shipping_zip_code=data.get('shipping_zip_code', data.get('billing_zip_code', '')),
            shipping_country=data.get('shipping_country', data['billing_country']),
            tax_id=data.get('tax_id', ''),
            notes=data.get('notes', ''),
            tags=data.get('tags', [])
        )
        
        client.save()
        
        return jsonify({
            'message': 'Client created successfully',
            'client': client.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/<client_id>', methods=['PUT'])
@jwt_required()
def update_client(client_id):
    """Update existing client"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        client = Client.objects(id=client_id, user=current_user_id).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Update fields
        allowed_fields = [
            'company_name', 'contact_person', 'email', 'phone',
            'billing_address', 'billing_city', 'billing_state', 'billing_zip_code', 'billing_country',
            'shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip_code', 'shipping_country',
            'tax_id', 'notes', 'tags'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(client, field, data[field])
        
        client.save()
        
        return jsonify({
            'message': 'Client updated successfully',
            'client': client.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/<client_id>', methods=['DELETE'])
@jwt_required()
def delete_client(client_id):
    """Delete client (soft delete)"""
    try:
        current_user_id = get_jwt_identity()
        
        client = Client.objects(id=client_id, user=current_user_id).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Soft delete
        client.is_active = False
        client.save()
        
        return jsonify({
            'message': 'Client deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/tags', methods=['GET'])
@jwt_required()
def get_client_tags():
    """Get all unique tags used by clients"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get all tags from active clients
        clients = Client.objects(user=current_user_id, is_active=True)
        all_tags = []
        
        for client in clients:
            if client.tags:
                all_tags.extend(client.tags)
        
        # Remove duplicates and sort
        unique_tags = sorted(list(set(all_tags)))
        
        return jsonify({
            'tags': unique_tags
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
