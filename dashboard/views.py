from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from store.forms import (
    CategoryForm,
    ContactSettingsForm,
    ProductForm,
    ShopSettingsForm,
)
from store.models import Category, ContactSettings, Product, ShopSettings
from store.utils import upi_deep_link
from orders.models import Order

from .decorators import staff_member_required


def _safe_next(value):
    """Only allow relative paths, so ?next= can't be used for an open redirect."""
    if value and value.startswith('/') and not value.startswith('//'):
        return value
    return 'dashboard:home'


@staff_member_required
def dashboard_home(request):
    stats = {
        'total_sales': Order.objects.exclude(status=Order.Status.CANCELLED)
                                     .aggregate(total=Sum('total'))['total'] or 0,
        'total_orders': Order.objects.count(),
        'out_of_stock': Product.objects.filter(stock=0, is_deleted=False).count(),
        'pending_orders': Order.objects.filter(status=Order.Status.PENDING).count(),
    }
    orders = Order.objects.all()[:20]
    products = Product.objects.filter(is_deleted=False)
    categories = Category.objects.all()
    upi_orders = Order.objects.filter(payment_method=Order.PaymentMethod.UPI).count()
    unverified_count = Order.objects.filter(
        payment_method__in=[c for c, _ in Order.PaymentMethod.choices if c != Order.PaymentMethod.COD],
        payment_verified_at__isnull=True,
    ).exclude(status=Order.Status.CANCELLED).count()
    return render(request, 'dashboard/dashboard_home.html', {
        'stats': stats,
        'orders': orders,
        'products': products,
        'categories': categories,
        'upi_orders': upi_orders,
        'unverified_count': unverified_count,
        'shop_settings': ShopSettings.load(),
    })


@staff_member_required
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status')
    if new_status in Order.Status.values:
        order.status = new_status
        order.save(update_fields=['status'])
        messages.success(request, f'Order #{order.pk} status updated to {order.get_status_display()}.')
    else:
        messages.error(request, 'Invalid status selected.')
    return redirect('dashboard:home')


@staff_member_required
def mark_payment_received(request, pk):
    """Manually reconcile a prepaid order after checking the bank account."""
    order = get_object_or_404(Order, pk=pk)

    if request.method != 'POST':
        return redirect('dashboard:home')

    if not order.is_prepaid:
        messages.error(request, f'Order #{order.pk} is Cash on Delivery, nothing to reconcile.')
    elif order.status == Order.Status.CANCELLED:
        messages.error(request, f'Order #{order.pk} is cancelled, payment cannot be verified.')
    elif order.payment_verified:
        messages.info(
            request,
            f'Order #{order.pk} was already verified by {order.payment_verified_by} on '
            f'{order.payment_verified_at:%b %d, %Y %H:%M}.',
        )
    else:
        order.mark_payment_received(request.user)
        messages.success(request, f'Payment verified for order #{order.pk}.')

    return redirect(_safe_next(request.POST.get('next')))


@staff_member_required
def payment_settings(request):
    settings_obj = ShopSettings.load()
    if request.method == 'POST':
        form = ShopSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment settings updated.')
            return redirect('dashboard:payment_settings')
    else:
        form = ShopSettingsForm(instance=settings_obj)
    sample_link = upi_deep_link(
        settings_obj.upi_id or 'yourshop@okhdfcbank',
        amount=100,
        payee_name=settings_obj.upi_payee_name,
        note='LocalShop order',
    )
    return render(request, 'dashboard/payment_settings.html', {
        'form': form,
        'settings_obj': settings_obj,
        'sample_link': sample_link,
    })


@staff_member_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('dashboard:home')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Add Product'})


@staff_member_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('dashboard:home')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@staff_member_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_deleted = True
    product.is_active = False
    product.save(update_fields=['is_deleted', 'is_active'])
    messages.success(request, 'Product soft-deleted.')
    return redirect('dashboard:home')


@staff_member_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('dashboard:home')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/category_form.html', {'form': form, 'title': 'Add Category'})


@staff_member_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('dashboard:home')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/category_form.html', {'form': form, 'title': 'Edit Category', 'category': category})


@staff_member_required
def contact_settings(request):
    settings_obj = ContactSettings.load()
    if request.method == 'POST':
        form = ContactSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact details updated.')
            return redirect('dashboard:contact_settings')
    else:
        form = ContactSettingsForm(instance=settings_obj)
    return render(request, 'dashboard/contact_settings.html', {
        'form': form,
        'settings_obj': settings_obj,
    })