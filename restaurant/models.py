from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.IntegerField(default=0, help_text="Порядок отображения")
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name

class Dish(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=0)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='dishes')
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    
    class Meta:
        ordering = ['category__order', 'name']
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
    
    def __str__(self):
        return f"{self.name} — {self.price} ₽"

class Table(models.Model):
    STATUS_CHOICES = [
        ('free', 'Свободен'),
        ('occupied', 'Занят'),
        ('reserved', 'Забронирован'),
    ]
    
    number = models.IntegerField(unique=True)
    seats = models.IntegerField(help_text="Количество мест")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='free')
    
    class Meta:
        ordering = ['number']
        verbose_name = 'Стол'
        verbose_name_plural = 'Столы'
    
    def __str__(self):
        return f"Стол №{self.number} ({self.seats} мест)"

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('cooking', 'Готовится'),
        ('ready', 'Готов'),
        ('served', 'Подан'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменён'),
    ]
    
    PAYMENT_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('qr', 'QR-код'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.PROTECT, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    guests_count = models.IntegerField(default=1)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    
    def __str__(self):
        return f"Заказ #{self.id} (Стол {self.table.number})"
    
    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('cooking', 'Готовится'),
        ('ready', 'Готов'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=0)  # цена на момент заказа
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_cooking_at = models.DateTimeField(blank=True, null=True)
    ready_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'
    
    def __str__(self):
        return f"{self.dish.name} × {self.quantity}"
    
    def get_subtotal(self):
        return self.price * self.quantity
