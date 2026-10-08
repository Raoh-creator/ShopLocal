from urllib.parse import quote

from django.conf import settings

from pages.utils import build_tel_link, format_phone
from store.models import ContactSettings


def _contact():
    """Load the ContactSettings row, tolerating a database that predates the table."""
    try:
        return ContactSettings.load()
    except Exception:
        return None


def shop_settings(request):
    contact = _contact()

    # Dashboard values win; .env only fills the gaps so a fresh install still shows something.
    contact_email = (contact.email if contact else '') or getattr(settings, 'CONTACT_EMAIL', '')
    whatsapp_number = (contact.whatsapp_number if contact else '') or getattr(settings, 'WHATSAPP_NUMBER', '')
    phone = (contact.phone if contact else '') or getattr(settings, 'PHONE_NUMBER', '')

    gmail_link = ''
    if contact_email:
        gmail_link = f'https://mail.google.com/mail/?view=cm&fs=1&to={quote(contact_email)}'

    return {
        'shop_name': getattr(settings, 'SHOP_NAME', 'LocalShop'),
        'whatsapp_number': whatsapp_number,
        'phone_number': format_phone(phone),
        'tel_link': build_tel_link(phone),
        'contact_email': contact_email,
        'contact_address': (contact.address if contact else '') or getattr(settings, 'SHOP_ADDRESS', ''),
        'opening_hours': (contact.opening_hours if contact else '') or getattr(settings, 'SHOP_HOURS', ''),
        'gmail_link': gmail_link,
    }