import stripe
from flask import current_app

class StripeService:
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    def create_payment_intent(self, amount, currency='eur', metadata=None):
        """Create a Stripe PaymentIntent"""
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                }
            )
            return intent
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
    
    def retrieve_payment_intent(self, payment_intent_id):
        """Retrieve a PaymentIntent by ID"""
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
    
    def confirm_payment_intent(self, payment_intent_id, payment_method_id=None):
        """Confirm a PaymentIntent"""
        try:
            intent_data = {}
            if payment_method_id:
                intent_data['payment_method'] = payment_method_id
            
            intent = self.stripe.PaymentIntent.confirm(
                payment_intent_id,
                **intent_data
            )
            return intent
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
    
    def cancel_payment_intent(self, payment_intent_id):
        """Cancel a PaymentIntent"""
        try:
            intent = self.stripe.PaymentIntent.cancel(payment_intent_id)
            return intent
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
    
    def create_refund(self, payment_intent_id, amount=None, reason=None):
        """Create a refund for a PaymentIntent"""
        try:
            refund_data = {'payment_intent': payment_intent_id}
            if amount:
                refund_data['amount'] = amount
            if reason:
                refund_data['reason'] = reason
            
            refund = self.stripe.Refund.create(**refund_data)
            return refund
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
    
    def get_payment_methods(self, customer_id):
        """Get payment methods for a customer"""
        try:
            payment_methods = self.stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            return payment_methods.data
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
    
    def create_customer(self, email, name=None, metadata=None):
        """Create a Stripe customer"""
        try:
            customer_data = {'email': email}
            if name:
                customer_data['name'] = name
            if metadata:
                customer_data['metadata'] = metadata
            
            customer = self.stripe.Customer.create(**customer_data)
            return customer
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
    
    def update_customer(self, customer_id, **kwargs):
        """Update a Stripe customer"""
        try:
            customer = self.stripe.Customer.modify(customer_id, **kwargs)
            return customer
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
    
    def create_subscription(self, customer_id, price_id, metadata=None):
        """Create a subscription"""
        try:
            subscription_data = {
                'customer': customer_id,
                'items': [{'price': price_id}]
            }
            if metadata:
                subscription_data['metadata'] = metadata
            
            subscription = self.stripe.Subscription.create(**subscription_data)
            return subscription
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
    
    def cancel_subscription(self, subscription_id):
        """Cancel a subscription"""
        try:
            subscription = self.stripe.Subscription.delete(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
    
    def get_webhook_event(self, payload, sig_header, webhook_secret):
        """Verify and parse webhook event"""
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError as e:
            print(f"Invalid payload: {e}")
            raise e
        except stripe.error.SignatureVerificationError as e:
            print(f"Invalid signature: {e}")
            raise e
    
    def get_account_balance(self):
        """Get Stripe account balance"""
        try:
            balance = self.stripe.Balance.retrieve()
            return balance
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
    
    def create_transfer(self, amount, currency, destination, metadata=None):
        """Create a transfer to a connected account"""
        try:
            transfer_data = {
                'amount': amount,
                'currency': currency,
                'destination': destination
            }
            if metadata:
                transfer_data['metadata'] = metadata
            
            transfer = self.stripe.Transfer.create(**transfer_data)
            return transfer
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise e
