from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import datetime, timedelta
import json

# Importar clase OrderManager para usar procedimientos almacenados
from order_db_utils import OrderManager

@login_required
def order_list(request):
    """
    Lista de órdenes utilizando procedimientos almacenados
    """
    # Obtener parámetros de la petición
    marketplace = request.GET.get('marketplace', 'paris')
    status = request.GET.get('status', None)
    page = request.GET.get('page', 1)
    
    # Convertir página a entero
    try:
        page = int(page)
    except ValueError:
        page = 1
    
    # Configurar paginación
    items_per_page = 20
    offset = (page - 1) * items_per_page
    
    # Obtener rango de fechas (si existe)
    date_from = request.GET.get('date_from', None)
    date_to = request.GET.get('date_to', None)
    
    try:
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, 'Formato de fecha incorrecto')
        date_from = None
        date_to = None
    
    # Obtener órdenes según el marketplace
    if marketplace == 'paris':
        result = OrderManager.get_paris_orders(
            limit=items_per_page,
            offset=offset,
            status=status,
            date_from=date_from,
            date_to=date_to
        )
    else:
        result = OrderManager.get_ripley_orders(
            limit=items_per_page,
            offset=offset,
            status=status,
            date_from=date_from,
            date_to=date_to
        )
    
    # Preparar datos para paginación
    total_items = result['total']
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    # Preparar contexto para la plantilla
    context = {
        'orders': result['orders'],
        'marketplace': marketplace,
        'status': status or 'TODAS',
        'page': page,
        'total_pages': total_pages,
        'total_items': total_items,
        'date_from': date_from.strftime('%Y-%m-%d') if date_from else '',
        'date_to': date_to.strftime('%Y-%m-%d') if date_to else '',
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'previous_page': page - 1,
        'next_page': page + 1
    }
    
    return render(request, 'marketplace/order_list.html', context)

@login_required
def order_detail(request, marketplace, order_id):
    """
    Detalle de una orden utilizando procedimientos almacenados
    """
    # Obtener detalles de la orden según el marketplace
    if marketplace == 'paris':
        order_data = OrderManager.get_paris_order_detail(order_id)
        if not order_data:
            messages.error(request, f'La orden Paris {order_id} no existe')
            return redirect('order_list')
        
        # Calcular totales
        total_amount = sum(item.get('priceAfterDiscounts', 0) or 0 for item in order_data['items'])
        total_items = len(order_data['items'])
        
    else:
        order_data = OrderManager.get_ripley_order_detail(order_id)
        if not order_data:
            messages.error(request, f'La orden Ripley {order_id} no existe')
            return redirect('order_list')
        
        # Calcular totales
        total_amount = sum(line.get('total_price', 0) or 0 for line in order_data['lines'])
        total_items = len(order_data['lines'])
    
    # Preparar contexto para la plantilla
    context = {
        'order': order_data['order'],
        'items': order_data.get('items', order_data.get('lines', [])),
        'marketplace': marketplace,
        'total_amount': total_amount,
        'total_items': total_items
    }
    
    return render(request, 'marketplace/order_detail.html', context)

@login_required
@require_http_methods(["POST"])
def update_order_status(request):
    """
    Actualizar el estado de una orden utilizando procedimientos almacenados
    """
    # Obtener datos del formulario
    order_id = request.POST.get('order_id')
    marketplace = request.POST.get('marketplace')
    processed = request.POST.get('processed')
    printed = request.POST.get('printed')
    
    # Convertir valores de estado a booleanos
    if processed:
        processed = processed.lower() == 'true'
    else:
        processed = None
        
    if printed:
        printed = printed.lower() == 'true'
    else:
        printed = None
    
    # Validar datos
    if not order_id or not marketplace:
        return JsonResponse({
            'success': False,
            'message': 'Faltan parámetros requeridos'
        }, status=400)
    
    # Actualizar estado según el marketplace
    if marketplace == 'paris':
        success, message = OrderManager.update_paris_order_status(
            order_id=order_id,
            processed=processed,
            printed=printed,
            user_id=request.user.id
        )
    else:
        success, message = OrderManager.update_ripley_order_status(
            order_id=order_id,
            processed=processed,
            printed=printed,
            user_id=request.user.id
        )
    
    # Devolver respuesta
    if success:
        return JsonResponse({
            'success': True,
            'message': message
        })
    else:
        return JsonResponse({
            'success': False,
            'message': message
        }, status=400)

