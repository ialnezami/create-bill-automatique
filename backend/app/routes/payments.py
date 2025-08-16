from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import stripe
import paypalrestsdk
from ..models import Payment, Invoice, User
from ..services.stripe_service import StripeService
from ..services.paypal_service import PayPalService

payments_bp = Blueprint('payments', __name__)
stripe_service = StripeService()
paypal_service = PayPalService()

# Configure Stripe
stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

# Configure PayPal
paypalrestsdk.configure({
    "mode": current_app.config['PAYPAL_ENVIRONMENT'],
    "client_id": current_app.config['PAYPAL_CLIENT_ID'],
    "client_secret": current_app.config['PAYPAL_CLIENT_SECRET']
})

@payments_bp.route('/stripe/create-intent', methods=['POST'])
@jwt_required()
def create_stripe_payment_intent():
    """Create Stripe PaymentIntent"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('invoice_id') or not data.get('amount'):
            return jsonify({'error': 'Invoice ID and amount are required'}), 400
        
        # Get invoice
        invoice = Invoice.objects(id=data['invoice_id'], user=current_user_id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Create PaymentIntent
        intent = stripe_service.create_payment_intent(
            amount=int(float(data['amount']) * 100),  # Convert to cents
            currency=data.get('currency', 'eur'),
            metadata={
                'invoice_id': str(invoice.id),
                'user_id': current_user_id
            }
        )
        
        return jsonify({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/paypal/create-order', methods=['POST'])
@jwt_required()
def create_paypal_order():
    """Create PayPal order"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('invoice_id') or not data.get('amount'):
            return jsonify({'error': 'Invoice ID and amount are required'}), 400
        
        # Get invoice
        invoice = Invoice.objects(id=data['invoice_id'], user=current_user_id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Create PayPal order
        order = paypal_service.create_order(
            amount=data['amount'],
            currency=data.get('currency', 'EUR'),
            invoice_id=str(invoice.id),
            description=f"Payment for invoice {invoice.invoice_number}"
        )
        
        if order:
            return jsonify({
                'order_id': order.id,
                'approval_url': order.links[1].href
            }), 200
        else:
            return jsonify({'error': 'Failed to create PayPal order'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, current_app.config['STRIPE_WEBHOOK_SECRET']
        )
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            handle_stripe_payment_success(payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            handle_stripe_payment_failure(payment_intent)
        
        return jsonify({'status': 'success'}), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/paypal/webhook', methods=['POST'])
def paypal_webhook():
    """Handle PayPal webhook events"""
    try:
        # Verify webhook (PayPal webhook verification would go here)
        data = request.get_json()
        
        if data.get('event_type') == 'PAYMENT.CAPTURE.COMPLETED':
            handle_paypal_payment_success(data)
        elif data.get('event_type') == 'PAYMENT.CAPTURE.DENIED':
            handle_paypal_payment_failure(data)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get payment details"""
    try:
        current_user_id = get_jwt_identity()
        
        payment = Payment.objects(id=payment_id, user=current_user_id).first()
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify({
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/invoice/<invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice_payments(invoice_id):
    """Get all payments for a specific invoice"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify invoice belongs to user
        invoice = Invoice.objects(id=invoice_id, user=current_user_id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        payments = Payment.objects(invoice=invoice_id).order_by('-created_at')
        payment_list = [payment.to_dict() for payment in payments]
        
        return jsonify({
            'payments': payment_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handle_stripe_payment_success(payment_intent):
    """Handle successful Stripe payment"""
    try:
        invoice_id = payment_intent.metadata.get('invoice_id')
        amount = payment_intent.amount / 100  # Convert from cents
        
        # Create payment record
        payment = Payment(
            payment_id=payment_intent.id,
            invoice=invoice_id,
            user=payment_intent.metadata.get('user_id'),
            client=payment_intent.metadata.get('client_id'),
            amount=amount,
            currency=payment_intent.currency.upper(),
            payment_method='stripe',
            provider='stripe',
            provider_payment_id=payment_intent.id,
            status='completed'
        )
        
        payment.mark_as_completed()
        payment.save()
        
    except Exception as e:
        print(f"Error handling Stripe payment success: {e}")

def handle_stripe_payment_failure(payment_intent):
    """Handle failed Stripe payment"""
    try:
        invoice_id = payment_intent.metadata.get('invoice_id')
        
        # Create payment record
        payment = Payment(
            payment_id=payment_intent.id,
            invoice=invoice_id,
            user=payment_intent.metadata.get('user_id'),
            client=payment_intent.metadata.get('client_id'),
            amount=payment_intent.amount / 100,
            currency=payment_intent.currency.upper(),
            payment_method='stripe',
            provider='stripe',
            provider_payment_id=payment_intent.id,
            status='failed',
            error_message=payment_intent.last_payment_error.message if payment_intent.last_payment_error else 'Payment failed'
        )
        
        payment.mark_as_failed()
        payment.save()
        
    except Exception as e:
        print(f"Error handling Stripe payment failure: {e}")

def handle_paypal_payment_success(data):
    """Handle successful PayPal payment"""
    try:
        # Extract payment information from PayPal webhook data
        # This would need to be implemented based on PayPal's webhook structure
        
        pass
        
    except Exception as e:
        print(f"Error handling PayPal payment success: {e}")

def handle_paypal_payment_failure(data):
    """Handle failed PayPal payment"""
    try:
        # Extract payment information from PayPal webhook data
        # This would need to be implemented based on PayPal's webhook structure
        
        pass
        
    except Exception as e:
        print(f"Error handling PayPal payment failure: {e}")
