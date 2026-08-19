from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from restaurants.models import Restaurant
from meals.models import Meal

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)

class RestaurantSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Restaurant.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
        
class MealSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Meal.objects.filter(is_available=True)

    def lastmod(self, obj):
        return obj.updated_at
