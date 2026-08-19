from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Order, OrderItem
from meals.models import Meal
import json
from admin_panel.decorators import delivery_required, delivery_forbidden
from django.db import models

# Create your views here.
@delivery_required
def delivery_dashboard(request):
    # Show ready orders for acceptance, and current delivery orders
    if request.user.role == 'admin':
        orders = Order.objects.filter(status__in=['ready', 'picked_up', 'in_transit'])
    elif request.user.role == 'delivery':
        orders = Order.objects.filter(status__in=['ready', 'picked_up', 'in_transit'])
    else:
        return render(request, 'orders/access_denied.html')
    
    return render(request, 'orders/delivery_dashboard.html', {'orders': orders})


@login_required
def delivery_orders_poll(request):
    """Lightweight polling endpoint for delivery users to fetch available orders."""
    if request.user.role not in ['delivery', 'admin']:
        return JsonResponse({'success': False, 'error': 'Forbidden'}, status=403)

    try:
        if request.user.role == 'admin':
            orders = Order.objects.filter(status__in=['ready', 'picked_up', 'in_transit']).order_by('-created_at')[:50]
        else:
            orders = Order.objects.filter(status__in=['ready', 'picked_up', 'in_transit']).order_by('-created_at')[:50]

        data = []
        for o in orders:
            data.append({
                'id': o.id,
                'status': o.status,
                'total_amount': float(o.total_amount),
                'created_at': o.created_at.isoformat() if hasattr(o.created_at, 'isoformat') else str(o.created_at),
                'user': getattr(o.user, 'username', None),
                'restaurant': getattr(getattr(o, 'restaurant', None), 'name', None),
            })

        return JsonResponse({'success': True, 'orders': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def delivery_stats(request):
    """Stats for delivery dashboard cards. Uses existing statuses mapping.
    - Pending Orders: orders with status 'confirmed'
    - Completed Today: delivered today
    - In Transit: orders with status 'ready' (proxy for picked up/on the way)
    - Earnings Today: sum of delivered today total_amount
    Admin sees across platform; Delivery sees confirmed/ready/delivered.
    """
    if request.user.role not in ['delivery', 'admin']:
        return JsonResponse({'success': False, 'error': 'Forbidden'}, status=403)
    try:
        from django.utils import timezone
        today = timezone.now().date()
        # For now the same scope for admin and delivery until assignment implemented
        base_qs = Order.objects.all()

        pending_count = base_qs.filter(status='ready').count()  # Orders ready for delivery pickup
        completed_today = base_qs.filter(status='delivered', updated_at__date=today).count()
        in_transit = base_qs.filter(status__in=['picked_up', 'in_transit']).count()  # Orders currently being delivered
        earnings_today = base_qs.filter(status='delivered', updated_at__date=today).aggregate(total=models.Sum('total_amount'))['total'] or 0

        return JsonResponse({
            'success': True,
            'stats': {
                'pending': pending_count,
                'completed_today': completed_today,
                'in_transit': in_transit,
                'earnings_today': float(earnings_today),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def delivery_accept_order(request, order_id):
    """Allow a delivery user to accept an order that is ready for pickup."""
    if request.user.role not in ['delivery', 'admin']:
        return JsonResponse({'success': False, 'error': 'Forbidden'}, status=403)

    try:
        order = get_object_or_404(Order, id=order_id)
        # Delivery can only accept orders that are ready (restaurant finished preparing)
        if order.status != 'ready':
            return JsonResponse({'success': False, 'error': 'Order must be ready for pickup before delivery can accept it'}, status=400)

        order.status = 'picked_up'
        order.save()
        return JsonResponse({'success': True, 'order_id': order.id, 'status': order.status})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def delivery_update_status(request, order_id):
    """Update order status by delivery or admin: picked_up → in_transit → delivered."""
    if request.user.role not in ['delivery', 'admin']:
        return JsonResponse({'success': False, 'error': 'Forbidden'}, status=403)
    try:
        order = get_object_or_404(Order, id=order_id)
        try:
            data = json.loads(request.body or '{}')
        except Exception:
            data = {}
        new_status = data.get('status')
        allowed = {'picked_up', 'in_transit', 'delivered'}
        if new_status not in allowed:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

        # Basic linear flow guard
        flow_index = {
            'confirmed': 0, 'preparing': 0,
            'picked_up': 1,
            'in_transit': 2,
            'delivered': 3
        }
        current_idx = flow_index.get(order.status, 0)
        target_idx = flow_index.get(new_status, 0)
        if target_idx < current_idx:
            return JsonResponse({'success': False, 'error': 'Cannot move status backwards'}, status=400)

        order.status = new_status
        order.save()
        return JsonResponse({'success': True, 'order_id': order.id, 'status': order.status})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def delivery_history(request):
    """Return recent delivered orders for delivery dashboard history."""
    if request.user.role not in ['delivery', 'admin']:
        return JsonResponse({'success': False, 'error': 'Forbidden'}, status=403)
    try:
        orders = Order.objects.filter(status='delivered').order_by('-updated_at')[:50]
        items = []
        for o in orders:
            items.append({
                'id': o.id,
                'user': getattr(o.user, 'username', None),
                'restaurant': getattr(getattr(o, 'restaurant', None), 'name', None),
                'total_amount': float(o.total_amount),
                'updated_at': o.updated_at.isoformat() if hasattr(o.updated_at, 'isoformat') else str(o.updated_at)
            })
        return JsonResponse({'success': True, 'orders': items})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def restaurant_update_status(request, order_id):
    """Allow restaurant owner to update order status from preparing to ready."""
    if request.user.role != 'owner':
        return JsonResponse({'success': False, 'error': 'Only restaurant owners can update order status'}, status=403)
    
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Verify the order belongs to this restaurant owner
        if not order.restaurant or order.restaurant.owner != request.user:
            return JsonResponse({'success': False, 'error': 'You can only update orders for your restaurant'}, status=403)
        
        try:
            data = json.loads(request.body or '{}')
        except Exception:
            data = {}
        
        new_status = data.get('status')
        
        # Restaurant owners can only transition from 'preparing' to 'ready'
        if order.status != 'preparing':
            return JsonResponse({'success': False, 'error': 'Order must be in preparing status to mark as ready'}, status=400)
        
        if new_status != 'ready':
            return JsonResponse({'success': False, 'error': 'Restaurant owners can only mark orders as ready'}, status=400)
        
        order.status = 'ready'
        order.save()
        
        return JsonResponse({
            'success': True, 
            'order_id': order.id, 
            'status': order.status,
            'status_display': order.get_status_display()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@delivery_forbidden
def cart_view(request):
    """Display shopping cart"""
    # Get cart items for the current user
    cart_items = OrderItem.objects.filter(order__user=request.user, order__status='pending')
    
    # Calculate cart total properly
    cart_total = 0
    for item in cart_items:
        cart_total += float(item.total_price)
    
    context = {
        'cart_items': cart_items,
        'cart_total': f"{cart_total:.2f}",
    }
    return render(request, 'orders/cart.html', context)


@login_required
@delivery_forbidden
def checkout_view(request):
    """Display checkout form"""
    # Get cart items for the current user
    cart_items = OrderItem.objects.filter(order__user=request.user, order__status='pending')
    cart_total = sum(item.total_price for item in cart_items)
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty. Add some items before checkout.')
        return redirect('meals:meal_list')
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@delivery_forbidden
def process_checkout(request):
    """Process checkout and create order"""
    if request.method == 'POST':
        # Get cart items
        cart_items = OrderItem.objects.filter(order__user=request.user, order__status='pending')
        
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('orders:cart')
        
        # (Form fields omitted for brevity; not used by current flow)
        
        # Calculate total
        total_amount = sum(item.total_price for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            restaurant=cart_items.first().meal.restaurant,
            status='confirmed',
            total_amount=total_amount
        )
        
        # Update cart items to belong to this order
        cart_items.update(order=order)
        
        # Store delivery information (you might want to create a separate model for this)
        # For now, we'll just redirect to success page
        
        messages.success(request, 'Order placed successfully!')
        return redirect('orders:checkout_success', order_id=order.id)
    
    return redirect('orders:checkout')


@login_required
def checkout_success(request, order_id):
    """Display checkout success page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/checkout_success.html', context)


@login_required
@require_http_methods(["POST"])
def update_cart_item(request, item_id):
    """Update cart item quantity via AJAX"""
    try:
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
        
        # Handle both FormData and JSON data
        if request.content_type == 'application/x-www-form-urlencoded' or 'multipart/form-data' in request.content_type:
            quantity = int(request.POST.get('quantity', 1))
        else:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        
        if 1 <= quantity <= 25:
            item.quantity = quantity
            item.save()
            
            # Calculate subtotal manually since total_price is a property
            subtotal = sum(float(order_item.price * order_item.quantity) for order_item in OrderItem.objects.filter(order=item.order))
            
            return JsonResponse({
                'success': True,
                'total_price': float(item.total_price),
                'subtotal': subtotal
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid quantity'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def remove_cart_item(request, item_id):
    """Remove item from cart via AJAX"""
    try:
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status='pending')
        order = item.order
        item.delete()
        
        # Update order total
        order.total_amount = sum(item.total_price for item in order.items.all())
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def cart_count(request):
    """Get cart item count for navigation"""
    count = OrderItem.objects.filter(order__user=request.user, order__status='pending').count()
    return JsonResponse({'count': count})


@login_required
def order_tracking(request, order_id):
    """Track order status"""
    # Allow access to order if:
    # 1. User owns the order, OR
    # 2. User is restaurant owner and order is from their restaurant, OR  
    # 3. User is admin
    try:
        if request.user.role == 'admin':
            # Admin can see any order
            order = get_object_or_404(Order, id=order_id)
        elif request.user.role == 'owner':
            # Restaurant owner can see orders from their restaurant or their own orders
            from restaurants.models import Restaurant
            restaurant = Restaurant.objects.filter(owner=request.user).first()
            order = get_object_or_404(Order, id=order_id)
            
            # Check if user owns the order OR order is from their restaurant
            if order.user != request.user and (not restaurant or order.restaurant != restaurant):
                raise PermissionError("You don't have permission to view this order")
        else:
            # Regular users can only see their own orders
            order = get_object_or_404(Order, id=order_id, user=request.user)
    except PermissionError:
        from django.http import Http404
        raise Http404("Order not found or you don't have permission to view it")
    
    # Calculate order statistics
    total_items = sum(item.quantity for item in order.items.all())
    
    # Check if current user is the restaurant owner of this order
    is_restaurant_owner = (
        request.user.role == 'owner' and 
        order.restaurant and 
        order.restaurant.owner == request.user
    )
    
    context = {
        'order': order,
        'total_items': total_items,
        'is_restaurant_owner': is_restaurant_owner,
    }
    return render(request, 'orders/order_tracking.html', context)
