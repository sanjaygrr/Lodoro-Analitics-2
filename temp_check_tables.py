"""
Script temporal para verificar la estructura de las tablas
"""
import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar después de configurar Django
from django.db import connection

def check_table_structure(table_name):
    """Verifica la estructura de una tabla"""
    print(f"\n=== Estructura de la tabla {table_name} ===")
    
    with connection.cursor() as cursor:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        for column in columns:
            print(f"{column[0]}: {column[1]}")

def check_table_data(table_name, limit=5):
    """Verifica los datos de una tabla"""
    print(f"\n=== Datos de la tabla {table_name} (primeros {limit} registros) ===")
    
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                print(json.dumps(data, indent=2, default=str))
                print("-" * 40)

if __name__ == "__main__":
    # Verificar estructura de tablas
    check_table_structure("ripley_customers")
    check_table_data("ripley_customers")
    
    check_table_structure("paris_orders")
    check_table_data("paris_orders", 1)
    
    check_table_structure("ripley_orders")
    check_table_data("ripley_orders", 1) 