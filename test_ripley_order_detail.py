#!/usr/bin/env python
"""
Script para probar el procedimiento almacenado get_ripley_order_detail
"""
import os
import django
import json
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

# Para serializar Decimal y datetime en JSON
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def test_procedure_direct():
    """Probar el procedimiento directamente"""
    with connection.cursor() as cursor:
        print("=== PRUEBA DIRECTA DEL PROCEDIMIENTO GET_RIPLEY_ORDER_DETAIL ===")
        
        # Obtener un ID de orden de ejemplo
        cursor.execute("SELECT order_id FROM ripley_orders LIMIT 1")
        result = cursor.fetchone()
        if not result:
            print("No se encontraron órdenes en la base de datos")
            return
        
        order_id = result[0]
        print(f"Usando order_id: {order_id}")
        
        try:
            # Llamar al procedimiento
            cursor.execute(f"CALL get_ripley_order_detail(%s)", [order_id])
            
            # Obtener resultados de la orden
            order_columns = [col[0] for col in cursor.description]
            order_row = cursor.fetchone()
            
            if not order_row:
                print("No se encontró la orden")
                return
            
            order_dict = dict(zip(order_columns, order_row))
            print(f"Orden encontrada con campos: {', '.join(order_columns)}")
            print(f"order_id: {order_dict.get('order_id')}")
            print(f"commercial_id: {order_dict.get('commercial_id')}")
            
            # Verificar si hay líneas
            if cursor.nextset():
                lines_columns = [col[0] for col in cursor.description]
                lines_rows = cursor.fetchall()
                print(f"\nLíneas encontradas: {len(lines_rows)}")
                print(f"Campos de líneas: {', '.join(lines_columns)}")
                
                # Mostrar primera línea
                if lines_rows:
                    line_dict = dict(zip(lines_columns, lines_rows[0]))
                    print(f"\nPrimera línea:")
                    for key, value in line_dict.items():
                        print(f"  {key}: {value}")
            else:
                print("No se encontraron líneas")
        except Exception as e:
            print(f"Error al probar el procedimiento: {e}")

def test_service():
    """Probar el servicio OrderService"""
    print("\n=== PRUEBA A TRAVÉS DE ORDERSERVICE ===")
    
    # Importar OrderService
    from marketplace.order_service import OrderService
    
    # Obtener un ID de orden de ejemplo
    with connection.cursor() as cursor:
        cursor.execute("SELECT order_id FROM ripley_orders LIMIT 1")
        result = cursor.fetchone()
        if not result:
            print("No se encontraron órdenes en la base de datos")
            return
        
        order_id = result[0]
        print(f"Usando order_id: {order_id}")
        
    try:
        # Obtener detalles de la orden
        result = OrderService.get_order_detail('ripley', order_id)
        
        if not result:
            print("No se encontró la orden")
            return
        
        print("Orden encontrada")
        print(f"Campos de la orden: {list(result['order'].keys())}")
        print(f"order_id: {result['order'].get('order_id')}")
        print(f"commercial_id: {result['order'].get('commercial_id')}")
        
        # Verificar si hay líneas
        if 'items' in result and result['items']:
            print(f"\nLíneas encontradas: {len(result['items'])}")
            print(f"Campos de la primera línea: {list(result['items'][0].keys())}")
            
            # Mostrar primera línea
            print(f"\nPrimera línea:")
            for key, value in result['items'][0].items():
                print(f"  {key}: {value}")
        else:
            print("No se encontraron líneas")
    except Exception as e:
        print(f"Error al usar OrderService: {e}")

if __name__ == "__main__":
    test_procedure_direct()
    test_service() 