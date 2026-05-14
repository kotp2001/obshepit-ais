import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from restaurant.models import Category, Dish, Table

User = get_user_model()

print("Создание миграций...")
call_command('makemigrations', 'restaurant', interactive=False)
print("Миграции созданы")

print("Применение миграций...")
call_command('migrate', interactive=False)
print("Миграции применены")

print("Создание суперпользователя...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Админ создан: admin/admin123")
else:
    print("Админ уже существует")

print("Заполнение тестовыми данными...")

if Category.objects.count() == 0:
    categories = [
        {'name': 'Салаты', 'icon': 'salad', 'order': 1},
        {'name': 'Горячие блюда', 'icon': 'hot', 'order': 2},
        {'name': 'Гарниры', 'icon': 'fries', 'order': 3},
        {'name': 'Напитки', 'icon': 'drink', 'order': 4},
        {'name': 'Десерты', 'icon': 'cake', 'order': 5},
    ]
    for cat in categories:
        Category.objects.create(**cat)
    print("Категории добавлены")

if Dish.objects.count() == 0:
    dishes = [
        {'name': 'Цезарь с курицей', 'price': 450, 'category_id': 1, 'description': 'С курицей, сухариками, соусом'},
        {'name': 'Греческий салат', 'price': 380, 'category_id': 1, 'description': 'Сыр фета, оливки, овощи'},
        {'name': 'Стейк из говядины', 'price': 890, 'category_id': 2, 'description': 'Мраморная говядина 250г'},
        {'name': 'Куриное филе на гриле', 'price': 420, 'category_id': 2, 'description': 'С овощами гриль'},
        {'name': 'Картофель фри', 'price': 150, 'category_id': 3, 'description': 'Хрустящий картофель'},
        {'name': 'Рис отварной', 'price': 120, 'category_id': 3, 'description': 'С маслом и зеленью'},
        {'name': 'Чай чёрный', 'price': 80, 'category_id': 4, 'description': 'Цейлонский чай'},
        {'name': 'Кофе американо', 'price': 120, 'category_id': 4, 'description': 'Свежесваренный кофе'},
        {'name': 'Чизкейк', 'price': 250, 'category_id': 5, 'description': 'Классический чизкейк'},
        {'name': 'Тирамису', 'price': 280, 'category_id': 5, 'description': 'Кофейный десерт'},
    ]
    for dish in dishes:
        Dish.objects.create(**dish)
    print("Блюда добавлены")

if Table.objects.count() == 0:
    tables = [
        {'number': 1, 'seats': 2, 'status': 'free', 'x_position': 100, 'y_position': 100},
        {'number': 2, 'seats': 2, 'status': 'free', 'x_position': 250, 'y_position': 100},
        {'number': 3, 'seats': 4, 'status': 'free', 'x_position': 400, 'y_position': 100},
        {'number': 4, 'seats': 4, 'status': 'free', 'x_position': 550, 'y_position': 100},
        {'number': 5, 'seats': 6, 'status': 'free', 'x_position': 150, 'y_position': 250},
        {'number': 6, 'seats': 8, 'status': 'free', 'x_position': 350, 'y_position': 250},
    ]
    for table in tables:
        Table.objects.create(**table)
    print("Столы добавлены")

print("Готово!")
