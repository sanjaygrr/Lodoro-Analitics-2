from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .stored_procedure_service import AnalyticsService

@login_required
def sales_dashboard(request):
    """
    Panel de ventas utilizando procedimientos almacenados
    """
    # Obtener parámetros de la petición
    marketplace = request.GET.get('marketplace', 'TODOS')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Fechas por defecto (últimos 30 días)
    today = timezone.now().date()
    
    try:
        if date_from:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        else:
            start_date = today - timedelta(days=30)
            date_from = start_date.strftime('%Y-%m-%d')
        
        if date_to:
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            end_date = today
            date_to = end_date.strftime('%Y-%m-%d')
    except ValueError:
        messages.error(request, 'Formato de fecha incorrecto')
        start_date = today - timedelta(days=30)
        end_date = today
        date_from = start_date.strftime('%Y-%m-%d')
        date_to = end_date.strftime('%Y-%m-%d')
    
    # Obtener estadísticas usando el servicio
    stats = AnalyticsService.get_sales_summary(
        marketplace=marketplace,
        start_date=start_date,
        end_date=end_date
    )
    
    # Preparar datos para la plantilla
    context = {
        'marketplace': marketplace,
        'date_from': date_from,
        'date_to': date_to,
        'stats': stats
    }
    
    return render(request, 'analytics/sales_dashboard.html', context)

@login_required
def product_performance(request):
    """
    Vista de rendimiento de productos utilizando procedimientos almacenados
    """
    # Obtener parámetros de la petición
    marketplace = request.GET.get('marketplace', 'TODOS')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    
    # Fechas por defecto (últimos 30 días)
    today = timezone.now().date()
    
    try:
        if date_from:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        else:
            start_date = today - timedelta(days=30)
            date_from = start_date.strftime('%Y-%m-%d')
        
        if date_to:
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            end_date = today
            date_to = end_date.strftime('%Y-%m-%d')
            
        page = int(page)
    except ValueError:
        messages.error(request, 'Parámetros incorrectos')
        start_date = today - timedelta(days=30)
        end_date = today
        date_from = start_date.strftime('%Y-%m-%d')
        date_to = end_date.strftime('%Y-%m-%d')
        page = 1
    
    # Configurar paginación
    items_per_page = 20
    offset = (page - 1) * items_per_page
    
    # Crear el procedimiento si no existe
    AnalyticsService.create_product_performance_procedure()
    
    # Obtener productos usando el servicio
    result = AnalyticsService.get_product_performance(
        marketplace=marketplace,
        start_date=start_date,
        end_date=end_date,
        search_query=search_query,
        limit=items_per_page,
        offset=offset
    )
    
    # Preparar datos para paginación
    total_items = result['total']
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    # Preparar contexto para la plantilla
    context = {
        'marketplace': marketplace,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'products': result['products'],
        'total_items': total_items,
        'page': page,
        'total_pages': total_pages,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'previous_page': page - 1,
        'next_page': page + 1
    }
    
    return render(request, 'analytics/product_performance.html', context) 