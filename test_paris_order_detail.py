#!/usr/bin/env python
"""
Script para probar el procedimiento almacenado get_paris_order_detail
"""
import os
import django
import json
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection
from marketplace.order_service import OrderService

def test_order_detail(order_id="572c0f20-173a-4136-9090-56153783efca"):
    """Probar el procedimiento get_paris_order_detail con un ID específico"""
    print(f"\n=== Probando get_paris_order_detail con order_id={order_id} ===")
    
    # Probar usando el servicio
    result = OrderService.get_order_detail('paris', order_id)
    
    if not result:
        print("- No se encontró la orden")
        return
    
    order = result['order']
    items = result['items']
    
    print(f"- Orden encontrada con campos: {list(order.keys())}")
    print(f"- order_id: {order.get('order_id')}")
    print(f"- originOrderNumber: {order.get('originOrderNumber')}")
    print(f"- subOrderNumber: {order.get('subOrderNumber')}")
    
    if items:
        print(f"- Items encontrados: {len(items)}")
        print(f"- Campos del primer item: {list(items[0].keys())}")
    else:
        print("- No se encontraron items")

if __name__ == "__main__":
    # Usar el ID proporcionado como argumento o el predeterminado
    order_id = sys.argv[1] if len(sys.argv) > 1 else "572c0f20-173a-4136-9090-56153783efca"
    test_order_detail(order_id) 