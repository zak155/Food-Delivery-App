from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined', 'restaurant_count')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 25
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom fields', {'fields': ('role',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    def restaurant_count(self, obj):
        """Display number of restaurants owned by this user"""
        count = obj.restaurants.count()
        if count > 0:
            url = reverse('admin:restaurants_restaurant_changelist') + f'?owner__id__exact={obj.id}'
            return format_html('<a href="{}">{} restaurant(s)</a>', url, count)
        return '0'
    restaurant_count.short_description = 'Restaurants'
    
    actions = ['make_active', 'make_inactive', 'change_role_to_customer']
    
    def make_active(self, request, queryset):
        """Bulk action to activate users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were successfully activated.')
    make_active.short_description = "Activate selected users"
    
    def make_inactive(self, request, queryset):
        """Bulk action to deactivate users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were successfully deactivated.')
    make_inactive.short_description = "Deactivate selected users"
    
    def change_role_to_customer(self, request, queryset):
        """Bulk action to change role to customer"""
        updated = queryset.update(role='customer')
        self.message_user(request, f'{updated} users were successfully changed to customer role.')
    change_role_to_customer.short_description = "Change role to customer"
