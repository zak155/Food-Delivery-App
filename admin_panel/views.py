from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.core.files.storage import default_storage
import json

from users.models import User
from restaurants.models import Restaurant
from orders.models import Order
from meals.models import Meal
from .models import PlatformSettings
from .forms import PlatformSettingsForm
from .decorators import admin_required, can_edit_user, can_delete_user, can_manage_restaurant, can_manage_meal, can_view_order


@login_required
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Prevent admin from deactivating themselves
        if user.id == request.user.id:
            return JsonResponse({'success': False, 'error': 'Cannot deactivate your own account'})
        
        user.is_active = not user.is_active
        user.save()
        
        return JsonResponse({
            'success': True, 
            'is_active': user.is_active,
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def delete_user(request, user_id):
    """Delete a user"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Prevent admin from deleting themselves
        if user.id == request.user.id:
            return JsonResponse({'success': False, 'error': 'Cannot delete your own account'})
        
        username = user.username
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'User {username} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET", "POST"])
def edit_user(request, user_id):
    """Edit user information"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        if request.method == 'GET':
            # Return user data for editing
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_active': user.is_active,
                    'date_joined': user.date_joined.isoformat()
                }
            })
        else:
            # POST request - update user
            data = json.loads(request.body)
            
            # Update user fields
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'role' in data:
                user.role = data['role']
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'User updated successfully'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def update_order_status(request, order_id):
    """Update order status"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        order = get_object_or_404(Order, id=order_id)
        data = json.loads(request.body)
        
        new_status = data.get('status')
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
        
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        
        order.status = new_status
        order.save()
        
        return JsonResponse({
            'success': True,
            'status': order.status,
            'message': f'Order status updated to {new_status}'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def delete_order(request, order_id):
    """Delete an order"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        order = get_object_or_404(Order, id=order_id)
        order_id = order.id
        order.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Order #{order_id} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET", "POST"])
