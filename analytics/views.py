from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, DecimalField, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from datetime import datetime, timedelta
import json

from marketplace.models import (
    ParisOrder, RipleyOrder, 
    ParisItem, RipleyOrderLine,
)
from .models import SalesAnalytics, ProductPerformance

@login_required
def sales_dashboard(request):
    """Vista del panel de análisis de ventas"""
    # Filtros
    marketplace = request.GET.get('marketplace', 'TODOS')
    period = request.GET.get('period', 'MES')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Fechas por defecto
    today = datetime.now()
    if not date_to:
        date_to = today.strftime('%Y-%m-%d')
    
    if not date_from:
        if period == 'DIA':
            date_from = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        elif period == 'SEMANA':
            date_from = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        elif period == 'MES':
            date_from = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        elif period == 'AÑO':
            date_from = (today - timedelta(days=365*2)).strftime('%Y-%m-%d')
    
    try:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        start_date = today - timedelta(days=365)
        end_date = today
    
    # Datos para gráficos
    paris_data = None
    ripley_data = None
    total_data = None
    
    # Función para truncar fecha según el período
    truncate_func = TruncMonth
    if period == 'DIA':
        truncate_func = TruncDay
    elif period == 'SEMANA':
        truncate_func = TruncWeek
    elif period == 'AÑO':
        truncate_func = TruncYear
    
    # Obtener datos de Paris
    if marketplace in ['PARIS', 'TODOS']:
        paris_orders = ParisOrder.objects.filter(
            createdAt__gte=start_date,
            createdAt__lte=end_date
        )
        
        paris_data = paris_orders.annotate(
            date=truncate_func('createdAt')
        ).values('date').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount'),
            avg_order=ExpressionWrapper(
                Sum('total_amount') / Count('id'),
                output_field=DecimalField()
            )
        ).order_by('date')
        
        paris_data = list(paris_data)
    
    # Obtener datos de Ripley
    if marketplace in ['RIPLEY', 'TODOS']:
        ripley_orders = RipleyOrder.objects.filter(
            created_date__gte=start_date,
            created_date__lte=end_date
        )
        
        ripley_data = ripley_orders.annotate(
            date=truncate_func('created_date')
        ).values('date').annotate(
            count=Count('order_id'),
            total_amount=Sum('total_price'),
            avg_order=ExpressionWrapper(
                Sum('total_price') / Count('order_id'),
                output_field=DecimalField()
            )
        ).order_by('date')
        
        ripley_data = list(ripley_data)
    
    # Productos más vendidos
    top_paris_products = None
    top_ripley_products = None
    
    if marketplace in ['PARIS', 'TODOS']:
        # Usamos el campo orderId para relacionar con ParisOrder
        top_paris_products = ParisItem.objects.filter(
            orderId__in=ParisOrder.objects.filter(
                createdAt__gte=start_date,
                createdAt__lte=end_date
            ).values_list('id', flat=True)
        ).values('sku', 'name').annotate(
            total_quantity=Count('id'),  # Cada item es una unidad
            total_revenue=Sum('priceAfterDiscounts')
        ).order_by('-total_quantity')[:10]
    
    if marketplace in ['RIPLEY', 'TODOS']:
        # Usamos el campo order_id para relacionar con RipleyOrder
        top_ripley_products = RipleyOrderLine.objects.filter(
            order_id__in=RipleyOrder.objects.filter(
                created_date__gte=start_date,
                created_date__lte=end_date
            ).values_list('order_id', flat=True)
        ).values('product_sku', 'product_title').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_quantity')[:10]
        
        # Adaptar los nombres de campos para mantener compatibilidad con la plantilla
        top_ripley_products = [{
            'sku': item['product_sku'],
            'name': item['product_title'],
            'total_quantity': item['total_quantity'],
            'total_revenue': item['total_revenue']
        } for item in top_ripley_products]
    
    # Resumen total
    total_orders = 0
    total_sales = 0
    total_average = 0
    
    if marketplace in ['PARIS', 'TODOS']:
        paris_summary = ParisOrder.objects.filter(
            createdAt__gte=start_date,
            createdAt__lte=end_date
        ).aggregate(
            total_orders=Count('id'),
            total_sales=Sum('total_amount')
        )
        
        total_orders += paris_summary['total_orders'] or 0
        total_sales += paris_summary['total_sales'] or 0
    
    if marketplace in ['RIPLEY', 'TODOS']:
        ripley_summary = RipleyOrder.objects.filter(
            created_date__gte=start_date,
            created_date__lte=end_date
        ).aggregate(
            total_orders=Count('order_id'),
            total_sales=Sum('total_price')
        )
        
        total_orders += ripley_summary['total_orders'] or 0
        total_sales += ripley_summary['total_sales'] or 0
    
    if total_orders > 0:
        total_average = total_sales / total_orders
    
    # Guardar análisis
    if request.method == 'POST' and 'save_analysis' in request.POST:
        SalesAnalytics.objects.create(
            marketplace=marketplace,
            period=period,
            start_date=start_date.date(),
            end_date=end_date.date(),
            total_sales=total_sales,
            total_orders=total_orders,
            average_order_value=total_average
        )
        
        # Guardar rendimiento de productos
        if marketplace in ['PARIS', 'TODOS'] and top_paris_products:
            for product in top_paris_products:
                ProductPerformance.objects.create(
                    sku=product['sku'],
                    name=product['name'],
                    total_quantity=product['total_quantity'],
                    total_revenue=product['total_revenue'],
                    marketplace='PARIS',
                    period_start=start_date.date(),
                    period_end=end_date.date()
                )
        
        if marketplace in ['RIPLEY', 'TODOS'] and top_ripley_products:
            for product in top_ripley_products:
                ProductPerformance.objects.create(
                    sku=product['sku'],
                    name=product['name'],
                    total_quantity=product['total_quantity'],
                    total_revenue=product['total_revenue'],
                    marketplace='RIPLEY',
                    period_start=start_date.date(),
                    period_end=end_date.date()
                )
        
        return redirect('sales_dashboard')
    
    # Preparar datos para gráficos en formato JSON
    paris_chart_data = []
    ripley_chart_data = []
    
    if paris_data:
        for item in paris_data:
            paris_chart_data.append({
                'date': item['date'].strftime('%Y-%m-%d'),
                'count': item['count'],
                'total_amount': float(item['total_amount']),
                'avg_order': float(item['avg_order'])
            })
    
    if ripley_data:
        for item in ripley_data:
            ripley_chart_data.append({
                'date': item['date'].strftime('%Y-%m-%d'),
                'count': item['count'],
                'total_amount': float(item['total_amount']),
                'avg_order': float(item['avg_order'])
            })
    
    context = {
        'marketplace': marketplace,
        'period': period,
        'date_from': date_from,
        'date_to': date_to,
        'start_date': start_date,
        'end_date': end_date,
        
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_average': total_average,
        
        'paris_chart_data': json.dumps(paris_chart_data),
        'ripley_chart_data': json.dumps(ripley_chart_data),
        
        'top_paris_products': top_paris_products,
        'top_ripley_products': top_ripley_products,
    }
    
    return render(request, 'analytics/sales_dashboard.html', context)

