from urllib.parse import quote

from django.conf import settings


def contact_details():
    """Return the shop's contact details, preferring the dashboard over .env."""
    from store.models import ContactSettings

    try:
        saved = ContactSettings.load()
    except Exception:
        saved = None

    return {
        'email': (saved.email if saved else '') or getattr(settings, 'CONTACT_EMAIL', ''),
        'whatsapp_number': (saved.whatsapp_number if saved else '') or getattr(settings, 'WHATSAPP_NUMBER', ''),
        'phone': (saved.phone if saved else '') or getattr(settings, 'PHONE_NUMBER', ''),
    }


def build_whatsapp_link(message=None):
    """Return a wa.me deep link with a pre-filled message."""
    number = contact_details()['whatsapp_number'].replace('+', '').replace(' ', '')
    text = message or getattr(settings, 'WHATSAPP_MESSAGE', '')
    return f'https://wa.me/{number}?text={quote(text)}'


def build_gmail_link(subject='', body=''):
    """Return a web Gmail compose link pre-addressed to the shop owner."""
    to = contact_details()['email']
    params = {}
    if to:
        params['to'] = to
    if subject:
        params['subject'] = subject
    if body:
        params['body'] = body
    query = '&'.join(f'{k}={quote(v)}' for k, v in params.items())
    return f'https://mail.google.com/mail/?view=cm&fs=1&{query}'


def format_phone(raw):
    """Strip a phone number down to digits and a leading +, ready for a tel: link."""
    raw = (raw or '').strip()
    if not raw:
        return ''
    digits = ''.join(ch for ch in raw if ch.isdigit() or ch == '+')
    return '+' + digits.lstrip('+')


def build_tel_link(number=None):
    """Return a tel: URI for the shop phone number, or '' when none is set."""
    number = number or contact_details()['phone']
    return f'tel:{format_phone(number)}' if number else ''