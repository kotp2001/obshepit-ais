from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField('Название категории', max_length=100)
    icon = models.CharField('Иконка (emoji)', max_length=10, default='🍽️')
    order = models.PositiveSmallIntegerField('Порядок отображения', default=0)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order']
    
    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField('Название блюда', max_length=200)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField(
        'Цена', 
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='dishes',
        verbose_name='Категория'
    )
    image = models.ImageField('Изображение', upload_to='dishes/', blank=True, null=True)
    is_available = models.BooleanField('Доступно', default=True)
    preparation_time = models.PositiveSmallIntegerField('Время приготовления (мин)', default=15)
    
    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['category__order', 'name']
    
    def __str__(self):
        return f'{self.name} — {self.price} ₽'


class Table(models.Model):
    STATUS_CHOICES = [
        ('free', 'Свободен'),
        ('occupied', 'Занят'),
        ('reserved', 'Забронирован'),
    ]
    
    number = models.PositiveSmallIntegerField('Номер стола', unique=True)
    seats = models.PositiveSmallIntegerField('Количество мест', default=2)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='free')
    position_x = models.DecimalField('Позиция X (%)', max_digits=5, decimal_places=2, default=0)
    position_y = models.DecimalField('Позиция Y (%)', max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Стол'
        verbose_name_plural = 'Столы'
        ordering = ['number']
    
    def __str__(self):
        return f'Стол №{self.number} ({self.get_status_display()})'


class Order(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('ready', 'Готов к выдаче'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменён'),
    ]
    
    PAYMENT_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Банковская карта'),
        ('qr', 'QR-код'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.PROTECT, verbose_name='Стол')
    status = models.CharField('Статус заказа', max_length=20, choices=STATUS_CHOICES, default='active')
    payment_method = models.CharField('Способ оплаты', max_length=20, choices=PAYMENT_CHOICES, blank=True, null=True)
    total_amount = models.DecimalField('Итоговая сумма', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Заказ #{self.id} — Стол {self.table.number}'


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('cooking', 'Готовится'),
        ('ready', 'Готов'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name='Заказ')
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, verbose_name='Блюдо')
    quantity = models.PositiveSmallIntegerField('Количество', default=1)
    price = models.DecimalField('Цена позиции', max_digits=8, decimal_places=2)
    status = models.CharField('Статус приготовления', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('Время добавления', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
    
    def __str__(self):
        return f'{self.dish.name} × {self.quantity}'


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Выполнено'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.PROTECT, verbose_name='Стол')
    guest_name = models.CharField('Имя гостя', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    booking_time = models.DateTimeField('Время бронирования')
    guests_count = models.PositiveSmallIntegerField('Количество гостей', default=2)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField('Примечания', blank=True)
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-booking_time']
    
    def __str__(self):
        return f'{self.guest_name} — Стол {self.table.number} ({self.booking_time})'


class MaintenanceLog(models.Model):
    """Журнал технического обслуживания (Приложение Б)"""
    date = models.DateField('Дата проведения', auto_now_add=True)
    work_description = models.TextField('Проведённая работа')
    performed_by = models.CharField('Выполнил', max_length=100)
    signature = models.CharField('Подпись', max_length=50, blank=True)
    notes = models.TextField('Примечания', blank=True)
    
    class Meta:
        verbose_name = 'Запись журнала ТО'
        verbose_name_plural = 'Журнал технического обслуживания'
        ordering = ['-date']
    
    def __str__(self):
        return f'{self.date} — {self.work_description[:50]}'


class Employee(models.Model):
    """Модель сотрудника для привязки роли к пользователю Django"""
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('waiter', 'Официант'),
        ('cook', 'Повар'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Пользователь',
        related_name='employee'
    )
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    hire_date = models.DateField('Дата приёма', auto_now_add=True)
    is_active = models.BooleanField('Активен', default=True)
    
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
    
    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
