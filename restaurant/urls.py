from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    # Авторизация
    path('', views.login_page, name='login'),
    path('api/login/', views.api_login, name='api_login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Официант
    path('waiter/', views.waiter_hall, name='waiter_hall'),
    path('api/tables/', views.api_tables, name='api_tables'),
    path('api/dishes/', views.api_dishes, name='api_dishes'),
    path('api/orders/create/', views.api_create_order, name='api_create_order'),
    path('api/orders/<int:order_id>/serve/', views.api_serve_order, name='api_serve_order'),
    path('api/orders/<int:order_id>/pay/', views.api_pay_order, name='api_pay_order'),
    
    # Кухня
    path('kitchen/', views.kitchen_view, name='kitchen'),
    path('api/kitchen/orders/', views.api_kitchen_orders, name='api_kitchen_orders'),
    path('api/kitchen/item/<int:item_id>/status/', views.api_update_item_status, name='api_update_item_status'),
    path('api/kitchen/order/<int:order_id>/ready/', views.api_mark_order_ready, name='api_mark_order_ready'),
    
    # Админ-панель
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    
    # Отчёты
    path('reports/', views.reports_view, name='reports'),
    path('api/reports/', views.api_reports, name='api_reports'),
    path('api/reports/export/orders/', views.export_orders_excel, name='export_orders'),
    path('api/reports/export/dishes/', views.export_dishes_excel, name='export_dishes'),
    
    # Чек
    path('receipt/<int:order_id>/', views.receipt_view, name='receipt'),
]
