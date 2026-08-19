"""
URL configuration for Food_Ordering_Platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView

from django.contrib import sitemaps
from django.contrib.sitemaps.views import sitemap
from .sitemap import StaticViewSitemap, RestaurantSitemap, MealSitemap


def redirect_to_home(request):
    return redirect('users:home')

sitemaps_dict = {
    'static': StaticViewSitemap,
    'restaurants': RestaurantSitemap,
    'meals': MealSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path("admin-api/", include("admin_panel.urls", namespace="admin_api")),
    path("", redirect_to_home, name="home"),
    path("users/", include("users.urls", namespace="users")),
    path("meals/", include("meals.urls", namespace="meals")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("restaurants/", include("restaurants.urls", namespace="restaurants")),
    path('google8c6d73d201086114.html', TemplateView.as_view(template_name='google8c6d73d201086114.html')),

    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps_dict}, name='sitemap'),
]


# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
