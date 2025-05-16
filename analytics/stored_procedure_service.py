"""
Servicio para análisis utilizando procedimientos almacenados
"""
from django.db import connection
from datetime import datetime, date
from typing import Dict, List, Any, Tuple, Optional

class AnalyticsService:
    """
    Servicio para obtener estadísticas y análisis usando procedimientos almacenados
    """
    
    @staticmethod
    def get_sales_summary(marketplace: str = 'TODOS', start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Obtiene un resumen de ventas usando procedimientos almacenados
        
        Args:
            marketplace: Filtro de marketplace (PARIS, RIPLEY, TODOS)
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
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
                [start_date, end_date]
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
            
            # Filtrar por marketplace si es necesario
            if marketplace == 'PARIS':
                stats = {
                    'total_orders': total_paris,
                    'processed': paris_processed,
                    'printed': paris_printed,
                    'pending': total_paris - paris_processed
                }
            elif marketplace == 'RIPLEY':
                stats = {
                    'total_orders': total_ripley,
                    'processed': ripley_processed,
                    'printed': ripley_printed,
                    'pending': total_ripley - ripley_processed
                }
            else:
                stats = {
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
            
            return stats
    
    @staticmethod
    def get_product_performance(marketplace: str = 'TODOS', 
                              start_date: Optional[date] = None, 
                              end_date: Optional[date] = None,
                              search_query: str = '',
                              limit: int = 100,
                              offset: int = 0) -> Dict[str, Any]:
        """
        Obtiene estadísticas de rendimiento de productos
        
        Args:
            marketplace: Filtro de marketplace (PARIS, RIPLEY, TODOS)
            start_date: Fecha de inicio
            end_date: Fecha de fin
            search_query: Texto para búsqueda de productos
            limit: Cantidad de registros a devolver
            offset: Desplazamiento para paginación
            
        Returns:
            Diccionario con productos y estadísticas
        """
        products = []
        total_count = 0
        
        with connection.cursor() as cursor:
            # Convertir marketplace a formato esperado por el procedimiento
            db_marketplace = None
            if marketplace in ['PARIS', 'RIPLEY']:
                db_marketplace = marketplace
            
            # Inicializar variable para el total
            cursor.execute("SET @p_total_count = 0")
            
            # Llamar al procedimiento almacenado (crear este procedimiento)
            cursor.execute(
                "CALL get_product_performance(%s, %s, %s, %s, %s, %s, @p_total_count)",
                [db_marketplace, start_date, end_date, search_query, limit, offset]
            )
            
            # Obtener resultados
            result = cursor.fetchall()
            
            # Obtener el total de registros
            cursor.execute("SELECT @p_total_count")
            total_count = cursor.fetchone()[0]
            
            # Convertir a diccionario para facilitar su uso
            column_names = [col[0] for col in cursor.description]
            products = [
                dict(zip(column_names, row))
                for row in result
            ]
        
        return {
            'products': products,
            'total': total_count,
            'limit': limit,
            'offset': offset
        }
    
    @staticmethod
    def create_product_performance_procedure():
        """
        Crea el procedimiento almacenado para el rendimiento de productos si no existe
        """
        with connection.cursor() as cursor:
            # Verificar si existe el procedimiento
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.ROUTINES 
                WHERE ROUTINE_TYPE = 'PROCEDURE' 
                AND ROUTINE_NAME = 'get_product_performance'
                AND ROUTINE_SCHEMA = DATABASE()
            """)
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                # Crear el procedimiento
                cursor.execute("""
                    CREATE PROCEDURE get_product_performance(
                        IN p_marketplace VARCHAR(50),
                        IN p_date_from DATE,
                        IN p_date_to DATE,
                        IN p_search VARCHAR(255),
                        IN p_limit INT,
                        IN p_offset INT,
                        OUT p_total_count INT
                    )
                    BEGIN
                        -- Variables para resultados
                        DECLARE paris_count INT DEFAULT 0;
                        DECLARE ripley_count INT DEFAULT 0;
                        
                        -- Crear tabla temporal para resultados
                        CREATE TEMPORARY TABLE IF NOT EXISTS temp_products (
                            sku VARCHAR(100),
                            name VARCHAR(500),
                            total_quantity INT,
                            total_revenue DECIMAL(10,2),
                            marketplace VARCHAR(50)
                        );
                        
                        -- Limpiar tabla temporal
                        TRUNCATE TABLE temp_products;
                        
                        -- Obtener productos de Paris si es necesario
                        IF p_marketplace IS NULL OR p_marketplace = 'PARIS' THEN
                            -- Contar primero para la paginación
                            SELECT COUNT(DISTINCT pi.sku) INTO paris_count
                            FROM paris_items pi
                            JOIN paris_orders po ON pi.orderId = po.id
                            WHERE po.createdAt >= COALESCE(p_date_from, '1900-01-01')
                            AND po.createdAt <= COALESCE(p_date_to, '2999-12-31')
                            AND (
                                p_search IS NULL OR p_search = '' OR
                                pi.sku LIKE CONCAT('%', p_search, '%') OR
                                pi.name LIKE CONCAT('%', p_search, '%')
                            );
                            
                            -- Insertar en la tabla temporal
                            INSERT INTO temp_products
                            SELECT 
                                pi.sku,
                                pi.name,
                                COUNT(pi.id) AS total_quantity,
                                SUM(pi.priceAfterDiscounts) AS total_revenue,
                                'PARIS' AS marketplace
                            FROM paris_items pi
                            JOIN paris_orders po ON pi.orderId = po.id
                            WHERE po.createdAt >= COALESCE(p_date_from, '1900-01-01')
                            AND po.createdAt <= COALESCE(p_date_to, '2999-12-31')
                            AND (
                                p_search IS NULL OR p_search = '' OR
                                pi.sku LIKE CONCAT('%', p_search, '%') OR
                                pi.name LIKE CONCAT('%', p_search, '%')
                            )
                            GROUP BY pi.sku, pi.name;
                        END IF;
                        
                        -- Obtener productos de Ripley si es necesario
                        IF p_marketplace IS NULL OR p_marketplace = 'RIPLEY' THEN
                            -- Contar primero para la paginación
                            SELECT COUNT(DISTINCT rol.product_sku) INTO ripley_count
                            FROM ripley_order_lines rol
                            JOIN ripley_orders ro ON rol.order_id = ro.order_id
                            WHERE ro.created_date >= COALESCE(p_date_from, '1900-01-01')
                            AND ro.created_date <= COALESCE(p_date_to, '2999-12-31')
                            AND (
                                p_search IS NULL OR p_search = '' OR
                                rol.product_sku LIKE CONCAT('%', p_search, '%') OR
                                rol.product_title LIKE CONCAT('%', p_search, '%')
                            );
                            
                            -- Insertar en la tabla temporal
                            INSERT INTO temp_products
                            SELECT 
                                rol.product_sku AS sku,
                                rol.product_title AS name,
                                SUM(rol.quantity) AS total_quantity,
                                SUM(rol.total_price) AS total_revenue,
                                'RIPLEY' AS marketplace
                            FROM ripley_order_lines rol
                            JOIN ripley_orders ro ON rol.order_id = ro.order_id
                            WHERE ro.created_date >= COALESCE(p_date_from, '1900-01-01')
                            AND ro.created_date <= COALESCE(p_date_to, '2999-12-31')
                            AND (
                                p_search IS NULL OR p_search = '' OR
                                rol.product_sku LIKE CONCAT('%', p_search, '%') OR
                                rol.product_title LIKE CONCAT('%', p_search, '%')
                            )
                            GROUP BY rol.product_sku, rol.product_title;
                        END IF;
                        
                        -- Calcular el total de registros para paginación
                        SELECT COUNT(*) INTO p_total_count FROM temp_products;
                        
                        -- Devolver resultados paginados y ordenados
                        SELECT * FROM temp_products
                        ORDER BY total_quantity DESC
                        LIMIT p_limit OFFSET p_offset;
                        
                        -- Limpiar tabla temporal
                        DROP TEMPORARY TABLE IF EXISTS temp_products;
                    END;
                """)
                return True
            
            return False 