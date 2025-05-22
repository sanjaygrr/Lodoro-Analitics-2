from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import connection

@login_required
def dashboard(request):
    """Vista para el dashboard principal mejorada con resumen de órdenes de todos los marketplaces"""
    resumen = {}
    marketplaces = [
        ('Paris', 'paris_orders', 'originOrderDate'),
        ('Ripley', 'ripley_orders', 'created_date'),
        ('Falabella', 'falabella_orders', 'created_at'),
        ('Mercado Libre', 'mercadolibre_orders', 'date_created'),
    ]
    with connection.cursor() as cursor:
        for nombre, tabla, fecha in marketplaces:
            cursor.execute(f'''
                SELECT 
                    COUNT(CASE WHEN orden_impresa = 0 AND orden_procesada = 0 AND orden_despachada = 0 THEN 1 END) as nuevas,
                    COUNT(CASE WHEN orden_impresa = 1 AND orden_procesada = 0 AND orden_despachada = 0 THEN 1 END) as por_procesar,
                    COUNT(CASE WHEN orden_procesada = 1 AND orden_despachada = 0 THEN 1 END) as por_despachar,
                    COUNT(CASE WHEN orden_despachada = 1 THEN 1 END) as despachadas
                FROM {tabla}
            ''')
            stats = dict(zip(['nuevas', 'por_procesar', 'por_despachar', 'despachadas'], cursor.fetchone()))
            resumen[nombre] = stats
    return render(request, 'core/dashboard.html', {'resumen': resumen})

@login_required
def profile(request):
    """Vista para el perfil del usuario"""
    return render(request, 'core/profile.html')

@login_required
def settings(request):
    """Vista para la configuración del sistema"""
    return render(request, 'core/settings.html') 