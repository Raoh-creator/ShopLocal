from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def money(value, symbol='\u20b9'):
    """Format a decimal value as a currency string, e.g. \u20b91,234.50."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        amount = Decimal('0')
    return f'{symbol}{amount:,.2f}'


PAYMENT_ICONS = {
    'COD': 'bi-cash-coin',
    'UPI': 'bi-google',
    'BANK_TRANSFER': 'bi-bank',
    'MOBILE_MONEY': 'bi-phone',
    'CARD': 'bi-credit-card',
}


@register.filter
def payment_icon(value):
    """Map an Order.PaymentMethod value to a Bootstrap Icons class name."""
    return PAYMENT_ICONS.get(value, 'bi-wallet2')


PAYMENT_HINTS = {
    'COD': 'Pay in cash when your order arrives at your door.',
    'UPI': 'Pay instantly with any UPI app — GPay, PhonePe, Paytm.',
    'BANK_TRANSFER': 'We share our account details, you confirm the transfer.',
    'MOBILE_MONEY': 'Send to our mobile money wallet and confirm below.',
    'CARD': 'We will contact you on WhatsApp to take the payment.',
}


@register.filter
def payment_hint(value):
    """Short reassuring description shown under each payment option."""
    return PAYMENT_HINTS.get(value, '')