from django.urls import path
from . import views

app_name = 'admin_api'

urlpatterns = [
    # User Management
    path('users/create/', views.create_user, name='create_user'),
    path('users/analytics/', views.user_analytics, name='user_analytics'),
    path('platform/analytics/', views.platform_analytics, name='platform_analytics'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    
    # Order Management
    path('orders/list/', views.order_list, name='order_list'),
    path('orders/analytics/', views.order_analytics, name='order_analytics'),
    path('orders/bulk-delete/', views.bulk_delete_orders, name='bulk_delete_orders'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('orders/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    
    # Restaurant Management
    path('restaurants/<int:restaurant_id>/edit/', views.edit_restaurant, name='edit_restaurant'),
    path('restaurants/<int:restaurant_id>/delete/', views.delete_restaurant, name='delete_restaurant'),
    path('restaurants/<int:restaurant_id>/toggle-status/', views.toggle_restaurant_status, name='toggle_restaurant_status'),
    path('restaurants/list/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/create/', views.create_restaurant, name='create_restaurant'),
    path('restaurants/analytics/', views.restaurant_analytics, name='restaurant_analytics'),
    path('restaurants/<int:restaurant_id>/update-rating/', views.update_restaurant_rating, name='update_restaurant_rating'),
    path('restaurants/bulk-toggle-status/', views.bulk_toggle_restaurant_status, name='bulk_toggle_restaurant_status'),
    path('restaurants/bulk-delete/', views.bulk_delete_restaurants, name='bulk_delete_restaurants'),
    
    # Meal Management
    path('meals/create/', views.create_meal, name='create_meal'),
    path('meals/list/', views.meal_list, name='meal_list'),
    path('meals/analytics/', views.meal_analytics, name='meal_analytics'),
    path('meals/<int:meal_id>/edit/', views.edit_meal, name='edit_meal'),
    path('meals/<int:meal_id>/delete/', views.delete_meal, name='delete_meal'),
    path('meals/<int:meal_id>/toggle-availability/', views.toggle_meal_availability, name='toggle_meal_availability'),
    
    # Platform Settings
    path('settings/', views.platform_settings, name='platform_settings'),
    path('settings/update/', views.update_platform_settings_ajax, name='update_platform_settings'),
    path('settings/get/', views.get_platform_settings, name='get_platform_settings'),
    path('settings/site-info/', views.update_site_info, name='update_site_info'),
]
