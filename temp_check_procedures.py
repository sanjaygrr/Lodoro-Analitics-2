"""
Script temporal para verificar los procedimientos almacenados
"""
import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar después de configurar Django
from django.db import connection
from marketplace.order_service import OrderService

def print_json(data):
    """Imprime un objeto como JSON con formato"""
    print(json.dumps(data, indent=2, default=str))

def check_paris_order(order_id):
    """Verifica un procedimiento almacenado para órdenes de Paris"""
    print(f"\n=== Verificando orden de Paris: {order_id} ===")
    
    # Recrear los procedimientos almacenados
    OrderService.create_stored_procedures()
    
    # Obtener los detalles de la orden
    order_data = OrderService.get_order_detail('paris', order_id)
    
    if order_data:
        print("\nDatos de la orden:")
        print_json(order_data['order'])
        
        print("\nPrimeros 2 productos:")
        for i, item in enumerate(order_data['items'][:2]):
            print(f"\nProducto {i+1}:")
            print_json(item)
    else:
        print(f"No se encontró la orden {order_id}")

def check_ripley_order(order_id):
    """Verifica un procedimiento almacenado para órdenes de Ripley"""
    print(f"\n=== Verificando orden de Ripley: {order_id} ===")
    
    # Recrear los procedimientos almacenados
    OrderService.create_stored_procedures()
    
    # Obtener los detalles de la orden
    order_data = OrderService.get_order_detail('ripley', order_id)
    
    if order_data:
        print("\nDatos de la orden:")
        print_json(order_data['order'])
        
        print("\nPrimeros 2 productos:")
        for i, item in enumerate(order_data['items'][:2]):
            print(f"\nProducto {i+1}:")
            print_json(item)
    else:
        print(f"No se encontró la orden {order_id}")

def check_order_ids():
    """Verifica los IDs de órdenes disponibles"""
    print("\n=== Verificando IDs de órdenes disponibles ===")
    
    with connection.cursor() as cursor:
        # Verificar órdenes de Paris
        cursor.execute("SELECT id, subOrderNumber, originOrderNumber FROM paris_orders LIMIT 5")
        paris_orders = cursor.fetchall()
        
        print("\nÓrdenes de Paris:")
        for order in paris_orders:
            print(f"ID: {order[0]}, subOrderNumber: {order[1]}, originOrderNumber: {order[2]}")
        
        # Verificar órdenes de Ripley
        cursor.execute("SELECT order_id, commercial_id FROM ripley_orders LIMIT 5")
        ripley_orders = cursor.fetchall()
        
        print("\nÓrdenes de Ripley:")
        for order in ripley_orders:
            print(f"order_id: {order[0]}, commercial_id: {order[1]}")

if __name__ == "__main__":
    # Verificar IDs de órdenes disponibles
    check_order_ids()
    
    # Si se proporciona un ID de orden como argumento, verificarlo
    if len(sys.argv) > 2:
        marketplace = sys.argv[1].lower()
        order_id = sys.argv[2]
        
        if marketplace == 'paris':
            check_paris_order(order_id)
        elif marketplace == 'ripley':
            check_ripley_order(order_id)
        else:
            print(f"Marketplace no válido: {marketplace}")
    else:
        # Usar IDs de ejemplo
        check_paris_order('12345')  # Reemplazar con un ID real
        check_ripley_order('23528596001-A')  # Reemplazar con un ID real 