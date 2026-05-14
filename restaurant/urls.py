from django.urls import path
from . import views

urlpatterns = [
    path('api/dishes/', views.api_dishes),
    path('api/categories/', views.api_categories),
    path('api/tables/', views.api_tables),
    path('api/orders/create/', views.api_create_order),
    path('api/orders/active/', views.api_active_orders),
    path('api/orders/update-item/', views.api_update_item_status),
    path('api/orders/pay/', views.api_pay_order),
    path('api/bookings/create/', views.api_create_booking),
    path('api/bookings/', views.api_bookings),
    path('api/reports/', views.api_reports),
]
