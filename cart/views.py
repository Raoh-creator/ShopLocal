from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from store.models import Product

CART_SESSION_KEY = 'cart'


def get_cart(request):
    """Return the session cart dict: {product_id: {'quantity': int}}"""
    return request.session.setdefault(CART_SESSION_KEY, {})


def _cart_detail(request):
    cart = get_cart(request)
    items = []
    total = 0
    for product_id, data in cart.items():
        product = Product.objects.filter(
            pk=int(product_id), is_active=True, is_deleted=False
        ).first()
        if not product:
            continue
        quantity = int(data.get('quantity', 1))
        subtotal = product.price * quantity
        total += subtotal
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })
    return {
        'items': items,
        'total': total,
        'count': sum(item['quantity'] for item in items),
    }


def cart_detail(request):
    data = _cart_detail(request)
    return render(request, 'cart/cart_detail.html', data)


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True, is_deleted=False)
    cart = get_cart(request)
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] = min(
            product.stock, cart[str(product_id)]['quantity'] + quantity
        )
    else:
        cart[str(product_id)] = {'quantity': min(product.stock, quantity)}

    request.session.modified = True
    return redirect('cart:cart_detail')


@require_POST
def buy_now(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True, is_deleted=False)
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    request.session[CART_SESSION_KEY] = {
        str(product_id): {'quantity': min(product.stock, quantity)}
    }
    request.session.modified = True
    return redirect('orders:checkout')


@require_POST
def update_cart(request, product_id):
    cart = get_cart(request)
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    product = get_object_or_404(Product, pk=product_id, is_active=True, is_deleted=False)
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] = min(product.stock, quantity)
        request.session.modified = True
    return redirect('cart:cart_detail')


@require_POST
def remove_from_cart(request, product_id):
    cart = get_cart(request)
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session.modified = True
    return redirect('cart:cart_detail')


@require_POST
def clear_cart(request):
    request.session.pop(CART_SESSION_KEY, None)
    return redirect('cart:cart_detail')