import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

def check_function_exists(function_name):
    """Verificar si una función existe en la base de datos"""
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.ROUTINES 
            WHERE ROUTINE_TYPE = 'FUNCTION' 
            AND ROUTINE_NAME = '{function_name}'
            AND ROUTINE_SCHEMA = DATABASE()
        """)
        result = cursor.fetchone()
        return result[0] > 0

def check_procedure_exists(procedure_name):
    """Verificar si un procedimiento existe en la base de datos"""
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.ROUTINES 
            WHERE ROUTINE_TYPE = 'PROCEDURE' 
            AND ROUTINE_NAME = '{procedure_name}'
            AND ROUTINE_SCHEMA = DATABASE()
        """)
        result = cursor.fetchone()
        return result[0] > 0

# ==================== FUNCIONES PARA OBTENER ÓRDENES ====================

def create_get_paris_orders_procedure():
    """Crear procedimiento para obtener órdenes de Paris"""
    procedure_name = 'get_paris_orders'
    
    if not check_procedure_exists(procedure_name):
        print(f"Creando procedimiento '{procedure_name}'...")
        with connection.cursor() as cursor:
            cursor.execute(f"DROP PROCEDURE IF EXISTS {procedure_name}")
            
            cursor.execute("""
                CREATE PROCEDURE get_paris_orders(
                    IN p_limit INT,
                    IN p_offset INT,
                    IN p_status VARCHAR(50),
                    IN p_date_from DATE,
                    IN p_date_to DATE,
                    OUT p_total_count INT
                )
                BEGIN
                    -- Declarar variables
                    DECLARE where_clause VARCHAR(500) DEFAULT '';
                    
                    -- Construir cláusula WHERE dinámica
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
                    
                    -- Obtener total de registros para paginación
                    SET @count_sql = CONCAT("
                        SELECT COUNT(*) INTO @total_count
                        FROM paris_orders po
                        WHERE 1=1 ", where_clause
                    );
                    
                    PREPARE stmt FROM @count_sql;
                    EXECUTE stmt;
                    DEALLOCATE PREPARE stmt;
                    
                    SET p_total_count = @total_count;
                    
                    -- Consulta principal con paginación
                    SET @main_sql = CONCAT("
                        SELECT 
                            po.id,
                            po.originOrderNumber,
                            po.subOrderNumber,
                            po.originOrderDate,
                            po.createdAt,
                            po.customer_name,
                            po.customer_email,
                            po.billing_firstName,
                            po.billing_lastName,
                            po.billing_address1,
                            po.billing_city,
                            po.billing_phone,
                            po.orden_impresa,
                            po.orden_procesada,
                            (SELECT COUNT(*) FROM paris_items pi WHERE pi.orderId = po.id) AS total_items,
                            (SELECT SUM(pi.priceAfterDiscounts) FROM paris_items pi WHERE pi.orderId = po.id) AS total_amount
                        FROM paris_orders po
                        WHERE 1=1 ", 
                        where_clause,
                        " ORDER BY po.createdAt DESC
                        LIMIT ", p_limit, " OFFSET ", p_offset
                    );
                    
                    PREPARE stmt FROM @main_sql;
                    EXECUTE stmt;
                    DEALLOCATE PREPARE stmt;
                END;
            """)
            print(f"Procedimiento '{procedure_name}' creado exitosamente.")
    else:
        print(f"El procedimiento '{procedure_name}' ya existe.")

