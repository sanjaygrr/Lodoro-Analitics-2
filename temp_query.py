import os
import json
from datetime import datetime, date
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
import django
django.setup()
from django.db import connection

# Función para convertir objetos no serializables a strings
def convert_to_serializable(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, Decimal):
        return float(obj)
    return str(obj)

# Consultar orden de Paris
def get_paris_order(order_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM paris_orders WHERE id = %s OR originOrderNumber = %s', 
                      [order_id, order_id])
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
        if not rows:
            print(f"No se encontró orden de Paris con ID: {order_id}")
            return None
        
        order = dict(zip(columns, rows[0]))
        
        # Convertir valores no serializables
        for key, value in order.items():
            if isinstance(value, (datetime, date, Decimal)):
                order[key] = convert_to_serializable(value)
        
        # Obtener items de la orden
        cursor.execute('SELECT * FROM paris_items WHERE orderId = %s', [order_id])
        columns = [col[0] for col in cursor.description]
        items = []
        
        for row in cursor.fetchall():
            item = dict(zip(columns, row))
            # Convertir valores no serializables
            for key, value in item.items():
                if isinstance(value, (datetime, date, Decimal)):
                    item[key] = convert_to_serializable(value)
            items.append(item)
        
        return {
            'order': order,
            'items': items
        }

# Consultar orden de Ripley
def get_ripley_order(order_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM ripley_orders WHERE order_id = %s', [order_id])
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
        if not rows:
            print(f"No se encontró orden de Ripley con ID: {order_id}")
            return None
        
        order = dict(zip(columns, rows[0]))
        
        # Convertir valores no serializables
        for key, value in order.items():
            if isinstance(value, (datetime, date, Decimal)):
                order[key] = convert_to_serializable(value)
        
        # Obtener líneas de la orden
        cursor.execute('SELECT * FROM ripley_order_lines WHERE order_id = %s', [order_id])
        columns = [col[0] for col in cursor.description]
        items = []
        
        for row in cursor.fetchall():
            item = dict(zip(columns, row))
            # Convertir valores no serializables
            for key, value in item.items():
                if isinstance(value, (datetime, date, Decimal)):
                    item[key] = convert_to_serializable(value)
            items.append(item)
        
        return {
            'order': order,
            'items': items
        }

# Buscar una orden de Paris reciente
def find_paris_order():
    with connection.cursor() as cursor:
        cursor.execute('SELECT id FROM paris_orders ORDER BY originOrderDate DESC LIMIT 1')
        result = cursor.fetchone()
        if result:
            return result[0]
        return None

# Ejecutar consultas
paris_order_id = find_paris_order()
ripley_order_id = "23528596001-A"

print("\n=== ORDEN DE PARIS ===")
if paris_order_id:
    print(f"Usando ID de orden de Paris: {paris_order_id}")
    paris_order = get_paris_order(paris_order_id)
    if paris_order:
        print(json.dumps(paris_order, indent=2, ensure_ascii=False))
else:
    print("No se encontraron órdenes de Paris en la base de datos")

print("\n=== ORDEN DE RIPLEY ===")
ripley_order = get_ripley_order(ripley_order_id)
if ripley_order:
    print(json.dumps(ripley_order, indent=2, ensure_ascii=False)) 