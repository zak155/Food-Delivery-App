from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from .models import Meal, Favorite
from orders.models import Order, OrderItem
from admin_panel.decorators import delivery_forbidden

# Create your views here.
def meal_list(request):
    meals = Meal.objects.filter(is_available=True)
    restaurant = None
    
    # Filter by restaurant if specified
    restaurant_id = request.GET.get('restaurant')
    if restaurant_id:
        try:
            from restaurants.models import Restaurant
            restaurant = Restaurant.objects.get(id=restaurant_id)
            meals = meals.filter(restaurant=restaurant)
        except Restaurant.DoesNotExist:
            pass
    else:
        # If no restaurant filter, show random meals
        meals = meals.order_by('?')
    
    # Add favorite status for authenticated users
    if request.user.is_authenticated:
        favorite_meal_ids = set(
            Favorite.objects.filter(user=request.user, meal__in=meals)
            .values_list('meal_id', flat=True)
        )
        for meal in meals:
            meal.is_favorite = meal.id in favorite_meal_ids
    else:
        for meal in meals:
            meal.is_favorite = False
    
    # Pagination - 6 meals per page
    paginator = Paginator(meals, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'meals': page_obj,
        'restaurant': restaurant,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, "meals/meal_list.html", context)


@login_required
@delivery_forbidden
def meal_detail(request, meal_id):
    """Display meal detail page"""
    meal = get_object_or_404(Meal, id=meal_id)
    
    # Check if meal is in user's favorites
    is_favorite = Favorite.objects.filter(user=request.user, meal=meal).exists()
    meal.is_favorite = is_favorite
    
    context = {
        'meal': meal,
    }
    return render(request, 'meals/product_detail.html', context)


@login_required
@delivery_forbidden
def add_to_cart(request, meal_id):
    """Add meal to cart"""
    if request.method == 'POST':
        try:
            meal = get_object_or_404(Meal, id=meal_id)
            quantity = int(request.POST.get('quantity', 1))
            
            if not meal.is_available:
                return JsonResponse({'success': False, 'error': 'This meal is currently unavailable.'})
            
            if quantity < 1 or quantity > 25:
                return JsonResponse({'success': False, 'error': 'Quantity must be between 1 and 25.'})
            
            # Get or create pending order for user
            order, created = Order.objects.get_or_create(
                user=request.user,
                status='pending',
                defaults={'restaurant': meal.restaurant, 'total_amount': 0}
            )
            
            # Get or create order item
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                meal=meal,
                defaults={'quantity': quantity, 'price': meal.price}
            )
            
            if not created:
                order_item.quantity += quantity
                order_item.save()
            
            # Update order total
            order.total_amount = sum(item.total_price for item in order.items.all())
            order.save()
            
            return JsonResponse({'success': True, 'message': f'{meal.name} added to cart!'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, meal_id):
    """Add or remove meal from user's favorites"""
    try:
        meal = get_object_or_404(Meal, id=meal_id)
        user = request.user
        
        # Check if already favorited
        favorite, created = Favorite.objects.get_or_create(user=user, meal=meal)
        
        if created:
            # Added to favorites
            return JsonResponse({
                'success': True, 
                'action': 'added',
                'message': f'{meal.name} added to favorites!',
                'is_favorite': True
            })
        else:
            # Remove from favorites
            favorite.delete()
            return JsonResponse({
                'success': True, 
                'action': 'removed',
                'message': f'{meal.name} removed from favorites!',
                'is_favorite': False
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def user_favorites(request):
    """Display user's favorite meals"""
    favorites = Favorite.objects.filter(user=request.user).select_related('meal', 'meal__restaurant')
    meals = [favorite.meal for favorite in favorites]
    
    # Set is_favorite to True for all meals in favorites page
    for meal in meals:
        meal.is_favorite = True
    
    # Pagination for favorites
    paginator = Paginator(meals, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'meals': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'title': 'My Favorite Meals'
    }
    return render(request, "meals/meal_list.html", context)
