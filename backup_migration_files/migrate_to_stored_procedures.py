#!/usr/bin/env python
"""
Script para realizar la migración a funciones almacenadas MySQL en Lodoro Analytics.
Este script realiza los siguientes pasos:
1. Crea la tabla de historial de cambios de estado
2. Crea los procedimientos almacenados para gestión de órdenes
3. Ejecuta algunas pruebas básicas para verificar su funcionamiento
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
print("Configurando Django...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar módulos necesarios
print("Importando módulos...")
from django.db import connection
from django.contrib.auth.models import User

# Paso 1: Crear la tabla de historial
print("\n========== Paso 1: Crear tabla de historial ==========")
from create_order_management_functions import create_order_status_history_table
create_order_status_history_table()

# Paso 2: Crear procedimientos almacenados para órdenes
print("\n========== Paso 2: Crear procedimientos almacenados ==========")
from create_order_management_functions import (
    create_get_paris_orders_procedure,
    create_get_ripley_orders_procedure,
    create_get_paris_order_detail_procedure,
    create_get_ripley_order_detail_procedure,
    create_update_paris_order_status_procedure,
    create_update_ripley_order_status_procedure,
    create_get_order_stats_procedure
)

# Crear procedimientos para obtener órdenes
create_get_paris_orders_procedure()
create_get_ripley_orders_procedure()

# Crear procedimientos para detalles de órdenes
create_get_paris_order_detail_procedure()
create_get_ripley_order_detail_procedure()

# Crear procedimientos para actualizar estados
create_update_paris_order_status_procedure()
create_update_ripley_order_status_procedure()

# Crear procedimiento para estadísticas
create_get_order_stats_procedure()

# Paso 3: Probar los procedimientos almacenados
print("\n========== Paso 3: Pruebas básicas ==========")
from order_db_utils import OrderManager

# Probar obtención de estadísticas
print("\nProbando estadísticas...")
stats = OrderManager.get_order_stats()
print(f"Total de órdenes: {stats['summary']['total']}")
print(f"- Paris: {stats['paris']['total']}")
print(f"- Ripley: {stats['ripley']['total']}")

# Probar listado de órdenes (tomamos solo 1 para verificar que funciona)
print("\nProbando listado de órdenes Paris...")
paris_orders = OrderManager.get_paris_orders(limit=1)
print(f"Total de órdenes Paris: {paris_orders['total']}")

print("\nProbando listado de órdenes Ripley...")
ripley_orders = OrderManager.get_ripley_orders(limit=1)
print(f"Total de órdenes Ripley: {ripley_orders['total']}")

# Paso 4: Información sobre próximos pasos
print("\n========== Migración completada ==========")
print("""
La migración de consultas SQL directas a procedimientos almacenados ha sido completada.

Para usar estos procedimientos en tus vistas de Django:
1. Importa la clase OrderManager:
   from order_db_utils import OrderManager

2. Usa los métodos de OrderManager en tus vistas. Por ejemplo:
   orders = OrderManager.get_paris_orders()
   
3. Puedes ver ejemplos de implementación en el archivo:
   marketplace/views_stored_procs.py

Beneficios de esta migración:
- Mayor rendimiento
- Menor transferencia de datos
- Lógica centralizada en la base de datos
- Mejor mantenibilidad
- Registro de historial de cambios

Para obtener más detalles sobre los procedimientos disponibles,
consulta los archivos create_order_management_functions.py y order_db_utils.py.
""")

# Crear registro en la base de datos para documentar la migración
print("\nRegistrando migración en la base de datos...")
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
    
    cursor.execute("""
        INSERT INTO system_migrations (name, description, executed_at, executed_by)
        VALUES (%s, %s, %s, %s)
    """, [
        'migrate_to_stored_procedures',
        'Migración de consultas SQL directas a procedimientos almacenados',
        datetime.now(),
        os.environ.get('USER', 'unknown')
    ])

print("Migración registrada correctamente.\n")
print("Proceso completado con éxito.") 