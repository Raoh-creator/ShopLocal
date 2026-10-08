from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from cart.views import _cart_detail, get_cart, CART_SESSION_KEY
from store.models import ShopSettings
from store.utils import upi_deep_link, upi_qr_data_uri
from .forms import CheckoutForm
from .models import Order


def checkout(request):
    cart_data = _cart_detail(request)
    if not cart_data['items']:
        messages.info(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user if request.user.is_authenticated else None)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data.get('last_name', '').strip(),
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                village=form.cleaned_data['village'].strip(),
                address=form.cleaned_data['address'],
                payment_method=form.cleaned_data['payment_method'],
                payment_proof=form.cleaned_data.get('payment_proof', '').strip(),
                payment_confirmed_at=(
                    timezone.now()
                    if form.cleaned_data['payment_method'] != Order.PaymentMethod.COD
                    else None
                ),
                total=cart_data['total'],
            )
            for item in cart_data['items']:
                product = item['product']
                order.items.create(
                    product=product,
                    product_name=product.name,
                    price=product.price,
                    quantity=item['quantity'],
                )
                product.decrement_stock(item['quantity'])
            request.session.pop(CART_SESSION_KEY, None)
            messages.success(request, 'Your order has been placed successfully!')
            return redirect('orders:order_detail', pk=order.pk)
    else:
        form = CheckoutForm(user=request.user if request.user.is_authenticated else None)

    settings_obj = ShopSettings.load()
    upi_available = bool(settings_obj.upi_enabled and (settings_obj.upi_id or settings_obj.upi_qr))
    if not upi_available:
        form.fields['payment_method'].choices = [
            (v, l) for v, l in form.fields['payment_method'].choices if v != Order.PaymentMethod.UPI
        ]

    upi_link = upi_deep_link(
        settings_obj.upi_id,
        amount=cart_data['total'],
        payee_name=settings_obj.upi_payee_name,
        note='LocalShop order',
    )
    # Dynamic QR carries the amount, so scanning pre-fills it in the customer's
    # UPI app. The uploaded static QR is only a fallback: it encodes just the
    # payee VPA, which leaves the amount empty for the customer to type.
    upi_qr_dynamic = upi_qr_data_uri(upi_link) if settings_obj.upi_id else ''

    return render(request, 'orders/checkout.html', {
        'form': form,
        'items': cart_data['items'],
        'total': cart_data['total'],
        'upi_available': upi_available,
        'upi_id': settings_obj.upi_id,
        'upi_qr': upi_qr_dynamic or (settings_obj.upi_qr.url if settings_obj.upi_qr else ''),
        'upi_qr_is_dynamic': bool(upi_qr_dynamic),
        'upi_link': upi_link,
    })


@login_required
def order_history(request):
    orders = request.user.orders.all()
    return render(request, 'orders/order_history.html', {'orders': orders})


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.user and order.user != request.user:
        order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})