def create_get_ripley_orders_procedure():
    """Crear procedimiento para obtener órdenes de Ripley"""
    procedure_name = 'get_ripley_orders'
    
    if not check_procedure_exists(procedure_name):
        print(f"Creando procedimiento '{procedure_name}'...")
        with connection.cursor() as cursor:
            cursor.execute(f"DROP PROCEDURE IF EXISTS {procedure_name}")
            
            cursor.execute("""
                CREATE PROCEDURE get_ripley_orders(
                    IN p_limit INT,
                    IN p_offset INT,
                    IN p_status VARCHAR(50),
                    IN p_date_from DATE,
                    IN p_date_to DATE,
                    OUT p_total_count INT
                )
                BEGIN
                    -- Declarar variables
                    DECLARE where_clause VARCHAR(500) DEFAULT '';
                    
                    -- Construir cláusula WHERE dinámica
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
                    
                    -- Obtener total de registros para paginación
                    SET @count_sql = CONCAT("
                        SELECT COUNT(*) INTO @total_count
                        FROM ripley_orders ro
                        WHERE 1=1 ", where_clause
                    );
                    
                    PREPARE stmt FROM @count_sql;
                    EXECUTE stmt;
                    DEALLOCATE PREPARE stmt;
                    
                    SET p_total_count = @total_count;
                    
                    -- Consulta principal con paginación
                    SET @main_sql = CONCAT("
                        SELECT 
                            ro.order_id,
                            ro.commercial_id,
                            ro.created_date,
                            ro.last_updated_date,
                            ro.customer_id,
                            ro.order_state,
                            ro.payment_type,
                            ro.shipping_price,
                            ro.total_price,
                            ro.orden_impresa,
                            ro.orden_procesada,
                            (SELECT COUNT(*) FROM ripley_order_lines rol WHERE rol.order_id = ro.order_id) AS total_items
                        FROM ripley_orders ro
                        WHERE 1=1 ", 
                        where_clause,
                        " ORDER BY ro.created_date DESC
                        LIMIT ", p_limit, " OFFSET ", p_offset
                    );
                    
                    PREPARE stmt FROM @main_sql;
                    EXECUTE stmt;
                    DEALLOCATE PREPARE stmt;
                END;
            """)
            print(f"Procedimiento '{procedure_name}' creado exitosamente.")
    else:
        print(f"El procedimiento '{procedure_name}' ya existe.")

# ==================== FUNCIONES PARA DETALLES DE ÓRDENES ====================

def create_get_paris_order_detail_procedure():
    """Crear procedimiento para obtener detalles de una orden de Paris"""
    procedure_name = 'get_paris_order_detail'
    
    if not check_procedure_exists(procedure_name):
        print(f"Creando procedimiento '{procedure_name}'...")
        with connection.cursor() as cursor:
            cursor.execute(f"DROP PROCEDURE IF EXISTS {procedure_name}")
            
            cursor.execute("""
                CREATE PROCEDURE get_paris_order_detail(
                    IN p_order_id VARCHAR(100)
                )
                BEGIN
                    -- Obtener información de la orden
                    SELECT *
                    FROM paris_orders
                    WHERE id = p_order_id OR subOrderNumber = p_order_id;
                    
                    -- Obtener items de la orden
                    SELECT *
                    FROM paris_items
                    WHERE orderId = (
                        SELECT id FROM paris_orders 
                        WHERE id = p_order_id OR subOrderNumber = p_order_id
                        LIMIT 1
                    );
                END;
            """)
            print(f"Procedimiento '{procedure_name}' creado exitosamente.")
    else:
        print(f"El procedimiento '{procedure_name}' ya existe.")

def create_get_ripley_order_detail_procedure():
    """Crear procedimiento para obtener detalles de una orden de Ripley"""
    procedure_name = 'get_ripley_order_detail'
    
    if not check_procedure_exists(procedure_name):
        print(f"Creando procedimiento '{procedure_name}'...")
        with connection.cursor() as cursor:
            cursor.execute(f"DROP PROCEDURE IF EXISTS {procedure_name}")
            
            cursor.execute("""
                CREATE PROCEDURE get_ripley_order_detail(
                    IN p_order_id VARCHAR(100)
                )
                BEGIN
                    -- Obtener información de la orden
                    SELECT *
                    FROM ripley_orders
                    WHERE order_id = p_order_id;
                    
                    -- Obtener líneas de la orden
                    SELECT *
                    FROM ripley_order_lines
                    WHERE order_id = p_order_id;
                END;
            """)
            print(f"Procedimiento '{procedure_name}' creado exitosamente.")
    else:
        print(f"El procedimiento '{procedure_name}' ya existe.")

# ==================== FUNCIONES PARA ACTUALIZAR ESTADOS ====================

