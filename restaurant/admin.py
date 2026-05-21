from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Category, Dish, Table, Order, OrderItem, Booking, MaintenanceLog, Employee

# Отключаем кастомную админку Django Jazzmin если она мешает
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'order']
    list_editable = ['order']
    search_fields = ['name']
    ordering = ['order']

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name']
    list_editable = ['price', 'is_available']

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'seats', 'status', 'position_x', 'position_y']
    list_filter = ['status']
    list_editable = ['status', 'seats']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['dish', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'status', 'total_amount', 'created_at', 'payment_method']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['table__number', 'id']
    readonly_fields = ['created_at', 'updated_at', 'total_amount']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'dish', 'quantity', 'status', 'price']
    list_filter = ['status', 'order__created_at']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['table', 'guest_name', 'phone', 'booking_time', 'status', 'created_at']
    list_filter = ['status', 'booking_time']
    search_fields = ['guest_name', 'phone']

@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ['date', 'work_description', 'performed_by', 'signature']
    list_filter = ['date', 'performed_by']
    search_fields = ['work_description', 'notes']
    date_hierarchy = 'date'

# Кастомная настройка пользователя
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name = 'Данные сотрудника'
    verbose_name_plural = 'Данные сотрудника'

class CustomUserAdmin(UserAdmin):
    inlines = (EmployeeInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_employee_role']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'employee__role']
    
    def get_employee_role(self, obj):
        try:
            return obj.employee.role
        except Employee.DoesNotExist:
            return 'Нет роли'
    get_employee_role.short_description = 'Роль'

# Перерегистрируем User с нашей кастомной админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email', 'phone']

# Настройка заголовков админки
admin.site.site_header = 'АИС "Общепит" - Панель администратора'
admin.site.site_title = 'АИС Общепит'
admin.site.index_title = 'Управление системой'
