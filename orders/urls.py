from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.delivery_dashboard, name='delivery_dashboard'),
    path('poll/', views.delivery_orders_poll, name='delivery_orders_poll'),
    path('stats/', views.delivery_stats, name='delivery_stats'),
    path('accept/<int:order_id>/', views.delivery_accept_order, name='delivery_accept_order'),
    path('update-status/<int:order_id>/', views.delivery_update_status, name='delivery_update_status'),
    path('history/', views.delivery_history, name='delivery_history'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('checkout-success/<int:order_id>/', views.checkout_success, name='checkout_success'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-cart-item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart-count/', views.cart_count, name='cart_count'),
    path('order-tracking/<int:order_id>/', views.order_tracking, name='order_tracking'),
    path('restaurant-update-status/<int:order_id>/', views.restaurant_update_status, name='restaurant_update_status'),
]