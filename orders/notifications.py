"""Email notifications sent to customers when an order changes status."""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Order

logger = logging.getLogger(__name__)


# Per-status copy. Keys are Order.Status values.
STATUS_EMAILS = {
    Order.Status.PROCESSING: {
        'subject': 'is being processed',
        'headline': 'We are preparing your order',
        'body': 'We have received your order and our team is packing it now. You will get another email once it ships.',
        'accent': '#1E3A8A',
    },
    Order.Status.SHIPPED: {
        'subject': 'has shipped',
        'headline': 'Your order is on the way',
        'body': 'Your order has left our store and is out for delivery. Keep your phone handy for the delivery agent.',
        'accent': '#F97316',
    },
    Order.Status.DELIVERED: {
        'subject': 'has been delivered',
        'headline': 'Your order was delivered',
        'body': 'We hope everything arrived in good condition. Reply to this email if anything is not right.',
        'accent': '#16A34A',
    },
    Order.Status.CANCELLED: {
        'subject': 'has been cancelled',
        'headline': 'Your order was cancelled',
        'body': 'This order has been cancelled. If you paid online, any amount collected will be refunded to the original payment method within 5 to 7 business days.',
        'accent': '#DC2626',
    },
}

STATUS_LABELS = dict(Order.Status.choices)


def absolute_url(path):
    """Turn a site-relative path into an absolute URL for use in an email."""
    if not path:
        return ''
    if path.startswith('http://') or path.startswith('https://'):
        return path
    base = getattr(settings, 'BASE_URL', '').rstrip('/')
    return f'{base}{path}' if base else path


def send_order_status_email(order, previous_status=None):
    """Email the customer that their order moved to a new status.

    Returns True when a message was handed to the email backend. Never raises,
    so a mail server outage can never roll back or block a status change.
    """
    template = STATUS_EMAILS.get(order.status)
    if not template:
        return False
    if not order.email:
        logger.warning('Order %s has no email address, skipping notification.', order.pk)
        return False

    shop_name = getattr(settings, 'SHOP_NAME', 'LocalShop')
    from_email = (
        getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        or getattr(settings, 'EMAIL_HOST_USER', '')
    )
    if not from_email:
        logger.warning('No DEFAULT_FROM_EMAIL or EMAIL_HOST_USER set, skipping notification.')
        return False

    context = {
        'shop_name': shop_name,
        'order': order,
        'order_number': order.pk,
        'customer_name': order.full_name() or order.first_name,
        'status': order.status,
        'status_display': order.get_status_display(),
        'previous_status': previous_status,
        'previous_status_display': STATUS_LABELS.get(previous_status, ''),
        'headline': template['headline'],
        'body': template['body'],
        'accent': template['accent'],
        'items': [
            {'name': item.product_name, 'quantity': item.quantity, 'subtotal': item.subtotal()}
            for item in order.items.all()
        ],
        'total': order.total,
        'order_url': absolute_url(order.get_absolute_url()),
        'support_email': getattr(settings, 'CONTACT_EMAIL', ''),
    }

    subject = f'[{shop_name}] Order #{order.pk} {template["subject"]}'
    try:
        html_body = render_to_string('orders/emails/status_changed.html', context)
        message = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_body),
            from_email=from_email,
            to=[order.email],
        )
        message.attach_alternative(html_body, 'text/html')
        message.send(fail_silently=False)
    except Exception:
        logger.exception('Failed to send status email for order %s to %s', order.pk, order.email)
        return False

    logger.info('Sent "%s" status email for order %s to %s', order.status, order.pk, order.email)
    return True
