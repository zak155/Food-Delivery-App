from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Restaurant
from .forms import RestaurantForm
from meals.models import Meal
from meals.forms import MealForm, MealSearchForm
from orders.models import Order


@login_required
def dashboard(request):
    """Basic restaurant dashboard"""
    if request.user.role == 'admin':
        restaurants = Restaurant.objects.all()
    elif request.user.role == 'owner':
        restaurants = Restaurant.objects.filter(owner=request.user)
    else:
        return render(request, 'restaurants/access_denied.html')
    
    return render(request, 'restaurants/dashboard.html', {'restaurants': restaurants})


@login_required
def restaurant_dashboard(request, restaurant_id=None):
    """Detailed restaurant dashboard for owners and admins"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get restaurant data
    if restaurant_id:
        # Specific restaurant requested
        if request.user.role == 'admin':
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
            restaurants = Restaurant.objects.all()
        else:
            restaurants = Restaurant.objects.filter(owner=request.user)
            restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    else:
        # Default behavior (for backward compatibility)
        if request.user.role == 'admin':
            # For admins, show restaurant selection if multiple restaurants exist
            restaurants = Restaurant.objects.all()
            if restaurants.count() > 1:
                # Show restaurant selection page
                context = {'restaurants': restaurants, 'action': 'dashboard'}
                return render(request, 'restaurants/select_restaurant_for_action.html', context)
            else:
                restaurant = restaurants.first()
        else:
            restaurants = Restaurant.objects.filter(owner=request.user)
            restaurant = restaurants.first() if restaurants.exists() else None
    
    # Get meals for the restaurant with pagination
    meals = []
    recent_orders = []
    meals_paginator = None
    meals_page_obj = None
    
    if restaurant:
        # Get all meals for pagination
        all_meals = Meal.objects.filter(restaurant=restaurant).order_by('-created_at')
        meals_paginator = Paginator(all_meals, 5)
        page_number = request.GET.get('meals_page', 1)
        meals_page_obj = meals_paginator.get_page(page_number)
        meals = meals_page_obj
        
        recent_orders = Order.objects.filter(restaurant=restaurant).select_related('user').order_by('-created_at')[:5]
    
    context = {
        'restaurant': restaurant,
        'restaurants': restaurants,
        'meals': meals,
        'recent_orders': recent_orders,
        'meals_page_obj': meals_page_obj,
        'meals_paginator': meals_paginator,
        'is_meals_paginated': meals_page_obj.has_other_pages() if meals_page_obj else False,
    }
    return render(request, 'restaurants/restaurant_dashboard.html', context)


@login_required
def manage_meals(request, restaurant_id=None):
    """Manage meals for restaurant"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get restaurant
    if restaurant_id:
        # Specific restaurant requested
        if request.user.role == 'admin':
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        else:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    else:
        # Default behavior (for backward compatibility)
        if request.user.role == 'admin':
            # For admins, show restaurant selection if multiple restaurants exist
            restaurants = Restaurant.objects.all()
            if restaurants.count() > 1:
                # Show restaurant selection page
                context = {'restaurants': restaurants, 'action': 'manage_meals'}
                return render(request, 'restaurants/select_restaurant_for_action.html', context)
            else:
                restaurant = restaurants.first()
        else:
            restaurant = Restaurant.objects.filter(owner=request.user).first()
    
    if not restaurant:
        messages.error(request, 'No restaurant found.')
        return redirect('restaurants:restaurant_dashboard')
    
    # Handle search and filtering
    search_form = MealSearchForm(request.GET)
    meals = Meal.objects.filter(restaurant=restaurant)
    
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        is_available = search_form.cleaned_data.get('is_available')
        
        if search:
            meals = meals.filter(name__icontains=search)
        if is_available:
            meals = meals.filter(is_available=(is_available == 'true'))
    
    # Pagination
    paginator = Paginator(meals, 10)
    page_number = request.GET.get('page')
    meals = paginator.get_page(page_number)
    
    context = {
        'restaurant': restaurant,
        'meals': meals,
        'search_form': search_form,
    }
    return render(request, 'restaurants/manage_meals.html', context)


