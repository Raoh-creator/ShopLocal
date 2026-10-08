from .views import get_cart


def cart_counter(request):
    """Cart item count for the navbar badge (guest + authenticated users)."""
    cart = get_cart(request)
    count = sum(int(data.get('quantity', 1)) for data in cart.values())
    return {'cart_count': count}