from .models import PlatformSettings

def platform_settings(request):
    """Add platform settings to all templates"""
    try:
        settings = PlatformSettings.get_settings()
        return {
            'platform_settings': settings,
            'site_name': settings.site_name,
            'site_description': settings.site_description,
            'site_logo': settings.site_logo,
            'site_favicon': settings.site_favicon,
            'contact_email': settings.contact_email,
            'support_phone': settings.support_phone,
            'business_hours': settings.business_hours,
            'company_address': settings.company_address,
            'default_delivery_fee': settings.default_delivery_fee,
            'free_delivery_threshold': settings.free_delivery_threshold,
            'tax_rate': settings.tax_rate,
            'allow_registration': settings.allow_registration,
            'allow_restaurant_registration': settings.allow_restaurant_registration,
            'maintenance_mode': settings.maintenance_mode,
            'facebook_url': settings.facebook_url,
            'twitter_url': settings.twitter_url,
            'instagram_url': settings.instagram_url,
            'meta_title': settings.meta_title,
            'meta_description': settings.meta_description,
            'meta_keywords': settings.meta_keywords,
        }
    except Exception:
        # Return default values if settings don't exist
        return {
            'platform_settings': None,
            'site_name': 'FoodOrdering',
            'site_description': 'Order delicious meals from top restaurants',
            'site_logo': None,
            'site_favicon': None,
            'contact_email': 'support@foodordering.com',
            'support_phone': '+1 (555) 123-4567',
            'business_hours': 'Mon-Sun: 9:00 AM - 10:00 PM',
            'company_address': '123 Foodie Lane, Culinary City, FO 12345',
            'default_delivery_fee': 5.00,
            'free_delivery_threshold': 50.00,
            'tax_rate': 0.08,
            'allow_registration': True,
            'allow_restaurant_registration': True,
            'maintenance_mode': False,
            'facebook_url': '',
            'twitter_url': '',
            'instagram_url': '',
            'meta_title': 'FoodOrdering - Delicious Food Delivered',
            'meta_description': 'Order delicious food online from top restaurants. Fast delivery, fresh ingredients, great taste.',
            'meta_keywords': 'food delivery, online food, order food, restaurants, meals',
        }
