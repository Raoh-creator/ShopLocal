from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('settings/payment/', views.payment_settings, name='payment_settings'),
    path('settings/contact/', views.contact_settings, name='contact_settings'),
    path('order/<int:pk>/status/', views.update_order_status, name='update_order_status'),
    path('order/<int:pk>/payment-received/', views.mark_payment_received, name='mark_payment_received'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
]