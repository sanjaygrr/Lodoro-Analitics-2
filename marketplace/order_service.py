"""
Servicio para gestión de órdenes utilizando procedimientos almacenados
"""
from django.db import connection
import logging
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)

class OrderService:
    """
    Servicio para gestionar órdenes utilizando procedimientos almacenados
    """
    
    @staticmethod
    def create_stored_procedures():
        """
        Crea o actualiza los procedimientos almacenados necesarios para el servicio
        """
        with connection.cursor() as cursor:
            # Procedimiento para obtener detalles de una orden de Paris con información de Bsale
            cursor.execute("""
                DROP PROCEDURE IF EXISTS get_paris_order_detail_with_bsale;
            """)
            cursor.execute("""
                CREATE PROCEDURE get_paris_order_detail_with_bsale(IN p_order_id VARCHAR(50))
                BEGIN
                    -- Obtener datos de la orden
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
                        -- Información adicional para mostrar en la pantalla
                        CONCAT(po.billing_firstName, ' ', po.billing_lastName) AS full_name,
                        CONCAT(po.billing_address1, ' ', IFNULL(po.billing_address2, '')) AS full_address,
                        po.billing_city AS city,
                        po.billing_stateCode AS state,
                        po.billing_phone AS phone,
                        po.customer_email AS email,
                        -- Totales para mostrar en la pantalla
                        (SELECT SUM(pi.priceAfterDiscounts) FROM paris_items pi WHERE pi.orderId = po.id) AS products_total,
                        (SELECT SUM(pi.grossPrice) FROM paris_items pi WHERE pi.orderId = po.id) AS order_total
                    FROM paris_orders po
                    WHERE po.id = p_order_id OR po.originOrderNumber = p_order_id OR po.subOrderNumber = p_order_id;
                    
                    -- Obtener los items de la orden con información de Bsale
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
                    WHERE pi.orderId = p_order_id;
                END
            """)
            
            # Procedimiento para obtener detalles de una orden de Ripley con información de Bsale
            cursor.execute("""
                DROP PROCEDURE IF EXISTS get_ripley_order_detail_with_bsale;
            """)
            cursor.execute("""
                CREATE PROCEDURE get_ripley_order_detail_with_bsale(IN p_order_id VARCHAR(50))
                BEGIN
                    -- Obtener datos de la orden (solo de la tabla ripley_orders)
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
                        ro.commercial_id AS boleta_number,
                        'https://example.com/boleta/' AS boleta_url,
                        ro.orden_impresa,
                        ro.orden_procesada,
                        -- Información adicional del cliente usando los nombres correctos de columnas
                        rc.firstname AS first_name,
                        rc.lastname AS last_name,
                        -- Información adicional para mostrar en la pantalla
                        CONCAT(rc.firstname, ' ', rc.lastname) AS full_name,
                        ro.shipping_zone_label AS address_commune,
                        ro.shipping_zone_label AS address_city,
                        ro.shipping_zone_code AS address_region,
                        -- Totales para mostrar en la pantalla
                        (ro.total_price - ro.shipping_price) AS products_total,
                        ro.total_price AS order_total
                    FROM ripley_orders ro
                    LEFT JOIN ripley_customers rc ON ro.customer_id = rc.customer_id
                    WHERE ro.order_id = p_order_id OR ro.commercial_id = p_order_id;
                    
                    -- Obtener las líneas de la orden con información de Bsale
                    -- Usando los nombres correctos de columnas según la estructura de la tabla
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
                    WHERE rol.order_id = p_order_id;
                END
            """)
    
    @staticmethod
    def get_orders(marketplace, limit=50, offset=0, status=None, date_from=None, date_to=None):
        """
        Obtiene las órdenes de un marketplace específico
        """
        if marketplace not in ['paris', 'ripley']:
            return {'orders': [], 'total': 0}
        
        with connection.cursor() as cursor:
            # Determinar el procedimiento a llamar según el marketplace
            procedure_name = f"get_{marketplace}_orders"
            
            # Preparar los parámetros
            params = [limit, offset]
            
            # Añadir parámetros opcionales
            if status:
                params.append(status)
            else:
                params.append(None)
                
            if date_from:
                params.append(date_from.strftime('%Y-%m-%d'))
            else:
                params.append(None)
                
            if date_to:
                params.append(date_to.strftime('%Y-%m-%d'))
            else:
                params.append(None)
            
            # Para procedimientos que esperan un parámetro de salida (OUT)
            # Inicializar la variable de salida
            cursor.execute("SET @p_total_count = 0")
            
            # Ejecutar el procedimiento con el parámetro OUT
            query = f"CALL {procedure_name}({', '.join(['%s'] * len(params))}, @p_total_count)"
            cursor.execute(query, params)
            
            # Obtener los resultados
            orders = []
            if cursor.description:  # Verificar si hay resultados
                columns = [col[0] for col in cursor.description]
                
                # Debug para ver qué columnas se están devolviendo
                logger.debug(f"{marketplace}: Primer registro: {columns}")
                
                for row in cursor.fetchall():
                    order = dict(zip(columns, row))
                    orders.append(order)
            
            # Obtener el valor del parámetro OUT
            cursor.execute("SELECT @p_total_count")
            total_result = cursor.fetchone()
            total = total_result[0] if total_result else 0
            
            # Debug para ver cuántos registros se recuperaron
            logger.debug(f"{marketplace}: Total registros: {total}, Recuperados: {len(orders)}")
            
            return {
                'orders': orders,
                'total': total
            }
    
    @staticmethod
    def get_order_detail(marketplace, order_id):
        """
        Obtiene los detalles de una orden específica
        """
        if marketplace not in ['paris', 'ripley']:
            return None
        
        # Asegurar que order_id sea string para evitar problemas con bytes
        order_id = str(order_id)
        
        with connection.cursor() as cursor:
            # Crear un diccionario para almacenar los resultados
            result = {'order': None, 'items': []}
            
            if marketplace == 'ripley':
                # Consulta para obtener los datos de la orden de Ripley
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
                        
                        /* Número de Boleta - Buscar en Bsale */
                        (SELECT bd.number 
                         FROM bsale_documents bd 
                         LEFT JOIN bsale_references br ON bd.id = br.document_id 
                         WHERE br.number = ro.commercial_id OR br.number = ro.order_id 
                         LIMIT 1) AS boleta_number,
                        
                        /* URL de Boleta - Buscar en Bsale */
                        (SELECT CONCAT('https://app.bsale.cl/view/2/', bd.id) 
                         FROM bsale_documents bd 
                         LEFT JOIN bsale_references br ON bd.id = br.document_id 
                         WHERE br.number = ro.commercial_id OR br.number = ro.order_id 
                         LIMIT 1) AS boleta_url,
                        
                        ro.orden_impresa,
                        ro.orden_procesada,
                        rc.firstname AS first_name,
                        rc.lastname AS last_name,
                        CONCAT(rc.firstname, ' ', rc.lastname) AS full_name,
                        ro.shipping_zone_label AS address_commune,
                        ro.shipping_zone_label AS address_city,
                        ro.shipping_zone_code AS address_region,
                        
                        /* Totales con impuestos y despacho */
                        ro.price AS subtotal_sin_iva,
                        ROUND(ro.price * 0.19, 0) AS iva,
                        ro.price AS productos_sin_iva,
                        ROUND(ro.price * 1.19, 0) AS productos_con_iva,
                        ro.shipping_price AS despacho,
                        (ro.total_price - ro.shipping_price) AS products_total,
                        ro.total_price AS order_total,
                        ROUND(ro.total_price * 1.19, 0) AS total_con_iva
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
                        return None
                
                # Consulta para obtener los items de la orden de Ripley
                cursor.execute("""
                    SELECT 
                        rol.order_line_id,
                        rol.order_id,
                        rol.product_sku AS sku,
                        
                        /* SKU correcto y código Bsale */
                        COALESCE(bv.code, rol.product_sku) AS codigo_bsale,
                        COALESCE(bv.barCode, rol.product_sku) AS codigo_barras,
                        
                        rol.product_title AS product_name,
                        rol.quantity,
                        rol.price_unit AS unit_price,
                        ROUND(rol.price_unit * 1.19, 0) AS unit_price_con_iva,
                        rol.total_price,
                        ROUND(rol.total_price * 1.19, 0) AS total_price_con_iva,
                        rol.order_line_state,
                        bv.id AS bsale_variant_id,
                        bv.barCode AS bsale_barcode,
                        bv.code AS bsale_code,
                        bp.name AS bsale_product_name,
                        
                        /* Información adicional para vinculación */
                        CASE 
                            WHEN bv.id IS NOT NULL THEN 1 
                            ELSE 0 
                        END AS vinculado_bsale
                    FROM ripley_order_lines rol
                    LEFT JOIN bsale_variants bv ON rol.product_sku = bv.barCode OR rol.product_sku = bv.code
                    LEFT JOIN bsale_products bp ON bv.product_id = bp.id
                    WHERE rol.order_id = %s
                """, [order_id])
            
            else:  # marketplace == 'paris'
                # Consulta para obtener los datos de la orden de Paris
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
                        
                        /* Número de Boleta - Buscar en Bsale */
                        COALESCE(
                            (SELECT bd.number 
                             FROM bsale_documents bd 
                             LEFT JOIN bsale_references br ON bd.id = br.document_id 
                             WHERE br.number = po.originOrderNumber OR br.number = po.subOrderNumber 
                             LIMIT 1), 
                            po.originOrderNumber
                        ) AS boleta_number,
                        
                        /* URL de Boleta - Buscar en Bsale */
                        COALESCE(
                            (SELECT CONCAT('https://app.bsale.cl/view/2/', bd.id) 
                             FROM bsale_documents bd 
                             LEFT JOIN bsale_references br ON bd.id = br.document_id 
                             WHERE br.number = po.originOrderNumber OR br.number = po.subOrderNumber 
                             LIMIT 1),
                            'https://example.com/boleta/'
                        ) AS boleta_url,
                        
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
                        
                        /* Totales con impuestos y despacho */
                        (SELECT SUM(pi.priceAfterDiscounts) FROM paris_items pi WHERE pi.orderId = po.id) AS products_total,
                        (SELECT SUM(pi.grossPrice) FROM paris_items pi WHERE pi.orderId = po.id) AS order_total,
                        ROUND((SELECT SUM(pi.priceAfterDiscounts) FROM paris_items pi WHERE pi.orderId = po.id) / 1.19, 0) AS total_sin_iva,
                        ROUND((SELECT SUM(pi.priceAfterDiscounts) FROM paris_items pi WHERE pi.orderId = po.id) * 0.19, 0) AS iva,
                        
                        /* Buscar información de despacho en los items */
                        COALESCE(
                            (SELECT SUM(pi.priceAfterDiscounts) 
                             FROM paris_items pi 
                             WHERE pi.orderId = po.id AND LOWER(pi.name) LIKE '%despacho%'), 
                            0
                        ) AS despacho,
                        
                        /* Total con IVA */
                        (SELECT SUM(pi.grossPrice) FROM paris_items pi WHERE pi.orderId = po.id) AS total_con_iva
                    FROM paris_orders po
                    WHERE po.id = %s OR po.originOrderNumber = %s OR po.subOrderNumber = %s
                """, [order_id, order_id, order_id])
                
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    order_row = cursor.fetchone()
                    
                    if order_row:
                        result['order'] = dict(zip(columns, order_row))
                    else:
                        return None
                
                # Consulta para obtener los items de la orden de Paris
                cursor.execute("""
                    SELECT 
                        pi.id AS item_id,
                        pi.sku,
                        
                        /* SKU correcto y código Bsale */
                        COALESCE(bv.code, pi.sku) AS codigo_bsale,
                        COALESCE(bv.barCode, pi.sku) AS codigo_barras,
                        
                        pi.name,
                        pi.position AS quantity,
                        pi.priceAfterDiscounts,
                        ROUND(pi.priceAfterDiscounts / 1.19, 0) AS precio_sin_iva,
                        ROUND(pi.priceAfterDiscounts * 0.19, 0) AS iva_item,
                        pi.grossPrice AS totalPrice,
                        bv.id AS bsale_variant_id,
                        bv.barCode AS bsale_barcode,
                        bv.code AS bsale_code,
                        bp.name AS bsale_product_name,
                        
                        /* Distinguir si es producto de despacho */
                        CASE 
                            WHEN LOWER(pi.name) LIKE '%despacho%' THEN 1 
                            ELSE 0 
                        END AS es_despacho,
                        
                        /* Información adicional para vinculación */
                        CASE 
                            WHEN bv.id IS NOT NULL THEN 1 
                            ELSE 0 
                        END AS vinculado_bsale
                    FROM paris_items pi
                    LEFT JOIN bsale_variants bv ON pi.sku = bv.barCode OR pi.sku = bv.code
                    LEFT JOIN bsale_products bp ON bv.product_id = bp.id
                    WHERE pi.orderId = %s
                """, [order_id])
            
            # Procesar los items
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    result['items'].append(item)
            
            return result
    
    @staticmethod
    def update_order_status(marketplace, order_id, processed=None, printed=None, user_id=None):
        """
        Actualiza el estado de una orden
        """
        if marketplace not in ['paris', 'ripley']:
            return False, "Marketplace no válido"
        
        with connection.cursor() as cursor:
            # Determinar el procedimiento a llamar según el marketplace
            procedure_name = f"update_{marketplace}_order_status"
            
            # Preparar los parámetros
            params = [order_id]
            
            # Añadir parámetros opcionales
            if processed is not None:
                params.append(1 if processed else 0)
            else:
                params.append(None)
                
            if printed is not None:
                params.append(1 if printed else 0)
            else:
                params.append(None)
                
            if user_id is not None:
                params.append(user_id)
            else:
                params.append(None)
            
            # Ejecutar el procedimiento
            cursor.callproc(procedure_name, params)
            
            # Verificar el resultado
            cursor.nextset()  # Saltar el primer resultado (que es None)
            result = cursor.fetchone()
            
            success = result[0] == 1 if result else False
            message = result[1] if result and len(result) > 1 else "Operación completada"
            
            return success, message
    
    @staticmethod
    def get_order_stats(date_from=None, date_to=None):
        """
        Obtiene estadísticas de órdenes
        """
        # Valores por defecto
        if not date_from:
            date_from = datetime.now().date() - timedelta(days=30)
        if not date_to:
            date_to = datetime.now().date()
        
        with connection.cursor() as cursor:
            # Ejecutar el procedimiento
            cursor.callproc("get_order_stats", [
                date_from.strftime('%Y-%m-%d'),
                date_to.strftime('%Y-%m-%d')
            ])
            
            # Obtener los resultados
            cursor.nextset()  # Saltar el primer resultado (que es None)
            
            # Estadísticas generales
            general_stats = {}
            if cursor.description:  # Verificar si hay resultados
                columns = [col[0] for col in cursor.description]
                row = cursor.fetchone()
                if row:
                    general_stats = dict(zip(columns, row))
            
            # Estadísticas por día
            cursor.nextset()
            daily_stats = []
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    stat = dict(zip(columns, row))
                    daily_stats.append(stat)
            
            # Estadísticas por marketplace
            cursor.nextset()
            marketplace_stats = []
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    stat = dict(zip(columns, row))
                    marketplace_stats.append(stat)
            
            return {
                'general': general_stats,
                'daily': daily_stats,
                'marketplace': marketplace_stats
            } 