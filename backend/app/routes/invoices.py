from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from decimal import Decimal
from ..models import Invoice, InvoiceItem, User, Client
from ..services.invoice_service import InvoiceService

invoices_bp = Blueprint('invoices', __name__)
invoice_service = InvoiceService()

@invoices_bp.route('/', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get all invoices for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status')
        client_id = request.args.get('client_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = {'user': current_user_id}
        if status:
            query['status'] = status
        if client_id:
            query['client'] = client_id
        if start_date:
            query['issue_date__gte'] = datetime.fromisoformat(start_date)
        if end_date:
            query['issue_date__lte'] = datetime.fromisoformat(end_date)
        
        # Get invoices with pagination
        invoices = Invoice.objects(**query).order_by('-created_at').skip((page - 1) * per_page).limit(per_page)
        total = Invoice.objects(**query).count()
        
        # Get client details for each invoice
        invoice_list = []
        for invoice in invoices:
            invoice_data = invoice.to_dict()
            invoice_data['client'] = invoice.client.to_dict() if invoice.client else None
            invoice_list.append(invoice_data)
        
        return jsonify({
            'invoices': invoice_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/<invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Get specific invoice by ID"""
    try:
        current_user_id = get_jwt_identity()
        
        invoice = Invoice.objects(id=invoice_id, user=current_user_id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        invoice_data = invoice.to_dict()
        invoice_data['client'] = invoice.client.to_dict() if invoice.client else None
        
        return jsonify({
            'invoice': invoice_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/', methods=['POST'])
@jwt_required()
def create_invoice():
    """Create new invoice"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['client_id', 'due_date', 'items']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Field {field} is required'}), 400
        
        # Validate items
        if not data['items'] or len(data['items']) == 0:
            return jsonify({'error': 'At least one item is required'}), 400
        
        # Get client
        client = Client.objects(id=data['client_id'], user=current_user_id).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Get user for invoice number generation
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate invoice number
        invoice_number = invoice_service.generate_invoice_number(user)
        
        # Create invoice items
        items = []
        for item_data in data['items']:
            item = InvoiceItem(
                description=item_data['description'],
                quantity=Decimal(str(item_data['quantity'])),
                unit_price=Decimal(str(item_data['unit_price'])),
                tax_rate=Decimal(str(item_data.get('tax_rate', 0))),
                discount_rate=Decimal(str(item_data.get('discount_rate', 0)))
            )
            items.append(item)
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            user=user,
            client=client,
            due_date=datetime.fromisoformat(data['due_date']),
            currency=data.get('currency', user.default_currency),
            items=items,
            notes=data.get('notes', ''),
            terms_conditions=data.get('terms_conditions', ''),
            shipping_fee=Decimal(str(data.get('shipping_fee', 0))),
            handling_fee=Decimal(str(data.get('handling_fee', 0)))
        )
        
        # Calculate totals
        invoice.calculate_totals()
        invoice.save()
        
        # Update user's next invoice number
        user.next_invoice_number = str(int(user.next_invoice_number) + 1).zfill(4)
        user.save()
        
        return jsonify({
            'message': 'Invoice created successfully',
            'invoice': invoice.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/<invoice_id>', methods=['PUT'])
@jwt_required()
def update_invoice(invoice_id):
    """Update existing invoice"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        invoice = Invoice.objects(id=invoice_id, user=current_user_id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Check if invoice can be edited
        if invoice.status in ['paid', 'cancelled']:
            return jsonify({'error': 'Cannot edit paid or cancelled invoice'}), 400
        
        # Update basic fields
        if 'due_date' in data:
            invoice.due_date = datetime.fromisoformat(data['due_date'])
        if 'notes' in data:
            invoice.notes = data['notes']
        if 'terms_conditions' in data:
            invoice.terms_conditions = data['terms_conditions']
        if 'shipping_fee' in data:
            invoice.shipping_fee = Decimal(str(data['shipping_fee']))
        if 'handling_fee' in data:
            invoice.handling_fee = Decimal(str(data['handling_fee']))
        
        # Update items if provided
        if 'items' in data:
            items = []
            for item_data in data['items']:
                item = InvoiceItem(
                    description=item_data['description'],
                    quantity=Decimal(str(item_data['quantity'])),
                    unit_price=Decimal(str(item_data['unit_price'])),
                    tax_rate=Decimal(str(item_data.get('tax_rate', 0))),
                    discount_rate=Decimal(str(item_data.get('discount_rate', 0)))
                )
                items.append(item)
            invoice.items = items
        
        # Recalculate totals
        invoice.calculate_totals()
        invoice.save()
        
        return jsonify({
            'message': 'Invoice updated successfully',
            'invoice': invoice.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/<invoice_id>/send', methods=['POST'])
@jwt_required()
def send_invoice(invoice_id):
    """Send invoice by email"""
    try:
        current_user_id = get_jwt_identity()
        
        invoice = Invoice.objects(id=invoice_id, user=current_user_id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        if invoice.status != 'draft':
            return jsonify({'error': 'Only draft invoices can be sent'}), 400
        
        # Send invoice email
        success = invoice_service.send_invoice_email(invoice)
        
        if success:
            invoice.mark_as_sent()
            invoice.save()
            
            return jsonify({
                'message': 'Invoice sent successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send invoice email'
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/<invoice_id>', methods=['DELETE'])
@jwt_required()
def delete_invoice(invoice_id):
    """Delete invoice"""
    try:
        current_user_id = get_jwt_identity()
        
        invoice = Invoice.objects(id=invoice_id, user=current_user_id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Check if invoice can be deleted
        if invoice.status in ['paid', 'sent']:
            return jsonify({'error': 'Cannot delete sent or paid invoice'}), 400
        
        invoice.delete()
        
        return jsonify({
            'message': 'Invoice deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/<invoice_id>/pdf', methods=['GET'])
@jwt_required()
def get_invoice_pdf(invoice_id):
    """Generate and return invoice PDF"""
    try:
        current_user_id = get_jwt_identity()
        
        invoice = Invoice.objects(id=invoice_id, user=current_user_id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Generate PDF
        pdf_data = invoice_service.generate_invoice_pdf(invoice)
        
        if pdf_data:
            return pdf_data, 200, {
                'Content-Type': 'application/pdf',
                'Content-Disposition': f'attachment; filename=invoice_{invoice.invoice_number}.pdf'
            }
        else:
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
