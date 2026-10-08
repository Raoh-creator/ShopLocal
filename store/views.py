from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def _visible_products():
    return Product.objects.filter(is_active=True, is_deleted=False)


def product_list(request):
    products = _visible_products()
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)

    categories = Category.objects.filter(is_active=True)
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'products': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(_visible_products(), slug=slug)
    related = _visible_products().filter(category=product.category).exclude(pk=product.pk)[:4]
    return render(request, 'store/product_detail.html', {'product': product, 'related': related})