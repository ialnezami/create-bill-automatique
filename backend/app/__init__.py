from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_socketio import SocketIO
from mongoengine import connect
from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
jwt = JWTManager()
mail = Mail()
celery = Celery(__name__)
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    
    # Database configuration
    app.config['MONGODB_HOST'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/invoice_app')
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    
    # Stripe configuration
    app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY')
    app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
    app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    # PayPal configuration
    app.config['PAYPAL_CLIENT_ID'] = os.getenv('PAYPAL_CLIENT_ID')
    app.config['PAYPAL_CLIENT_SECRET'] = os.getenv('PAYPAL_CLIENT_SECRET')
    app.config['PAYPAL_ENVIRONMENT'] = os.getenv('PAYPAL_ENVIRONMENT', 'sandbox')
    
    # Initialize extensions
    jwt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    
    # Initialize i18n service
    from .services.i18n_service import i18n_service
    i18n_service.init_app(app)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Connect to MongoDB
    connect(host=app.config['MONGODB_HOST'])
    
    # Configure Celery
    celery.conf.update(
        broker_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
        result_backend=os.getenv('REDIS_URL', 'redis://localhost:6379')
    )
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.invoices import invoices_bp
    from .routes.payments import payments_bp
    from .routes.clients import clients_bp
    from .routes.reports import reports_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(invoices_bp, url_prefix='/api/invoices')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(clients_bp, url_prefix='/api/clients')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    
    return app
