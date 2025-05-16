#!/usr/bin/env python
"""
Script para verificar los valores de originOrderNumber y subOrderNumber en las órdenes de Paris
"""
import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection
from marketplace.order_service import OrderService

def check_paris_orders():
    """Verificar los valores de originOrderNumber y subOrderNumber en las órdenes de Paris"""
    print("\n=== Verificando órdenes de Paris ===")
    
    # Consultar directamente la base de datos
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, originOrderNumber, subOrderNumber
            FROM paris_orders
            LIMIT 10
        """)
        
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
        print(f"- Órdenes encontradas: {len(rows)}")
        print(f"- Columnas: {', '.join(columns)}")
        
        for i, row in enumerate(rows, 1):
            row_dict = dict(zip(columns, row))
            print(f"  Orden #{i}:")
            print(f"    ID: {row_dict['id']}")
            print(f"    originOrderNumber: {row_dict['originOrderNumber']}")
            print(f"    subOrderNumber: {row_dict['subOrderNumber']}")
    
    # Verificar usando el servicio
    print("\n=== Verificando órdenes de Paris usando OrderService ===")
    result = OrderService.get_orders('paris', limit=5)
    
    print(f"- Órdenes recuperadas: {len(result['orders'])}")
    
    for i, order in enumerate(result['orders'], 1):
        print(f"  Orden #{i}:")
        print(f"    order_id: {order.get('order_id')}")
        print(f"    originOrderNumber: {order.get('originOrderNumber')}")
        print(f"    subOrderNumber: {order.get('subOrderNumber')}")

def main():
    """Función principal"""
    print("=== VERIFICACIÓN DE ÓRDENES DE PARIS ===")
    
    # Verificar órdenes
    check_paris_orders()
    
    print("\n=== VERIFICACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main() 