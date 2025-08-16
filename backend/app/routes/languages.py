from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.i18n_service import i18n_service
from ..models import User
from ..middleware.auth import auth_required, handle_errors

languages_bp = Blueprint('languages', __name__)

@languages_bp.route('/supported', methods=['GET'])
def get_supported_languages():
    """Get list of supported languages"""
    languages = i18n_service.get_supported_languages()
    
    return jsonify({
        'languages': languages,
        'default_language': i18n_service.default_language
    }), 200

@languages_bp.route('/current', methods=['GET'])
@auth_required
@handle_errors
def get_current_language():
    """Get current user's language preference"""
    current_user_id = get_jwt_identity()
    
    user = User.objects(id=current_user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    preferred_language = getattr(user, 'preferred_language', i18n_service.default_language)
    
    return jsonify({
        'language': preferred_language,
        'language_name': i18n_service.get_language_name(preferred_language)
    }), 200

@languages_bp.route('/set', methods=['PUT'])
@auth_required
@handle_errors
def set_language():
    """Set user's language preference"""
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    if not data or 'language' not in data:
        return jsonify({'error': 'Language is required'}), 400
    
    language = data['language']
    
    # Check if language is supported
    if not i18n_service.is_language_supported(language):
        return jsonify({'error': 'Language not supported'}), 400
    
    # Update user's language preference
    user = User.objects(id=current_user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.preferred_language = language
    user.save()
    
    return jsonify({
        'message': 'Language preference updated successfully',
        'language': language,
        'language_name': i18n_service.get_language_name(language)
    }), 200

@languages_bp.route('/detect', methods=['GET'])
def detect_language():
    """Detect language from request headers"""
    # Get language from Accept-Language header
    detected_lang = request.accept_languages.best_match(
        i18n_service.supported_languages.keys()
    )
    
    if detected_lang:
        return jsonify({
            'detected_language': detected_lang,
            'language_name': i18n_service.get_language_name(detected_lang),
            'supported': True
        }), 200
    else:
        return jsonify({
            'detected_language': None,
            'default_language': i18n_service.default_language,
            'supported': False
        }), 200

@languages_bp.route('/format/currency', methods=['POST'])
@auth_required
@handle_errors
def format_currency():
    """Format currency according to locale"""
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    if not data or 'amount' not in data:
        return jsonify({'error': 'Amount is required'}), 400
    
    amount = float(data['amount'])
    currency = data.get('currency', 'USD')
    locale = data.get('locale')
    
    # If no locale specified, use user's preference
    if not locale:
        user = User.objects(id=current_user_id).first()
        if user:
            locale = getattr(user, 'preferred_language', i18n_service.default_language)
        else:
            locale = i18n_service.default_language
    
    formatted_currency = i18n_service.format_currency(amount, currency, locale)
    
    return jsonify({
        'formatted': formatted_currency,
        'locale': locale,
        'currency': currency
    }), 200

@languages_bp.route('/format/date', methods=['POST'])
@auth_required
@handle_errors
def format_date():
    """Format date according to locale"""
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    if not data or 'date' not in data:
        return jsonify({'error': 'Date is required'}), 400
    
    date_str = data['date']
    format_type = data.get('format_type', 'long')
    locale = data.get('locale')
    
    # If no locale specified, use user's preference
    if not locale:
        user = User.objects(id=current_user_id).first()
        if user:
            locale = getattr(user, 'preferred_language', i18n_service.default_language)
        else:
            locale = i18n_service.default_language
    
    formatted_date = i18n_service.format_date(date_str, locale, format_type)
    
    return jsonify({
        'formatted': formatted_date,
        'locale': locale,
        'format_type': format_type
    }), 200

@languages_bp.route('/tax-rules/<country_code>', methods=['GET'])
def get_tax_rules(country_code):
    """Get tax rules for a specific country"""
    tax_rules = i18n_service.get_tax_rules(country_code.upper())
    
    if not tax_rules:
        return jsonify({'error': 'Country not supported'}), 404
    
    return jsonify({
        'country_code': country_code.upper(),
        'tax_rules': tax_rules
    }), 200

@languages_bp.route('/invoice-text/<key>', methods=['GET'])
def get_invoice_text(key):
    """Get localized invoice text"""
    locale = request.args.get('locale', 'en')
    
    if not i18n_service.is_language_supported(locale):
        locale = i18n_service.default_language
    
    text = i18n_service.get_invoice_text(key, locale)
    
    return jsonify({
        'key': key,
        'text': text,
        'locale': locale
    }), 200

@languages_bp.route('/translations/<locale>', methods=['GET'])
def get_translations(locale):
    """Get all translations for a locale"""
    if not i18n_service.is_language_supported(locale):
        return jsonify({'error': 'Language not supported'}), 400
    
    # This would typically load from a translation file
    # For now, return a sample of common translations
    common_translations = {
        'dashboard': 'Dashboard',
        'invoices': 'Invoices',
        'clients': 'Clients',
        'payments': 'Payments',
        'reports': 'Reports',
        'settings': 'Settings',
        'profile': 'Profile',
        'logout': 'Logout',
        'save': 'Save',
        'cancel': 'Cancel',
        'delete': 'Delete',
        'edit': 'Edit',
        'create': 'Create',
        'search': 'Search',
        'filter': 'Filter',
        'export': 'Export',
        'import': 'Import'
    }
    
    return jsonify({
        'locale': locale,
        'translations': common_translations
    }), 200