@login_required
def product_performance(request):
    """Vista para el rendimiento de productos"""
    # Filtros
    marketplace = request.GET.get('marketplace', 'TODOS')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    
    # Fechas por defecto
    today = datetime.now()
    if not date_to:
        date_to = today.strftime('%Y-%m-%d')
    
    if not date_from:
        date_from = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        start_date = today - timedelta(days=30)
        end_date = today
    
    # Buscar productos según marketplace
    products = []
    
    if marketplace in ['PARIS', 'TODOS']:
        paris_products = ParisItem.objects.filter(
            orderId__in=ParisOrder.objects.filter(
                createdAt__gte=start_date,
                createdAt__lte=end_date
            ).values_list('id', flat=True)
        )
        
        if search_query:
            paris_products = paris_products.filter(
                Q(sku__icontains=search_query) |
                Q(name__icontains=search_query)
            )
        
        paris_products = paris_products.values('sku', 'name').annotate(
            total_quantity=Count('id'),  # Cada item es una unidad
            total_revenue=Sum('priceAfterDiscounts'),
            marketplace=F('orderId').output_field.empty_strings_allowed  # Truco para agregar columna constante
        ).order_by('-total_quantity')
        
        for product in paris_products:
            product['marketplace'] = 'PARIS'
            products.append(product)
    
    if marketplace in ['RIPLEY', 'TODOS']:
        ripley_products = RipleyOrderLine.objects.filter(
            order_id__in=RipleyOrder.objects.filter(
                created_date__gte=start_date,
                created_date__lte=end_date
            ).values_list('order_id', flat=True)
        )
        
        if search_query:
            ripley_products = ripley_products.filter(
                Q(product_sku__icontains=search_query) |
                Q(product_title__icontains=search_query)
            )
        
        ripley_products = ripley_products.values('product_sku', 'product_title').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price'),
            marketplace=F('order_id').output_field.empty_strings_allowed  # Truco para agregar columna constante
        ).order_by('-total_quantity')
        
        for product in ripley_products:
            product['marketplace'] = 'RIPLEY'
            # Adaptar nombres de campos para mantener compatibilidad
            products.append({
                'sku': product['product_sku'],
                'name': product['product_title'],
                'total_quantity': product['total_quantity'],
                'total_revenue': product['total_revenue'],
                'marketplace': 'RIPLEY'
            })
    
    # Ordenar productos combinados por cantidad vendida
    products.sort(key=lambda x: x['total_quantity'], reverse=True)
    
    context = {
        'marketplace': marketplace,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'products': products,
    }
    
    return render(request, 'analytics/product_performance.html', context)

@login_required
def saved_analytics(request):
    """Vista para ver análisis guardados"""
    analytics = SalesAnalytics.objects.all().order_by('-created_at')
    return render(request, 'analytics/saved_analytics.html', {'analytics': analytics})
