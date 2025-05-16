#!/usr/bin/env python
"""
Script para verificar la tabla bsale_references
"""
import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

def check_table_structure():
    """Verificar la estructura de la tabla bsale_references"""
    with connection.cursor() as cursor:
        cursor.execute("""
            DESCRIBE bsale_references
        """)
        columns = cursor.fetchall()
        
        print(f"\n=== Estructura de la tabla bsale_references ===")
        for col in columns:
            print(f"- {col[0]} ({col[1]})")
        
        return columns

def check_table_data(limit=10):
    """Verificar datos en la tabla bsale_references"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM bsale_references")
        count = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT * FROM bsale_references LIMIT {limit}")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
        print(f"\n=== Datos en la tabla bsale_references ===")
        print(f"- Total registros: {count}")
        print(f"- Columnas: {', '.join(columns)}")
        
        if rows:
            print(f"- Muestra de datos ({len(rows)} registros):")
            for i, row in enumerate(rows, 1):
                row_dict = dict(zip(columns, row))
                print(f"  Registro #{i}: {json.dumps(row_dict, default=str)}")
        else:
            print("- No hay datos en la tabla")
        
        return count, columns, rows

def check_references_for_orders():
    """Verificar referencias para órdenes de Paris y Ripley"""
    with connection.cursor() as cursor:
        # Verificar relación con Paris
        cursor.execute("""
            SELECT br.*, po.originOrderNumber, po.subOrderNumber
            FROM bsale_references br
            JOIN paris_orders po ON br.orderId = po.id
            LIMIT 5
        """)
        
        columns = [col[0] for col in cursor.description]
        paris_rows = cursor.fetchall()
        
        print(f"\n=== Referencias para órdenes de Paris ===")
        if paris_rows:
            print(f"- Encontradas {len(paris_rows)} referencias")
            for i, row in enumerate(paris_rows, 1):
                row_dict = dict(zip(columns, row))
                print(f"  Registro #{i}: {json.dumps(row_dict, default=str)}")
        else:
            print("- No se encontraron referencias para órdenes de Paris")
        
        # Verificar relación con Ripley
        try:
            cursor.execute("""
                SELECT br.*, ro.order_id, ro.commercial_id
                FROM bsale_references br
                JOIN ripley_orders ro ON br.orderId = ro.order_id
                LIMIT 5
            """)
            
            columns = [col[0] for col in cursor.description]
            ripley_rows = cursor.fetchall()
            
            print(f"\n=== Referencias para órdenes de Ripley ===")
            if ripley_rows:
                print(f"- Encontradas {len(ripley_rows)} referencias")
                for i, row in enumerate(ripley_rows, 1):
                    row_dict = dict(zip(columns, row))
                    print(f"  Registro #{i}: {json.dumps(row_dict, default=str)}")
            else:
                print("- No se encontraron referencias para órdenes de Ripley")
        except Exception as e:
            print(f"Error al buscar referencias de Ripley: {str(e)}")

def main():
    """Función principal"""
    print("=== VERIFICACIÓN DE TABLA BSALE_REFERENCES ===")
    
    # Verificar estructura
    check_table_structure()
    
    # Verificar datos
    check_table_data()
    
    # Verificar relaciones con órdenes
    check_references_for_orders()
    
    print("\n=== VERIFICACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main() 