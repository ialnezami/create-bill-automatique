from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from ..models import Invoice, Payment, Client
from decimal import Decimal

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """Get dashboard summary data"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get date range (default to last 30 days)
        days = int(request.args.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get invoices in date range
        invoices = Invoice.objects(
            user=current_user_id,
            issue_date__gte=start_date,
            issue_date__lte=end_date
        )
        
        # Get payments in date range
        payments = Payment.objects(
            user=current_user_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Calculate totals
        total_invoices = invoices.count()
        total_amount = sum(invoice.total_amount for invoice in invoices)
        total_paid = sum(payment.amount for payment in payments if payment.status == 'completed')
        total_pending = sum(invoice.balance_due for invoice in invoices if invoice.status in ['sent', 'draft'])
        
        # Get invoice status counts
        status_counts = {}
        for invoice in invoices:
            status = invoice.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get monthly revenue data
        monthly_revenue = get_monthly_revenue(current_user_id, days)
        
        # Get top clients
        top_clients = get_top_clients(current_user_id, days)
        
        return jsonify({
            'summary': {
                'total_invoices': total_invoices,
                'total_amount': float(total_amount),
                'total_paid': float(total_paid),
                'total_pending': float(total_pending),
                'days': days
            },
            'status_counts': status_counts,
            'monthly_revenue': monthly_revenue,
            'top_clients': top_clients
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/revenue', methods=['GET'])
@jwt_required()
def get_revenue_report():
    """Get detailed revenue report"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        else:
            start_date = datetime.utcnow() - timedelta(days=365)
            
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        else:
            end_date = datetime.utcnow()
        
        # Get invoices in date range
        invoices = Invoice.objects(
            user=current_user_id,
            issue_date__gte=start_date,
            issue_date__lte=end_date
        ).order_by('issue_date')
        
        # Group by month
        monthly_data = {}
        for invoice in invoices:
            month_key = invoice.issue_date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'month': month_key,
                    'total_amount': Decimal('0.0'),
                    'total_paid': Decimal('0.0'),
                    'invoice_count': 0
                }
            
            monthly_data[month_key]['total_amount'] += invoice.total_amount
            monthly_data[month_key]['invoice_count'] += 1
            
            if invoice.status == 'paid':
                monthly_data[month_key]['total_paid'] += invoice.total_amount
        
        # Convert to list and sort
        revenue_data = list(monthly_data.values())
        revenue_data.sort(key=lambda x: x['month'])
        
        # Convert Decimal to float for JSON serialization
        for item in revenue_data:
            item['total_amount'] = float(item['total_amount'])
            item['total_paid'] = float(item['total_paid'])
        
        return jsonify({
            'revenue_data': revenue_data,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/clients', methods=['GET'])
@jwt_required()
def get_client_report():
    """Get client performance report"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get date range
        days = int(request.args.get('days', 365))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all clients
        clients = Client.objects(user=current_user_id, is_active=True)
        
        client_data = []
        for client in clients:
            # Get invoices for this client
            invoices = Invoice.objects(
                user=current_user_id,
                client=client.id,
                issue_date__gte=start_date,
                issue_date__lte=end_date
            )
            
            total_amount = sum(invoice.total_amount for invoice in invoices)
            total_paid = sum(invoice.paid_amount for invoice in invoices)
            invoice_count = invoices.count()
            
            if invoice_count > 0:
                client_data.append({
                    'client_id': str(client.id),
                    'company_name': client.company_name,
                    'contact_person': client.contact_person,
                    'email': client.email,
                    'total_amount': float(total_amount),
                    'total_paid': float(total_paid),
                    'invoice_count': invoice_count,
                    'average_invoice': float(total_amount / invoice_count) if invoice_count > 0 else 0
                })
        
        # Sort by total amount
        client_data.sort(key=lambda x: x['total_amount'], reverse=True)
        
        return jsonify({
            'clients': client_data,
            'total_clients': len(client_data),
            'days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/export', methods=['POST'])
@jwt_required()
def export_report():
    """Export report data"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        report_type = data.get('type', 'revenue')
        format_type = data.get('format', 'csv')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        
        # Generate report data based on type
        if report_type == 'revenue':
            report_data = generate_revenue_export(current_user_id, start_date, end_date)
        elif report_type == 'clients':
            report_data = generate_clients_export(current_user_id, start_date, end_date)
        elif report_type == 'invoices':
            report_data = generate_invoices_export(current_user_id, start_date, end_date)
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
        # For now, return JSON. In production, you'd generate CSV/Excel files
        return jsonify({
            'report_data': report_data,
            'type': report_type,
            'format': format_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_monthly_revenue(user_id, days):
    """Get monthly revenue data for dashboard"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    invoices = Invoice.objects(
        user=user_id,
        issue_date__gte=start_date,
        issue_date__lte=end_date
    )
    
    monthly_data = {}
    for invoice in invoices:
        month_key = invoice.issue_date.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = Decimal('0.0')
        monthly_data[month_key] += invoice.total_amount
    
    # Convert to list and sort
    revenue_list = [{'month': month, 'amount': float(amount)} for month, amount in monthly_data.items()]
    revenue_list.sort(key=lambda x: x['month'])
    
    return revenue_list

def get_top_clients(user_id, days):
    """Get top performing clients"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Aggregate invoices by client
    pipeline = [
        {'$match': {
            'user': user_id,
            'issue_date': {'$gte': start_date, '$lte': end_date}
        }},
        {'$group': {
            '_id': '$client',
            'total_amount': {'$sum': '$total_amount'},
            'invoice_count': {'$sum': 1}
        }},
        {'$sort': {'total_amount': -1}},
        {'$limit': 5}
    ]
    
    # This would need to be implemented with proper MongoDB aggregation
    # For now, return empty list
    return []

def generate_revenue_export(user_id, start_date, end_date):
    """Generate revenue export data"""
    invoices = Invoice.objects(
        user=user_id,
        issue_date__gte=start_date,
        issue_date__lte=end_date
    ).order_by('issue_date')
    
    export_data = []
    for invoice in invoices:
        export_data.append({
            'invoice_number': invoice.invoice_number,
            'issue_date': invoice.issue_date.isoformat(),
            'due_date': invoice.due_date.isoformat(),
            'client': invoice.client.company_name if invoice.client else '',
            'status': invoice.status,
            'subtotal': float(invoice.subtotal),
            'tax_total': float(invoice.tax_total),
            'total_amount': float(invoice.total_amount),
            'paid_amount': float(invoice.paid_amount),
            'balance_due': float(invoice.balance_due)
        })
    
    return export_data

def generate_clients_export(user_id, start_date, end_date):
    """Generate clients export data"""
    clients = Client.objects(user=user_id, is_active=True)
    
    export_data = []
    for client in clients:
        # Get invoice summary for this client
        invoices = Invoice.objects(
            user=user_id,
            client=client.id
        )
        
        if start_date:
            invoices = invoices.filter(issue_date__gte=start_date)
        if end_date:
            invoices = invoices.filter(issue_date__lte=end_date)
        
        total_amount = sum(invoice.total_amount for invoice in invoices)
        total_paid = sum(invoice.paid_amount for invoice in invoices)
        
        export_data.append({
            'company_name': client.company_name,
            'contact_person': client.contact_person,
            'email': client.email,
            'phone': client.phone,
            'billing_address': client.billing_address,
            'billing_city': client.billing_city,
            'billing_country': client.billing_country,
            'total_amount': float(total_amount),
            'total_paid': float(total_paid),
            'invoice_count': invoices.count()
        })
    
    return export_data

def generate_invoices_export(user_id, start_date, end_date):
    """Generate invoices export data"""
    invoices = Invoice.objects(user=user_id)
    
    if start_date:
        invoices = invoices.filter(issue_date__gte=start_date)
    if end_date:
        invoices = invoices.filter(issue_date__lte=end_date)
    
    export_data = []
    for invoice in invoices:
        export_data.append({
            'invoice_number': invoice.invoice_number,
            'issue_date': invoice.issue_date.isoformat(),
            'due_date': invoice.due_date.isoformat(),
            'client': invoice.client.company_name if invoice.client else '',
            'status': invoice.status,
            'currency': invoice.currency,
            'subtotal': float(invoice.subtotal),
            'tax_total': float(invoice.tax_total),
            'discount_total': float(invoice.discount_total),
            'shipping_fee': float(invoice.shipping_fee),
            'handling_fee': float(invoice.handling_fee),
            'total_amount': float(invoice.total_amount),
            'paid_amount': float(invoice.paid_amount),
            'balance_due': float(invoice.balance_due),
            'notes': invoice.notes,
            'created_at': invoice.created_at.isoformat()
        })
    
    return export_data
