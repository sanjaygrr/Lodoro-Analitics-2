#!/usr/bin/env python
"""
Script para completar la migración a procedimientos almacenados
Este script:
1. Crea todos los procedimientos almacenados necesarios
2. Verifica que todos los procedimientos se hayan creado
3. Actualiza la tabla de migración con el cambio
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
print("Configurando Django...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

# Importar funciones para crear procedimientos almacenados
from create_order_management_functions import (
    create_get_paris_orders_procedure,
    create_get_ripley_orders_procedure,
    create_get_paris_order_detail_procedure,
    create_get_ripley_order_detail_procedure,
    create_update_paris_order_status_procedure,
    create_update_ripley_order_status_procedure,
    create_get_order_stats_procedure,
    create_order_status_history_table
)

# Importar servicio de analytics
from analytics.stored_procedure_service import AnalyticsService

def create_system_migration_table():
    """Crear tabla para registrar migraciones del sistema"""
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `system_migrations` (
                `id` int NOT NULL AUTO_INCREMENT,
                `name` varchar(100) NOT NULL,
                `description` text,
                `executed_at` datetime NOT NULL,
                `executed_by` varchar(50),
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
        """)
    print("Tabla de migraciones verificada/creada.")

def register_migration(name, description):
    """Registrar una migración en la base de datos"""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO system_migrations (name, description, executed_at, executed_by)
            VALUES (%s, %s, %s, %s)
        """, [
            name,
            description,
            datetime.now(),
            os.environ.get('USER', 'unknown')
        ])
    print(f"Migración '{name}' registrada correctamente.")

def check_all_procedures():
    """Verificar que todos los procedimientos necesarios existan"""
    required_procedures = [
        'get_paris_orders',
        'get_ripley_orders',
        'get_paris_order_detail',
        'get_ripley_order_detail',
        'update_paris_order_status',
        'update_ripley_order_status',
        'get_order_stats',
        'get_product_performance'
    ]
    
    all_exist = True
    missing = []
    
    with connection.cursor() as cursor:
        for proc in required_procedures:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.ROUTINES 
                WHERE ROUTINE_TYPE = 'PROCEDURE' 
                AND ROUTINE_NAME = %s
                AND ROUTINE_SCHEMA = DATABASE()
            """, [proc])
            
            if cursor.fetchone()[0] == 0:
                all_exist = False
                missing.append(proc)
    
    return all_exist, missing

def main():
    """Función principal"""
    print("Iniciando migración completa a procedimientos almacenados...")
    
    # Paso 1: Crear tabla de migraciones
    print("\n=== Paso 1: Crear tabla para registrar migraciones ===")
    create_system_migration_table()
    
    # Paso 2: Crear tabla de historial de cambios de estado
    print("\n=== Paso 2: Crear tabla de historial de cambios de estado ===")
    create_order_status_history_table()
    
    # Paso 3: Crear procedimientos almacenados para marketplace
    print("\n=== Paso 3: Crear procedimientos almacenados para marketplace ===")
    create_get_paris_orders_procedure()
    create_get_ripley_orders_procedure()
    create_get_paris_order_detail_procedure()
    create_get_ripley_order_detail_procedure()
    create_update_paris_order_status_procedure()
    create_update_ripley_order_status_procedure()
    create_get_order_stats_procedure()
    
    # Paso 4: Crear procedimientos almacenados para analytics
    print("\n=== Paso 4: Crear procedimientos almacenados para analytics ===")
    AnalyticsService.create_product_performance_procedure()
    
    # Paso 5: Verificar todos los procedimientos
    print("\n=== Paso 5: Verificar procedimientos ===")
    all_exist, missing = check_all_procedures()
    
    if all_exist:
        print("Todos los procedimientos almacenados necesarios están instalados.")
    else:
        print(f"ADVERTENCIA: Faltan los siguientes procedimientos: {', '.join(missing)}")
        print("Por favor, revise los errores y vuelva a ejecutar el script.")
        sys.exit(1)
    
    # Paso 6: Registrar la migración
    print("\n=== Paso 6: Registrar migración ===")
    register_migration(
        "complete_migration_to_stored_procedures", 
        "Migración completa a procedimientos almacenados para marketplace y analytics"
    )
    
    print("\n=== Migración completada con éxito ===")
    print("""
RESUMEN:
- Se han creado todos los procedimientos almacenados necesarios
- Se ha creado la tabla de historial de cambios de estado
- Se ha registrado la migración en la base de datos

PASOS SIGUIENTES:
1. En los templates, actualice los enlaces a las vistas:
   - Use /analytics/dashboard/sp/ en lugar de /analytics/dashboard/
   - Use /analytics/products/sp/ en lugar de /analytics/products/

2. Para volver al sistema anterior, puede seguir utilizando las rutas originales

Todas las vistas están preparadas para utilizar procedimientos almacenados,
lo que mejora el rendimiento y facilita el mantenimiento del sistema.
""")

if __name__ == "__main__":
    main()