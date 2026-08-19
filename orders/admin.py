from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from .models import Order, OrderItem

# Inline admin for order items
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('meal', 'quantity', 'price')
    readonly_fields = ()
    ordering = ('meal__name',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('meal')

# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'status', 'total_amount', 'item_count', 'created_at')
    list_filter = ('status', 'created_at', 'restaurant', 'user__role')
    search_fields = ('user__username', 'restaurant__name', 'id')
    ordering = ('-created_at',)
    list_per_page = 25
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'restaurant', 'status', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
    
    def item_count(self, obj):
        """Display number of items in this order"""
        count = obj.items.count()
        return f"{count} item(s)"
    item_count.short_description = 'Items'
    
    actions = ['mark_confirmed', 'mark_delivered', 'mark_cancelled']
    
    def mark_confirmed(self, request, queryset):
        """Bulk action to mark orders as confirmed"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} orders were successfully marked as confirmed.')
    mark_confirmed.short_description = "Mark selected orders as confirmed"
    
    def mark_delivered(self, request, queryset):
        """Bulk action to mark orders as delivered"""
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders were successfully marked as delivered.')
    mark_delivered.short_description = "Mark selected orders as delivered"
    
    def mark_cancelled(self, request, queryset):
        """Bulk action to mark orders as cancelled"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} orders were successfully marked as cancelled.')
    mark_cancelled.short_description = "Mark selected orders as cancelled"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'meal', 'quantity', 'price', 'calculated_total', 'created_at')
    list_filter = ('created_at', 'order__status', 'order__restaurant')
    search_fields = ('order__id', 'meal__name', 'order__user__username')
    ordering = ('-created_at',)
    list_per_page = 25
    
    def calculated_total(self, obj):
        """Calculate total price for this order item"""
        return f"${obj.price * obj.quantity:.2f}"
    calculated_total.short_description = 'Total Price'
