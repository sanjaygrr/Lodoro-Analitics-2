#!/usr/bin/env python
"""
Script para corregir el procedimiento almacenado get_paris_order_detail
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

def fix_paris_order_detail_procedure():
    """Corregir el procedimiento get_paris_order_detail"""
    with connection.cursor() as cursor:
        print("Corrigiendo procedimiento get_paris_order_detail...")
        
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
                pi.sku,
                pi.name,
                pi.subOrderNumber,
                pi.basePrice,
                pi.grossPrice,
                pi.priceAfterDiscounts,
                pi.taxRate,
                pi.size,
                pi.tax,
                pi.position
            FROM paris_items pi
            WHERE pi.orderId = p_order_id;
        END;
        """
        cursor.execute(sql)
        print("Procedimiento get_paris_order_detail corregido.")

def test_procedure():
    """Probar el procedimiento corregido"""
    with connection.cursor() as cursor:
        print("\nProbando procedimiento get_paris_order_detail...")
        
        # Obtener un ID de orden de ejemplo
        cursor.execute("SELECT id FROM paris_orders LIMIT 1")
        result = cursor.fetchone()
        if not result:
            print("No se encontraron órdenes en la base de datos")
            return
        
        order_id = result[0]
        print(f"Usando order_id: {order_id}")
        
        # Llamar al procedimiento
        cursor.execute(f"CALL get_paris_order_detail(%s)", [order_id])
        
        # Obtener resultados de la orden
        order_columns = [col[0] for col in cursor.description]
        order_row = cursor.fetchone()
        
        if not order_row:
            print("No se encontró la orden")
            return
        
        print(f"Orden encontrada con campos: {', '.join(order_columns)}")
        print(f"order_id en la respuesta: {dict(zip(order_columns, order_row)).get('order_id')}")
        
        # Verificar si hay items
        if cursor.nextset():
            items_columns = [col[0] for col in cursor.description]
            items_rows = cursor.fetchall()
            print(f"Items encontrados: {len(items_rows)}")
            print(f"Campos de items: {', '.join(items_columns)}")
        else:
            print("No se encontraron items")

def fix_ripley_order_detail_procedure():
    """Corregir el procedimiento get_ripley_order_detail"""
    with connection.cursor() as cursor:
        print("\nCorrigiendo procedimiento get_ripley_order_detail...")
        
        # Eliminar procedimiento existente
        cursor.execute("DROP PROCEDURE IF EXISTS get_ripley_order_detail")
        
        # Crear procedimiento corregido
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
                rol.id,
                rol.order_id,
                rol.order_line_id,
                rol.offer_id,
                rol.offer_sku,
                rol.product_title,
                rol.quantity,
                rol.price,
                rol.total_price,
                rol.created_date,
                rol.state
            FROM ripley_order_lines rol
            WHERE rol.order_id = p_order_id;
        END;
        """
        cursor.execute(sql)
        print("Procedimiento get_ripley_order_detail corregido.")

if __name__ == "__main__":
    fix_paris_order_detail_procedure()
    test_procedure()
    fix_ripley_order_detail_procedure() 