def create_update_paris_order_status_procedure():
    """Crear procedimiento para actualizar el estado de una orden de Paris"""
    procedure_name = 'update_paris_order_status'
    
    if not check_procedure_exists(procedure_name):
        print(f"Creando procedimiento '{procedure_name}'...")
        with connection.cursor() as cursor:
            cursor.execute(f"DROP PROCEDURE IF EXISTS {procedure_name}")
            
            cursor.execute("""
                CREATE PROCEDURE update_paris_order_status(
                    IN p_order_id VARCHAR(100),
                    IN p_processed BOOLEAN,
                    IN p_printed BOOLEAN,
                    IN p_user_id INT,
                    OUT p_success BOOLEAN,
                    OUT p_message VARCHAR(255)
                )
                BEGIN
                    DECLARE order_exists INT DEFAULT 0;
                    DECLARE order_real_id VARCHAR(36);
                    
                    -- Verificar si la orden existe y obtener su ID real
                    SELECT COUNT(*), id INTO order_exists, order_real_id
                    FROM paris_orders
                    WHERE id = p_order_id OR subOrderNumber = p_order_id
                    LIMIT 1;
                    
                    IF order_exists > 0 THEN
                        -- Actualizar estado de la orden
                        UPDATE paris_orders
                        SET 
                            orden_procesada = CASE WHEN p_processed IS NOT NULL THEN p_processed ELSE orden_procesada END,
                            orden_impresa = CASE WHEN p_printed IS NOT NULL THEN p_printed ELSE orden_impresa END,
                            last_updated_by = p_user_id,
                            last_updated_at = NOW()
                        WHERE id = order_real_id;
                        
                        -- Registrar historial de cambios
                        INSERT INTO order_status_history (
                            order_id, 
                            marketplace, 
                            previous_processed_status,
                            new_processed_status,
                            previous_printed_status,
                            new_printed_status,
                            user_id, 
                            created_at
                        )
                        SELECT 
                            id,
                            'paris',
                            -- Solo para el historial, asumimos valores previos
                            CASE WHEN p_processed IS NULL THEN NULL 
                                 ELSE NOT p_processed END,
                            p_processed,
                            CASE WHEN p_printed IS NULL THEN NULL 
                                 ELSE NOT p_printed END,
                            p_printed,
                            p_user_id,
                            NOW()
                        FROM paris_orders
                        WHERE id = order_real_id;
                        
                        SET p_success = TRUE;
                        SET p_message = CONCAT('Orden Paris ', p_order_id, ' actualizada correctamente.');
                    ELSE
                        SET p_success = FALSE;
                        SET p_message = CONCAT('La orden Paris ', p_order_id, ' no existe.');
                    END IF;
                END;
            """)
            print(f"Procedimiento '{procedure_name}' creado exitosamente.")
    else:
        print(f"El procedimiento '{procedure_name}' ya existe.")

def create_update_ripley_order_status_procedure():
    """Crear procedimiento para actualizar el estado de una orden de Ripley"""
    procedure_name = 'update_ripley_order_status'
    
    if not check_procedure_exists(procedure_name):
        print(f"Creando procedimiento '{procedure_name}'...")
        with connection.cursor() as cursor:
            cursor.execute(f"DROP PROCEDURE IF EXISTS {procedure_name}")
            
            cursor.execute("""
                CREATE PROCEDURE update_ripley_order_status(
                    IN p_order_id VARCHAR(100),
                    IN p_processed BOOLEAN,
                    IN p_printed BOOLEAN,
                    IN p_user_id INT,
                    OUT p_success BOOLEAN,
                    OUT p_message VARCHAR(255)
                )
                BEGIN
                    DECLARE order_exists INT DEFAULT 0;
                    
                    -- Verificar si la orden existe
                    SELECT COUNT(*) INTO order_exists
                    FROM ripley_orders
                    WHERE order_id = p_order_id;
                    
                    IF order_exists > 0 THEN
                        -- Actualizar estado de la orden
                        UPDATE ripley_orders
                        SET 
                            orden_procesada = CASE WHEN p_processed IS NOT NULL THEN p_processed ELSE orden_procesada END,
                            orden_impresa = CASE WHEN p_printed IS NOT NULL THEN p_printed ELSE orden_impresa END,
                            last_updated_by = p_user_id,
                            last_updated_date = NOW()
                        WHERE order_id = p_order_id;
                        
                        -- Registrar historial de cambios
                        INSERT INTO order_status_history (
                            order_id, 
                            marketplace, 
                            previous_processed_status,
                            new_processed_status,
                            previous_printed_status,
                            new_printed_status,
                            user_id, 
                            created_at
                        )
                        SELECT 
                            order_id,
                            'ripley',
                            -- Solo para el historial, asumimos valores previos
                            CASE WHEN p_processed IS NULL THEN NULL 
                                 ELSE NOT p_processed END,
                            p_processed,
                            CASE WHEN p_printed IS NULL THEN NULL 
                                 ELSE NOT p_printed END,
                            p_printed,
                            p_user_id,
                            NOW()
                        FROM ripley_orders
                        WHERE order_id = p_order_id;
                        
                        SET p_success = TRUE;
                        SET p_message = CONCAT('Orden Ripley ', p_order_id, ' actualizada correctamente.');
                    ELSE
                        SET p_success = FALSE;
                        SET p_message = CONCAT('La orden Ripley ', p_order_id, ' no existe.');
                    END IF;
                END;
            """)
            print(f"Procedimiento '{procedure_name}' creado exitosamente.")
    else:
        print(f"El procedimiento '{procedure_name}' ya existe.")

