from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('simple-admin-dashboard/', views.simple_admin_dashboard_view, name='simple_admin_dashboard'),
    path('business-registration/', views.business_registration_view, name='business_registration'),
    path('validate-email/', views.validate_email, name='validate_email'),
    path('validate-restaurant-name/', views.validate_restaurant_name, name='validate_restaurant_name'),
    path('restaurants/', views.all_restaurants_view, name='all_restaurants'),
]
