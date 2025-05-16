import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

# Función para obtener la estructura de una tabla
def describe_table(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        print(f"\nEstructura de la tabla '{table_name}':")
        print("-" * 80)
        for column in columns:
            print(f"Columna: {column[0]}, Tipo: {column[1]}, Nulo: {column[2]}, Clave: {column[3]}, Default: {column[4]}")
        print("-" * 80)

# Tablas a inspeccionar
tables = [
    'paris_orders',
    'ripley_orders',
    'paris_items',
    'ripley_order_lines'
]

# Inspeccionar cada tabla
for table in tables:
    try:
        describe_table(table)
    except Exception as e:
        print(f"Error al inspeccionar la tabla '{table}': {e}")

print("\nInspección completada.") 