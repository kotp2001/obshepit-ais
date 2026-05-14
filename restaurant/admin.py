from django.contrib import admin
from .models import Category, Dish, Table, Order, OrderItem, Booking

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'order']
    list_editable = ['order']

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name']

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'seats', 'status']
    list_editable = ['status']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'created_at', 'status', 'total_amount']
    list_filter = ['status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'dish', 'quantity', 'status']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'table', 'booking_date', 'booking_time', 'status']
    list_filter = ['status', 'booking_date']
