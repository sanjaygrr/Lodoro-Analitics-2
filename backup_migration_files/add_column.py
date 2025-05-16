import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

def check_column_exists(table_name, column_name):
    """Verificar si una columna existe en una tabla"""
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_NAME = '{table_name}' 
            AND COLUMN_NAME = '{column_name}'
        """)
        result = cursor.fetchone()
        return result[0] > 0

def add_column(table_name, column_name, column_definition):
    """Agregar una columna a una tabla si no existe"""
    if not check_column_exists(table_name, column_name):
        with connection.cursor() as cursor:
            print(f"Agregando columna {column_name} a la tabla {table_name}...")
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
            print(f"Columna {column_name} agregada exitosamente.")
    else:
        print(f"La columna {column_name} ya existe en la tabla {table_name}.")

# Agregar la columna orden_procesada a la tabla paris_orders
add_column('paris_orders', 'orden_procesada', 'TINYINT(1) DEFAULT 0')

print("Proceso completado.") 