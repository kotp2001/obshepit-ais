from django.contrib import admin
from django.urls import path, include
from restaurant import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('menu/', views.menu_view, name='menu'),
    path('booking/', views.booking_view, name='booking'),
    path('waiter/', views.waiter_hall, name='waiter'),
    path('kitchen/', views.kitchen_view, name='kitchen'),
    path('reports/', views.reports_view, name='reports'),
    path('api/', include('restaurant.urls')),
]