@login_required
def add_meal(request, restaurant_id=None):
    """Add a new meal"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get restaurant
    if restaurant_id:
        # Specific restaurant requested
        if request.user.role == 'admin':
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        else:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    else:
        # Default behavior (for backward compatibility)
        if request.user.role == 'admin':
            # For admins, show restaurant selection if multiple restaurants exist
            restaurants = Restaurant.objects.all()
            if restaurants.count() > 1:
                # Show restaurant selection page
                context = {'restaurants': restaurants, 'action': 'add_meal'}
                return render(request, 'restaurants/select_restaurant_for_action.html', context)
            else:
                restaurant = restaurants.first()
        else:
            restaurant = Restaurant.objects.filter(owner=request.user).first()
    
    if not restaurant:
        messages.error(request, 'No restaurant found.')
        return redirect('restaurants:restaurant_dashboard')
    
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES, restaurant=restaurant)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.restaurant = restaurant
            meal.save()
            messages.success(request, f'Meal "{meal.name}" added successfully!')
            # Redirect back to manage meals for this specific restaurant
            return redirect('restaurants:manage_meals_for_restaurant', restaurant_id=restaurant.id)
    else:
        form = MealForm(restaurant=restaurant)
    
    context = {
        'form': form,
        'restaurant': restaurant,
    }
    return render(request, 'restaurants/add_meal.html', context)


@login_required
def edit_meal(request, meal_id):
    """Edit an existing meal"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get meal
    if request.user.role == 'admin':
        meal = get_object_or_404(Meal, id=meal_id)
    else:
        meal = get_object_or_404(Meal, id=meal_id, restaurant__owner=request.user)
    
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES, instance=meal, restaurant=meal.restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Meal "{meal.name}" updated successfully!')
            # Redirect back to context-aware manage meals
            return redirect('restaurants:manage_meals_for_restaurant', restaurant_id=meal.restaurant.id)
    else:
        form = MealForm(instance=meal, restaurant=meal.restaurant)
    
    context = {
        'form': form,
        'meal': meal,
        'restaurant': meal.restaurant,
    }
    return render(request, 'restaurants/edit_meal.html', context)


