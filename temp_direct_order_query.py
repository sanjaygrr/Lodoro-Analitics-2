"""
Script para ejecutar las consultas directamente sin usar el procedimiento almacenado
"""
import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar después de configurar Django
from django.db import connection

def print_json(data):
    """Imprime un objeto como JSON con formato"""
    print(json.dumps(data, indent=2, default=str))

def test_ripley_order_direct(order_id):
    """Prueba obtener una orden de Ripley mediante consultas directas"""
    print(f"\n=== Probando orden de Ripley (consulta directa): {order_id} ===")
    
    # Crear un diccionario para almacenar los resultados
    result = {'order': None, 'items': []}
    
    with connection.cursor() as cursor:
        # Consulta para obtener los datos de la orden
        cursor.execute("""
            SELECT 
                ro.order_id,
                ro.commercial_id,
                ro.created_date,
                ro.order_state,
                ro.payment_type,
                ro.total_price,
                ro.shipping_price,
                ro.price AS subtotal_price,
                ro.shipping_type_label,
                ro.shipping_zone_label,
                ro.customer_id,
                rc.firstname AS first_name,
                rc.lastname AS last_name,
                CONCAT(rc.firstname, ' ', rc.lastname) AS full_name,
                ro.shipping_zone_label AS address_commune,
                ro.shipping_zone_label AS address_city,
                ro.shipping_zone_code AS address_region,
                (ro.total_price - ro.shipping_price) AS products_total,
                ro.total_price AS order_total
            FROM ripley_orders ro
            LEFT JOIN ripley_customers rc ON ro.customer_id = rc.customer_id
            WHERE ro.order_id = %s OR ro.commercial_id = %s
        """, [order_id, order_id])
        
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            order_row = cursor.fetchone()
            
            if order_row:
                result['order'] = dict(zip(columns, order_row))
            else:
                print(f"No se encontró la orden {order_id}")
                return None
        
        # Consulta para obtener los items de la orden
        cursor.execute("""
            SELECT 
                rol.order_line_id,
                rol.order_id,
                rol.product_sku AS sku,
                rol.product_title AS product_name,
                rol.quantity,
                rol.price_unit AS unit_price,
                rol.total_price,
                rol.order_line_state,
                bv.id AS bsale_variant_id,
                bv.barcode AS bsale_barcode,
                bv.code AS bsale_code,
                bp.name AS bsale_product_name
            FROM ripley_order_lines rol
            LEFT JOIN bsale_variants bv ON rol.product_sku = bv.barcode OR rol.product_sku = bv.code
            LEFT JOIN bsale_products bp ON bv.product_id = bp.id
            WHERE rol.order_id = %s
        """, [order_id])
        
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                result['items'].append(item)
    
    # Imprimir los resultados
    if result['order']:
        print("\nDatos de la orden:")
        print_json(result['order'])
        
        print(f"\nItems de la orden ({len(result['items'])} items):")
        for i, item in enumerate(result['items'][:2]):  # Mostrar solo los primeros 2 items
            print(f"\nItem {i+1}:")
            print_json(item)
    
    return result

def test_paris_order_direct(order_id):
    """Prueba obtener una orden de Paris mediante consultas directas"""
    print(f"\n=== Probando orden de Paris (consulta directa): {order_id} ===")
    
    # Crear un diccionario para almacenar los resultados
    result = {'order': None, 'items': []}
    
    with connection.cursor() as cursor:
        # Consulta para obtener los datos de la orden
        cursor.execute("""
            SELECT 
                po.id AS order_id,
                po.originOrderNumber,
                po.subOrderNumber,
                po.originOrderDate,
                po.createdAt,
                po.customer_name,
                po.customer_email,
                po.customer_documentType,
                po.customer_documentNumber,
                po.billing_firstName,
                po.billing_lastName,
                po.billing_address1,
                po.billing_address2,
                po.billing_city,
                po.billing_stateCode,
                po.billing_countryCode,
                po.billing_phone,
                po.billing_communaCode,
                po.originOrderNumber AS boleta_number,
                'https://example.com/boleta/' AS boleta_url,
                COALESCE((SELECT SUM(pi.priceAfterDiscounts) FROM paris_items pi WHERE pi.orderId = po.id), 0) AS total_amount,
                po.orden_impresa,
                po.orden_procesada,
                po.orden_impresa AS printed,
                po.orden_procesada AS processed,
                CONCAT(po.billing_firstName, ' ', po.billing_lastName) AS full_name,
                CONCAT(po.billing_address1, ' ', IFNULL(po.billing_address2, '')) AS full_address,
                po.billing_city AS city,
                po.billing_stateCode AS state,
                po.billing_phone AS phone,
                po.customer_email AS email,
                (SELECT SUM(pi.priceAfterDiscounts) FROM paris_items pi WHERE pi.orderId = po.id) AS products_total,
                (SELECT SUM(pi.grossPrice) FROM paris_items pi WHERE pi.orderId = po.id) AS order_total
            FROM paris_orders po
            WHERE po.id = %s OR po.originOrderNumber = %s OR po.subOrderNumber = %s
        """, [order_id, order_id, order_id])
        
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            order_row = cursor.fetchone()
            
            if order_row:
                result['order'] = dict(zip(columns, order_row))
            else:
                print(f"No se encontró la orden {order_id}")
                return None
        
        # Consulta para obtener los items de la orden
        cursor.execute("""
            SELECT 
                pi.id AS item_id,
                pi.sku,
                pi.name,
                pi.position AS quantity,
                pi.priceAfterDiscounts,
                pi.grossPrice AS totalPrice,
                bv.id AS bsale_variant_id,
                bv.barcode AS bsale_barcode,
                bv.code AS bsale_code,
                bp.name AS bsale_product_name
            FROM paris_items pi
            LEFT JOIN bsale_variants bv ON pi.sku = bv.barcode OR pi.sku = bv.code
            LEFT JOIN bsale_products bp ON bv.product_id = bp.id
            WHERE pi.orderId = %s
        """, [order_id])
        
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                result['items'].append(item)
    
    # Imprimir los resultados
    if result['order']:
        print("\nDatos de la orden:")
        print_json(result['order'])
        
        print(f"\nItems de la orden ({len(result['items'])} items):")
        for i, item in enumerate(result['items'][:2]):  # Mostrar solo los primeros 2 items
            print(f"\nItem {i+1}:")
            print_json(item)
    
    return result

if __name__ == "__main__":
    # Probar con una orden de Ripley
    ripley_order = test_ripley_order_direct('100074886-B')
    
    # Probar con una orden de Paris
    paris_order = test_paris_order_direct('00000e3c-197b-4f35-874a-9c48924bd5d5') 