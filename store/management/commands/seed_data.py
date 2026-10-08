from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import CustomUser
from store.models import Category, Product


class Command(BaseCommand):
    help = 'Seed LocalShop with sample categories, products, and demo users.'

    @transaction.atomic
    def handle(self, *args, **options):
        owner, created = CustomUser.objects.get_or_create(
            username='owner',
            defaults={
                'email': 'owner@localshop.test',
                'role': CustomUser.Role.SHOP_OWNER,
                'first_name': 'Shop',
                'last_name': 'Owner',
            },
        )
        if created:
            owner.set_password('ownerpass123')
            owner.save()
            self.stdout.write(self.style.SUCCESS('Created shop owner: owner / ownerpass123'))

        customer, created = CustomUser.objects.get_or_create(
            username='customer',
            defaults={
                'email': 'customer@localshop.test',
                'role': CustomUser.Role.CUSTOMER,
                'first_name': 'Demo',
                'last_name': 'Customer',
            },
        )
        if created:
            customer.set_password('customerpass123')
            customer.save()
            self.stdout.write(self.style.SUCCESS('Created customer: customer / customerpass123'))

        categories = {
            'electronics': ('Electronics', 'Gadgets, accessories and more.'),
            'apparel': ('Apparel', 'Trendy and comfortable clothing.'),
            'home-kitchen': ('Home & Kitchen', 'Everything for a cozy home.'),
            'sports': ('Sports & Outdoors', 'Gear for an active lifestyle.'),
            'beauty': ('Beauty & Care', 'Personal care essentials.'),
        }
        for slug, (name, description) in categories.items():
            category, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': description},
            )
            category.name = name
            category.description = description
            category.save()

        product_data = [
            ('electronics', 'Wireless Bluetooth Headphones', 'bnc', Decimal('59.99'), 4, 25),
            ('electronics', 'Smart Phone Stand', 'smt', Decimal('14.99'), 2, 60),
            ('electronics', 'Portable Power Bank 10000mAh', 'pow', Decimal('29.99'), 3, 40),
            ('apparel', 'Classic Cotton T-Shirt', 'tsh', Decimal('19.99'), 1, 100),
            ('apparel', 'Hooded Zip Sweatshirt', 'hdz', Decimal('39.99'), 2, 35),
            ('home-kitchen', 'Stainless Steel Water Bottle', 'wtr', Decimal('24.99'), 3, 55),
            ('home-kitchen', 'Ceramic Coffee Mug Set', 'cfs', Decimal('21.99'), 2, 0),
            ('sports', 'Yoga Mat 6mm', 'yog', Decimal('34.99'), 1, 45),
            ('sports', 'Adjustable Dumbbells', 'dum', Decimal('89.99'), 4, 12),
            ('beauty', 'Vitamin C Face Serum', 'vcs', Decimal('27.99'), 3, 0),
            ('beauty', 'Moisturizing Lip Balm', 'lip', Decimal('6.99'), 2, 90),
        ]
        for category_slug, name, prefix, price, _place, stock in product_data:
            category = Category.objects.get(slug=category_slug)
            slug = f'{prefix}-{category_slug}'
            Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'category': category,
                    'name': name,
                    'price': price,
                    'stock': stock,
                    'description': f'A great quality {name.lower()} available at {name}.',
                    'is_active': True,
                    'is_deleted': False,
                },
            )
        self.stdout.write(self.style.SUCCESS('Seeded categories and products.'))