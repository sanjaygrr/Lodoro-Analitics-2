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

def create_get_marketplace_stats_function():
    """Crear una función que devuelve estadísticas de órdenes por marketplace"""
    function_name = 'get_marketplace_stats'
    
    if not check_function_exists(function_name):
        print(f"Creando función '{function_name}'...")
        with connection.cursor() as cursor:
            # Borrar la función si existe para recrearla
            cursor.execute(f"DROP FUNCTION IF EXISTS {function_name}")
            
            # Crear la función
            cursor.execute("""
                CREATE FUNCTION get_marketplace_stats(marketplace_name VARCHAR(50)) 
                RETURNS INT
                DETERMINISTIC
                READS SQL DATA
                BEGIN
                    DECLARE total_orders INT;
                    
                    SELECT COUNT(*) INTO total_orders 
                    FROM lodoro_order_scan 
                    WHERE marketplace = marketplace_name;
                    
                    RETURN total_orders;
                END;
            """)
            print(f"Función '{function_name}' creada exitosamente.")
    else:
        print(f"La función '{function_name}' ya existe.")

def create_calculate_order_value_function():
    """Crear una función que calcula el valor total de una orden"""
    function_name = 'calculate_order_value'
    
    if not check_function_exists(function_name):
        print(f"Creando función '{function_name}'...")
        with connection.cursor() as cursor:
            # Borrar la función si existe para recrearla
            cursor.execute(f"DROP FUNCTION IF EXISTS {function_name}")
            
            # Crear la función
            cursor.execute("""
                CREATE FUNCTION calculate_order_value(p_order_id VARCHAR(50), p_marketplace VARCHAR(50)) 
                RETURNS DECIMAL(10,2)
                DETERMINISTIC
                READS SQL DATA
                BEGIN
                    DECLARE total_value DECIMAL(10,2);
                    
                    -- Este es un ejemplo. La implementación real dependerá de tu estructura de datos
                    -- Lógica para Paris
                    IF p_marketplace = 'paris' THEN
                        SELECT COALESCE(SUM(pi.price * pi.quantity), 0) INTO total_value
                        FROM paris_items pi
                        JOIN paris_orders po ON pi.order_id = po.id
                        WHERE po.id = p_order_id;
                    
                    -- Lógica para Ripley
                    ELSEIF p_marketplace = 'ripley' THEN
                        SELECT COALESCE(SUM(rol.unit_price * rol.quantity), 0) INTO total_value
                        FROM ripley_order_lines rol
                        WHERE rol.order_id = p_order_id;
                    
                    ELSE
                        SET total_value = 0;
                    END IF;
                    
                    RETURN total_value;
                END;
            """)
            print(f"Función '{function_name}' creada exitosamente.")
    else:
        print(f"La función '{function_name}' ya existe.")

# Crear funciones almacenadas
create_get_marketplace_stats_function()
create_calculate_order_value_function()

print("Proceso completado.") 