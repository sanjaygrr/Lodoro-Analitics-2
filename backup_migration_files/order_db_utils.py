"""
Utilidades para trabajar con procedimientos almacenados de gestión de órdenes
"""
import os
import django
import sys
from typing import Any, Dict, List, Tuple, Union, Optional
from datetime import date, datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos
from django.db import connection

class StoredProcedureResult:
    """Clase para manejar múltiples conjuntos de resultados de un procedimiento almacenado"""
    def __init__(self, cursor):
        self.cursor = cursor
        self.result_sets = []
        self._collect_results()
    
    def _collect_results(self):
        """Recolecta todos los conjuntos de resultados disponibles"""
        result_set = self.cursor.fetchall()
        if result_set:
            self.result_sets.append(result_set)
        
        # Intentar obtener más resultados si están disponibles
        while self.cursor.nextset():
            result_set = self.cursor.fetchall()
            if result_set:
                self.result_sets.append(result_set)
    
    def get_result_set(self, index=0):
        """Obtiene un conjunto de resultados específico"""
        if 0 <= index < len(self.result_sets):
            return self.result_sets[index]
        return []
    
    def count(self):
        """Devuelve el número de conjuntos de resultados"""
        return len(self.result_sets)
    
    def all(self):
        """Devuelve todos los conjuntos de resultados"""
        return self.result_sets

