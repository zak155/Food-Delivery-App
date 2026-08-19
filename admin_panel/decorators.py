from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Decorator to ensure only admin users can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
            messages.error(request, 'Please log in to access this page.')
            return redirect('users:login')
        
        if request.user.role != 'admin':
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Admin access required'}, status=403)
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('users:home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def owner_or_admin_required(view_func):
    """Decorator to ensure only owner or admin users can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
            messages.error(request, 'Please log in to access this page.')
            return redirect('users:login')
        
        if request.user.role not in ['admin', 'owner']:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Owner or Admin access required'}, status=403)
            messages.error(request, 'Access denied. Owner or Admin privileges required.')
            return redirect('users:home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def customer_or_owner_required(view_func):
    """Decorator to ensure only customer or owner users can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
            messages.error(request, 'Please log in to access this page.')
            return redirect('users:login')
        
        if request.user.role not in ['customer', 'owner']:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Customer or Owner access required'}, status=403)
            messages.error(request, 'Access denied. Customer or Owner privileges required.')
            return redirect('users:home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def delivery_required(view_func):
    """Decorator to ensure only delivery users (or optionally admin) can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
            messages.error(request, 'Please log in to access this page.')
            return redirect('users:login')

        if request.user.role not in ['delivery', 'admin']:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Delivery access required'}, status=403)
            messages.error(request, 'Access denied. Delivery privileges required.')
            return redirect('users:home')

        return view_func(request, *args, **kwargs)
    return wrapper


def delivery_forbidden(view_func):
    """Decorator to block delivery users from customer-only views (cart, meals, checkout)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
            messages.error(request, 'Please log in to access this page.')
            return redirect('users:login')

        if getattr(request.user, 'role', None) == 'delivery':
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Delivery users cannot perform this action'}, status=403)
            messages.error(request, 'Delivery users cannot access this page.')
            return redirect('orders:delivery_dashboard')

        return view_func(request, *args, **kwargs)
    return wrapper

def can_edit_user(user, target_user):
    """Check if a user can edit another user"""
    # Admin can edit anyone except themselves
    if user.role == 'admin' and user.id != target_user.id:
        return True
    
    # Users can edit their own profile
    if user.id == target_user.id:
        return True
    
    return False


def can_delete_user(user, target_user):
    """Check if a user can delete another user"""
    # Admin can delete anyone except themselves
    if user.role == 'admin' and user.id != target_user.id:
        return True
    
    return False


def can_manage_restaurant(user, restaurant):
    """Check if a user can manage a restaurant"""
    # Admin can manage any restaurant
    if user.role == 'admin':
        return True
    
    # Owner can manage their own restaurant
    if user.role == 'owner' and hasattr(restaurant, 'owner') and restaurant.owner == user:
        return True
    
    return False


def can_manage_meal(user, meal):
    """Check if a user can manage a meal"""
    # Admin can manage any meal
    if user.role == 'admin':
        return True
    
    # Owner can manage meals from their restaurant
    if user.role == 'owner' and hasattr(meal, 'restaurant') and hasattr(meal.restaurant, 'owner') and meal.restaurant.owner == user:
        return True
    
    return False


def can_view_order(user, order):
    """Check if a user can view an order"""
    # Admin can view any order
    if user.role == 'admin':
        return True
    
    # Customer can view their own orders
    if user.role == 'customer' and order.user == user:
        return True
    
    # Owner can view orders for their restaurant
    if user.role == 'owner' and hasattr(order, 'restaurant') and hasattr(order.restaurant, 'owner') and order.restaurant.owner == user:
        return True
    
    return False
