import os
import django
import sys
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

def use_get_marketplace_stats():
    """Ejemplo de uso de la función get_marketplace_stats"""
    with connection.cursor() as cursor:
        # Llamar a la función almacenada
        cursor.execute("SELECT get_marketplace_stats(%s)", ['paris'])
        paris_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT get_marketplace_stats(%s)", ['ripley'])
        ripley_count = cursor.fetchone()[0]
        
        print(f"Total de órdenes de Paris: {paris_count}")
        print(f"Total de órdenes de Ripley: {ripley_count}")
        print(f"Total general: {paris_count + ripley_count}")
    
    return paris_count, ripley_count

def use_calculate_order_value(order_id, marketplace):
    """Ejemplo de uso de la función calculate_order_value"""
    with connection.cursor() as cursor:
        # Llamar a la función almacenada
        cursor.execute("SELECT calculate_order_value(%s, %s)", [order_id, marketplace])
        order_value = cursor.fetchone()[0]
        
        print(f"Valor total de la orden {order_id} ({marketplace}): ${order_value}")
    
    return order_value

def use_update_order_status(order_id, marketplace, new_status, processed_by):
    """Ejemplo de uso del procedimiento update_order_status"""
    with connection.cursor() as cursor:
        # Declarar variables para los parámetros OUT
        cursor.execute("SET @p_success = FALSE")
        cursor.execute("SET @p_message = ''")
        
        # Llamar al procedimiento almacenado
        cursor.execute(
            "CALL update_order_status(%s, %s, %s, %s, @p_success, @p_message)",
            [order_id, marketplace, new_status, processed_by]
        )
        
        # Obtener los valores de los parámetros OUT
        cursor.execute("SELECT @p_success, @p_message")
        success, message = cursor.fetchone()
        
        print(f"Resultado: {'Éxito' if success else 'Error'}")
        print(f"Mensaje: {message}")
    
    return success, message

def use_generate_daily_report(date):
    """Ejemplo de uso del procedimiento generate_daily_report"""
    with connection.cursor() as cursor:
        # Declarar variables para los parámetros OUT
        cursor.execute("SET @p_total_orders = 0")
        cursor.execute("SET @p_total_paris = 0")
        cursor.execute("SET @p_total_ripley = 0")
        
        # Llamar al procedimiento almacenado
        cursor.execute(
            "CALL generate_daily_report(%s, @p_total_orders, @p_total_paris, @p_total_ripley)",
            [date]
        )
        
        # Obtener los valores de los parámetros OUT
        cursor.execute("SELECT @p_total_orders, @p_total_paris, @p_total_ripley")
        total_orders, total_paris, total_ripley = cursor.fetchone()
        
        print(f"Reporte diario para {date}:")
        print(f"Total de órdenes: {total_orders}")
        print(f"Total de órdenes de Paris: {total_paris}")
        print(f"Total de órdenes de Ripley: {total_ripley}")
    
    return total_orders, total_paris, total_ripley

# Ejemplo de uso
if __name__ == "__main__":
    print("=== Usando funciones almacenadas ===")
    use_get_marketplace_stats()
    
    # Estos ejemplos requieren IDs válidos en tu base de datos
    # use_calculate_order_value('ORD123456', 'paris')
    
    print("\n=== Usando procedimientos almacenados ===")
    # use_update_order_status('ORD123456', 'paris', 'PROCESSED', 1)
    
    # Generar reporte para hoy
    today = datetime.now().date()
    use_generate_daily_report(today)
    
    print("\nProceso completado.") 