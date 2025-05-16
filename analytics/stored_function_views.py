from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
import json

# Importar nuestras utilidades para funciones almacenadas
from mysql_stored_utils import (
    get_marketplace_stats,
    calculate_order_value,
    update_order_status,
    generate_daily_report
)

@login_required
def dashboard(request):
    """
    Dashboard principal que utiliza funciones almacenadas para mostrar estadísticas
    """
    # Obtener estadísticas de los marketplaces
    paris_count = get_marketplace_stats('paris')
    ripley_count = get_marketplace_stats('ripley')
    total_count = paris_count + ripley_count
    
    # Generar datos para el gráfico de los últimos 7 días
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)
    
    daily_stats = []
    current_date = start_date
    
    while current_date <= end_date:
        total_orders, total_paris, total_ripley = generate_daily_report(current_date)
        daily_stats.append({
            'fecha': current_date.strftime('%d/%m/%Y'),
            'paris': total_paris,
            'ripley': total_ripley,
            'total': total_orders
        })
        current_date += timedelta(days=1)
    
    context = {
        'paris_count': paris_count,
        'ripley_count': ripley_count,
        'total_count': total_count,
        'daily_stats': json.dumps(daily_stats),
        'start_date': start_date.strftime('%d/%m/%Y'),
        'end_date': end_date.strftime('%d/%m/%Y'),
    }
    
    return render(request, 'analytics/dashboard_with_stored_functions.html', context)

@login_required
@require_http_methods(["POST"])
def update_order(request):
    """
    Vista para actualizar el estado de una orden usando procedimientos almacenados
    """
    order_id = request.POST.get('order_id')
    marketplace = request.POST.get('marketplace')
    new_status = request.POST.get('status')
    user_id = request.user.id
    
    if not all([order_id, marketplace, new_status]):
        return JsonResponse({
            'success': False,
            'message': 'Faltan parámetros requeridos'
        }, status=400)
    
    # Usar el procedimiento almacenado para actualizar el estado
    success, message = update_order_status(order_id, marketplace, new_status, user_id)
    
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
def order_detail(request, marketplace, order_id):
    """
    Detalle de una orden utilizando funciones almacenadas para calcular valores
    """
    # En un caso real, obtendríamos los detalles de la orden desde la base de datos
    # Aquí solo usamos la función almacenada para calcular el valor total
    
    total_value = calculate_order_value(order_id, marketplace)
    
    # En un caso real, buscaríamos los detalles completos de la orden en la base de datos
    # y los pasaríamos al contexto de la plantilla
    
    with connection.cursor() as cursor:
        if marketplace == 'paris':
            cursor.execute("""
                SELECT po.*, pi.customer_name, pi.customer_email, pi.billing_address1,
                       pi.billing_city, pi.customer_phone, pi.orden_impresa
                FROM paris_orders po
                LEFT JOIN paris_items pi ON po.id = pi.orderId
                WHERE po.id = %s OR po.subOrderNumber = %s
                LIMIT 1
            """, [order_id, order_id])
            order = cursor.fetchone()
            
            if order:
                cursor.execute("""
                    SELECT * FROM paris_items 
                    WHERE orderId = %s
                """, [order[0]])  # Usar el ID real de la orden
                items = cursor.fetchall()
            else:
                items = []
                
        elif marketplace == 'ripley':
            cursor.execute("""
                SELECT * FROM ripley_orders
                WHERE order_id = %s
                LIMIT 1
            """, [order_id])
            order = cursor.fetchone()
            
            if order:
                cursor.execute("""
                    SELECT * FROM ripley_order_lines
                    WHERE order_id = %s
                """, [order_id])
                items = cursor.fetchall()
            else:
                items = []
        else:
            order = None
            items = []
    
    context = {
        'marketplace': marketplace,
        'order_id': order_id,
        'order': order,
        'items': items,
        'total_value': total_value,
    }
    
    return render(request, 'analytics/order_detail.html', context)

@login_required
def custom_report(request):
    """
    Generar reportes personalizados para un rango de fechas
    """
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Formato de fecha incorrecto')
            return redirect('custom_report')
        
        # Generar reporte para cada día en el rango
        report_data = []
        current_date = start_date
        
        while current_date <= end_date:
            total_orders, total_paris, total_ripley = generate_daily_report(current_date)
            report_data.append({
                'fecha': current_date.strftime('%d/%m/%Y'),
                'total_ordenes': total_orders,
                'total_paris': total_paris,
                'total_ripley': total_ripley
            })
            current_date += timedelta(days=1)
        
        context = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'report_data': report_data
        }
        
        return render(request, 'analytics/custom_report_results.html', context)
    
    # Mostrar formulario para seleccionar fechas
    return render(request, 'analytics/custom_report_form.html') 