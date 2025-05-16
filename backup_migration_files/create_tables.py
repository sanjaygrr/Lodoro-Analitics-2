import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

def check_table_exists(table_name):
    """Verificar si una tabla existe en la base de datos"""
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.TABLES 
            WHERE TABLE_NAME = '{table_name}'
        """)
        result = cursor.fetchone()
        return result[0] > 0

def create_api_status_table():
    """Crear la tabla lodoro_api_status si no existe"""
    if not check_table_exists('lodoro_api_status'):
        print("Creando tabla 'lodoro_api_status'...")
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE `lodoro_api_status` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `name` varchar(100) NOT NULL,
                    `status` varchar(50) NOT NULL,
                    `last_check` datetime NOT NULL,
                    `error_message` longtext,
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """)
            print("Tabla 'lodoro_api_status' creada exitosamente.")
    else:
        print("La tabla 'lodoro_api_status' ya existe.")

def create_order_scan_table():
    """Crear la tabla lodoro_order_scan si no existe"""
    if not check_table_exists('lodoro_order_scan'):
        print("Creando tabla 'lodoro_order_scan'...")
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE `lodoro_order_scan` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `order_id` varchar(100) NOT NULL,
                    `marketplace` varchar(50) NOT NULL,
                    `status` varchar(50) NOT NULL,
                    `processed_at` datetime DEFAULT NULL,
                    `created_at` datetime NOT NULL,
                    `notes` longtext,
                    `paris_order_id` varchar(36) DEFAULT NULL,
                    `processed_by_id` int DEFAULT NULL,
                    `ripley_order_id` varchar(50) DEFAULT NULL,
                    PRIMARY KEY (`id`),
                    KEY `lodoro_order_scan_paris_order_id_fk` (`paris_order_id`),
                    KEY `lodoro_order_scan_processed_by_id_fk` (`processed_by_id`),
                    KEY `lodoro_order_scan_ripley_order_id_fk` (`ripley_order_id`),
                    CONSTRAINT `lodoro_order_scan_paris_order_id_fk` FOREIGN KEY (`paris_order_id`) REFERENCES `paris_orders` (`id`) ON DELETE SET NULL,
                    CONSTRAINT `lodoro_order_scan_processed_by_id_fk` FOREIGN KEY (`processed_by_id`) REFERENCES `auth_user` (`id`) ON DELETE SET NULL,
                    CONSTRAINT `lodoro_order_scan_ripley_order_id_fk` FOREIGN KEY (`ripley_order_id`) REFERENCES `ripley_orders` (`order_id`) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """)
            print("Tabla 'lodoro_order_scan' creada exitosamente.")
    else:
        print("La tabla 'lodoro_order_scan' ya existe.")

# Crear tablas
create_api_status_table()
create_order_scan_table()

print("Proceso completado.") 