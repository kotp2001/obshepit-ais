from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
import json
from decimal import Decimal
from collections import defaultdict
from .models import Category, Dish, Table, Order, OrderItem, Booking

# ==================== СТРАНИЦЫ ====================

def landing(request):
    return render(request, 'landing.html')

def admin_panel(request):
    return render(request, 'admin_panel.html')

def menu_view(request):
    return render(request, 'menu.html')

def booking_view(request):
    return render(request, 'booking.html')

def waiter_hall(request):
    return render(request, 'waiter_hall.html')

def kitchen_view(request):
    return render(request, 'kitchen.html')

def reports_view(request):
    return render(request, 'reports.html')

# ==================== API АВТОРИЗАЦИИ ====================

@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    try:
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            from django.contrib.auth import login
            login(request, user)
            
            role = 'staff'
            if user.is_superuser:
                role = 'admin'
            elif hasattr(user, 'profile') and user.profile.role:
                role = user.profile.role
            
            return JsonResponse({'success': True, 'role': role, 'username': user.username})
        else:
            return JsonResponse({'success': False, 'error': 'Неверный логин или пароль'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ==================== API ОСНОВНЫЕ ====================

@require_http_methods(["GET"])
def api_dishes(request):
    dishes = Dish.objects.filter(is_available=True).select_related('category')
    data = [{
        'id': d.id,
        'name': d.name,
        'description': d.description,
        'price': float(d.price),
        'category': d.category.name,
        'category_id': d.category.id,
    } for d in dishes]
    return JsonResponse({'success': True, 'data': data})

@require_http_methods(["GET"])
def api_categories(request):
    categories = Category.objects.all().order_by('order')
    data = [{'id': c.id, 'name': c.name, 'icon': c.icon} for c in categories]
    return JsonResponse({'success': True, 'data': data})

@require_http_methods(["GET"])
def api_tables(request):
    tables = Table.objects.all().order_by('number')
    data = [{
        'id': t.id,
        'number': t.number,
        'seats': t.seats,
        'status': t.status,
    } for t in tables]
    return JsonResponse({'success': True, 'data': data})

@csrf_exempt
@require_http_methods(["POST"])
def api_create_order(request):
    try:
        body = json.loads(request.body)
        table_id = body.get('table_id')
        items = body.get('items', [])
        guest_count = body.get('guest_count', 1)
        
        table = Table.objects.get(id=table_id)
        order = Order.objects.create(table=table, status='new', guest_count=guest_count)
        
        total = Decimal('0')
        for item in items:
            dish = Dish.objects.get(id=item['dish_id'])
            OrderItem.objects.create(
                order=order,
                dish=dish,
                quantity=item['quantity'],
                price=dish.price,
                status='pending'
            )
            total += dish.price * item['quantity']
        
        order.total_amount = total
        order.save()
        table.status = 'occupied'
        table.save()
        
        return JsonResponse({'success': True, 'order_id': order.id, 'total': float(total)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_http_methods(["GET"])
def api_active_orders(request):
    orders = Order.objects.filter(status__in=['new', 'cooking', 'ready']).select_related('table').prefetch_related('items__dish')
    data = []
    for order in orders:
        items = [{
            'id': item.id,
            'dish_name': item.dish.name,
            'quantity': item.quantity,
            'status': item.status,
        } for item in order.items.all()]
        data.append({
            'id': order.id,
            'table_number': order.table.number,
            'created_at': order.created_at.strftime('%H:%M'),
            'status': order.status,
            'items': items,
        })
    return JsonResponse({'success': True, 'data': data})

@csrf_exempt
@require_http_methods(["POST"])
def api_update_item_status(request):
    try:
        body = json.loads(request.body)
        item_id = body.get('item_id')
        status = body.get('status')
        
        item = OrderItem.objects.get(id=item_id)
        item.status = status
        item.save()
        
        order = item.order
        all_items = order.items.all()
        if all(i.status == 'ready' for i in all_items):
            order.status = 'ready'
        elif any(i.status in ['pending', 'cooking'] for i in all_items):
            order.status = 'cooking'
        order.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_mark_order_ready(request):
    try:
        body = json.loads(request.body)
        order_id = body.get('order_id')
        order = Order.objects.get(id=order_id)
        order.status = 'ready'
        order.ready_at = timezone.now()
        order.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_take_order(request):
    try:
        body = json.loads(request.body)
        order_id = body.get('order_id')
        order = Order.objects.get(id=order_id)
        order.status = 'served'
        order.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_pay_order(request):
    try:
        body = json.loads(request.body)
        order_id = body.get('order_id')
        payment_method = body.get('payment_method')
        
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.payment_method = payment_method
        order.save()
        
        table = order.table
        table.status = 'free'
        table.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_http_methods(["GET"])
def api_order_receipt(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        items = []
        for item in order.items.all():
            items.append({
                'name': item.dish.name,
                'quantity': item.quantity,
                'price': float(item.price),
                'total': float(item.price * item.quantity)
            })
        
        receipt_data = {
            'order_id': order.id,
            'table_number': order.table.number,
            'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
            'items': items,
            'total': float(order.total_amount),
            'payment_method': dict(Order.PAYMENT_CHOICES).get(order.payment_method, 'Не оплачен')
        }
        return JsonResponse({'success': True, 'data': receipt_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_create_booking(request):
    try:
        body = json.loads(request.body)
        table_id = body.get('table_id')
        guest_name = body.get('guest_name')
        guest_phone = body.get('guest_phone')
        guests_count = body.get('guests_count')
        booking_date = body.get('booking_date')
        booking_time = body.get('booking_time')
        
        table = Table.objects.get(id=table_id)
        
        exists = Booking.objects.filter(
            table=table,
            booking_date=booking_date,
            booking_time=booking_time
        ).exists()
        
        if exists:
            return JsonResponse({'success': False, 'error': 'Это время уже занято'}, status=400)
        
        Booking.objects.create(
            table=table,
            guest_name=guest_name,
            guest_phone=guest_phone,
            guests_count=guests_count,
            booking_date=booking_date,
            booking_time=booking_time,
            status='pending'
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_http_methods(["GET"])
def api_bookings(request):
    date = request.GET.get('date', timezone.now().date().isoformat())
    bookings = Booking.objects.filter(booking_date=date).select_related('table')
    data = [{
        'id': b.id,
        'table_number': b.table.number,
        'time': b.booking_time.strftime('%H:%M'),
        'guest_name': b.guest_name,
        'guests_count': b.guests_count,
        'status': b.status,
    } for b in bookings]
    return JsonResponse({'success': True, 'data': data})

@require_http_methods(["GET"])
def api_reports(request):
    period = request.GET.get('period', 'week')
    
    if period == 'day':
        start_date = timezone.now().date()
    elif period == 'week':
        start_date = timezone.now().date() - timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now().date() - timedelta(days=30)
    else:
        start_date = timezone.now().date() - timedelta(days=7)
    
    orders = Order.objects.filter(created_at__date__gte=start_date, status='paid')
    
    total_revenue = sum(float(o.total_amount) for o in orders)
    total_orders = orders.count()
    avg_check = total_revenue / total_orders if total_orders > 0 else 0
    
    dish_count = defaultdict(int)
    for order in orders:
        for item in order.items.all():
            dish_count[item.dish.name] += item.quantity
    
    popular_dishes = [{'name': k, 'count': v} for k, v in sorted(dish_count.items(), key=lambda x: -x[1])[:5]]
    
    daily_data = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        day_orders = orders.filter(created_at__date=day)
        daily_data.append({
            'date': day.strftime('%d.%m'),
            'revenue': sum(float(o.total_amount) for o in day_orders),
            'orders': day_orders.count(),
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_check': avg_check,
            'popular_dishes': popular_dishes,
            'daily_data': daily_data,
            
 @csrf_exempt
@require_http_methods(["POST"])
def api_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return JsonResponse({'success': True})
        }
    })
