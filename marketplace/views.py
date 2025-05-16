from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from datetime import datetime, timedelta
from django.db import connection
import json
from decimal import Decimal

from .models import (
    ApiConfig, 
    ParisOrder, ParisItem, ParisSubOrder, ParisStatus, ParisPago, ParisDeliveryOption,
    RipleyOrder, RipleyCustomer, RipleyAddress, RipleyOrderLine, RipleyRefund,
    FalabellaProduct
)
from .order_service import OrderService

# Función para convertir objetos no serializables a tipos serializables
def convert_to_serializable(obj):
    """
    Convierte recursivamente objetos no serializables a tipos serializables en una estructura de datos anidada.
    Maneja datetime, Decimal, y otros tipos no serializables.
    Funciona con diccionarios, listas y valores individuales.
    """
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_serializable(item) for item in obj)
    else:
        return obj

@login_required
def api_config_list(request):
    """Lista de configuraciones de API"""
    configs = ApiConfig.objects.all().order_by('marketplace', 'name')
    return render(request, 'marketplace/api_config_list.html', {'configs': configs})

@login_required
def paris_orders(request):
    """Vista de órdenes de Paris usando procedimientos almacenados"""
    status_filter = request.GET.get('status', '')
    processed_filter = request.GET.get('processed', '')
    printed_filter = request.GET.get('printed', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    
    # Mapear los filtros a los formatos esperados por el procedimiento almacenado
    status = None
    if processed_filter == 'yes':
        status = 'PROCESADA'
    elif processed_filter == 'no':
        status = 'NUEVA'
    
    if printed_filter == 'yes':
        status = 'IMPRESA'
    elif printed_filter == 'no':
        status = 'NO_IMPRESA'
    
    # Convertir fechas a objetos datetime si se proporcionan
    date_from_obj = None
    date_to_obj = None
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Paginación
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1
    
    items_per_page = 50
    offset = (page - 1) * items_per_page
    
    # Obtener órdenes usando el servicio
    result = OrderService.get_orders(
        marketplace='paris',
        limit=items_per_page,
        offset=offset,
        status=status,
        date_from=date_from_obj,
        date_to=date_to_obj
    )
    
    # Preparar datos para paginación
    total_orders = result['total']
    total_pages = (total_orders + items_per_page - 1) // items_per_page
    
    # Calcular el monto total si está disponible en los datos
    try:
        total_amount = sum(order.get('total_amount', 0) or 0 for order in result['orders'])
    except Exception:
        total_amount = 0
    
    context = {
        'orders': result['orders'],
        'total_orders': total_orders,
        'total_amount': total_amount,
        'status_filter': status_filter,
        'processed_filter': processed_filter,
        'printed_filter': printed_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'page': page,
        'total_pages': total_pages,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'previous_page': page - 1,
        'next_page': page + 1
    }
    
    return render(request, 'marketplace/paris_orders.html', context)

@login_required
def paris_order_detail(request, order_id):
    """Detalle de una orden de Paris usando procedimientos almacenados"""
    # Obtener detalle de la orden usando el servicio
    order_data = OrderService.get_order_detail('paris', order_id)
    
    if not order_data:
        messages.error(request, f'La orden Paris {order_id} no existe')
        return redirect('paris_orders')
    
    order = order_data['order']
    items = order_data['items']
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'process':
            success, message = OrderService.update_order_status(
                marketplace='paris',
                order_id=order_id,
                processed=True,
                user_id=request.user.id
            )
            
            if success:
                messages.success(request, f'Orden {order_id} marcada como procesada')
            else:
                messages.error(request, f'Error al procesar la orden: {message}')
        
        elif action == 'print':
            success, message = OrderService.update_order_status(
                marketplace='paris',
                order_id=order_id,
                printed=True,
                user_id=request.user.id
            )
            
            if success:
                messages.success(request, f'Orden {order_id} marcada como impresa')
            else:
                messages.error(request, f'Error al marcar como impresa: {message}')
        
        elif action == 'cancel':
            messages.warning(request, 'La acción de cancelar no está disponible actualmente')
        
        elif action == 'ship':
            messages.warning(request, 'La acción de enviar no está disponible actualmente')
        
        return redirect('paris_order_detail', order_id=order_id)
    
    # Calcular el total de la orden
    total_amount = sum(item.get('priceAfterDiscounts', 0) or 0 for item in items)
    
    context = {
        'order': order,
        'items': items,
        'total_amount': total_amount
    }
    
    return render(request, 'marketplace/paris_order_detail.html', context)

@login_required
def ripley_orders(request):
    """Vista de órdenes de Ripley usando procedimientos almacenados"""
    status_filter = request.GET.get('status', '')
    processed_filter = request.GET.get('processed', '')
    printed_filter = request.GET.get('printed', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    
    # Mapear los filtros a los formatos esperados por el procedimiento almacenado
    status = None
    if processed_filter == 'yes':
        status = 'PROCESADA'
    elif processed_filter == 'no':
        status = 'NUEVA'
    
    if printed_filter == 'yes':
        status = 'IMPRESA'
    elif printed_filter == 'no':
        status = 'NO_IMPRESA'
    
    # Convertir fechas a objetos datetime si se proporcionan
    date_from_obj = None
    date_to_obj = None
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Paginación
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1
    
    items_per_page = 50
    offset = (page - 1) * items_per_page
    
    # Obtener órdenes usando el servicio
    result = OrderService.get_orders(
        marketplace='ripley',
        limit=items_per_page,
        offset=offset,
        status=status,
        date_from=date_from_obj,
        date_to=date_to_obj
    )
    
    # Preparar datos para paginación
    total_orders = result['total']
    total_pages = (total_orders + items_per_page - 1) // items_per_page
    
    # Calcular el monto total si está disponible en los datos
    try:
        total_amount = sum(order.get('total_price', 0) or 0 for order in result['orders'])
    except Exception:
        total_amount = 0
    
    context = {
        'orders': result['orders'],
        'total_orders': total_orders,
        'total_amount': total_amount,
        'status_filter': status_filter,
        'processed_filter': processed_filter,
        'printed_filter': printed_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'page': page,
        'total_pages': total_pages,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'previous_page': page - 1,
        'next_page': page + 1
    }
    
    return render(request, 'marketplace/ripley_orders.html', context)

@login_required
def ripley_order_detail(request, order_id):
    """Detalle de una orden de Ripley usando procedimientos almacenados"""
    # Obtener detalle de la orden usando el servicio
    order_data = OrderService.get_order_detail('ripley', order_id)
    
    if not order_data:
        messages.error(request, f'La orden Ripley {order_id} no existe')
        return redirect('ripley_orders')
    
    order = order_data['order']
    order_lines = order_data['items']
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'process':
            success, message = OrderService.update_order_status(
                marketplace='ripley',
                order_id=order_id,
                processed=True,
                user_id=request.user.id
            )
            
            if success:
                messages.success(request, f'Orden {order_id} marcada como procesada')
            else:
                messages.error(request, f'Error al procesar la orden: {message}')
        
        elif action == 'print':
            success, message = OrderService.update_order_status(
                marketplace='ripley',
                order_id=order_id,
                printed=True,
                user_id=request.user.id
            )
            
            if success:
                messages.success(request, f'Orden {order_id} marcada como impresa')
            else:
                messages.error(request, f'Error al marcar como impresa: {message}')
        
        elif action == 'cancel':
            messages.warning(request, 'La acción de cancelar no está disponible actualmente')
        
        elif action == 'ship':
            messages.warning(request, 'La acción de enviar no está disponible actualmente')
        
        return redirect('ripley_order_detail', order_id=order_id)
    
    # Calcular el total de la orden
    total_amount = sum(line.get('total_price', 0) or 0 for line in order_lines)
    
    context = {
        'order': order,
        'order_lines': order_lines,
        'total_amount': total_amount
    }
    
    return render(request, 'marketplace/ripley_order_detail.html', context)

@login_required
def orders_summary(request):
    """Resumen de órdenes usando procedimientos almacenados"""
    # Obtener el rango de fechas (por defecto: últimos 30 días)
    date_to = datetime.now().date()
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
    
    # Obtener estadísticas usando el servicio
    stats = OrderService.get_order_stats(date_from=date_from, date_to=date_to)
    
    context = {
        'stats': stats,
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'marketplace/orders_summary.html', context)

@login_required
@require_http_methods(["POST"])
def update_order_status(request):
    """Actualizar el estado de una orden usando procedimientos almacenados"""
    # Obtener datos del formulario
    order_id = request.POST.get('order_id')
    marketplace = request.POST.get('marketplace')
    action = request.POST.get('action')
    
    if not order_id or not marketplace or not action:
        return JsonResponse({
            'success': False,
            'message': 'Faltan parámetros requeridos'
        }, status=400)
    
    # Determinar los valores de estado según la acción
    processed = None
    printed = None
    
    if action == 'process':
        processed = True
    elif action == 'unprocess':
        processed = False
    elif action == 'print':
        printed = True
    elif action == 'unprint':
        printed = False
    else:
        return JsonResponse({
            'success': False,
            'message': 'Acción no válida'
        }, status=400)
    
    # Actualizar estado usando el servicio
    success, message = OrderService.update_order_status(
        marketplace=marketplace,
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
@require_http_methods(["POST"])
def bulk_update_orders(request):
    """Actualización masiva de órdenes usando procedimientos almacenados"""
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
        # Actualizar estado usando el servicio
        success, _ = OrderService.update_order_status(
            marketplace=marketplace,
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

@login_required
def order_scanning(request):
    """Vista para el pistolaje (escaneo) de órdenes"""
    scan_message = None
    scan_status = None
    order_data = None
    scanned_items = []
    
    # Crear o actualizar los procedimientos almacenados
    OrderService.create_stored_procedures()
    
    if request.method == 'POST':
        # Obtener el código escaneado
        scanned_code = str(request.POST.get('scanned_code', '').strip())
        order_id = str(request.POST.get('order_id', ''))
        
        # Si no hay order_id, asumimos que estamos escaneando un número de orden
        if not order_id and scanned_code:
            order_found = False
            
            # Primero buscamos en Paris por subOrderNumber
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, subOrderNumber, originOrderNumber
                    FROM paris_orders
                    WHERE subOrderNumber = %s OR originOrderNumber = %s
                """, [scanned_code, scanned_code])
                order_result = cursor.fetchone()
                
                if order_result:
                    order_id = str(order_result[0])
                    marketplace = 'paris'
                    order_found = True
                else:
                    # Si no se encuentra en Paris, buscamos en Ripley por commercial_id u order_id
                    cursor.execute("""
                        SELECT order_id, commercial_id
                        FROM ripley_orders
                        WHERE order_id = %s OR commercial_id = %s
                    """, [scanned_code, scanned_code])
                    ripley_result = cursor.fetchone()
                    
                    if ripley_result:
                        order_id = str(ripley_result[0])
                        marketplace = 'ripley'
                        order_found = True
            
            if order_found:
                # Obtener los detalles completos de la orden con información de Bsale
                order_data = OrderService.get_order_detail(marketplace, order_id)
                if order_data:
                    # Inicializar el estado de escaneo de los items
                    for item in order_data['items']:
                        # Verificar si es un costo de despacho (podría tener un SKU específico o precio 0)
                        is_shipping = False
                        
                        # Determinar claves según marketplace
                        if marketplace == 'paris':
                            price_key = 'priceAfterDiscounts'
                            name_key = 'name'
                        else:  # ripley
                            price_key = 'total_price'
                            name_key = 'product_name'
                        
                        if (item.get(name_key, '').lower().find('despacho') >= 0 or 
                            item.get(price_key, 0) == 0):
                            is_shipping = True
                        
                        item['scanned'] = is_shipping  # Los costos de despacho se marcan como ya escaneados
                    
                    # Guardar el marketplace en la sesión para saber cómo procesar los items
                    order_data['marketplace'] = marketplace
                    
                    # Convertir objetos no serializables a tipos serializables antes de guardar en sesión
                    serializable_order_data = convert_to_serializable(order_data)
                    
                    # Guardar en sesión
                    request.session['order_data'] = serializable_order_data
                    request.session['scanned_items'] = []
                    
                    scan_message = f"Orden {scanned_code} encontrada en {marketplace.capitalize()}. Escanee los productos."
                    scan_status = 'success'
                else:
                    scan_message = f"No se pudo cargar los detalles de la orden {scanned_code}."
                    scan_status = 'error'
            else:
                scan_message = f"No se encontró ninguna orden con el código {scanned_code}."
                scan_status = 'error'
        
        # Si ya tenemos un order_id, asumimos que estamos escaneando un producto
        elif order_id and scanned_code:
            # Recuperar datos de la sesión
            order_data = request.session.get('order_data', {})
            scanned_items = request.session.get('scanned_items', [])
            marketplace = order_data.get('marketplace', 'paris')
            
            # Buscar el código de barras en bsale_variants
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT bv.id, bv.description, bv.barcode, bv.code, bp.name
                    FROM bsale_variants bv
                    LEFT JOIN bsale_products bp ON bv.product_id = bp.id
                    WHERE bv.barcode = %s OR bv.code = %s
                """, [scanned_code, scanned_code])
                product = cursor.fetchone()
                
                if product:
                    product_id = product[0]
                    product_name = product[1] or product[4]  # Usar descripción o nombre del producto
                    bsale_barcode = product[2]
                    bsale_code = product[3]
                    
                    # Verificar si el producto pertenece a la orden
                    found = False
                    all_scanned = True
                    
                    # Buscar en los items de la orden por código de barras o código de Bsale
                    for item in order_data['items']:
                        # Verificar si el SKU coincide con alguno de los códigos de Bsale
                        sku = item.get('sku', '')
                        bsale_variant_id = item.get('bsale_variant_id')
                        bsale_item_barcode = item.get('bsale_barcode', '')
                        bsale_item_code = item.get('bsale_code', '')
                        
                        # Comparar con múltiples posibles coincidencias
                        if ((sku == scanned_code or 
                             bsale_item_barcode == scanned_code or 
                             bsale_item_code == scanned_code or 
                             bsale_variant_id == product_id) and 
                            not item.get('scanned', False)):
                            
                            item['scanned'] = True
                            
                            # Determinar el nombre del producto a mostrar
                            if marketplace == 'paris':
                                display_name = item.get('name', item.get('bsale_product_name', 'Producto sin nombre'))
                            else:  # ripley
                                display_name = item.get('product_name', item.get('bsale_product_name', 'Producto sin nombre'))
                            
                            scanned_items.append({
                                'code': scanned_code,
                                'name': display_name,
                                'time': datetime.now().strftime('%H:%M:%S')
                            })
                            found = True
                            scan_message = f"Producto {display_name} escaneado correctamente."
                            scan_status = 'success'
                            break
                    
                    # Verificar si todos los productos han sido escaneados
                    for item in order_data['items']:
                        if not item.get('scanned', False):
                            all_scanned = False
                            break
                    
                    if all_scanned:
                        # Marcar la orden como procesada
                        success, message = OrderService.update_order_status(
                            marketplace=marketplace,
                            order_id=order_data['order']['order_id'],
                            processed=True,
                            user_id=request.user.id
                        )
                        
                        if success:
                            scan_message = "¡Todos los productos han sido escaneados! Orden procesada correctamente."
                            scan_status = 'complete'
                            # Limpiar la sesión
                            request.session.pop('order_data', None)
                            request.session.pop('scanned_items', None)
                        else:
                            scan_message = f"Error al procesar la orden: {message}"
                            scan_status = 'error'
                    
                    if not found:
                        scan_message = f"El producto {product_name} no pertenece a esta orden."
                        scan_status = 'warning'
                else:
                    scan_message = f"No se encontró ningún producto con el código {scanned_code}."
                    scan_status = 'error'
            
            # Convertir a formatos serializables antes de guardar en la sesión
            serializable_order_data = convert_to_serializable(order_data)
            serializable_scanned_items = convert_to_serializable(scanned_items)
            
            # Actualizar la sesión con datos serializables
            request.session['order_data'] = serializable_order_data
            request.session['scanned_items'] = serializable_scanned_items
    else:
        # Limpiar la sesión al cargar la página por GET
        request.session.pop('order_data', None)
        request.session.pop('scanned_items', None)
    
    # Si tenemos datos de orden en la sesión, usarlos
    if not order_data and 'order_data' in request.session:
        order_data = request.session.get('order_data')
        scanned_items = request.session.get('scanned_items', [])
    
    context = {
        'scan_message': scan_message,
        'scan_status': scan_status,
        'order_data': order_data,
        'scanned_items': scanned_items
    }
    
    return render(request, 'marketplace/order_scanning.html', context)
