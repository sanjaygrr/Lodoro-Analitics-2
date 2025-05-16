#!/usr/bin/env python
"""
Script para verificar la estructura de la tabla ripley_order_lines
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

def check_ripley_order_lines():
    """Verificar la estructura de la tabla ripley_order_lines"""
    with connection.cursor() as cursor:
        print("=== VERIFICACIÓN DE TABLA RIPLEY_ORDER_LINES ===\n")
        
        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'ripley_order_lines'")
        exists = cursor.fetchone() is not None
        print(f"Tabla ripley_order_lines existe: {exists}")
        
        if not exists:
            print("La tabla no existe.")
            return
        
        # Obtener estructura de la tabla
        cursor.execute("DESCRIBE ripley_order_lines")
        columns = cursor.fetchall()
        print("\n=== Estructura de la tabla ripley_order_lines ===")
        for col in columns:
            print(f"- {col[0]} ({col[1]})")
        
        # Obtener datos de muestra
        cursor.execute("SELECT * FROM ripley_order_lines LIMIT 5")
        rows = cursor.fetchall()
        column_names = [col[0] for col in cursor.description]
        
        print(f"\n=== Datos de muestra ({len(rows)} registros) ===")
        print(f"- Columnas: {', '.join(column_names)}")
        
        for i, row in enumerate(rows, 1):
            row_dict = dict(zip(column_names, row))
            print(f"  Registro #{i}: {row_dict}")

if __name__ == "__main__":
    check_ripley_order_lines() 