class OrderManager:
    """
    Clase para gestionar órdenes utilizando procedimientos almacenados
    """
    
    @staticmethod
    def get_paris_orders(limit=100, offset=0, status=None, date_from=None, date_to=None):
        """
        Obtiene un listado de órdenes de Paris con paginación y filtros
        
        Args:
            limit: Cantidad de registros a devolver
            offset: Desplazamiento para paginación
            status: Estado de la orden (NUEVA, PROCESADA, IMPRESA, NO_IMPRESA)
            date_from: Fecha de inicio para filtro
            date_to: Fecha de fin para filtro
            
        Returns:
            Diccionario con órdenes y total de registros
        """
        with connection.cursor() as cursor:
            # Inicializar variable para el total
            cursor.execute("SET @p_total_count = 0")
            
            # Llamar al procedimiento almacenado
            cursor.execute(
                "CALL get_paris_orders(%s, %s, %s, %s, %s, @p_total_count)",
                [limit, offset, status, date_from, date_to]
            )
            
            # Obtener resultados
            orders = cursor.fetchall()
            
            # Obtener el total de registros
            cursor.execute("SELECT @p_total_count")
            total_count = cursor.fetchone()[0]
            
            # Convertir a diccionario para facilitar su uso
            column_names = [col[0] for col in cursor.description]
            orders_dict = [
                dict(zip(column_names, row))
                for row in orders
            ]
            
            return {
                'orders': orders_dict,
                'total': total_count,
                'limit': limit,
                'offset': offset
            }
    
    @staticmethod
    def get_ripley_orders(limit=100, offset=0, status=None, date_from=None, date_to=None):
        """
        Obtiene un listado de órdenes de Ripley con paginación y filtros
        
        Args:
            limit: Cantidad de registros a devolver
            offset: Desplazamiento para paginación
            status: Estado de la orden (NUEVA, PROCESADA, IMPRESA, NO_IMPRESA)
            date_from: Fecha de inicio para filtro
            date_to: Fecha de fin para filtro
            
        Returns:
            Diccionario con órdenes y total de registros
        """
        with connection.cursor() as cursor:
            # Inicializar variable para el total
            cursor.execute("SET @p_total_count = 0")
            
            # Llamar al procedimiento almacenado
            cursor.execute(
                "CALL get_ripley_orders(%s, %s, %s, %s, %s, @p_total_count)",
                [limit, offset, status, date_from, date_to]
            )
            
            # Obtener resultados
            orders = cursor.fetchall()
            
            # Obtener el total de registros
            cursor.execute("SELECT @p_total_count")
            total_count = cursor.fetchone()[0]
            
            # Convertir a diccionario para facilitar su uso
            column_names = [col[0] for col in cursor.description]
            orders_dict = [
                dict(zip(column_names, row))
                for row in orders
            ]
            
            return {
                'orders': orders_dict,
                'total': total_count,
                'limit': limit,
                'offset': offset
            }
    
    @staticmethod
    def get_paris_order_detail(order_id):
        """
        Obtiene los detalles de una orden de Paris
        
        Args:
            order_id: ID de la orden
            
        Returns:
            Diccionario con detalles de la orden e items
        """
        with connection.cursor() as cursor:
            # Llamar al procedimiento almacenado
            cursor.execute("CALL get_paris_order_detail(%s)", [order_id])
            
            # Procesar múltiples conjuntos de resultados
            result = StoredProcedureResult(cursor)
            
            # Primer conjunto de resultados: información de la orden
            order_data = result.get_result_set(0)
            
            # Segundo conjunto de resultados: items de la orden
            items_data = result.get_result_set(1)
            
            # Si no hay datos de orden, devolver None
            if not order_data:
                return None
            
            # Convertir a diccionario
            order_columns = [col[0] for col in cursor.description]
            order_dict = dict(zip(order_columns, order_data[0]))
            
            # Obtener columnas para items
            cursor.execute("DESCRIBE paris_items")
            item_columns = [row[0] for row in cursor.fetchall()]
            
            # Convertir items a diccionario
            items_dict = [
                dict(zip(item_columns, item))
                for item in items_data
            ]
            
            return {
                'order': order_dict,
                'items': items_dict
            }
    
    @staticmethod
    def get_ripley_order_detail(order_id):
        """
        Obtiene los detalles de una orden de Ripley
        
        Args:
            order_id: ID de la orden
            
        Returns:
            Diccionario con detalles de la orden e items
        """
        with connection.cursor() as cursor:
            # Llamar al procedimiento almacenado
            cursor.execute("CALL get_ripley_order_detail(%s)", [order_id])
            
            # Procesar múltiples conjuntos de resultados
            result = StoredProcedureResult(cursor)
            
            # Primer conjunto de resultados: información de la orden
            order_data = result.get_result_set(0)
            
            # Segundo conjunto de resultados: líneas de la orden
            lines_data = result.get_result_set(1)
            
            # Si no hay datos de orden, devolver None
            if not order_data:
                return None
            
            # Convertir a diccionario
            order_columns = [col[0] for col in cursor.description]
            order_dict = dict(zip(order_columns, order_data[0]))
            
            # Obtener columnas para líneas
            cursor.execute("DESCRIBE ripley_order_lines")
            line_columns = [row[0] for row in cursor.fetchall()]
            
            # Convertir líneas a diccionario
            lines_dict = [
                dict(zip(line_columns, line))
                for line in lines_data
            ]
            
            return {
                'order': order_dict,
                'lines': lines_dict
            }
    
    @staticmethod
    def update_paris_order_status(order_id, processed=None, printed=None, user_id=None):
        """
        Actualiza el estado de una orden de Paris
        
        Args:
            order_id: ID de la orden
            processed: Estado de procesamiento (True/False)
            printed: Estado de impresión (True/False)
            user_id: ID del usuario que realiza la actualización
            
        Returns:
            Tupla con (éxito, mensaje)
        """
        with connection.cursor() as cursor:
            # Inicializar variables para los parámetros OUT
            cursor.execute("SET @p_success = FALSE")
            cursor.execute("SET @p_message = ''")
            
            # Llamar al procedimiento almacenado
            cursor.execute(
                "CALL update_paris_order_status(%s, %s, %s, %s, @p_success, @p_message)",
                [order_id, processed, printed, user_id]
            )
            
            # Obtener los valores de los parámetros OUT
            cursor.execute("SELECT @p_success, @p_message")
            success, message = cursor.fetchone()
            
            return success, message
    
    @staticmethod
    def update_ripley_order_status(order_id, processed=None, printed=None, user_id=None):
        """
        Actualiza el estado de una orden de Ripley
        
        Args:
            order_id: ID de la orden
            processed: Estado de procesamiento (True/False)
            printed: Estado de impresión (True/False)
            user_id: ID del usuario que realiza la actualización
            
        Returns:
            Tupla con (éxito, mensaje)
        """
        with connection.cursor() as cursor:
            # Inicializar variables para los parámetros OUT
            cursor.execute("SET @p_success = FALSE")
            cursor.execute("SET @p_message = ''")
            
            # Llamar al procedimiento almacenado
            cursor.execute(
                "CALL update_ripley_order_status(%s, %s, %s, %s, @p_success, @p_message)",
                [order_id, processed, printed, user_id]
            )
            
            # Obtener los valores de los parámetros OUT
            cursor.execute("SELECT @p_success, @p_message")
            success, message = cursor.fetchone()
            
            return success, message
    
    @staticmethod
    def get_order_stats(date_from=None, date_to=None):
        """
        Obtiene estadísticas de órdenes en un rango de fechas
        
        Args:
            date_from: Fecha de inicio para filtro
            date_to: Fecha de fin para filtro
            
        Returns:
            Diccionario con estadísticas
        """
        with connection.cursor() as cursor:
            # Inicializar variables para los parámetros OUT
            cursor.execute("SET @p_total_paris = 0")
            cursor.execute("SET @p_total_ripley = 0")
            cursor.execute("SET @p_paris_processed = 0")
            cursor.execute("SET @p_paris_printed = 0")
            cursor.execute("SET @p_ripley_processed = 0")
            cursor.execute("SET @p_ripley_printed = 0")
            
            # Llamar al procedimiento almacenado
            cursor.execute(
                "CALL get_order_stats(%s, %s, @p_total_paris, @p_total_ripley, @p_paris_processed, @p_paris_printed, @p_ripley_processed, @p_ripley_printed)",
                [date_from, date_to]
            )
            
            # Obtener los valores de los parámetros OUT
            cursor.execute("""
                SELECT 
                    @p_total_paris, 
                    @p_total_ripley, 
                    @p_paris_processed, 
                    @p_paris_printed, 
                    @p_ripley_processed, 
                    @p_ripley_printed
            """)
            
            total_paris, total_ripley, paris_processed, paris_printed, ripley_processed, ripley_printed = cursor.fetchone()
            
            # Calcular totales generales
            total_orders = total_paris + total_ripley
            total_processed = paris_processed + ripley_processed
            total_printed = paris_printed + ripley_printed
            
            return {
                'total_orders': total_orders,
                'paris': {
                    'total': total_paris,
                    'processed': paris_processed,
                    'printed': paris_printed,
                    'pending': total_paris - paris_processed
                },
                'ripley': {
                    'total': total_ripley,
                    'processed': ripley_processed,
                    'printed': ripley_printed,
                    'pending': total_ripley - ripley_processed
                },
                'summary': {
                    'total': total_orders,
                    'processed': total_processed,
                    'printed': total_printed,
                    'pending': total_orders - total_processed
                }
            }

