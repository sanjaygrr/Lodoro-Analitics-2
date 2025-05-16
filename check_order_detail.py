#!/usr/bin/env python
"""
Script para verificar el procedimiento almacenado get_paris_order_detail
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

def check_procedure_exists():
    """Verificar si el procedimiento almacenado existe"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.routines 
            WHERE routine_schema = DATABASE()
            AND routine_name = 'get_paris_order_detail'
        """)
        count = cursor.fetchone()[0]
        
        print(f"\n=== Procedimiento get_paris_order_detail ===")
        print(f"- Existe: {'Sí' if count > 0 else 'No'}")
        
        return count > 0

def get_procedure_definition():
    """Obtener la definición del procedimiento almacenado"""
    with connection.cursor() as cursor:
        try:
            cursor.execute("SHOW CREATE PROCEDURE get_paris_order_detail")
            definition = cursor.fetchone()
            
            print(f"\n=== Definición del procedimiento ===")
            print(definition[2])
            
            return definition[2]
        except Exception as e:
            print(f"Error al obtener definición: {str(e)}")
            return None

def test_procedure_direct(order_id):
    """Probar el procedimiento directamente"""
    with connection.cursor() as cursor:
        try:
            print(f"\n=== Probando procedimiento directamente con order_id={order_id} ===")
            
            # Ejecutar el procedimiento
            cursor.execute(f"CALL get_paris_order_detail(%s)", [order_id])
            
            # Obtener resultados de la orden
            columns = [col[0] for col in cursor.description]
            order_row = cursor.fetchone()
            
            if not order_row:
                print("- No se encontró la orden")
                return None, None
            
            order_dict = dict(zip(columns, order_row))
            
            print(f"- Orden encontrada: {json.dumps(order_dict, default=str)[:200]}...")
            print(f"- Columnas de la orden: {', '.join(columns)}")
            
            # Verificar si hay un segundo conjunto de resultados (items)
            items = []
            if cursor.nextset():
                items_columns = [col[0] for col in cursor.description]
                items_rows = cursor.fetchall()
                
                if items_rows:
                    items = [dict(zip(items_columns, row)) for row in items_rows]
                    print(f"- Items encontrados: {len(items)}")
                    print(f"- Columnas de items: {', '.join(items_columns)}")
                    if items:
                        print(f"- Primer item: {json.dumps(items[0], default=str)[:200]}...")
                else:
                    print("- No se encontraron items")
            else:
                print("- No hay segundo conjunto de resultados (items)")
            
            return order_dict, items
        except Exception as e:
            print(f"Error al ejecutar procedimiento: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None

def test_service(order_id):
    """Probar el servicio OrderService.get_order_detail"""
    print(f"\n=== Probando OrderService.get_order_detail con order_id={order_id} ===")
    try:
        result = OrderService.get_order_detail('paris', order_id)
        
        if not result:
            print("- No se encontró la orden")
            return None
        
        print(f"- Orden encontrada")
        print(f"- Campos de la orden: {list(result['order'].keys())}")
        print(f"- order_id en result['order']: {result['order'].get('order_id')}")
        print(f"- id en result['order']: {result['order'].get('id')}")
        
        if 'items' in result and result['items']:
            print(f"- Items encontrados: {len(result['items'])}")
            print(f"- Campos del primer item: {list(result['items'][0].keys()) if result['items'] else []}")
        else:
            print("- No se encontraron items")
        
        return result
    except Exception as e:
        print(f"Error al usar OrderService: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def create_fix_procedure():
    """Crear una versión corregida del procedimiento almacenado"""
    with connection.cursor() as cursor:
        print("\n=== Creando procedimiento corregido ===")
        
        # Eliminar procedimiento existente
        cursor.execute("DROP PROCEDURE IF EXISTS get_paris_order_detail")
        
        # Crear procedimiento corregido
        sql = """
        CREATE PROCEDURE get_paris_order_detail(
            IN p_order_id VARCHAR(50)
        )
        BEGIN
            -- Consulta principal para la orden
            SELECT 
                po.id,
                po.id as order_id,
                po.origin,
                po.originOrderNumber,
                po.subOrderNumber,
                po.originInvoiceType,
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
                po.orden_impresa as printed,
                po.orden_procesada as processed
            FROM paris_orders po
            WHERE po.id = p_order_id;
            
            -- Consulta para los items
            SELECT 
                pi.id,
                pi.orderId,
                pi.subOrderNumber,
                pi.sku,
                pi.skuName,
                pi.quantity,
                pi.basePrice,
                pi.priceAfterDiscounts,
                pi.discountAmount,
                pi.discountPercentage,
                pi.taxAmount,
                pi.totalAmount
            FROM paris_items pi
            WHERE pi.orderId = p_order_id;
        END;
        """
        cursor.execute(sql)
        print("- Procedimiento creado correctamente")

def main():
    """Función principal"""
    print("=== VERIFICACIÓN DE PROCEDIMIENTO GET_PARIS_ORDER_DETAIL ===")
    
    # Verificar si se proporcionó un order_id como argumento
    if len(sys.argv) > 1:
        order_id = sys.argv[1]
    else:
        # Obtener un ID de orden de ejemplo
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM paris_orders LIMIT 1")
            result = cursor.fetchone()
            if result:
                order_id = result[0]
            else:
                print("No se encontraron órdenes en la base de datos")
                return
    
    print(f"Usando order_id: {order_id}")
    
    # Verificar si el procedimiento existe
    exists = check_procedure_exists()
    
    if exists:
        # Obtener definición
        get_procedure_definition()
        
        # Probar procedimiento directamente
        order_dict, items = test_procedure_direct(order_id)
        
        # Probar a través del servicio
        result = test_service(order_id)
        
        # Si hay problemas, corregir el procedimiento
        if not result or 'order_id' not in result['order'] or not result['order'].get('order_id'):
            create_fix_procedure()
            
            # Probar nuevamente
            print("\n=== Probando procedimiento corregido ===")
            order_dict, items = test_procedure_direct(order_id)
            result = test_service(order_id)
    else:
        # Crear el procedimiento si no existe
        create_fix_procedure()
        
        # Probar
        order_dict, items = test_procedure_direct(order_id)
        result = test_service(order_id)
    
    print("\n=== VERIFICACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main() 