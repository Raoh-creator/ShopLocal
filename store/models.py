from django.conf import settings
from django.db import models
from django.urls import reverse


class ShopSettings(models.Model):
    """Singleton row holding shop-wide payment configuration."""

    upi_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='UPI ID customers send money to, e.g. shop@okhdfcbank',
    )
    upi_payee_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Name shown in the customer UPI app.',
    )
    upi_qr = models.ImageField(
        upload_to='payments/',
        blank=True,
        null=True,
        help_text='Optional static QR image. Leave empty to use the auto-generated UPI link instead.',
    )
    upi_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Shop settings'

    def __str__(self):
        return 'Shop settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactSettings(models.Model):
    """Singleton row holding the public contact details shown across the site.

    Seeded from the .env values on first run; once a row exists the dashboard
    is the source of truth, so the owner can change details without a restart.
    """

    email = models.EmailField(
        blank=True,
        help_text='Shown on the contact page and used as the fallback recipient for the contact form.',
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        help_text='Tap-to-call number. Spaces, dashes and a leading + are fine.',
    )
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        help_text='Digits only, including country code, e.g. 918837351115.',
    )
    address = models.TextField(blank=True, help_text='Shop address shown on the contact page.')
    opening_hours = models.CharField(
        max_length=120,
        blank=True,
        help_text='e.g. Mon - Sat: 9:00 AM - 8:00 PM',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Contact settings'

    def __str__(self):
        return 'Contact settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Return the single row, seeding it from .env the first time."""
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'email': getattr(settings, 'CONTACT_EMAIL', ''),
                'phone': getattr(settings, 'PHONE_NUMBER', ''),
                'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', ''),
                'address': getattr(settings, 'SHOP_ADDRESS', ''),
                'opening_hours': getattr(settings, 'SHOP_HOURS', ''),
            },
        )
        return obj


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False, help_text='Soft-delete flag used by the dashboard.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def out_of_stock(self):
        return self.stock == 0

    def decrement_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save(update_fields=['stock'])
            return True
        return False