#!/usr/bin/env python
"""
Script para corregir los procedimientos almacenados
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

def fix_paris_orders_procedure():
    """Corregir el procedimiento get_paris_orders"""
    with connection.cursor() as cursor:
        print("Corrigiendo procedimiento get_paris_orders...")
        
        # Eliminar procedimiento existente
        cursor.execute("DROP PROCEDURE IF EXISTS get_paris_orders")
        
        # Crear procedimiento corregido
        sql = """
        CREATE PROCEDURE get_paris_orders(
            IN p_limit INT,
            IN p_offset INT,
            IN p_status VARCHAR(50),
            IN p_date_from DATE,
            IN p_date_to DATE,
            OUT p_total_count INT
        )
        BEGIN
            -- Variables
            DECLARE where_clause VARCHAR(500) DEFAULT '';
            
            -- Construir filtros
            IF p_status IS NOT NULL THEN
                IF p_status = 'NUEVA' THEN
                    SET where_clause = CONCAT(where_clause, " AND (po.orden_procesada = FALSE OR po.orden_procesada IS NULL) ");
                ELSEIF p_status = 'PROCESADA' THEN
                    SET where_clause = CONCAT(where_clause, " AND po.orden_procesada = TRUE ");
                ELSEIF p_status = 'IMPRESA' THEN
                    SET where_clause = CONCAT(where_clause, " AND po.orden_impresa = TRUE ");
                ELSEIF p_status = 'NO_IMPRESA' THEN
                    SET where_clause = CONCAT(where_clause, " AND (po.orden_impresa = FALSE OR po.orden_impresa IS NULL) ");
                END IF;
            END IF;
            
            IF p_date_from IS NOT NULL THEN
                SET where_clause = CONCAT(where_clause, " AND po.createdAt >= '", p_date_from, "' ");
            END IF;
            
            IF p_date_to IS NOT NULL THEN
                SET where_clause = CONCAT(where_clause, " AND po.createdAt <= '", p_date_to, "' ");
            END IF;
            
            -- Contar registros
            SET @sql_count = CONCAT('SELECT COUNT(*) INTO @total FROM paris_orders po WHERE 1=1 ', where_clause);
            PREPARE stmt_count FROM @sql_count;
            EXECUTE stmt_count;
            DEALLOCATE PREPARE stmt_count;
            
            SET p_total_count = @total;
            
            -- Consulta principal (simplificada para evitar problemas)
            SET @sql_main = CONCAT('
                SELECT 
                    po.id as order_id,
                    po.originOrderNumber,
                    po.subOrderNumber,
                    po.originOrderDate,
                    po.createdAt,
                    po.customer_name,
                    po.customer_email,
                    po.orden_impresa,
                    po.orden_procesada,
                    (SELECT SUM(pi.priceAfterDiscounts) FROM paris_items pi WHERE pi.orderId = po.id) AS total_amount,
                    (SELECT GROUP_CONCAT(DISTINCT bd.number) 
                     FROM bsale_references br 
                     JOIN bsale_documents bd ON br.document_id = bd.id 
                     WHERE br.number = po.subOrderNumber OR br.number LIKE CONCAT("%", po.subOrderNumber, "%")) AS boleta_number,
                    (SELECT GROUP_CONCAT(DISTINCT bd.urlPdfOriginal) 
                     FROM bsale_references br 
                     JOIN bsale_documents bd ON br.document_id = bd.id 
                     WHERE br.number = po.subOrderNumber OR br.number LIKE CONCAT("%", po.subOrderNumber, "%")) AS boleta_url
                FROM paris_orders po
                WHERE 1=1 ', 
                where_clause, 
                ' ORDER BY po.createdAt DESC
                LIMIT ', p_limit, ' OFFSET ', p_offset
            );
            
            PREPARE stmt_main FROM @sql_main;
            EXECUTE stmt_main;
            DEALLOCATE PREPARE stmt_main;
        END;
        """
        cursor.execute(sql)
        print("Procedimiento get_paris_orders corregido.")

def create_get_ripley_orders_procedure():
    """Crear procedimiento get_ripley_orders"""
    with connection.cursor() as cursor:
        print("Corrigiendo procedimiento get_ripley_orders...")
        
        # Eliminar procedimiento existente
        cursor.execute("DROP PROCEDURE IF EXISTS get_ripley_orders")
        
        # Crear procedimiento
        sql = """
        CREATE PROCEDURE get_ripley_orders(
            IN p_limit INT,
            IN p_offset INT,
            IN p_status VARCHAR(50),
            IN p_date_from DATE,
            IN p_date_to DATE,
            OUT p_total_count INT
        )
        BEGIN
            -- Variables
            DECLARE where_clause VARCHAR(500) DEFAULT '';

            -- Construir filtros
            IF p_status IS NOT NULL THEN
                IF p_status = 'NUEVA' THEN
                    SET where_clause = CONCAT(where_clause, " AND (ro.orden_procesada = FALSE OR ro.orden_procesada IS NULL) ");
                ELSEIF p_status = 'PROCESADA' THEN
                    SET where_clause = CONCAT(where_clause, " AND ro.orden_procesada = TRUE ");
                ELSEIF p_status = 'IMPRESA' THEN
                    SET where_clause = CONCAT(where_clause, " AND ro.orden_impresa = TRUE ");
                ELSEIF p_status = 'NO_IMPRESA' THEN
                    SET where_clause = CONCAT(where_clause, " AND (ro.orden_impresa = FALSE OR ro.orden_impresa IS NULL) ");
                END IF;
            END IF;

            IF p_date_from IS NOT NULL THEN
                SET where_clause = CONCAT(where_clause, " AND ro.created_date >= '", p_date_from, "' "); 
            END IF;

            IF p_date_to IS NOT NULL THEN
                SET where_clause = CONCAT(where_clause, " AND ro.created_date <= '", p_date_to, "' ");

            END IF;

            -- Contar registros
            SET @sql_count = CONCAT('SELECT COUNT(*) INTO @total FROM ripley_orders ro WHERE 1=1 ', where_clause);
            PREPARE stmt_count FROM @sql_count;
            EXECUTE stmt_count;
            DEALLOCATE PREPARE stmt_count;

            SET p_total_count = @total;

            -- Consulta principal (simplificada para evitar problemas)
            SET @sql_main = CONCAT('
                SELECT
                    ro.order_id,
                    ro.commercial_id,
                    ro.created_date,
                    ro.order_state,
                    ro.payment_type,
                    ro.total_price as total_amount,
                    ro.orden_impresa,
                    ro.orden_procesada,
                    ro.shipping_type_label,
                    ro.shipping_zone_label,
                    (SELECT GROUP_CONCAT(DISTINCT bd.number)
                     FROM bsale_references br
                     JOIN bsale_documents bd ON br.document_id = bd.id
                     WHERE br.number = ro.commercial_id OR br.number LIKE CONCAT("%", ro.commercial_id, "%")) AS boleta_number,
                    (SELECT GROUP_CONCAT(DISTINCT bd.urlPdfOriginal)
                     FROM bsale_references br
                     JOIN bsale_documents bd ON br.document_id = bd.id
                     WHERE br.number = ro.commercial_id OR br.number LIKE CONCAT("%", ro.commercial_id, "%")) AS boleta_url
                FROM ripley_orders ro
                WHERE 1=1 ',
                where_clause,
                ' ORDER BY ro.created_date DESC
                LIMIT ', p_limit, ' OFFSET ', p_offset
            );

            PREPARE stmt_main FROM @sql_main;
            EXECUTE stmt_main;
            DEALLOCATE PREPARE stmt_main;
        END;
        """
        cursor.execute(sql)
        print("Procedimiento get_ripley_orders corregido.")

def test_procedures():
    """Probar que los procedimientos funcionen correctamente"""
    with connection.cursor() as cursor:
        # Probar get_paris_orders
        print("\nProbando get_paris_orders...")
        
        # Inicializar variable para el total
        cursor.execute("SET @p_total = 0")
        
        # Llamar al procedimiento
        cursor.execute("CALL get_paris_orders(10, 0, NULL, NULL, NULL, @p_total)")
        
        # Obtener resultados
        rows = cursor.fetchall()
        paris_count = len(rows)
        
        # Obtener el total
        cursor.execute("SELECT @p_total")
        total = cursor.fetchone()[0]
        
        print(f"- Total registros: {total}")
        print(f"- Registros recuperados: {paris_count}")
        
        # Probar get_ripley_orders
        print("\nProbando get_ripley_orders...")
        
        # Inicializar variable para el total
        cursor.execute("SET @p_total = 0")
        
        # Llamar al procedimiento
        cursor.execute("CALL get_ripley_orders(10, 0, NULL, NULL, NULL, @p_total)")
        
        # Obtener resultados
        rows = cursor.fetchall()
        ripley_count = len(rows)
        
        # Obtener el total
        cursor.execute("SELECT @p_total")
        total = cursor.fetchone()[0]
        
        print(f"- Total registros: {total}")
        print(f"- Registros recuperados: {ripley_count}")
        
        return paris_count, ripley_count

if __name__ == "__main__":
    fix_paris_orders_procedure()
    create_get_ripley_orders_procedure()
    
    paris_count, ripley_count = test_procedures()
    
    if paris_count > 0 or ripley_count > 0:
        print("\n✅ Los procedimientos almacenados están funcionando correctamente.")
        print(f"- Paris: {paris_count} órdenes recuperadas")
        print(f"- Ripley: {ripley_count} órdenes recuperadas")
    else:
        print("\n❌ Los procedimientos se han corregido pero no hay datos para mostrar.")
        print("Ejecuta los siguientes comandos para verificar si hay datos en las tablas:")
        print("1. python manage.py shell")
        print("2. from django.db import connection")
        print("3. cursor = connection.cursor()")
        print("4. cursor.execute('SELECT COUNT(*) FROM paris_orders')")
        print("5. cursor.fetchone()")
        print("6. cursor.execute('SELECT COUNT(*) FROM ripley_orders')")
        print("7. cursor.fetchone()") 