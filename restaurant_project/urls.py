from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from restaurant import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('waiter/hall/', views.waiter_hall, name='waiter_hall'),
    path('waiter/order/<int:table_id>/', views.create_order, name='create_order'),
    path('waiter/order/<int:order_id>/pay/', views.pay_order, name='pay_order'),
    path('waiter/order/<int:order_id>/receipt/', views.order_receipt, name='order_receipt'),
    path('cook/kitchen/', views.kitchen_view, name='kitchen_view'),
    path('cook/order/<int:order_item_id>/status/', views.update_order_item_status, name='update_order_item_status'),
    path('cook/order/<int:order_id>/ready/', views.mark_order_ready, name='mark_order_ready'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('api/tables/', views.api_tables, name='api_tables'),
    path('api/menu/', views.api_menu, name='api_menu'),
    path('api/order/create/', views.api_create_order, name='api_create_order'),
    path('api/order/<int:order_id>/pay/', views.api_pay_order, name='api_pay_order'),
    path('api/order-item/<int:item_id>/status/', views.api_update_order_item_status, name='api_update_order_item_status'),
    path('help/', views.help_manual, name='help_manual'),
    path('regulations/', views.regulations, name='regulations'),
    path('maintenance-log/', views.maintenance_log_view, name='maintenance_log'),
    path('backup/', views.backup_view, name='backup'),
    path('export/orders/', views.export_orders_excel, name='export_orders'),
    path('export/dishes/', views.export_dishes_excel, name='export_dishes'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
