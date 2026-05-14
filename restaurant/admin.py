from django.contrib import admin
from .models import Category, Dish, Table, Order, OrderItem, Booking

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'order']
    list_editable = ['order']
    search_fields = ['name']

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_available']

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'seats', 'status']
    list_filter = ['status']
    list_editable = ['status', 'seats']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'waiter', 'created_at', 'status', 'total_amount']
    list_filter = ['status', 'created_at']
    search_fields = ['table__number']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'dish', 'quantity', 'price', 'status']
    list_filter = ['status']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'table', 'booking_date', 'booking_time', 'guests_count', 'status']
    list_filter = ['status', 'booking_date']
    search_fields = ['guest_name', 'guest_phone']
