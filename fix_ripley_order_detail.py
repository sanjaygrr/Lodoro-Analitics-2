#!/usr/bin/env python
"""
Script para corregir el procedimiento almacenado get_ripley_order_detail
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

def fix_ripley_order_detail_procedure():
    """Corregir el procedimiento get_ripley_order_detail"""
    with connection.cursor() as cursor:
        print("Corrigiendo procedimiento get_ripley_order_detail...")
        
        try:
            # Verificar la estructura de la tabla ripley_order_lines
            print("\nVerificando estructura de la tabla ripley_order_lines...")
            cursor.execute("DESCRIBE ripley_order_lines")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            print(f"Columnas disponibles: {', '.join(column_names)}")
            
            # Eliminar procedimiento existente
            print("\nEliminando procedimiento existente...")
            cursor.execute("DROP PROCEDURE IF EXISTS get_ripley_order_detail")
            
            # Crear procedimiento corregido
            print("\nCreando procedimiento corregido...")
            sql = """
            CREATE PROCEDURE get_ripley_order_detail(
                IN p_order_id VARCHAR(50)
            )
            BEGIN
                -- Consulta principal para la orden
                SELECT 
                    ro.order_id,
                    ro.commercial_id,
                    ro.created_date,
                    ro.last_updated_date,
                    ro.acceptance_decision_date,
                    ro.customer_debited_date,
                    ro.currency_iso_code,
                    ro.can_cancel,
                    ro.has_customer_message,
                    ro.has_incident,
                    ro.customer_id,
                    ro.leadtime_to_ship,
                    ro.order_state,
                    ro.order_state_reason_code,
                    ro.order_state_reason_label,
                    ro.payment_type,
                    ro.payment_workflow,
                    ro.price,
                    ro.shipping_price,
                    ro.shipping_type_code,
                    ro.shipping_type_label,
                    ro.shipping_zone_code,
                    ro.shipping_zone_label,
                    ro.total_commission,
                    ro.total_price,
                    ro.orden_impresa as printed,
                    ro.orden_procesada as processed
                FROM ripley_orders ro
                WHERE ro.order_id = p_order_id;
                
                -- Consulta para las líneas
                SELECT 
                    rol.order_line_id,
                    rol.order_id,
                    rol.order_line_index,
                    rol.offer_id,
                    rol.offer_sku,
                    rol.product_title,
                    rol.quantity,
                    rol.price,
                    rol.total_price,
                    rol.created_date,
                    rol.order_line_state
                FROM ripley_order_lines rol
                WHERE rol.order_id = p_order_id;
            END;
            """
            cursor.execute(sql)
            print("Procedimiento get_ripley_order_detail corregido exitosamente.")
            
            # Verificar que el procedimiento se haya creado correctamente
            print("\nVerificando procedimiento creado...")
            cursor.execute("SHOW CREATE PROCEDURE get_ripley_order_detail")
            procedure_def = cursor.fetchone()[2]
            print(f"Procedimiento creado:\n{procedure_def}")
            
        except Exception as e:
            print(f"Error al corregir el procedimiento: {e}", file=sys.stderr)
            return False
        
        return True

def test_procedure():
    """Probar el procedimiento corregido"""
    with connection.cursor() as cursor:
        print("\nProbando procedimiento get_ripley_order_detail...")
        
        try:
            # Obtener un ID de orden de ejemplo
            cursor.execute("SELECT order_id FROM ripley_orders LIMIT 1")
            result = cursor.fetchone()
            if not result:
                print("No se encontraron órdenes en la base de datos")
                return False
            
            order_id = result[0]
            print(f"Usando order_id: {order_id}")
            
            # Llamar al procedimiento
            cursor.execute(f"CALL get_ripley_order_detail(%s)", [order_id])
            
            # Obtener resultados de la orden
            order_columns = [col[0] for col in cursor.description]
            order_row = cursor.fetchone()
            
            if not order_row:
                print("No se encontró la orden")
                return False
            
            print(f"Orden encontrada con campos: {', '.join(order_columns)}")
            print(f"order_id en la respuesta: {dict(zip(order_columns, order_row)).get('order_id')}")
            
            # Verificar si hay líneas
            if cursor.nextset():
                lines_columns = [col[0] for col in cursor.description]
                lines_rows = cursor.fetchall()
                print(f"Líneas encontradas: {len(lines_rows)}")
                print(f"Campos de líneas: {', '.join(lines_columns)}")
                return True
            else:
                print("No se encontraron líneas")
                return False
                
        except Exception as e:
            print(f"Error al probar el procedimiento: {e}", file=sys.stderr)
            return False

if __name__ == "__main__":
    success = fix_ripley_order_detail_procedure()
    if success:
        test_success = test_procedure()
        if test_success:
            print("\n✅ Procedimiento get_ripley_order_detail corregido y probado exitosamente.")
        else:
            print("\n❌ El procedimiento get_ripley_order_detail fue corregido pero la prueba falló.")
    else:
        print("\n❌ No se pudo corregir el procedimiento get_ripley_order_detail.") 