# ==================== FUNCIONES PARA ESTADÍSTICAS Y REPORTES ====================

def create_get_order_stats_procedure():
    """Crear procedimiento para obtener estadísticas de órdenes"""
    procedure_name = 'get_order_stats'
    
    if not check_procedure_exists(procedure_name):
        print(f"Creando procedimiento '{procedure_name}'...")
        with connection.cursor() as cursor:
            cursor.execute(f"DROP PROCEDURE IF EXISTS {procedure_name}")
            
            cursor.execute("""
                CREATE PROCEDURE get_order_stats(
                    IN p_date_from DATE,
                    IN p_date_to DATE,
                    OUT p_total_paris INT,
                    OUT p_total_ripley INT,
                    OUT p_paris_processed INT,
                    OUT p_paris_printed INT,
                    OUT p_ripley_processed INT,
                    OUT p_ripley_printed INT
                )
                BEGIN
                    -- Estadísticas de Paris
                    SELECT 
                        COUNT(*),
                        SUM(CASE WHEN orden_procesada = TRUE THEN 1 ELSE 0 END),
                        SUM(CASE WHEN orden_impresa = TRUE THEN 1 ELSE 0 END)
                    INTO 
                        p_total_paris, p_paris_processed, p_paris_printed
                    FROM paris_orders
                    WHERE 
                        (p_date_from IS NULL OR createdAt >= p_date_from) AND
                        (p_date_to IS NULL OR createdAt <= p_date_to);
                    
                    -- Estadísticas de Ripley
                    SELECT 
                        COUNT(*),
                        SUM(CASE WHEN orden_procesada = TRUE THEN 1 ELSE 0 END),
                        SUM(CASE WHEN orden_impresa = TRUE THEN 1 ELSE 0 END)
                    INTO 
                        p_total_ripley, p_ripley_processed, p_ripley_printed
                    FROM ripley_orders
                    WHERE 
                        (p_date_from IS NULL OR created_date >= p_date_from) AND
                        (p_date_to IS NULL OR created_date <= p_date_to);
                END;
            """)
            print(f"Procedimiento '{procedure_name}' creado exitosamente.")
    else:
        print(f"El procedimiento '{procedure_name}' ya existe.")

# ==================== CREAR TABLA DE HISTORIAL ====================

def create_order_status_history_table():
    """Crear tabla para almacenar el historial de cambios de estado de órdenes"""
    print("Verificando si la tabla 'order_status_history' existe...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.TABLES 
            WHERE TABLE_NAME = 'order_status_history'
        """)
        result = cursor.fetchone()
        
        if result[0] == 0:
            print("Creando tabla 'order_status_history'...")
            cursor.execute("""
                CREATE TABLE `order_status_history` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `order_id` varchar(100) NOT NULL,
                    `marketplace` varchar(50) NOT NULL,
                    `previous_processed_status` boolean,
                    `new_processed_status` boolean,
                    `previous_printed_status` boolean,
                    `new_printed_status` boolean,
                    `user_id` int,
                    `created_at` datetime NOT NULL,
                    PRIMARY KEY (`id`),
                    KEY `order_status_history_order_id_idx` (`order_id`),
                    KEY `order_status_history_user_id_idx` (`user_id`),
                    KEY `order_status_history_marketplace_idx` (`marketplace`),
                    CONSTRAINT `order_status_history_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """)
            print("Tabla 'order_status_history' creada exitosamente.")
        else:
            print("La tabla 'order_status_history' ya existe.")

# ==================== EJECUTAR CREACIÓN DE FUNCIONES Y PROCEDIMIENTOS ====================

def main():
    # Crear tabla de historial (necesaria para los procedimientos de actualización)
    create_order_status_history_table()
    
    # Crear procedimientos para obtener órdenes
    create_get_paris_orders_procedure()
    create_get_ripley_orders_procedure()
    
    # Crear procedimientos para detalles de órdenes
    create_get_paris_order_detail_procedure()
    create_get_ripley_order_detail_procedure()
    
    # Crear procedimientos para actualizar estados
    create_update_paris_order_status_procedure()
    create_update_ripley_order_status_procedure()
    
    # Crear procedimientos para estadísticas
    create_get_order_stats_procedure()
    
    print("Proceso completado.")

if __name__ == "__main__":
    main() 