@login_required
def dashboard(request):
    """
    Dashboard con estadísticas utilizando procedimientos almacenados
    """
    # Obtener rango de fechas (por defecto: últimos 30 días)
    date_to = timezone.now().date()
    date_from = date_to - timedelta(days=30)
    
    # Personalizar rango si se proporciona
    custom_from = request.GET.get('date_from')
    custom_to = request.GET.get('date_to')
    
    try:
        if custom_from:
            date_from = datetime.strptime(custom_from, '%Y-%m-%d').date()
        if custom_to:
            date_to = datetime.strptime(custom_to, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, 'Formato de fecha incorrecto')
    
    # Obtener estadísticas
    stats = OrderManager.get_order_stats(date_from=date_from, date_to=date_to)
    
    # Calcular porcentajes para gráficos
    paris_percent = 0
    ripley_percent = 0
    
    if stats['summary']['total'] > 0:
        paris_percent = (stats['paris']['total'] / stats['summary']['total']) * 100
        ripley_percent = (stats['ripley']['total'] / stats['summary']['total']) * 100
    
    # Preparar datos de porcentaje de procesamiento
    paris_processed_percent = 0
    ripley_processed_percent = 0
    
    if stats['paris']['total'] > 0:
        paris_processed_percent = (stats['paris']['processed'] / stats['paris']['total']) * 100
    
    if stats['ripley']['total'] > 0:
        ripley_processed_percent = (stats['ripley']['processed'] / stats['ripley']['total']) * 100
    
    # Preparar contexto para la plantilla
    context = {
        'stats': stats,
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'paris_percent': paris_percent,
        'ripley_percent': ripley_percent,
        'paris_processed_percent': paris_processed_percent,
        'ripley_processed_percent': ripley_processed_percent,
        'total_processed_percent': (stats['summary']['processed'] / stats['summary']['total']) * 100 if stats['summary']['total'] > 0 else 0
    }
    
    return render(request, 'marketplace/dashboard.html', context)

@login_required
@require_http_methods(["POST"])
def bulk_update_orders(request):
    """
    Actualización masiva de órdenes utilizando procedimientos almacenados
    """
    # Obtener datos del formulario
    order_ids = request.POST.getlist('order_ids[]')
    marketplace = request.POST.get('marketplace')
    action = request.POST.get('action')
    
    if not order_ids or not marketplace or not action:
        return JsonResponse({
            'success': False,
            'message': 'Faltan parámetros requeridos'
        }, status=400)
    
    # Determinar estados a actualizar según la acción
    processed = None
    printed = None
    
    if action == 'mark_processed':
        processed = True
    elif action == 'mark_unprocessed':
        processed = False
    elif action == 'mark_printed':
        printed = True
    elif action == 'mark_unprinted':
        printed = False
    else:
        return JsonResponse({
            'success': False,
            'message': 'Acción no válida'
        }, status=400)
    
    # Procesar cada orden
    success_count = 0
    failed_count = 0
    
    for order_id in order_ids:
        # Actualizar estado según el marketplace
        if marketplace == 'paris':
            success, _ = OrderManager.update_paris_order_status(
                order_id=order_id,
                processed=processed,
                printed=printed,
                user_id=request.user.id
            )
        else:
            success, _ = OrderManager.update_ripley_order_status(
                order_id=order_id,
                processed=processed,
                printed=printed,
                user_id=request.user.id
            )
        
        if success:
            success_count += 1
        else:
            failed_count += 1
    
    # Devolver respuesta
    return JsonResponse({
        'success': True,
        'message': f'Se actualizaron {success_count} órdenes exitosamente. {failed_count} órdenes fallaron.',
        'success_count': success_count,
        'failed_count': failed_count
    }) 