# Ejemplo de uso
if __name__ == "__main__":
    # Obtener órdenes de Paris
    print("=== Órdenes de Paris ===")
    paris_orders = OrderManager.get_paris_orders(limit=5, status='NUEVA')
    print(f"Total de órdenes: {paris_orders['total']}")
    for order in paris_orders['orders']:
        print(f"Orden: {order.get('subOrderNumber', 'N/A')} - Creada: {order.get('createdAt', 'N/A')}")
    
    # Obtener órdenes de Ripley
    print("\n=== Órdenes de Ripley ===")
    ripley_orders = OrderManager.get_ripley_orders(limit=5, status='NUEVA')
    print(f"Total de órdenes: {ripley_orders['total']}")
    for order in ripley_orders['orders']:
        print(f"Orden: {order.get('order_id', 'N/A')} - Creada: {order.get('created_date', 'N/A')}")
    
    # Obtener estadísticas
    print("\n=== Estadísticas de Órdenes ===")
    stats = OrderManager.get_order_stats()
    print(f"Total de órdenes: {stats['summary']['total']}")
    print(f"- Paris: {stats['paris']['total']} (Procesadas: {stats['paris']['processed']}, Pendientes: {stats['paris']['pending']})")
    print(f"- Ripley: {stats['ripley']['total']} (Procesadas: {stats['ripley']['processed']}, Pendientes: {stats['ripley']['pending']})")
    
    # Estos ejemplos requieren IDs válidos
    # Actualizar estado de orden (descomentar y usar IDs válidos)
    # paris_id = "sample_paris_id"
    # success, message = OrderManager.update_paris_order_status(paris_id, processed=True, printed=True, user_id=1)
    # print(f"\nActualización de orden Paris: {success} - {message}")
    
    # ripley_id = "sample_ripley_id"
    # success, message = OrderManager.update_ripley_order_status(ripley_id, processed=True, printed=False, user_id=1)
    # print(f"Actualización de orden Ripley: {success} - {message}") 