import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

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

def create_update_order_status_procedure():
    """Crear un procedimiento almacenado para actualizar el estado de una orden"""
    procedure_name = 'update_order_status'
    
    if not check_procedure_exists(procedure_name):
        print(f"Creando procedimiento '{procedure_name}'...")
        with connection.cursor() as cursor:
            # Borrar el procedimiento si existe para recrearlo
            cursor.execute(f"DROP PROCEDURE IF EXISTS {procedure_name}")
            
            # Crear el procedimiento
            cursor.execute("""
                CREATE PROCEDURE update_order_status(
                    IN p_order_id VARCHAR(100),
                    IN p_marketplace VARCHAR(50),
                    IN p_new_status VARCHAR(50),
                    IN p_processed_by INT,
                    OUT p_success BOOLEAN,
                    OUT p_message VARCHAR(255)
                )
                BEGIN
                    DECLARE order_exists INT DEFAULT 0;
                    
                    -- Verificar si la orden existe
                    SELECT COUNT(*) INTO order_exists
                    FROM lodoro_order_scan
                    WHERE order_id = p_order_id AND marketplace = p_marketplace;
                    
                    IF order_exists > 0 THEN
                        -- Actualizar el estado de la orden
                        UPDATE lodoro_order_scan
                        SET status = p_new_status,
                            processed_by_id = p_processed_by,
                            processed_at = NOW()
                        WHERE order_id = p_order_id AND marketplace = p_marketplace;
                        
                        SET p_success = TRUE;
                        SET p_message = CONCAT('Orden ', p_order_id, ' actualizada correctamente.');
                    ELSE
                        SET p_success = FALSE;
                        SET p_message = CONCAT('La orden ', p_order_id, ' no existe.');
                    END IF;
                END;
            """)
            print(f"Procedimiento '{procedure_name}' creado exitosamente.")
    else:
        print(f"El procedimiento '{procedure_name}' ya existe.")

def create_generate_daily_report_procedure():
    """Crear un procedimiento almacenado para generar reportes diarios"""
    procedure_name = 'generate_daily_report'
    
    if not check_procedure_exists(procedure_name):
        print(f"Creando procedimiento '{procedure_name}'...")
        with connection.cursor() as cursor:
            # Borrar el procedimiento si existe para recrearlo
            cursor.execute(f"DROP PROCEDURE IF EXISTS {procedure_name}")
            
            # Crear el procedimiento
            cursor.execute("""
                CREATE PROCEDURE generate_daily_report(
                    IN p_date DATE,
                    OUT p_total_orders INT,
                    OUT p_total_paris INT,
                    OUT p_total_ripley INT
                )
                BEGIN
                    -- Calcular estadísticas del día
                    SELECT COUNT(*) INTO p_total_orders
                    FROM lodoro_order_scan
                    WHERE DATE(created_at) = p_date;
                    
                    SELECT COUNT(*) INTO p_total_paris
                    FROM lodoro_order_scan
                    WHERE DATE(created_at) = p_date AND marketplace = 'paris';
                    
                    SELECT COUNT(*) INTO p_total_ripley
                    FROM lodoro_order_scan
                    WHERE DATE(created_at) = p_date AND marketplace = 'ripley';
                    
                    -- Opcionalmente, podríamos insertar estos datos en una tabla de reportes
                    -- pero aquí solo los devolvemos como parámetros de salida
                END;
            """)
            print(f"Procedimiento '{procedure_name}' creado exitosamente.")
    else:
        print(f"El procedimiento '{procedure_name}' ya existe.")

# Crear procedimientos almacenados
create_update_order_status_procedure()
create_generate_daily_report_procedure()

print("Proceso completado.") 