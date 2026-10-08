from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomUser
from store.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class PaymentMethod(models.TextChoices):
        COD = 'COD', 'Cash on Delivery'
        UPI = 'UPI', 'UPI / GPay'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
        MOBILE_MONEY = 'MOBILE_MONEY', 'Mobile Money'
        CARD = 'CARD', 'Credit / Debit Card'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    village = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Village / town of delivery, so the shop owner can decide if the location is deliverable.',
    )
    address = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD,
    )
    payment_proof = models.CharField(
        max_length=100,
        blank=True,
        help_text='UPI reference or transaction ID supplied by the customer.',
    )
    payment_confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the customer confirmed they had paid.',
    )
    payment_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When a shop owner confirmed the money actually arrived.',
    )
    payment_verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        help_text='Staff member who verified this payment.',
    )
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'Order #{self.pk}'

    def get_absolute_url(self):
        return reverse('orders:order_detail', args=[self.pk])

    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def is_prepaid(self):
        """True when payment should already have happened before dispatch."""
        return self.payment_method != self.PaymentMethod.COD

    @property
    def payment_verified(self):
        return self.payment_verified_at is not None

    @property
    def needs_payment_check(self):
        """Prepaid orders a shop owner still has to reconcile against the bank."""
        return (
            self.is_prepaid
            and not self.payment_verified
            and self.status != self.Status.CANCELLED
        )

    def mark_payment_received(self, user):
        self.payment_verified_at = timezone.now()
        self.payment_verified_by = user
        self.save(update_fields=['payment_verified_at', 'payment_verified_by', 'updated_at'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

    def subtotal(self):
        return self.price * self.quantity