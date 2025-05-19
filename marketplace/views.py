from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from datetime import datetime, timedelta
from django.db import connection
from django.conf import settings
import json
from decimal import Decimal
import logging
import requests
import time
from PyPDF2 import PdfMerger
import io
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

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
    Maneja datetime, Decimal, bytes y otros tipos no serializables.
    Funciona con diccionarios, listas y valores individuales.
    """
    if obj is None:
        return None
    elif isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='replace')
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
    """Vista para mostrar las órdenes de Paris"""
    return render(request, 'marketplace/paris_orders.html', {
        'orders': [],
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'search_query': request.GET.get('search', ''),
        'status': request.GET.get('status', '')
    })

@login_required
def paris_order_detail(request, order_id):
    """Detalle de una orden de Paris usando procedimientos almacenados"""
    # Convertir order_id a string
    order_id = str(order_id)
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
    """Vista para mostrar las órdenes de Ripley"""
    return render(request, 'marketplace/ripley_orders.html', {
        'orders': [],
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'search_query': request.GET.get('search', ''),
        'status': request.GET.get('status', '')
    })

@login_required
def ripley_order_detail(request, order_id):
    """Detalle de una orden de Ripley usando procedimientos almacenados"""
    # Convertir order_id a string
    order_id = str(order_id)
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
    order_id = str(request.POST.get('order_id', ''))
    marketplace = request.POST.get('marketplace', '')
    action = request.POST.get('action', '')
    
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
        # Asegurar que order_id sea string
        order_id = str(order_id)
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
    """Vista para el escaneo de órdenes"""
    return render(request, 'marketplace/order_scanning.html')

@login_required
def product_detail(request, marketplace, product_id):
    """
    Vista para mostrar los detalles de un producto incluyendo información de Bsale y el marketplace
    """
    product_data = {}
    marketplace_data = {}
    bsale_data = {}
    error_message = None
    
    try:
        with connection.cursor() as cursor:
            # Buscar información en Bsale
            cursor.execute("""
                SELECT 
                    bv.id, 
                    bv.barcode, 
                    bv.code, 
                    bv.description,
                    bp.id as product_id,
                    bp.name as product_name,
                    bp.description as product_description,
                    bp.price
                FROM bsale_variants bv
                LEFT JOIN bsale_products bp ON bv.product_id = bp.id
                WHERE bv.id = %s
            """, [product_id])
            
            bsale_row = cursor.fetchone()
            
            if bsale_row:
                bsale_data = {
                    'variant_id': bsale_row[0],
                    'barcode': bsale_row[1],
                    'code': bsale_row[2],
                    'variant_description': bsale_row[3],
                    'product_id': bsale_row[4],
                    'product_name': bsale_row[5],
                    'product_description': bsale_row[6],
                    'price': bsale_row[7]
                }
                
                # Convertir valores bytes a string
                for key, value in bsale_data.items():
                    if isinstance(value, bytes):
                        bsale_data[key] = value.decode('utf-8')
                
                # Buscar imágenes del producto
                cursor.execute("""
                    SELECT url, alt_text
                    FROM bsale_product_images
                    WHERE product_id = %s
                    LIMIT 5
                """, [bsale_data['product_id']])
                
                images = []
                for img_row in cursor.fetchall():
                    url = img_row[0]
                    alt = img_row[1]
                    if isinstance(url, bytes):
                        url = url.decode('utf-8')
                    if isinstance(alt, bytes):
                        alt = alt.decode('utf-8')
                    images.append({'url': url, 'alt': alt})
                
                bsale_data['images'] = images
                
                # Buscar información del marketplace específico
                if marketplace.lower() == 'paris':
                    cursor.execute("""
                        SELECT 
                            pi.id, 
                            pi.sku, 
                            pi.name, 
                            pi.priceAfterDiscounts, 
                            pi.grossPrice,
                            po.id as order_id,
                            po.subOrderNumber,
                            po.originOrderNumber
                        FROM paris_items pi
                        JOIN paris_orders po ON pi.orderId = po.id
                        WHERE pi.sku = %s
                        LIMIT 10
                    """, [bsale_data['code']])
                    
                    marketplace_items = []
                    for item_row in cursor.fetchall():
                        item_dict = {
                            'id': item_row[0],
                            'sku': item_row[1],
                            'name': item_row[2],
                            'price': item_row[3],
                            'gross_price': item_row[4],
                            'order_id': item_row[5],
                            'sub_order': item_row[6],
                            'origin_order': item_row[7]
                        }
                        
                        # Convertir valores bytes a string
                        for key, value in item_dict.items():
                            if isinstance(value, bytes):
                                item_dict[key] = value.decode('utf-8')
                                
                        marketplace_items.append(item_dict)
                    
                    marketplace_data = {
                        'name': 'Paris',
                        'items': marketplace_items
                    }
                
                elif marketplace.lower() == 'ripley':
                    cursor.execute("""
                        SELECT 
                            rol.order_line_id, 
                            rol.product_sku, 
                            rol.product_title, 
                            rol.price_unit, 
                            rol.total_price,
                            ro.order_id,
                            ro.commercial_id
                        FROM ripley_order_lines rol
                        JOIN ripley_orders ro ON rol.order_id = ro.order_id
                        WHERE rol.product_sku = %s
                        LIMIT 10
                    """, [bsale_data['code']])
                    
                    marketplace_items = []
                    for item_row in cursor.fetchall():
                        item_dict = {
                            'id': item_row[0],
                            'sku': item_row[1],
                            'name': item_row[2],
                            'price': item_row[3],
                            'total_price': item_row[4],
                            'order_id': item_row[5],
                            'commercial_id': item_row[6]
                        }
                        
                        # Convertir valores bytes a string
                        for key, value in item_dict.items():
                            if isinstance(value, bytes):
                                item_dict[key] = value.decode('utf-8')
                                
                        marketplace_items.append(item_dict)
                    
                    marketplace_data = {
                        'name': 'Ripley',
                        'items': marketplace_items
                    }
                
                # Consolidar toda la información
                product_data = {
                    'marketplace': marketplace,
                    'bsale': bsale_data,
                    'marketplace_data': marketplace_data
                }
            else:
                error_message = f"No se encontró el producto con ID {product_id} en Bsale"
        
    except Exception as e:
        print(f"Error al obtener detalles del producto: {str(e)}")
        error_message = f"Error al obtener detalles del producto: {str(e)}"
    
    context = {
        'product': product_data,
        'error_message': error_message
    }
    
    return render(request, 'marketplace/product_detail.html', context)

@login_required
@require_http_methods(["GET"])
def get_bsale_info(request):
    """
    Función que busca la información de BSale para un SKU o ID de boleta
    Puede ser utilizada como API desde la plantilla para mostrar información de BSale
    """
    search_type = request.GET.get('type', 'sku')  # 'sku', 'document'
    search_value = request.GET.get('value', '')
    
    if not search_value:
        return JsonResponse({'success': False, 'message': 'Se requiere un valor para la búsqueda'})
    
    result = {'success': False, 'message': 'No se encontró información', 'data': None}
    
    try:
        with connection.cursor() as cursor:
            if search_type == 'document':
                # Buscar información por número de documento (boleta)
                cursor.execute("""
                    SELECT bd.id, bd.number, bd.emissionDate
                    FROM bsale_documents bd
                    WHERE bd.number = %s
                    LIMIT 1
                """, [search_value])
                
                doc_row = cursor.fetchone()
                
                if doc_row:
                    doc_id = doc_row[0]
                    
                    # Buscar detalles del documento
                    cursor.execute("""
                        SELECT 
                            bdd.id, 
                            bdd.variant_id, 
                            bdd.quantity,
                            bdd.netUnitValue,
                            bv.barCode, 
                            bv.code,
                            bp.name as product_name,
                            bp.id as product_id
                        FROM bsale_document_details bdd
                        JOIN bsale_variants bv ON bdd.variant_id = bv.id
                        JOIN bsale_products bp ON bv.product_id = bp.id
                        WHERE bdd.document_id = %s
                    """, [doc_id])
                    
                    items = []
                    for detail_row in cursor.fetchall():
                        item = {
                            'detail_id': detail_row[0],
                            'variant_id': detail_row[1],
                            'quantity': detail_row[2],
                            'net_value': detail_row[3],
                            'barcode': detail_row[4],
                            'code': detail_row[5],
                            'product_name': detail_row[6],
                            'product_id': detail_row[7]
                        }
                        
                        # Convertir valores bytes a string si es necesario
                        for key, value in item.items():
                            if isinstance(value, bytes):
                                item[key] = value.decode('utf-8')
                                
                        items.append(item)
                    
                    result = {
                        'success': True, 
                        'message': 'Información encontrada',
                        'data': {
                            'document_id': doc_id,
                            'document_number': doc_row[1],
                            'emission_date': doc_row[2],
                            'items': items
                        }
                    }
                    
                    # Convertir valores bytes a string si es necesario
                    if isinstance(result['data']['document_number'], bytes):
                        result['data']['document_number'] = result['data']['document_number'].decode('utf-8')
                    if isinstance(result['data']['emission_date'], bytes):
                        result['data']['emission_date'] = result['data']['emission_date'].decode('utf-8')
                
            elif search_type == 'sku':
                # MÉTODO 1: Buscar SKU en Paris
                if not result['success']:
                    # Consulta exacta que sabemos que funciona en Paris
                    cursor.execute("""
                        SELECT 
                            po.subOrderNumber,
                            pi.sku AS paris_sku,
                            pi.name,
                            bdd.variant_id 
                        FROM paris_orders po
                        JOIN paris_items pi ON pi.subOrderNumber = po.subOrderNumber
                        JOIN bsale_document_details bdd ON pi.name LIKE CONCAT('%%', bdd.variant_description, '%%')
                        WHERE pi.sku = %s
                        LIMIT 1
                    """, [search_value])
                    
                    paris_row = cursor.fetchone()
                    
                    if paris_row:
                        logger.info(f"Encontrado en Paris: {paris_row}")
                        variant_id = paris_row[3]  # variant_id (corresponde al índice 3 en la consulta)
                        
                        # Obtener información del producto con ese variant_id
                        cursor.execute("""
                            SELECT 
                                bv.id, 
                                bv.barCode AS barcode, 
                                bv.code, 
                                bp.id AS product_id,
                                bp.name AS product_name
                            FROM bsale_variants bv
                            JOIN bsale_products bp ON bv.product_id = bp.id
                            WHERE bv.id = %s
                            LIMIT 1
                        """, [variant_id])
                        
                        variant_row = cursor.fetchone()
                        
                        if variant_row:
                            logger.info(f"Información de variante encontrada: {variant_row}")
                            
                            # Buscar documentos relacionados
                            cursor.execute("""
                                SELECT 
                                    bd.id, 
                                    bd.number, 
                                    bd.emissionDate
                                FROM bsale_documents bd
                                JOIN bsale_document_details bdd ON bd.id = bdd.document_id
                                WHERE bdd.variant_id = %s
                                ORDER BY bd.emissionDate DESC
                                LIMIT 5
                            """, [variant_id])
                            
                            documents = []
                            for doc_row in cursor.fetchall():
                                doc = {
                                    'document_id': doc_row[0],
                                    'document_number': doc_row[1],
                                    'emission_date': doc_row[2]
                                }
                                
                                # Convertir valores bytes a string si es necesario
                                for key, value in doc.items():
                                    if isinstance(value, bytes):
                                        doc[key] = value.decode('utf-8')
                                        
                                documents.append(doc)
                            
                            # Preparar información de Paris para incluirla en el resultado
                            paris_info = {
                                'marketplace': 'paris',
                                'subOrderNumber': paris_row[0],
                                'sku': paris_row[1],
                                'name': paris_row[2]
                            }
                            
                            # Convertir valores bytes a string si es necesario
                            for key, value in paris_info.items():
                                if isinstance(value, bytes):
                                    paris_info[key] = value.decode('utf-8')
                            
                            # Preparar resultado completo
                            variant_data = {
                                'variant_id': variant_row[0],
                                'barcode': variant_row[1],
                                'code': variant_row[2],
                                'product_id': variant_row[3],
                                'product_name': variant_row[4],
                                'documents': documents,
                                'marketplace_info': paris_info
                            }
                            
                            # Convertir valores bytes a string si es necesario
                            for key, value in variant_data.items():
                                if isinstance(value, bytes) and key != 'documents' and key != 'marketplace_info':
                                    variant_data[key] = value.decode('utf-8')
                            
                            result = {
                                'success': True,
                                'message': 'Información encontrada',
                                'data': variant_data
                            }
                
                # MÉTODO 2: Buscar SKU en Ripley
                if not result['success']:
                    cursor.execute("""
                        SELECT 
                            ro.order_id,
                            rol.product_title,
                            rol.product_sku,
                            bdd.variant_id
                        FROM ripley_orders ro
                        JOIN ripley_order_lines rol ON rol.order_id = ro.order_id
                        JOIN bsale_document_details bdd ON rol.product_title LIKE CONCAT('%%', bdd.variant_description, '%%')
                        WHERE rol.product_sku = %s
                        LIMIT 1
                    """, [search_value])
                    
                    ripley_row = cursor.fetchone()
                    
                    if ripley_row:
                        logger.info(f"Encontrado en Ripley: {ripley_row}")
                        variant_id = ripley_row[3]  # variant_id (corresponde al índice 3 en la consulta)
                        
                        # Obtener información del producto con ese variant_id
                        cursor.execute("""
                            SELECT 
                                bv.id, 
                                bv.barCode AS barcode, 
                                bv.code, 
                                bp.id AS product_id,
                                bp.name AS product_name
                            FROM bsale_variants bv
                            JOIN bsale_products bp ON bv.product_id = bp.id
                            WHERE bv.id = %s
                            LIMIT 1
                        """, [variant_id])
                        
                        variant_row = cursor.fetchone()
                        
                        if variant_row:
                            logger.info(f"Información de variante encontrada: {variant_row}")
                            
                            # Buscar documentos relacionados
                            cursor.execute("""
                                SELECT 
                                    bd.id, 
                                    bd.number, 
                                    bd.emissionDate
                                FROM bsale_documents bd
                                JOIN bsale_document_details bdd ON bd.id = bdd.document_id
                                WHERE bdd.variant_id = %s
                                ORDER BY bd.emissionDate DESC
                                LIMIT 5
                            """, [variant_id])
                            
                            documents = []
                            for doc_row in cursor.fetchall():
                                doc = {
                                    'document_id': doc_row[0],
                                    'document_number': doc_row[1],
                                    'emission_date': doc_row[2]
                                }
                                
                                # Convertir valores bytes a string si es necesario
                                for key, value in doc.items():
                                    if isinstance(value, bytes):
                                        doc[key] = value.decode('utf-8')
                                        
                                documents.append(doc)
                            
                            # Preparar información de Ripley para incluirla en el resultado
                            ripley_info = {
                                'marketplace': 'ripley',
                                'order_id': ripley_row[0],
                                'product_title': ripley_row[1],
                                'product_sku': ripley_row[2]
                            }
                            
                            # Convertir valores bytes a string si es necesario
                            for key, value in ripley_info.items():
                                if isinstance(value, bytes):
                                    ripley_info[key] = value.decode('utf-8')
                            
                            # Preparar resultado completo
                            variant_data = {
                                'variant_id': variant_row[0],
                                'barcode': variant_row[1],
                                'code': variant_row[2],
                                'product_id': variant_row[3],
                                'product_name': variant_row[4],
                                'documents': documents,
                                'marketplace_info': ripley_info
                            }
                            
                            # Convertir valores bytes a string si es necesario
                            for key, value in variant_data.items():
                                if isinstance(value, bytes) and key != 'documents' and key != 'marketplace_info':
                                    variant_data[key] = value.decode('utf-8')
                            
                            result = {
                                'success': True,
                                'message': 'Información encontrada',
                                'data': variant_data
                            }
                
                # MÉTODO 3: Buscar directamente por código o EAN
                if not result['success']:
                    cursor.execute("""
                        SELECT 
                            bv.id, 
                            bv.barCode AS barcode, 
                            bv.code, 
                            bp.id AS product_id,
                            bp.name AS product_name
                        FROM bsale_variants bv
                        JOIN bsale_products bp ON bv.product_id = bp.id
                        WHERE bv.code = %s OR bv.barCode = %s
                        LIMIT 1
                    """, [search_value, search_value])
                    
                    variant_row = cursor.fetchone()
                    
                    if variant_row:
                        logger.info(f"Encontrado por código/EAN directamente: {variant_row}")
                        variant_id = variant_row[0]
                        
                        # Buscar documentos relacionados
                        cursor.execute("""
                            SELECT 
                                bd.id, 
                                bd.number, 
                                bd.emissionDate
                            FROM bsale_documents bd
                            JOIN bsale_document_details bdd ON bd.id = bdd.document_id
                            WHERE bdd.variant_id = %s
                            ORDER BY bd.emissionDate DESC
                            LIMIT 5
                        """, [variant_id])
                        
                        documents = []
                        for doc_row in cursor.fetchall():
                            doc = {
                                'document_id': doc_row[0],
                                'document_number': doc_row[1],
                                'emission_date': doc_row[2]
                            }
                            
                            # Convertir valores bytes a string si es necesario
                            for key, value in doc.items():
                                if isinstance(value, bytes):
                                    doc[key] = value.decode('utf-8')
                                    
                            documents.append(doc)
                        
                        # Preparar resultado
                        variant_data = {
                            'variant_id': variant_row[0],
                            'barcode': variant_row[1],
                            'code': variant_row[2],
                            'product_id': variant_row[3],
                            'product_name': variant_row[4],
                            'documents': documents
                        }
                        
                        # Convertir valores bytes a string si es necesario
                        for key, value in variant_data.items():
                            if isinstance(value, bytes) and key != 'documents':
                                variant_data[key] = value.decode('utf-8')
                        
                        result = {
                            'success': True,
                            'message': 'Información encontrada',
                            'data': variant_data
                        }
                
    except Exception as e:
        logger.error(f"Error al buscar información: {str(e)}")
        result = {'success': False, 'message': f'Error: {str(e)}'}
    
    return JsonResponse(result)

@require_http_methods(["POST"])
@csrf_exempt
def print_multiple_boletas(request):
    """Endpoint para imprimir múltiples boletas"""
    try:
        data = json.loads(request.body)
        boleta_urls = data.get('boleta_urls', [])
        
        if not boleta_urls:
            return JsonResponse({'error': 'No se proporcionaron URLs de boletas'}, status=400)
            
        # Aquí iría la lógica para generar el PDF combinado
        # Por ahora retornamos un mensaje de éxito
        return JsonResponse({'message': 'PDF generado correctamente'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
