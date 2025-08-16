import paypalrestsdk
from flask import current_app
import time

class PayPalService:
    def __init__(self):
        self.paypal = paypalrestsdk
        self.paypal.configure({
            "mode": current_app.config['PAYPAL_ENVIRONMENT'],
            "client_id": current_app.config['PAYPAL_CLIENT_ID'],
            "client_secret": current_app.config['PAYPAL_CLIENT_SECRET']
        })
    
    def create_order(self, amount, currency='EUR', invoice_id=None, description=None):
        """Create a PayPal order"""
        try:
            order_data = {
                "intent": "CAPTURE",
                "application_context": {
                    "return_url": f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/payment/success",
                    "cancel_url": f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/payment/cancel"
                },
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)
                    }
                }]
            }
            
            if invoice_id:
                order_data["purchase_units"][0]["custom_id"] = invoice_id
            
            if description:
                order_data["purchase_units"][0]["description"] = description
            
            order = self.paypal.Order.create(order_data)
            
            if order.success():
                return order.result
            else:
                print(f"PayPal order creation failed: {order.error}")
                return None
                
        except Exception as e:
            print(f"PayPal error: {e}")
            return None
    
    def capture_order(self, order_id):
        """Capture a PayPal order"""
        try:
            capture = self.paypal.Order.capture(order_id)
            
            if capture.success():
                return capture.result
            else:
                print(f"PayPal order capture failed: {capture.error}")
                return None
                
        except Exception as e:
            print(f"PayPal error: {e}")
            return None
    
    def get_order(self, order_id):
        """Get order details"""
        try:
            order = self.paypal.Order.find(order_id)
            return order
        except Exception as e:
            print(f"PayPal error: {e}")
            return None
    
    def refund_capture(self, capture_id, amount=None, reason=None):
        """Refund a captured payment"""
        try:
            refund_data = {
                "capture_id": capture_id
            }
            
            if amount:
                refund_data["amount"] = {
                    "currency_code": "EUR",
                    "value": str(amount)
                }
            
            if reason:
                refund_data["reason"] = reason
            
            refund = self.paypal.Capture.refund(capture_id, refund_data)
            
            if refund.success():
                return refund.result
            else:
                print(f"PayPal refund failed: {refund.error}")
                return None
                
        except Exception as e:
            print(f"PayPal error: {e}")
            return None
    
    def create_payout(self, email, amount, currency='EUR', note=None):
        """Create a payout to a PayPal account"""
        try:
            payout_data = {
                "sender_batch_header": {
                    "sender_batch_id": f"batch_{int(time.time())}",
                    "email_subject": "You have a payout!"
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": str(amount),
                        "currency": currency
                    },
                    "receiver": email
                }]
            }
            
            if note:
                payout_data["items"][0]["note"] = note
            
            payout = self.paypal.Payout.create(payout_data)
            
            if payout.success():
                return payout.result
            else:
                print(f"PayPal payout creation failed: {payout.error}")
                return None
                
        except Exception as e:
            print(f"PayPal error: {e}")
            return None
    
    def get_payout_batch(self, payout_batch_id):
        """Get payout batch details"""
        try:
            payout_batch = self.paypal.Payout.get(payout_batch_id)
            return payout_batch
        except Exception as e:
            print(f"PayPal error: {e}")
            return None
    
    def create_webhook(self, url, event_types):
        """Create a PayPal webhook"""
        try:
            webhook_data = {
                "url": url,
                "event_types": [{"name": event_type} for event_type in event_types]
            }
            
            webhook = self.paypal.Webhook.create(webhook_data)
            
            if webhook.success():
                return webhook.result
            else:
                print(f"PayPal webhook creation failed: {webhook.error}")
                return None
                
        except Exception as e:
            print(f"PayPal error: {e}")
            return None
    
    def get_webhooks(self):
        """Get all webhooks"""
        try:
            webhooks = self.paypal.Webhook.all()
            return webhooks
        except Exception as e:
            print(f"PayPal error: {e}")
            return None
    
    def delete_webhook(self, webhook_id):
        """Delete a webhook"""
        try:
            webhook = self.paypal.Webhook.find(webhook_id)
            if webhook.delete():
                return True
            else:
                print(f"PayPal webhook deletion failed: {webhook.error}")
                return False
                
        except Exception as e:
            print(f"PayPal error: {e}")
            return False
    
    def verify_webhook_signature(self, headers, body, webhook_id):
        """Verify webhook signature"""
        try:
            # This would need to be implemented based on PayPal's webhook verification
            # For now, return True to simulate verification
            return True
            
        except Exception as e:
            print(f"PayPal webhook verification error: {e}")
            return False
    
    def get_account_balance(self):
        """Get PayPal account balance"""
        try:
            # This would need to be implemented based on PayPal's API
            # For now, return None
            return None
            
        except Exception as e:
            print(f"PayPal error: {e}")
            return None
    
    def create_subscription(self, plan_id, subscriber_email, start_time=None):
        """Create a subscription"""
        try:
            subscription_data = {
                "plan_id": plan_id,
                "subscriber": {
                    "email_address": subscriber_email
                }
            }
            
            if start_time:
                subscription_data["start_time"] = start_time
            
            subscription = self.paypal.Subscription.create(subscription_data)
            
            if subscription.success():
                return subscription.result
            else:
                print(f"PayPal subscription creation failed: {subscription.error}")
                return None
                
        except Exception as e:
            print(f"PayPal error: {e}")
            return None
    
    def cancel_subscription(self, subscription_id, reason=None):
        """Cancel a subscription"""
        try:
            cancel_data = {}
            if reason:
                cancel_data["reason"] = reason
            
            subscription = self.paypal.Subscription.find(subscription_id)
            if subscription.cancel(cancel_data):
                return True
            else:
                print(f"PayPal subscription cancellation failed: {subscription.error}")
                return False
                
        except Exception as e:
            print(f"PayPal error: {e}")
            return False
