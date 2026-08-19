from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class PlatformSettings(models.Model):
    """Platform-wide settings that affect the entire website"""
    
    # Site Information
    site_name = models.CharField(max_length=100, default="FoodOrdering", help_text="The name of your platform")
    site_description = models.TextField(default="Your favorite food delivery platform", help_text="Brief description of your platform")
    site_logo = models.ImageField(upload_to='platform/logos/', null=True, blank=True, help_text="Platform logo")
    site_favicon = models.ImageField(upload_to='platform/favicons/', null=True, blank=True, help_text="Platform favicon")
    
    # Contact Information
    contact_email = models.EmailField(default="admin@foodordering.com", help_text="Main contact email")
    support_phone = models.CharField(max_length=20, default="+1 (555) 123-4567", help_text="Support phone number")
    support_email = models.EmailField(default="support@foodordering.com", help_text="Support email")
    
    # Business Information
    company_address = models.TextField(default="123 Food Street, City, State 12345", help_text="Company address")
    business_hours = models.CharField(max_length=100, default="Mon-Sun: 9:00 AM - 10:00 PM", help_text="Business hours")
    
    # Platform Configuration
    default_delivery_fee = models.DecimalField(max_digits=5, decimal_places=2, default=2.99, help_text="Default delivery fee")
    free_delivery_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=25.00, help_text="Minimum order for free delivery")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=8.5, help_text="Tax rate percentage")
    
    # Feature Toggles
    allow_registration = models.BooleanField(default=True, help_text="Allow new user registration")
    allow_restaurant_registration = models.BooleanField(default=True, help_text="Allow new restaurant registration")
    maintenance_mode = models.BooleanField(default=False, help_text="Enable maintenance mode")
    
    # Social Media
    facebook_url = models.URLField(blank=True, null=True, help_text="Facebook page URL")
    twitter_url = models.URLField(blank=True, null=True, help_text="Twitter profile URL")
    instagram_url = models.URLField(blank=True, null=True, help_text="Instagram profile URL")
    
    # SEO Settings
    meta_title = models.CharField(max_length=60, default="FoodOrdering - Delicious Food Delivery", help_text="SEO meta title")
    meta_description = models.TextField(default="Order delicious food from top restaurants in your area. Fast delivery, great taste!", help_text="SEO meta description")
    meta_keywords = models.CharField(max_length=200, default="food delivery, restaurant, order online", help_text="SEO meta keywords")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Platform Settings"
        verbose_name_plural = "Platform Settings"
    
    def __str__(self):
        return f"Platform Settings - {self.site_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and PlatformSettings.objects.exists():
            # If this is a new instance and one already exists, update the existing one
            existing = PlatformSettings.objects.first()
            for field in self._meta.fields:
                if field.name not in ['id', 'created_at', 'updated_at']:
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            return existing
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get the platform settings, creating default if none exist"""
        settings, created = cls.objects.get_or_create(
            defaults={
                'site_name': 'FoodOrdering',
                'site_description': 'Your favorite food delivery platform',
                'contact_email': 'admin@foodordering.com',
                'support_phone': '+1 (555) 123-4567',
                'support_email': 'support@foodordering.com',
                'company_address': '123 Food Street, City, State 12345',
                'business_hours': 'Mon-Sun: 9:00 AM - 10:00 PM',
                'default_delivery_fee': 2.99,
                'free_delivery_threshold': 25.00,
                'tax_rate': 8.5,
                'allow_registration': True,
                'allow_restaurant_registration': True,
                'maintenance_mode': False,
                'meta_title': 'FoodOrdering - Delicious Food Delivery',
                'meta_description': 'Order delicious food from top restaurants in your area. Fast delivery, great taste!',
                'meta_keywords': 'food delivery, restaurant, order online',
            }
        )
        return settings