from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, F
from datetime import datetime, timedelta
import json
import openpyxl
from openpyxl.styles import Font, Alignment
from .models import Table, Dish, Category, Order, OrderItem

# === АВТОРИЗАЦИЯ ===

HARDCODED_USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'waiter': {'password': 'waiter123', 'role': 'waiter'},
    'chef': {'password': 'chef123', 'role': 'chef'},
}

def login_page(request):
    if request.session.get('user_role'):
        return redirect_by_role(request.session['user_role'])
    return render(request, 'restaurant/login.html')

def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '')
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    user = HARDCODED_USERS.get(username)
    if user and user['password'] == password:
        request.session['user_role'] = user['role']
        request.session['username'] = username
        request.session.save()
        return JsonResponse({'success': True, 'role': user['role']})
    
    return JsonResponse({'error': 'Неверный логин или пароль'}, status=401)

def logout_view(request):
    request.session.flush()
    return redirect('restaurant:login')

def redirect_by_role(role):
    mapping = {'admin': 'restaurant:admin_panel', 'waiter': 'restaurant:waiter_hall', 'chef': 'restaurant:kitchen'}
    return redirect(mapping.get(role, 'restaurant:login'))

def role_required(*roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            role = request.session.get('user_role')
            if not role or role not in roles:
                return redirect('restaurant:login')
            return view_func(request, *args, **kwargs)
        wrapper.__name__ = view_func.__name__
        return wrapper
    return decorator

# === ОФИЦИАНТ ===

@role_required('waiter')
def waiter_hall(request):
    return render(request, 'restaurant/waiter_hall.html')

def api_tables(request):
    tables = Table.objects.all().values('id', 'number', 'seats', 'status')
    return JsonResponse({'tables': list(tables)})

def api_dishes(request):
    categories = Category.objects.prefetch_related('dishes').filter(dishes__is_available=True).distinct()
    data = []
    for cat in categories:
        dishes = [
            {'id': d.id, 'name': d.name, 'price': int(d.price), 'description': d.description}
            for d in cat.dishes.filter(is_available=True)
        ]
        if dishes:
            data.append({'id': cat.id, 'name': cat.name, 'dishes': dishes})
    return JsonResponse({'categories': data})

def api_create_order(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        table_id = data.get('table_id')
        guests = data.get('guests', 1)
        items = data.get('items', [])
        
        if not table_id or not items:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        table = get_object_or_404(Table, id=table_id)
        if table.status != 'free':
            return JsonResponse({'error': 'Стол уже занят'}, status=409)
        
        order = Order.objects.create(table=table, guests_count=guests, status='new')
        
        for item in items:
            dish = get_object_or_404(Dish, id=item['dish_id'])
            OrderItem.objects.create(
                order=order,
                dish=dish,
                quantity=item['quantity'],
                price=dish.price
            )
        
        table.status = 'occupied'
        table.save()
        
        return JsonResponse({'success': True, 'order_id': order.id})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@role_required('waiter')
def api_serve_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'ready':
        return JsonResponse({'error': 'Заказ ещё не готов'}, status=400)
    order.status = 'served'
    order.save()
    return JsonResponse({'success': True})

@role_required('waiter')
def api_pay_order(request, order_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    order = get_object_or_404(Order, id=order_id)
    try:
        data = json.loads(request.body)
        payment_method = data.get('payment_method')
        if payment_method not in ['cash', 'card', 'qr']:
            return JsonResponse({'error': 'Invalid payment method'}, status=400)
        
        order.payment_method = payment_method
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        
        order.table.status = 'free'
        order.table.save()
        
        return JsonResponse({'success': True, 'receipt_url': f'/receipt/{order.id}/'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# === КУХНЯ ===

@role_required('chef')
def kitchen_view(request):
    return render(request, 'restaurant/kitchen.html')

def api_kitchen_orders(request):
    orders = Order.objects.filter(status__in=['new', 'cooking', 'ready']).prefetch_related(
        'items__dish'
    ).order_by('created_at')
    
    data = []
    for order in orders:
        items = [
            {
                'id': item.id,
                'dish_name': item.dish.name,
                'quantity': item.quantity,
                'status': item.status,
                'price': int(item.price)
            }
            for item in order.items.all()
        ]
        data.append({
            'id': order.id,
            'table_number': order.table.number,
            'created_at': order.created_at.strftime('%H:%M'),
            'status': order.status,
            'items': items,
            'all_ready': all(i['status'] == 'ready' for i in items)
        })
    
    return JsonResponse({'orders': data})

def api_update_item_status(request, item_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    item = get_object_or_404(OrderItem, id=item_id)
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'start':
            if item.status != 'pending':
                return JsonResponse({'error': 'Нельзя начать'}, status=400)
            item.status = 'cooking'
            item.started_cooking_at = timezone.now()
            if item.order.status == 'new':
                item.order.status = 'cooking'
                item.order.save()
        
        elif action == 'finish':
            if item.status != 'cooking':
                return JsonResponse({'error': 'Нельзя завершить'}, status=400)
            item.status = 'ready'
            item.ready_at = timezone.now()
        
        else:
            return JsonResponse({'error': 'Unknown action'}, status=400)
        
        item.save()
        return JsonResponse({'success': True, 'new_status': item.status})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_mark_order_ready(request, order_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    
    if not all(item.status == 'ready' for item in items):
        return JsonResponse({'error': 'Не все блюда готовы'}, status=400)
    
    order.status = 'ready'
    order.save()
    return JsonResponse({'success': True})

# === АДМИН ===

@role_required('admin')
def admin_panel(request):
    stats = {
        'total_orders': Order.objects.count(),
        'total_tables': Table.objects.count(),
        'total_dishes': Dish.objects.filter(is_available=True).count(),
    }
    return render(request, 'restaurant/admin_panel.html', {'stats': stats})

# === ОТЧЁТЫ ===

@role_required('admin')
def reports_view(request):
    return render(request, 'restaurant/reports.html')

def api_reports(request):
    period = request.GET.get('period', 'week')
    
    now = timezone.now()
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start = now - timedelta(days=7)
    elif period == 'month':
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=7)
    
    paid_orders = Order.objects.filter(
        status='paid', 
        paid_at__gte=start,
        paid_at__lte=now
    )
    
    total_revenue = paid_orders.aggregate(total=Sum('items__price__field'))['total'] or 0
    # Упрощённый расчёт: пересчитаем через Python
    total_revenue = sum(
        sum(item.price * item.quantity for item in order.items.all())
        for order in paid_orders
    )
    
    orders_count = paid_orders.count()
    avg_check = total_revenue / orders_count if orders_count else 0
    
    # Данные по дням
    daily_data = []
    for i in range(7 if period != 'month' else 30):
        day = (start + timedelta(days=i)).date()
        day_orders = [o for o in paid_orders if o.paid_at.date() == day]
        revenue = sum(
            sum(item.price * item.quantity for item in o.items.all())
            for o in day_orders
        )
        daily_data.append({'date': day.strftime('%d.%m'), 'revenue': revenue})
    
    # Топ блюд
    dish_stats = {}
    for order in paid_orders:
        for item in order.items.all():
            key = item.dish.name
            dish_stats[key] = dish_stats.get(key, 0) + item.quantity
    
    top_dishes = sorted(
        [{'name': k, 'count': v} for k, v in dish_stats.items()],
        key=lambda x: -x['count']
    )[:10]
    
    return JsonResponse({
        'total_revenue': int(total_revenue),
        'orders_count': orders_count,
        'avg_check': round(avg_check, 2),
        'daily_data': daily_data,
        'top_dishes': top_dishes
    })

def export_orders_excel(request):
    period = request.GET.get('period', 'week')
    now = timezone.now()
    
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start = now - timedelta(days=7)
    else:
        start = now - timedelta(days=30)
    
    orders = Order.objects.filter(
        paid_at__gte=start,
        paid_at__lte=now
    ).prefetch_related('table', 'items__dish')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Заказы"
    
    headers = ['ID', 'Дата', 'Стол', 'Статус', 'Блюда', 'Сумма', 'Оплата']
    ws.append(headers)
    
    for row in ws[1]:
        row.font = Font(bold=True)
        row.alignment = Alignment(horizontal='center')
    
    for order in orders:
        dishes = ', '.join(f"{i.dish.name}×{i.quantity}" for i in order.items.all())
        total = sum(i.price * i.quantity for i in order.items.all())
        ws.append([
            order.id,
            order.paid_at.strftime('%d.%m.%Y %H:%M') if order.paid_at else '',
            f"№{order.table.number}",
            dict(Order.STATUS_CHOICES).get(order.status, ''),
            dishes,
            int(total),
            dict(Order.PAYMENT_CHOICES).get(order.payment_method, '') if order.payment_method else ''
        ])
    
    for col in ws.columns:
        max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="orders_{period}.xlsx"'
    wb.save(response)
    return response

def export_dishes_excel(request):
    period = request.GET.get('period', 'week')
    now = timezone.now()
    
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start = now - timedelta(days=7)
    else:
        start = now - timedelta(days=30)
    
    paid_orders = Order.objects.filter(status='paid', paid_at__gte=start, paid_at__lte=now)
    
    dish_stats = {}
    for order in paid_orders:
        for item in order.items.all():
            key = item.dish.name
            if key not in dish_stats:
                dish_stats[key] = {'count': 0, 'revenue': 0, 'price': int(item.price)}
            dish_stats[key]['count'] += item.quantity
            dish_stats[key]['revenue'] += item.price * item.quantity
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Популярные блюда"
    
    headers = ['Блюдо', 'Продано (шт)', 'Цена', 'Выручка']
    ws.append(headers)
    
    for row in ws[1]:
        row.font = Font(bold=True)
        row.alignment = Alignment(horizontal='center')
    
    for name, stats in sorted(dish_stats.items(), key=lambda x: -x[1]['count']):
        ws.append([name, stats['count'], stats['price'], stats['revenue']])
    
    for col in ws.columns:
        max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="dishes_{period}.xlsx"'
    wb.save(response)
    return response

# === ЧЕК ===

def receipt_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'paid':
        return redirect('restaurant:login')
    
    items = [
        {
            'name': item.dish.name,
            'quantity': item.quantity,
            'price': int(item.price),
            'subtotal': int(item.price * item.quantity)
        }
        for item in order.items.all()
    ]
    
    context = {
        'order': order,
        'items': items,
        'total': sum(i['subtotal'] for i in items),
        'payment_label': dict(Order.PAYMENT_CHOICES).get(order.payment_method, ''),
        'created_at': order.created_at.strftime('%d.%m.%Y %H:%M')
    }
    return render(request, 'restaurant/receipt.html', context)
