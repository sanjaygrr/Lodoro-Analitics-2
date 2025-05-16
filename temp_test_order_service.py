"""
Script para verificar que el método get_order_detail funcione correctamente
"""
import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar después de configurar Django
from marketplace.order_service import OrderService

def print_json(data):
    """Imprime un objeto como JSON con formato"""
    print(json.dumps(data, indent=2, default=str))

def test_order_service():
    """Prueba el servicio de órdenes"""
    # Recrear los procedimientos almacenados
    print("Recreando los procedimientos almacenados...")
    OrderService.create_stored_procedures()
    
    # Probar con una orden de Ripley
    ripley_order_id = "100074886-B"
    print(f"\n=== Probando orden de Ripley: {ripley_order_id} ===")
    ripley_order = OrderService.get_order_detail("ripley", ripley_order_id)
    
    if ripley_order:
        print("\nDatos de la orden:")
        print_json(ripley_order['order'])
        
        print(f"\nItems de la orden ({len(ripley_order['items'])} items):")
        if ripley_order['items']:
            for i, item in enumerate(ripley_order['items'][:2]):  # Mostrar solo los primeros 2 items
                print(f"\nItem {i+1}:")
                print_json(item)
        else:
            print("No hay items en la orden")
    else:
        print(f"No se encontró la orden {ripley_order_id}")
    
    # Probar con una orden de Paris
    paris_order_id = "00000e3c-197b-4f35-874a-9c48924bd5d5"
    print(f"\n=== Probando orden de Paris: {paris_order_id} ===")
    paris_order = OrderService.get_order_detail("paris", paris_order_id)
    
    if paris_order:
        print("\nDatos de la orden:")
        print_json(paris_order['order'])
        
        print(f"\nItems de la orden ({len(paris_order['items'])} items):")
        if paris_order['items']:
            for i, item in enumerate(paris_order['items'][:2]):  # Mostrar solo los primeros 2 items
                print(f"\nItem {i+1}:")
                print_json(item)
        else:
            print("No hay items en la orden")
    else:
        print(f"No se encontró la orden {paris_order_id}")

if __name__ == "__main__":
    test_order_service() 