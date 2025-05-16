#!/usr/bin/env python
"""
Script para diagnosticar problemas con las órdenes
"""
import os
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection
from marketplace.order_service import OrderService

def check_table_exists(table_name):
    """Verificar si una tabla existe"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = %s
        """, [table_name])
        return cursor.fetchone()[0] > 0

def check_table_data(table_name, limit=5):
    """Verificar datos en una tabla"""
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
            print(f"\n=== Tabla {table_name} ===")
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

def test_direct_procedure(marketplace, limit=5):
    """Probar procedimiento almacenado directamente"""
    with connection.cursor() as cursor:
        try:
            print(f"\n=== Probando procedimiento get_{marketplace}_orders directamente ===")
            
            # Inicializar variable para el total
            cursor.execute("SET @p_total = 0")
            
            # Llamar al procedimiento
            cursor.execute(f"CALL get_{marketplace}_orders(%s, %s, %s, %s, %s, @p_total)", 
                           [limit, 0, None, None, None])
            
            # Obtener resultados
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
            # Obtener total
            cursor.execute("SELECT @p_total")
            total = cursor.fetchone()[0]
            
            print(f"- Total registros: {total}")
            print(f"- Columnas devueltas: {', '.join(columns)}")
            
            if rows:
                print(f"- Registros recuperados: {len(rows)}")
                for i, row in enumerate(rows, 1):
                    row_dict = dict(zip(columns, row))
                    print(f"  Registro #{i}: {json.dumps(row_dict, default=str)[:150]}...")
            else:
                print("- No se recuperaron registros")
                
            return total, columns, rows
        except Exception as e:
            print(f"Error al ejecutar procedimiento get_{marketplace}_orders: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0, [], []

def test_order_service(marketplace, limit=5):
    """Probar servicio de órdenes"""
    print(f"\n=== Probando OrderService.get_orders('{marketplace}') ===")
    try:
        result = OrderService.get_orders(marketplace, limit=limit)
        
        print(f"- Total reportado: {result['total']}")
        print(f"- Órdenes recuperadas: {len(result['orders'])}")
        
        if result['orders']:
            print(f"- Campos disponibles: {list(result['orders'][0].keys())}")
            for i, order in enumerate(result['orders'], 1):
                print(f"  Orden #{i}: {json.dumps(order, default=str)[:150]}...")
        else:
            print("- No se recuperaron órdenes")
            
        return result
    except Exception as e:
        print(f"Error al usar OrderService.get_orders('{marketplace}'): {str(e)}")
        import traceback
        traceback.print_exc()
        return {'orders': [], 'total': 0}

def main():
    """Función principal"""
    print("=== DIAGNÓSTICO DE ÓRDENES ===")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar tablas
    paris_exists = check_table_exists('paris_orders')
    ripley_exists = check_table_exists('ripley_orders')
    
    print(f"\nTabla paris_orders existe: {paris_exists}")
    print(f"Tabla ripley_orders existe: {ripley_exists}")
    
    # Verificar datos en tablas
    if paris_exists:
        check_table_data('paris_orders')
    
    if ripley_exists:
        check_table_data('ripley_orders')
    
    # Probar procedimientos directamente
    test_direct_procedure('paris')
    test_direct_procedure('ripley')
    
    # Probar a través del servicio
    test_order_service('paris')
    test_order_service('ripley')
    
    print("\n=== DIAGNÓSTICO COMPLETADO ===")

if __name__ == "__main__":
    main() 