from django.urls import path
from . import views
from .excel import export_orders_excel, export_popular_excel

urlpatterns = [
    # Главная страница (новая)
    path('', views.landing, name='landing'),
    
    # Страницы сайта
    path('menu/', views.menu_view, name='menu'),
    path('booking/', views.booking_view, name='booking'),
    path('waiter/', views.waiter_hall, name='waiter'),
    path('kitchen/', views.kitchen_view, name='kitchen'),
    path('reports/', views.reports_view, name='reports'),
    
    # Панель администратора
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    
    # API авторизации
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    
    # API endpoints
    path('api/dishes/', views.api_dishes, name='api_dishes'),
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/tables/', views.api_tables, name='api_tables'),
    path('api/orders/create/', views.api_create_order, name='api_create_order'),
    path('api/orders/active/', views.api_active_orders, name='api_active_orders'),
    path('api/orders/update-item/', views.api_update_item_status, name='api_update_item'),
    path('api/orders/pay/', views.api_pay_order, name='api_pay_order'),
    path('api/bookings/create/', views.api_create_booking, name='api_create_booking'),
    path('api/bookings/', views.api_bookings, name='api_bookings'),
    path('api/reports/', views.api_reports, name='api_reports'),
    # Export
    path('export/orders/', export_orders_excel, name='export_orders'),
    path('export/popular/', export_popular_excel, name='export_popular'),

    path('api/orders/mark-ready/', views.api_mark_order_ready, name='api_mark_ready'),
    path('api/orders/take/', views.api_take_order, name='api_take_order'),
    path('api/orders/pay/', views.api_pay_order, name='api_pay_order'),
    path('api/orders/receipt/<int:order_id>/', views.api_order_receipt, name='api_receipt'),
]
