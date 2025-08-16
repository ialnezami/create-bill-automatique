import json
import os
from typing import Dict, Any, Optional
from flask import request, current_app
from flask_babel import Babel, gettext, ngettext, lazy_gettext

class I18nService:
    """Internationalization service for multi-language support"""
    
    def __init__(self):
        self.babel = Babel()
        self.supported_languages = {
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'nl': 'Nederlands',
            'pl': 'Polski',
            'ru': 'Русский',
            'ja': '日本語',
            'ko': '한국어',
            'zh': '中文',
            'ar': 'العربية',
            'hi': 'हिन्दी'
        }
        
        self.default_language = 'en'
        self.fallback_language = 'en'
        
        # Currency formats by locale
        self.currency_formats = {
            'en': {'symbol': '$', 'position': 'before', 'decimal': '.', 'thousands': ','},
            'es': {'symbol': '€', 'position': 'after', 'decimal': ',', 'thousands': '.'},
            'fr': {'symbol': '€', 'position': 'after', 'decimal': ',', 'thousands': ' '},
            'de': {'symbol': '€', 'position': 'before', 'decimal': ',', 'thousands': '.'},
            'it': {'symbol': '€', 'position': 'after', 'decimal': ',', 'thousands': '.'},
            'pt': {'symbol': '€', 'position': 'after', 'decimal': ',', 'thousands': '.'},
            'nl': {'symbol': '€', 'position': 'before', 'decimal': ',', 'thousands': '.'},
            'pl': {'symbol': 'zł', 'position': 'after', 'decimal': ',', 'thousands': ' '},
            'ru': {'symbol': '₽', 'position': 'after', 'decimal': ',', 'thousands': ' '},
            'ja': {'symbol': '¥', 'position': 'before', 'decimal': '.', 'thousands': ','},
            'ko': {'symbol': '₩', 'position': 'before', 'decimal': '.', 'thousands': ','},
            'zh': {'symbol': '¥', 'position': 'before', 'decimal': '.', 'thousands': ','},
            'ar': {'symbol': 'د.ك', 'position': 'after', 'decimal': '.', 'thousands': ','},
            'hi': {'symbol': '₹', 'position': 'before', 'decimal': '.', 'thousands': ','}
        }
        
        # Date formats by locale
        self.date_formats = {
            'en': {'short': '%m/%d/%Y', 'long': '%B %d, %Y', 'time': '%I:%M %p'},
            'es': {'short': '%d/%m/%Y', 'long': '%d de %B de %Y', 'time': '%H:%M'},
            'fr': {'short': '%d/%m/%Y', 'long': '%d %B %Y', 'time': '%H:%M'},
            'de': {'short': '%d.%m.%Y', 'long': '%d. %B %Y', 'time': '%H:%M'},
            'it': {'short': '%d/%m/%Y', 'long': '%d %B %Y', 'time': '%H:%M'},
            'pt': {'short': '%d/%m/%Y', 'long': '%d de %B de %Y', 'time': '%H:%M'},
            'nl': {'short': '%d-%m-%Y', 'long': '%d %B %Y', 'time': '%H:%M'},
            'pl': {'short': '%d.%m.%Y', 'long': '%d %B %Y', 'time': '%H:%M'},
            'ru': {'short': '%d.%m.%Y', 'long': '%d %B %Y', 'time': '%H:%M'},
            'ja': {'short': '%Y/%m/%d', 'long': '%Y年%m月%d日', 'time': '%H:%M'},
            'ko': {'short': '%Y.%m.%d', 'long': '%Y년 %m월 %d일', 'time': '%H:%M'},
            'zh': {'short': '%Y/%m/%d', 'long': '%Y年%m月%d日', 'time': '%H:%M'},
            'ar': {'short': '%d/%m/%Y', 'long': '%d %B %Y', 'time': '%H:%M'},
            'hi': {'short': '%d/%m/%Y', 'long': '%d %B %Y', 'time': '%H:%M'}
        }
        
        # Tax calculation rules by country
        self.tax_rules = {
            'US': {'default_rate': 0.0, 'name': 'Sales Tax', 'calculation': 'state_based'},
            'CA': {'default_rate': 0.05, 'name': 'GST/HST', 'calculation': 'federal_provincial'},
            'GB': {'default_rate': 0.20, 'name': 'VAT', 'calculation': 'standard'},
            'DE': {'default_rate': 0.19, 'name': 'MwSt', 'calculation': 'standard'},
            'FR': {'default_rate': 0.20, 'name': 'TVA', 'calculation': 'standard'},
            'ES': {'default_rate': 0.21, 'name': 'IVA', 'calculation': 'standard'},
            'IT': {'default_rate': 0.22, 'name': 'IVA', 'calculation': 'standard'},
            'JP': {'default_rate': 0.10, 'name': '消費税', 'calculation': 'standard'},
            'AU': {'default_rate': 0.10, 'name': 'GST', 'calculation': 'standard'},
            'IN': {'default_rate': 0.18, 'name': 'GST', 'calculation': 'standard'}
        }
    
    def init_app(self, app):
        """Initialize the i18n service with Flask app"""
        self.babel.init_app(app)
        
        # Set up language detection
        @self.babel.localeselector
        def get_locale():
            # Try to get language from user preferences
            if hasattr(request, 'current_user') and request.current_user:
                user_lang = getattr(request.current_user, 'preferred_language', None)
                if user_lang and user_lang in self.supported_languages:
                    return user_lang
            
            # Try to get language from request headers
            lang = request.accept_languages.best_match(self.supported_languages.keys())
            if lang:
                return lang
            
            # Fallback to default language
            return self.default_language
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages
    
    def get_language_name(self, lang_code: str) -> str:
        """Get language name from language code"""
        return self.supported_languages.get(lang_code, lang_code)
    
    def is_language_supported(self, lang_code: str) -> bool:
        """Check if language is supported"""
        return lang_code in self.supported_languages
    
    def get_currency_format(self, locale: str) -> Dict[str, Any]:
        """Get currency format for locale"""
        return self.currency_formats.get(locale, self.currency_formats[self.default_language])
    
    def get_date_format(self, locale: str) -> Dict[str, str]:
        """Get date format for locale"""
        return self.date_formats.get(locale, self.date_formats[self.default_language])
    
    def get_tax_rules(self, country_code: str) -> Dict[str, Any]:
        """Get tax rules for country"""
        return self.tax_rules.get(country_code, self.tax_rules.get('US', {}))
    
    def format_currency(self, amount: float, currency: str, locale: str = 'en') -> str:
        """Format currency according to locale"""
        try:
            import locale as locale_module
            
            # Set locale for formatting
            locale_code = f"{locale}_US" if locale == 'en' else f"{locale}_{locale.upper()}"
            locale_module.setlocale(locale_module.LC_ALL, locale_code)
            
            # Format currency
            formatted = locale_module.currency(amount, grouping=True, international=False)
            
            return formatted
            
        except (ImportError, locale_module.Error):
            # Fallback formatting
            format_info = self.get_currency_format(locale)
            symbol = format_info['symbol']
            position = format_info['position']
            decimal = format_info['decimal']
            thousands = format_info['thousands']
            
            # Format number
            number_str = f"{amount:,.2f}".replace(',', thousands).replace('.', decimal)
            
            if position == 'before':
                return f"{symbol}{number_str}"
            else:
                return f"{number_str}{symbol}"
    
    def format_date(self, date_obj, locale: str = 'en', format_type: str = 'long') -> str:
        """Format date according to locale"""
        try:
            from datetime import datetime
            
            if isinstance(date_obj, str):
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            
            format_info = self.get_date_format(locale)
            date_format = format_info.get(format_type, format_info['long'])
            
            # Handle special format characters
            if '%B' in date_format:
                # Month names need localization
                month_names = self._get_month_names(locale)
                month_name = month_names[date_obj.month - 1]
                date_format = date_format.replace('%B', month_name)
            
            return date_obj.strftime(date_format)
            
        except Exception as e:
            current_app.logger.error(f"Error formatting date: {str(e)}")
            return str(date_obj)
    
    def _get_month_names(self, locale: str) -> list:
        """Get month names for locale"""
        month_names = {
            'en': ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December'],
            'es': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                   'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
            'fr': ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                   'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'],
            'de': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                   'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
            'it': ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
                   'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'],
            'pt': ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                   'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'],
            'nl': ['januari', 'februari', 'maart', 'april', 'mei', 'juni',
                   'juli', 'augustus', 'september', 'oktober', 'november', 'december'],
            'pl': ['styczeń', 'luty', 'marzec', 'kwiecień', 'maj', 'czerwiec',
                   'lipiec', 'sierpień', 'wrzesień', 'październik', 'listopad', 'grudzień'],
            'ru': ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
                   'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'],
            'ja': ['1月', '2月', '3月', '4月', '5月', '6月',
                   '7月', '8月', '9月', '10月', '11月', '12月'],
            'ko': ['1월', '2월', '3월', '4월', '5월', '6월',
                   '7월', '8월', '9월', '10월', '11월', '12월'],
            'zh': ['1月', '2月', '3月', '4月', '5月', '6月',
                   '7月', '8月', '9月', '10月', '11월', '12월'],
            'ar': ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                   'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'],
            'hi': ['जनवरी', 'फरवरी', 'मार्च', 'अप्रैल', 'मई', 'जून',
                   'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर']
        }
        
        return month_names.get(locale, month_names['en'])
    
    def get_text(self, key: str, locale: str = 'en', **kwargs) -> str:
        """Get localized text for key"""
        try:
            # Load translation file
            translation_file = os.path.join(
                current_app.root_path, 'translations', locale, 'LC_MESSAGES', 'messages.json'
            )
            
            if os.path.exists(translation_file):
                with open(translation_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                
                text = translations.get(key, key)
                
                # Replace placeholders
                if kwargs:
                    text = text.format(**kwargs)
                
                return text
            
            return key
            
        except Exception as e:
            current_app.logger.error(f"Error getting translation: {str(e)}")
            return key
    
    def get_plural_text(self, singular: str, plural: str, count: int, locale: str = 'en') -> str:
        """Get pluralized text"""
        if count == 1:
            return self.get_text(singular, locale)
        else:
            return self.get_text(plural, locale).format(count=count)
    
    def get_invoice_text(self, key: str, locale: str = 'en', **kwargs) -> str:
        """Get invoice-specific localized text"""
        invoice_keys = {
            'invoice': {'en': 'Invoice', 'es': 'Factura', 'fr': 'Facture', 'de': 'Rechnung'},
            'due_date': {'en': 'Due Date', 'es': 'Fecha de Vencimiento', 'fr': 'Date d\'Échéance', 'de': 'Fälligkeitsdatum'},
            'total': {'en': 'Total', 'es': 'Total', 'fr': 'Total', 'de': 'Gesamt'},
            'subtotal': {'en': 'Subtotal', 'es': 'Subtotal', 'fr': 'Sous-total', 'de': 'Zwischensumme'},
            'tax': {'en': 'Tax', 'es': 'Impuesto', 'fr': 'Taxe', 'de': 'Steuer'},
            'discount': {'en': 'Discount', 'es': 'Descuento', 'fr': 'Remise', 'de': 'Rabatt'},
            'amount_due': {'en': 'Amount Due', 'es': 'Monto a Pagar', 'fr': 'Montant Dû', 'de': 'Fälliger Betrag'},
            'payment_terms': {'en': 'Payment Terms', 'es': 'Términos de Pago', 'fr': 'Conditions de Paiement', 'de': 'Zahlungsbedingungen'},
            'thank_you': {'en': 'Thank you for your business!', 'es': '¡Gracias por su negocio!', 'fr': 'Merci pour votre entreprise !', 'de': 'Vielen Dank für Ihr Geschäft!'}
        }
        
        if key in invoice_keys:
            return invoice_keys[key].get(locale, invoice_keys[key]['en'])
        
        return self.get_text(key, locale, **kwargs)

# Global i18n service instance
i18n_service = I18nService()