@login_required
def delete_meal(request, meal_id):
    """Delete a meal"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get meal
    if request.user.role == 'admin':
        meal = get_object_or_404(Meal, id=meal_id)
    else:
        meal = get_object_or_404(Meal, id=meal_id, restaurant__owner=request.user)
    
    if request.method == 'POST':
        meal_name = meal.name
        meal.delete()
        messages.success(request, f'Meal "{meal_name}" deleted successfully!')
        # Redirect back to context-aware manage meals
        return redirect('restaurants:manage_meals_for_restaurant', restaurant_id=meal.restaurant.id)
    
    context = {
        'meal': meal,
    }
    return render(request, 'restaurants/delete_meal.html', context)


@login_required
def toggle_meal_availability(request, meal_id):
    """Toggle meal availability via AJAX"""
    if request.user.role not in ['owner', 'admin']:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    # Get meal
    if request.user.role == 'admin':
        meal = get_object_or_404(Meal, id=meal_id)
    else:
        meal = get_object_or_404(Meal, id=meal_id, restaurant__owner=request.user)
    
    if request.method == 'POST':
        meal.is_available = not meal.is_available
        meal.save()
        return JsonResponse({
            'success': True,
            'is_available': meal.is_available,
            'message': f'Meal is now {"available" if meal.is_available else "unavailable"}'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def restaurant_settings(request, restaurant_id=None):
    """Restaurant settings and profile management"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get restaurant
    if restaurant_id:
        # Specific restaurant requested
        if request.user.role == 'admin':
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        else:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    else:
        # Default behavior (for backward compatibility)
        if request.user.role == 'admin':
            # For admins, show restaurant selection if multiple restaurants exist
            restaurants = Restaurant.objects.all()
            if restaurants.count() > 1:
                # Show restaurant selection page
                context = {'restaurants': restaurants, 'action': 'settings'}
                return render(request, 'restaurants/select_restaurant_for_action.html', context)
            else:
                restaurant = restaurants.first()
        else:
            restaurant = Restaurant.objects.filter(owner=request.user).first()
    
    if not restaurant:
        messages.error(request, 'No restaurant found.')
        return redirect('restaurants:restaurant_dashboard')
    
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            # Check if hero image was uploaded
            if 'hero_image' in request.FILES:
                messages.success(request, 'Restaurant settings and hero image updated successfully!')
            else:
                messages.success(request, 'Restaurant settings updated successfully!')
            return redirect('restaurants:restaurant_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RestaurantForm(instance=restaurant)
    
    # Get restaurant statistics
    total_meals = Meal.objects.filter(restaurant=restaurant).count()
    available_meals = Meal.objects.filter(restaurant=restaurant, is_available=True).count()
    total_orders = Order.objects.filter(restaurant=restaurant).count()
    total_revenue = Order.objects.filter(restaurant=restaurant).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    context = {
        'form': form,
        'restaurant': restaurant,
        'total_meals': total_meals,
        'available_meals': available_meals,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
    }
    return render(request, 'restaurants/restaurant_settings.html', context)


@login_required
def restaurant_orders(request, restaurant_id=None):
    """View restaurant orders"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Access denied. Restaurant owner privileges required.')
        return redirect('users:home')
    
    # Get restaurant
    if restaurant_id:
        # Specific restaurant requested
        if request.user.role == 'admin':
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        else:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    else:
        # Default behavior (for backward compatibility)
        if request.user.role == 'admin':
            # For admins, show restaurant selection if multiple restaurants exist
            restaurants = Restaurant.objects.all()
            if restaurants.count() > 1:
                # Show restaurant selection page
                context = {'restaurants': restaurants, 'action': 'orders'}
                return render(request, 'restaurants/select_restaurant_for_action.html', context)
            else:
                restaurant = restaurants.first()
        else:
            restaurant = Restaurant.objects.filter(owner=request.user).first()
    
    if not restaurant:
        messages.error(request, 'No restaurant found.')
        return redirect('restaurants:restaurant_dashboard')
    
    # Get orders
    orders = Order.objects.filter(restaurant=restaurant).select_related('user').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 15)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'restaurant': restaurant,
        'orders': orders,
    }
    return render(request, 'restaurants/restaurant_orders.html', context)


@login_required
def restaurant_order_details(request, order_id):
    """Get order details for restaurant owner"""
    if request.user.role not in ['owner', 'admin']:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    try:
        # Get the order and verify it belongs to this restaurant owner
        if request.user.role == 'admin':
            order = get_object_or_404(Order, id=order_id)
        else:
            # Ensure the order belongs to one of the current owner's restaurants
            order = get_object_or_404(Order, id=order_id, restaurant__owner=request.user)
        
        # Get order items
        items = []
        for item in order.items.all():
            items.append({
                'meal_name': item.meal.name,
                'quantity': item.quantity,
                'price': float(item.price),
                'total': float(item.total_price)
            })
        
        order_data = {
            'id': order.id,
            'customer_name': order.user.get_full_name() or order.user.username,
            'customer_email': order.user.email,
            'status': order.status,
            'status_display': order.get_status_display(),
            'total_amount': float(order.total_amount),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M'),
            'items': items
        }
        
        return JsonResponse({'success': True, 'order': order_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required  
def restaurant_update_order_status(request, order_id):
    """Update order status for restaurant owner"""
    if request.user.role not in ['owner', 'admin']:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)
    
    try:
        # Get the order and verify it belongs to this restaurant owner
        if request.user.role == 'admin':
            order = get_object_or_404(Order, id=order_id)
        else:
            # Ensure the order belongs to one of the current owner's restaurants
            order = get_object_or_404(Order, id=order_id, restaurant__owner=request.user)
        
        import json
        try:
            data = json.loads(request.body)
        except:
            data = {}
        
        new_status = data.get('status')
        
        # Validate status transitions for restaurant owners
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['preparing', 'cancelled'],
            'preparing': ['ready', 'cancelled']
        }
        
        if order.status not in valid_transitions:
            return JsonResponse({'success': False, 'error': f'Cannot update order from {order.status} status'}, status=400)
        
        if new_status not in valid_transitions[order.status]:
            return JsonResponse({'success': False, 'error': f'Invalid status transition from {order.status} to {new_status}'}, status=400)
        
        order.status = new_status
        order.save()
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'status': order.status,
            'status_display': order.get_status_display()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def restaurant_detail(request, restaurant_id):
    """Public restaurant detail page for customers"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Get available meals for this restaurant
    meals = Meal.objects.filter(restaurant=restaurant, is_available=True).order_by('name')
    
    # Get restaurant statistics
    total_meals = meals.count()
    total_orders = Order.objects.filter(restaurant=restaurant).count()
    
    # Calculate average rating (mock data for now)
    avg_rating = 4.5  # This would come from a review system
    
    # Get similar restaurants (exclude current one)
    similar_restaurants = Restaurant.objects.exclude(id=restaurant_id)[:3]
    
    context = {
        'restaurant': restaurant,
        'meals': meals,
        'total_meals': total_meals,
        'total_orders': total_orders,
        'avg_rating': avg_rating,
        'similar_restaurants': similar_restaurants,
    }
    return render(request, 'restaurants/restaurant_detail.html', context)