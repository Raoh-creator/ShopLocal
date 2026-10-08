from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'full_name', 'village', 'email', 'total', 'payment_method', 'payment_verified_at', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_verified_at', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'village', 'payment_proof')
    inlines = [OrderItemInline]