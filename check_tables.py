#!/usr/bin/env python
"""
Script para verificar tablas relacionadas con bsale y boletas
"""
import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

def list_tables():
    """Listar todas las tablas en la base de datos"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n=== Tablas en la base de datos ({len(tables)}) ===")
        for table in tables:
            print(f"- {table}")
        
        return tables

def find_bsale_tables():
    """Buscar tablas relacionadas con bsale"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            AND table_name LIKE '%bsale%'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n=== Tablas relacionadas con bsale ({len(tables)}) ===")
        for table in tables:
            print(f"- {table}")
        
        return tables

def check_table_structure(table_name):
    """Verificar la estructura de una tabla"""
    with connection.cursor() as cursor:
        cursor.execute(f"""
            DESCRIBE {table_name}
        """)
        columns = cursor.fetchall()
        
        print(f"\n=== Estructura de la tabla {table_name} ===")
        for col in columns:
            print(f"- {col[0]} ({col[1]})")
        
        return columns

def check_table_data(table_name, limit=5):
    """Verificar datos en una tabla"""
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
            print(f"\n=== Datos en la tabla {table_name} ===")
            print(f"- Total registros: {count}")
            print(f"- Columnas: {', '.join(columns)}")
            
            if rows:
                print(f"- Muestra de datos ({len(rows)} registros):")
                for i, row in enumerate(rows, 1):
                    row_dict = dict(zip(columns, row))
                    print(f"  Registro #{i}: {json.dumps(row_dict, default=str)[:150]}...")
            else:
                print("- No hay datos en la tabla")
                
            return count, columns, rows
        except Exception as e:
            print(f"Error al consultar tabla {table_name}: {str(e)}")
            return 0, [], []

def find_boleta_related_columns():
    """Buscar columnas relacionadas con boletas en todas las tablas"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
            AND (column_name LIKE '%boleta%' OR column_name LIKE '%bsale%' OR column_name LIKE '%number%')
            ORDER BY table_name, column_name
        """)
        columns = cursor.fetchall()
        
        print(f"\n=== Columnas relacionadas con boletas ({len(columns)}) ===")
        current_table = None
        for table, column in columns:
            if table != current_table:
                print(f"\n- Tabla: {table}")
                current_table = table
            print(f"  - {column}")
        
        return columns

def main():
    """Función principal"""
    print("=== VERIFICACIÓN DE TABLAS DE BOLETAS ===")
    
    # Listar todas las tablas
    tables = list_tables()
    
    # Buscar tablas relacionadas con bsale
    bsale_tables = find_bsale_tables()
    
    # Buscar columnas relacionadas con boletas
    boleta_columns = find_boleta_related_columns()
    
    # Verificar estructura de tablas específicas
    if 'bsale_documents' in tables:
        check_table_structure('bsale_documents')
        check_table_data('bsale_documents')
    
    if 'bsale_document_details' in tables:
        check_table_structure('bsale_document_details')
        check_table_data('bsale_document_details')
    
    if 'paris_orders' in tables:
        check_table_structure('paris_orders')
    
    if 'ripley_orders' in tables:
        check_table_structure('ripley_orders')
    
    print("\n=== VERIFICACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main() 