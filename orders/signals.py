"""Detect order status changes and notify the customer by email.

Signals are used rather than the dashboard view so the email also fires when a
status is changed from the Django admin, a management command, or a shell.
"""
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Order
from .notifications import send_order_status_email

logger = logging.getLogger(__name__)

PREVIOUS_STATUS_ATTR = '_previous_status'


@receiver(pre_save, sender=Order)
def remember_previous_status(sender, instance, update_fields=None, **kwargs):
    """Stash the stored status on the instance before it gets overwritten."""
    if update_fields is not None and 'status' not in update_fields:
        setattr(instance, PREVIOUS_STATUS_ATTR, instance.status)
        return
    if not instance.pk:
        setattr(instance, PREVIOUS_STATUS_ATTR, None)
        return
    setattr(
        instance,
        PREVIOUS_STATUS_ATTR,
        sender.objects.filter(pk=instance.pk).values_list('status', flat=True).first(),
    )


@receiver(post_save, sender=Order)
def email_customer_on_status_change(sender, instance, created, raw=False, **kwargs):
    if created or raw:
        return
    previous = getattr(instance, PREVIOUS_STATUS_ATTR, None)
    if previous is None or previous == instance.status:
        return
    send_order_status_email(instance, previous_status=previous)