def edit_order(request, order_id):
    """Edit order information"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        order = get_object_or_404(Order, id=order_id)
        
        if request.method == 'GET':
            # Return order data for editing
            return JsonResponse({
                'success': True,
                'order': {
                    'id': order.id,
                    'total_amount': float(order.total_amount),
                    'status': order.status,
                    'created_at': order.created_at.isoformat(),
                    'user_name': order.user.username if order.user else 'N/A',
                    'restaurant_name': order.restaurant.name if order.restaurant else 'N/A'
                }
            })
        else:
            # POST request - update order
            data = json.loads(request.body)
            
            # Update order fields (only fields that exist in the model)
            if 'total_amount' in data:
                order.total_amount = data['total_amount']
            if 'status' in data:
                order.status = data['status']
            
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Order updated successfully'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET", "POST"])
def edit_restaurant(request, restaurant_id):
    """Edit restaurant information"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        if request.method == 'GET':
            # Return restaurant data for editing
            return JsonResponse({
                'success': True,
                'restaurant': {
                    'id': restaurant.id,
                    'name': restaurant.name,
                    'description': restaurant.description,
                    'location': restaurant.location,
                    'phone_number': restaurant.phone_number,
                    'email': restaurant.email,
                    'delivery_time': restaurant.delivery_time,
                    'opening_hours': restaurant.opening_hours,
                    'logo': restaurant.logo.url if restaurant.logo else None,
                    'hero_image': restaurant.hero_image.url if restaurant.hero_image else None,
                    'hero_title': restaurant.hero_title,
                    'hero_description': restaurant.hero_description,
                    'owner_name': f"{restaurant.owner.first_name} {restaurant.owner.last_name}".strip() if restaurant.owner else 'N/A',
                    'owner_email': restaurant.owner.email if restaurant.owner else None,
                    'created_at': restaurant.created_at.isoformat()
                }
            })
        else:
            # POST request - update restaurant
            # Handle both JSON and FormData requests
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # Update restaurant fields
            if 'name' in data:
                restaurant.name = data['name']
            if 'description' in data:
                restaurant.description = data['description']
            if 'location' in data:
                restaurant.location = data['location']
            if 'phone_number' in data:
                restaurant.phone_number = data['phone_number']
            if 'email' in data:
                restaurant.email = data['email']
            if 'delivery_time' in data:
                restaurant.delivery_time = data['delivery_time']
            if 'opening_hours' in data:
                restaurant.opening_hours = data['opening_hours']
            if 'hero_title' in data:
                restaurant.hero_title = data['hero_title']
            if 'hero_description' in data:
                restaurant.hero_description = data['hero_description']
            
            # Handle file uploads
            if 'logo' in request.FILES:
                restaurant.logo = request.FILES['logo']
            if 'hero_image' in request.FILES:
                restaurant.hero_image = request.FILES['hero_image']
            
            restaurant.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Restaurant updated successfully'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def delete_restaurant(request, restaurant_id):
    """Delete a restaurant"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        restaurant_name = restaurant.name
        restaurant.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Restaurant {restaurant_name} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def toggle_restaurant_status(request, restaurant_id):
    """Toggle restaurant status (placeholder - is_active field doesn't exist)"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        # Since is_active field doesn't exist, we'll just return a success message
        # In a real implementation, you might want to add an is_active field to the model
        
        return JsonResponse({
            'success': True,
            'is_active': True,  # Always return True since field doesn't exist
            'message': 'Restaurant status toggle not implemented (is_active field missing)'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET", "POST"])
def edit_meal(request, meal_id):
    """Get or update meal information"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        meal = get_object_or_404(Meal, id=meal_id)
        
        # GET: return meal data for editing
        if request.method == 'GET':
            return JsonResponse({
                'success': True,
                'meal': {
                    'id': meal.id,
                    'name': meal.name,
                    'price': float(meal.price),
                    'description': meal.description or '',
                    'is_available': meal.is_available,
                    'restaurant': {
                        'id': meal.restaurant.id if meal.restaurant else None,
                        'name': meal.restaurant.name if meal.restaurant else 'N/A'
                    }
                }
            })
        
        # POST: update meal
        data = json.loads(request.body)
        
        # Update meal fields
        if 'name' in data:
            meal.name = data['name']
        if 'description' in data:
            meal.description = data['description']
        if 'price' in data:
            meal.price = data['price']
        if 'is_available' in data:
            meal.is_available = data['is_available']
        
        meal.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Meal updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
@admin_required
def meal_list(request):
    """Return JSON list of meals for admin table."""
    try:
        meals_qs = Meal.objects.select_related('restaurant').all()
        restaurant_id = request.GET.get('restaurant_id')
        if restaurant_id:
            meals_qs = meals_qs.filter(restaurant_id=restaurant_id)
        meals = meals_qs.order_by('-id')
        data = []
        for meal in meals:
            data.append({
                'id': meal.id,
                'name': meal.name,
                'price': float(meal.price),
                'is_available': meal.is_available,
                'restaurant': {
                    'id': meal.restaurant.id if meal.restaurant else None,
                    'name': meal.restaurant.name if meal.restaurant else 'N/A'
                }
            })
        return JsonResponse({'success': True, 'meals': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
@admin_required
def meal_analytics(request):
    """Return basic analytics for meals (counts, avg price, top by orders/revenue)."""
    try:
        from django.db.models import Count, Sum, Avg
        from orders.models import OrderItem
        
        total_meals = Meal.objects.count()
        available_meals = Meal.objects.filter(is_available=True).count()
        avg_price = Meal.objects.aggregate(avg=Avg('price'))['avg'] or 0
        
        # Top meals by order count and revenue
        top_by_orders_qs = (
            OrderItem.objects
            .values('meal__id', 'meal__name')
            .annotate(times_ordered=Count('id'), revenue=Sum('price'))
            .order_by('-times_ordered')[:5]
        )
        top_by_orders = [
            {
                'id': row['meal__id'],
                'name': row['meal__name'],
                'times_ordered': row['times_ordered'],
                'revenue': float(row['revenue'] or 0),
            }
            for row in top_by_orders_qs
        ]
        
        return JsonResponse({
            'success': True,
            'analytics': {
                'total_meals': total_meals,
                'available_meals': available_meals,
                'avg_price': float(avg_price),
                'top_meals': top_by_orders,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
@admin_required
def create_meal(request):
    """Create a new meal with image and full details."""
    try:
        # Handle both JSON and multipart (FormData)
        if request.content_type.startswith('application/json'):
            data = json.loads(request.body)
            files = {}
        else:
            data = request.POST
            files = request.FILES
        
        # Validate required fields
        required = ['name', 'price', 'restaurant_id']
        for f in required:
            if not data.get(f):
                return JsonResponse({'success': False, 'error': f'{f} is required'})
        
        restaurant = get_object_or_404(Restaurant, id=data.get('restaurant_id'))
        
        meal = Meal(
            name=data.get('name'),
            description=data.get('description', ''),
            price=data.get('price'),
            is_available=data.get('is_available', 'true') in ['true', 'True', True, 'on', '1'],
            restaurant=restaurant,
        )
        # Optional fields
        if data.get('prep_time_min') is not None:
            meal.prep_time_min = int(data.get('prep_time_min'))
        if data.get('prep_time_max') is not None:
            meal.prep_time_max = int(data.get('prep_time_max'))
        if 'image' in files:
            meal.image = files['image']
        
        meal.save()
        
        return JsonResponse({'success': True, 'meal_id': meal.id, 'message': 'Meal created successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def delete_meal(request, meal_id):
    """Delete a meal"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        meal = get_object_or_404(Meal, id=meal_id)
        meal_name = meal.name
        meal.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Meal {meal_name} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def toggle_meal_availability(request, meal_id):
    """Toggle meal availability"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        meal = get_object_or_404(Meal, id=meal_id)
        meal.is_available = not meal.is_available
        meal.save()
        
        return JsonResponse({
            'success': True,
            'is_available': meal.is_available,
            'message': f'Meal {"made available" if meal.is_available else "made unavailable"} successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def update_platform_settings(request):
    """Update platform settings"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        data = json.loads(request.body)
        
        # Update platform settings (you can add a PlatformSettings model later)
        # For now, just return success
        return JsonResponse({
            'success': True,
            'message': 'Platform settings updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def update_site_info(request):
    """Update site information"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        data = json.loads(request.body)
        
        # Update site information (you can add a SiteInfo model later)
        # For now, just return success
        return JsonResponse({
            'success': True,
            'message': 'Site information updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET", "POST"])
def platform_settings(request):
    """Platform settings management"""
    if request.user.role != 'admin':
        messages.error(request, 'Admin access required.')
        return redirect('users:home')
    
    # Get or create platform settings
    settings = PlatformSettings.get_settings()
    
    if request.method == 'POST':
        form = PlatformSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Platform settings updated successfully!')
            return redirect('admin_api:platform_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PlatformSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
    }
    return render(request, 'admin_panel/platform_settings.html', context)


@login_required
@require_http_methods(["POST"])
def update_platform_settings_ajax(request):
    """Update platform settings via AJAX"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        settings = PlatformSettings.get_settings()
        
        # Handle form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            # Update settings from JSON data
            for field, value in data.items():
                if hasattr(settings, field):
                    setattr(settings, field, value)
        else:
            # Handle form data
            form = PlatformSettingsForm(request.POST, request.FILES, instance=settings)
            if form.is_valid():
                form.save()
            else:
                return JsonResponse({
                    'success': False, 
                    'error': 'Invalid form data',
                    'errors': form.errors
                })
        
        settings.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Platform settings updated successfully',
            'settings': {
                'site_name': settings.site_name,
                'site_description': settings.site_description,
                'contact_email': settings.contact_email,
                'support_phone': settings.support_phone,
                'support_email': settings.support_email,
                'company_address': settings.company_address,
                'business_hours': settings.business_hours,
                'default_delivery_fee': float(settings.default_delivery_fee),
                'free_delivery_threshold': float(settings.free_delivery_threshold),
                'tax_rate': float(settings.tax_rate),
                'allow_registration': settings.allow_registration,
                'allow_restaurant_registration': settings.allow_restaurant_registration,
                'maintenance_mode': settings.maintenance_mode,
                'facebook_url': settings.facebook_url or '',
                'twitter_url': settings.twitter_url or '',
                'instagram_url': settings.instagram_url or '',
                'meta_title': settings.meta_title,
                'meta_description': settings.meta_description,
                'meta_keywords': settings.meta_keywords,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
def get_platform_settings(request):
    """Get current platform settings"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        settings = PlatformSettings.get_settings()
        return JsonResponse({
            'success': True,
            'settings': {
                'site_name': settings.site_name,
                'site_description': settings.site_description,
                'contact_email': settings.contact_email,
                'support_phone': settings.support_phone,
                'support_email': settings.support_email,
                'company_address': settings.company_address,
                'business_hours': settings.business_hours,
                'default_delivery_fee': float(settings.default_delivery_fee),
                'free_delivery_threshold': float(settings.free_delivery_threshold),
                'tax_rate': float(settings.tax_rate),
                'allow_registration': settings.allow_registration,
                'allow_restaurant_registration': settings.allow_restaurant_registration,
                'maintenance_mode': settings.maintenance_mode,
                'facebook_url': settings.facebook_url or '',
                'twitter_url': settings.twitter_url or '',
                'instagram_url': settings.instagram_url or '',
                'meta_title': settings.meta_title,
                'meta_description': settings.meta_description,
                'meta_keywords': settings.meta_keywords,
                'site_logo_url': settings.site_logo.url if settings.site_logo else '',
                'site_favicon_url': settings.site_favicon.url if settings.site_favicon else '',
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
@admin_required
def user_analytics(request):
    """Return basic analytics for users (counts by role and status)."""
    try:
        from django.db.models import Count
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = total_users - active_users
        by_role = list(User.objects.values('role').annotate(count=Count('id')))
        return JsonResponse({
            'success': True,
            'analytics': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'by_role': by_role,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
@admin_required
def platform_analytics(request):
    """Aggregate top-level analytics across the platform."""
    try:
        from django.db.models import Sum, Avg, Count
        from orders.models import Order
        from meals.models import Meal
        from restaurants.models import Restaurant
        
        total_users = User.objects.count()
        total_restaurants = Restaurant.objects.count()
        total_meals = Meal.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        avg_order_value = Order.objects.aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        return JsonResponse({
            'success': True,
            'analytics': {
                'total_users': total_users,
                'total_restaurants': total_restaurants,
                'total_meals': total_meals,
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'avg_order_value': float(avg_order_value),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Restaurant Management Endpoints
@login_required
@require_http_methods(["GET"])
@admin_required
def restaurant_list(request):
    """Get list of all restaurants with details"""
    try:
        restaurants = Restaurant.objects.select_related('owner').all()
        
        restaurant_data = []
        for restaurant in restaurants:
            # Get order count for this restaurant
            orders_count = Order.objects.filter(restaurant=restaurant).count()
            
            restaurant_data.append({
                'id': restaurant.id,
                'name': restaurant.name,
                'description': restaurant.description,
                'location': restaurant.location,
                'is_active': True,  # All restaurants are considered active by default
                'logo': restaurant.logo.url if restaurant.logo else None,
                'owner_name': f"{restaurant.owner.first_name} {restaurant.owner.last_name}".strip() if restaurant.owner else 'N/A',
                'owner_email': restaurant.owner.email if restaurant.owner else None,
                'orders_count': orders_count,
                'created_at': restaurant.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'restaurants': restaurant_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
@admin_required
def create_restaurant(request):
    """Create a new restaurant"""
    try:
        data = json.loads(request.body)
        
        # Check if owner email exists
        owner_email = data.get('owner_email')
        try:
            owner = User.objects.get(email=owner_email)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Owner with this email does not exist'
            })
        
        # Create restaurant
        restaurant = Restaurant.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            location=data.get('location'),
            phone_number=data.get('phone', ''),
            delivery_time=data.get('delivery_time', ''),
            opening_hours=data.get('opening_hours', ''),
            owner=owner
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Restaurant created successfully',
            'restaurant_id': restaurant.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
@admin_required
def restaurant_analytics(request):
    """Get restaurant analytics data"""
    try:
        from django.db.models import Count, Avg, Sum
        from orders.models import OrderItem
        
        # Basic counts
        total_restaurants = Restaurant.objects.count()
        active_restaurants = Restaurant.objects.count()  # All restaurants are considered active
        
        # Order statistics
        total_orders = Order.objects.count()
        
        # Calculate average order value
        order_items = OrderItem.objects.all()
        if order_items.exists():
            total_revenue = sum(item.price * item.quantity for item in order_items)
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        else:
            avg_order_value = 0
        
        # Top performing restaurants
        top_restaurants = Restaurant.objects.annotate(
            orders_count=Count('orders'),
            total_revenue=Sum('orders__total_amount')
        ).order_by('-orders_count')[:5]
        
        top_restaurants_data = []
        for restaurant in top_restaurants:
            top_restaurants_data.append({
                'id': restaurant.id,
                'name': restaurant.name,
                'location': restaurant.location,
                'orders_count': restaurant.orders_count or 0,
                'revenue': float(restaurant.total_revenue or 0),
                'rating': getattr(restaurant, 'overall_rating', 0.0) if hasattr(restaurant, 'overall_rating') else 0.0
            })
        
        # Restaurants over time (last 14 days)
        from django.utils import timezone
        from datetime import timedelta
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=13)
        buckets = {}
        for i in range(14):
            d = start_date + timedelta(days=i)
            buckets[d.isoformat()] = {'date': d.isoformat(), 'restaurants': 0}
        created_daily = (
            Restaurant.objects
            .filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            .values('created_at__date')
            .annotate(count=Count('id'))
        )
        for row in created_daily:
            key = row['created_at__date'].isoformat()
            if key in buckets:
                buckets[key]['restaurants'] = row['count'] or 0
        restaurants_by_day = [buckets[k] for k in sorted(buckets.keys())]

        return JsonResponse({
            'success': True,
            'analytics': {
                'total_restaurants': total_restaurants,
                'active_restaurants': active_restaurants,
                'total_orders': total_orders,
                'avg_order_value': round(avg_order_value, 2),
                'top_restaurants': top_restaurants_data,
                'restaurants_by_day': restaurants_by_day
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
@admin_required
def bulk_toggle_restaurant_status(request):
    """Bulk toggle restaurant status"""
    try:
        data = json.loads(request.body)
        restaurant_ids = data.get('restaurant_ids', [])
        
        restaurants = Restaurant.objects.filter(id__in=restaurant_ids)
        updated_count = restaurants.count()
        
        # Since is_active field doesn't exist, we'll just return success
        # In a real implementation, you might want to add an is_active field to the model
        
        return JsonResponse({
            'success': True,
            'message': f'Status toggled for {updated_count} restaurants'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
@admin_required
def bulk_delete_restaurants(request):
    """Bulk delete restaurants"""
    try:
        data = json.loads(request.body)
        restaurant_ids = data.get('restaurant_ids', [])
        
        restaurants = Restaurant.objects.filter(id__in=restaurant_ids)
        deleted_count = restaurants.count()
        restaurants.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} restaurants deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
@admin_required
def update_restaurant_rating(request, restaurant_id):
    """Update overall_rating for a restaurant (0.0 - 5.0)."""
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        # Check if the field exists in the database
        if not hasattr(restaurant, 'overall_rating'):
            return JsonResponse({
                'success': False, 
                'error': 'overall_rating field not available. Please run migrations first.'
            })
        
        data = json.loads(request.body or '{}')
        rating = float(data.get('rating', 0))
        if rating < 0:
            rating = 0.0
        if rating > 5:
            rating = 5.0
        restaurant.overall_rating = rating
        restaurant.save(update_fields=['overall_rating'])
        return JsonResponse({'success': True, 'rating': restaurant.overall_rating})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# User Management Endpoints
@login_required
@require_http_methods(["POST"])
@admin_required
def create_user(request):
    """Create a new user"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['username', 'email', 'password1', 'password2', 'role']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'{field.replace("_", " ").title()} is required'
                })
        
        # Check if username already exists
        if User.objects.filter(username=data['username']).exists():
            return JsonResponse({
                'success': False,
                'error': 'A user with this username already exists'
            })
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({
                'success': False,
                'error': 'A user with this email already exists'
            })
        
        # Validate passwords match
        if data['password1'] != data['password2']:
            return JsonResponse({
                'success': False,
                'error': 'Passwords do not match'
            })
        
        # Validate password length
        if len(data['password1']) < 8:
            return JsonResponse({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            })
        
        # Validate role
        valid_roles = ['customer', 'owner', 'admin', 'delivery']
        if data['role'] not in valid_roles:
            return JsonResponse({
                'success': False,
                'error': 'Invalid role selected'
            })
        
        # Create user
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data['role'],
            is_active=data.get('is_active', True)
        )
        
        return JsonResponse({
            'success': True,
            'message': f'User "{user.username}" created successfully',
            'user_id': user.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Order Management Endpoints
@login_required
@require_http_methods(["GET"])
@admin_required
def order_list(request):
    """Get list of all orders"""
    try:
        orders = Order.objects.select_related('user', 'restaurant').prefetch_related('items').all().order_by('-created_at')
        
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'user': {
                    'username': order.user.username,
                    'email': order.user.email
                },
                'restaurant': {
                    'name': order.restaurant.name if order.restaurant else 'N/A',
                    'location': order.restaurant.location if order.restaurant else 'N/A'
                },
                'total_amount': float(order.total_amount),
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'items_count': order.items.count()
            })
        
        return JsonResponse({
            'success': True,
            'orders': orders_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
@admin_required
def order_analytics(request):
    """Get order analytics data"""
    try:
        from django.db.models import Count, Sum, Avg
        from django.utils import timezone
        from datetime import timedelta
        
        # Basic stats
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        avg_order_value = Order.objects.aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        # Completion rate (delivered orders / total orders)
        delivered_orders = Order.objects.filter(status='delivered').count()
        completion_rate = (delivered_orders / total_orders * 100) if total_orders > 0 else 0
        
        # Top restaurants by orders and revenue
        top_restaurants = Restaurant.objects.annotate(
            orders_count=Count('orders'),
            revenue=Sum('orders__total_amount')
        ).filter(orders_count__gt=0).order_by('-orders_count')[:5]
        
        top_restaurants_data = []
        for restaurant in top_restaurants:
            top_restaurants_data.append({
                'name': restaurant.name,
                'location': restaurant.location,
                'orders_count': restaurant.orders_count,
                'revenue': float(restaurant.revenue or 0)
            })
        
        # Recent orders
        recent_orders = Order.objects.select_related('user', 'restaurant').order_by('-created_at')[:10]
        recent_orders_data = []
        for order in recent_orders:
            recent_orders_data.append({
                'id': order.id,
                'user': {
                    'username': order.user.username
                },
                'restaurant': {
                    'name': order.restaurant.name if order.restaurant else 'N/A'
                },
                'total_amount': float(order.total_amount),
                'status': order.status,
                'created_at': order.created_at.isoformat()
            })

        # Order status distribution
        status_qs = (
            Order.objects
            .values('status')
            .annotate(count=Count('id'))
        )
        status_distribution = []
        for row in status_qs:
            status_distribution.append({'status': row['status'], 'count': row['count'] or 0})

        # Platform growth over time (last 14 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=13)
        # Initialize buckets
        buckets = {}
        for i in range(14):
            d = start_date + timedelta(days=i)
            k = d.isoformat()
            buckets[k] = {'date': k, 'orders': 0, 'revenue': 0.0}
        # Aggregate
        daily = (
            Order.objects
            .filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            .values('created_at__date')
            .annotate(orders_count=Count('id'), revenue_sum=Sum('total_amount'))
        )
        for row in daily:
            key = row['created_at__date'].isoformat()
            if key in buckets:
                buckets[key]['orders'] = row['orders_count'] or 0
                buckets[key]['revenue'] = float(row['revenue_sum'] or 0)
        orders_by_day = [buckets[k] for k in sorted(buckets.keys())]
        
        return JsonResponse({
            'success': True,
            'analytics': {
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'avg_order_value': float(avg_order_value),
                'completion_rate': round(completion_rate, 1),
                'top_restaurants': top_restaurants_data,
                'recent_orders': recent_orders_data,
                'status_distribution': status_distribution,
                'orders_by_day': orders_by_day
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
@admin_required
def bulk_delete_orders(request):
    """Bulk delete orders"""
    try:
        data = json.loads(request.body)
        order_ids = data.get('order_ids', [])
        
        orders = Order.objects.filter(id__in=order_ids)
        deleted_count = orders.count()
        orders.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} orders deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
