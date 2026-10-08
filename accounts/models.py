from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model supporting CUSTOMER, SHOP_OWNER and ADMIN roles."""

    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        SHOP_OWNER = 'SHOP_OWNER', 'Shop Owner'
        ADMIN = 'ADMIN', 'Administrator'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        help_text='Determines dashboard access and store management permissions.',
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_staff_member(self):
        return self.role in (self.Role.SHOP_OWNER, self.Role.ADMIN) or self.is_superuser