import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app, render_template_string
from flask_mail import Mail, Message
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.mail = Mail()
        self.smtp_config = {
            'server': current_app.config.get('MAIL_SERVER'),
            'port': current_app.config.get('MAIL_PORT'),
            'username': current_app.config.get('MAIL_USERNAME'),
            'password': current_app.config.get('MAIL_PASSWORD'),
            'use_tls': current_app.config.get('MAIL_USE_TLS', True)
        }
    
    def send_invoice_email(self, invoice, recipient_email=None):
        """Send invoice email to client"""
        try:
            if not recipient_email:
                recipient_email = invoice.client.email
            
            subject = f"Invoice #{invoice.invoice_number} from {invoice.user.company_name}"
            
            # Create HTML email template
            html_content = self._create_invoice_email_template(invoice)
            
            # Send email
            success = self._send_email(
                to_email=recipient_email,
                subject=subject,
                html_content=html_content,
                attachments=[('invoice.pdf', invoice.pdf_path)] if invoice.pdf_path else []
            )
            
            if success:
                logger.info(f"Invoice email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send invoice email to {recipient_email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending invoice email: {str(e)}")
            return False
    
    def send_payment_reminder(self, invoice, days_overdue):
        """Send payment reminder email"""
        try:
            subject = f"Payment Reminder - Invoice #{invoice.invoice_number}"
            
            html_content = self._create_reminder_template(invoice, days_overdue)
            
            success = self._send_email(
                to_email=invoice.client.email,
                subject=subject,
                html_content=html_content
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending payment reminder: {str(e)}")
            return False
    
    def send_payment_confirmation(self, payment):
        """Send payment confirmation email"""
        try:
            subject = f"Payment Received - Invoice #{payment.invoice.invoice_number}"
            
            html_content = self._create_payment_confirmation_template(payment)
            
            success = self._send_email(
                to_email=payment.invoice.client.email,
                subject=subject,
                html_content=html_content
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending payment confirmation: {str(e)}")
            return False
    
    def send_welcome_email(self, user):
        """Send welcome email to new users"""
        try:
            subject = f"Welcome to {current_app.config.get('APP_NAME', 'InvoicePro')}!"
            
            html_content = self._create_welcome_template(user)
            
            success = self._send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False
    
    def send_password_reset(self, user, reset_token):
        """Send password reset email"""
        try:
            subject = "Password Reset Request"
            
            reset_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
            
            html_content = self._create_password_reset_template(user, reset_url)
            
            success = self._send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return False
    
    def _send_email(self, to_email, subject, html_content, attachments=None):
        """Send email using configured SMTP or Flask-Mail"""
        try:
            # Try Flask-Mail first
            if hasattr(current_app, 'extensions') and 'mail' in current_app.extensions:
                msg = Message(
                    subject=subject,
                    recipients=[to_email],
                    html=html_content
                )
                
                # Add attachments
                if attachments:
                    for filename, filepath in attachments:
                        if os.path.exists(filepath):
                            with open(filepath, 'rb') as f:
                                msg.attach(filename, 'application/pdf', f.read())
                
                current_app.extensions['mail'].send(msg)
                return True
                
            # Fallback to SMTP
            else:
                return self._send_smtp_email(to_email, subject, html_content, attachments)
                
        except Exception as e:
            logger.error(f"Error in _send_email: {str(e)}")
            return False
    
    def _send_smtp_email(self, to_email, subject, html_content, attachments=None):
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_config['username']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachments
            if attachments:
                for filename, filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {filename}'
                            )
                            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            if self.smtp_config['use_tls']:
                server.starttls()
            
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"SMTP email error: {str(e)}")
            return False
    
    def _create_invoice_email_template(self, invoice):
        """Create HTML template for invoice email"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #f8f9fa; padding: 20px; border-radius: 5px; }
                .invoice-details { margin: 20px 0; }
                .total { background: #e9ecef; padding: 15px; border-radius: 5px; font-weight: bold; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 12px; color: #6c757d; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Invoice #{invoice.invoice_number}</h2>
                    <p><strong>From:</strong> {company_name}</p>
                    <p><strong>Date:</strong> {issue_date}</p>
                    <p><strong>Due Date:</strong> {due_date}</p>
                </div>
                
                <div class="invoice-details">
                    <h3>Bill To:</h3>
                    <p>{client_name}<br>
                    {client_address}</p>
                </div>
                
                <div class="total">
                    <h3>Total Amount: {currency} {total_amount}</h3>
                </div>
                
                <p>Please find attached the detailed invoice for your records.</p>
                
                <div class="footer">
                    <p>This is an automated message from {company_name}. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return template.format(
            invoice_number=invoice.invoice_number,
            company_name=invoice.user.company_name or 'Your Company',
            issue_date=invoice.issue_date.strftime('%B %d, %Y'),
            due_date=invoice.due_date.strftime('%B %d, %Y'),
            client_name=invoice.client.company_name,
            client_address=f"{invoice.client.billing_address}, {invoice.client.billing_city}",
            currency=invoice.currency,
            total_amount=f"{invoice.total_amount:.2f}"
        )
    
    def _create_reminder_template(self, invoice, days_overdue):
        """Create HTML template for payment reminder"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .reminder { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 5px; }
                .amount { font-size: 24px; font-weight: bold; color: #e74c3c; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="reminder">
                    <h2>Payment Reminder</h2>
                    <p>This is a friendly reminder that invoice #{invoice_number} is {days_overdue} days overdue.</p>
                    <p class="amount">Amount Due: {currency} {amount}</p>
                    <p>Please process this payment as soon as possible to avoid any late fees.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return template.format(
            invoice_number=invoice.invoice_number,
            days_overdue=days_overdue,
            currency=invoice.currency,
            amount=f"{invoice.balance_due:.2f}"
        )
    
    def _create_payment_confirmation_template(self, payment):
        """Create HTML template for payment confirmation"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .success { background: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 5px; }
                .amount { font-size: 24px; font-weight: bold; color: #155724; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">
                    <h2>Payment Received!</h2>
                    <p>Thank you for your payment of:</p>
                    <p class="amount">{currency} {amount}</p>
                    <p>Invoice: #{invoice_number}</p>
                    <p>Payment Method: {payment_method}</p>
                    <p>Transaction ID: {transaction_id}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return template.format(
            currency=payment.currency,
            amount=f"{payment.amount:.2f}",
            invoice_number=payment.invoice.invoice_number,
            payment_method=payment.payment_method.title(),
            transaction_id=payment.provider_transaction_id or 'N/A'
        )
    
    def _create_welcome_template(self, user):
        """Create HTML template for welcome email"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .welcome { background: #d1ecf1; border: 1px solid #bee5eb; padding: 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="welcome">
                    <h2>Welcome to InvoicePro!</h2>
                    <p>Hi {first_name},</p>
                    <p>Thank you for joining InvoicePro! We're excited to help you streamline your invoicing process.</p>
                    <p>Here are some things you can do to get started:</p>
                    <ul>
                        <li>Complete your company profile</li>
                        <li>Add your first client</li>
                        <li>Create your first invoice</li>
                        <li>Configure payment gateways</li>
                    </ul>
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    <p>Best regards,<br>The InvoicePro Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return template.format(
            first_name=user.first_name
        )
    
    def _create_password_reset_template(self, user, reset_url):
        """Create HTML template for password reset"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .reset { background: #f8d7da; border: 1px solid #f5c6cb; padding: 20px; border-radius: 5px; }
                .button { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="reset">
                    <h2>Password Reset Request</h2>
                    <p>Hi {first_name},</p>
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>
                    <p><a href="{reset_url}" class="button">Reset Password</a></p>
                    <p>If you didn't request this, you can safely ignore this email.</p>
                    <p>This link will expire in 1 hour.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return template.format(
            first_name=user.first_name,
            reset_url=reset_url
        )
