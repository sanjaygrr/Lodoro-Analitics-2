"""
Utilidades para trabajar con funciones y procedimientos almacenados en MySQL
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

class StoredProcedure:
    """
    Clase para simplificar el trabajo con procedimientos almacenados en MySQL
    """
    def __init__(self, name: str):
        self.name = name
        self.in_params = []
        self.out_params = []
        self.out_param_names = []
    
    def add_in_param(self, value: Any) -> 'StoredProcedure':
        """Añade un parámetro de entrada al procedimiento"""
        self.in_params.append(value)
        return self
    
    def add_out_param(self, name: str, default_value: Any = None) -> 'StoredProcedure':
        """Añade un parámetro de salida al procedimiento"""
        self.out_params.append(default_value)
        self.out_param_names.append(name)
        return self
    
    def execute(self) -> Tuple[Any, ...]:
        """Ejecuta el procedimiento almacenado y devuelve los parámetros de salida"""
        with connection.cursor() as cursor:
            # Inicializar variables para parámetros OUT
            for i, name in enumerate(self.out_param_names):
                cursor.execute(f"SET @{name} = %s", [self.out_params[i]])
            
            # Construir la llamada al procedimiento
            in_placeholders = ", ".join(["%s"] * len(self.in_params))
            out_vars = ", ".join([f"@{name}" for name in self.out_param_names])
            
            if in_placeholders and out_vars:
                call_stmt = f"CALL {self.name}({in_placeholders}, {out_vars})"
            elif in_placeholders:
                call_stmt = f"CALL {self.name}({in_placeholders})"
            elif out_vars:
                call_stmt = f"CALL {self.name}({out_vars})"
            else:
                call_stmt = f"CALL {self.name}()"
            
            # Ejecutar el procedimiento
            cursor.execute(call_stmt, self.in_params)
            
            # Obtener los valores de los parámetros OUT
            if self.out_param_names:
                out_select = ", ".join([f"@{name}" for name in self.out_param_names])
                cursor.execute(f"SELECT {out_select}")
                return cursor.fetchone()
            
            return tuple()

class StoredFunction:
    """
    Clase para simplificar el trabajo con funciones almacenadas en MySQL
    """
    def __init__(self, name: str):
        self.name = name
        self.params = []
    
    def add_param(self, value: Any) -> 'StoredFunction':
        """Añade un parámetro a la función"""
        self.params.append(value)
        return self
    
    def execute(self) -> Any:
        """Ejecuta la función almacenada y devuelve su resultado"""
        with connection.cursor() as cursor:
            # Construir la llamada a la función
            placeholders = ", ".join(["%s"] * len(self.params))
            
            if placeholders:
                call_stmt = f"SELECT {self.name}({placeholders})"
            else:
                call_stmt = f"SELECT {self.name}()"
            
            # Ejecutar la función
            cursor.execute(call_stmt, self.params)
            result = cursor.fetchone()
            return result[0] if result else None

# Funciones de conveniencia para el uso común

def call_procedure(name: str, in_params: List[Any] = None, out_params: Dict[str, Any] = None) -> Tuple[Any, ...]:
    """
    Llamar a un procedimiento almacenado con parámetros de entrada y salida
    
    Args:
        name: Nombre del procedimiento
        in_params: Lista de parámetros de entrada
        out_params: Diccionario de nombres de parámetros de salida y sus valores por defecto
        
    Returns:
        Tupla con los valores de los parámetros de salida
    """
    proc = StoredProcedure(name)
    
    # Agregar parámetros de entrada
    if in_params:
        for param in in_params:
            proc.add_in_param(param)
    
    # Agregar parámetros de salida
    if out_params:
        for name, default_value in out_params.items():
            proc.add_out_param(name, default_value)
    
    return proc.execute()

def call_function(name: str, params: List[Any] = None) -> Any:
    """
    Llamar a una función almacenada con parámetros
    
    Args:
        name: Nombre de la función
        params: Lista de parámetros
        
    Returns:
        Resultado de la función
    """
    func = StoredFunction(name)
    
    # Agregar parámetros
    if params:
        for param in params:
            func.add_param(param)
    
    return func.execute()

# Funciones específicas para casos de uso comunes en Lodoro Analytics

def get_marketplace_stats(marketplace: str) -> int:
    """
    Obtener estadísticas de un marketplace específico
    
    Args:
        marketplace: Nombre del marketplace ('paris' o 'ripley')
        
    Returns:
        Número total de órdenes para ese marketplace
    """
    return call_function('get_marketplace_stats', [marketplace])

def calculate_order_value(order_id: str, marketplace: str) -> float:
    """
    Calcular el valor total de una orden
    
    Args:
        order_id: ID de la orden
        marketplace: Nombre del marketplace ('paris' o 'ripley')
        
    Returns:
        Valor total de la orden
    """
    return call_function('calculate_order_value', [order_id, marketplace])

def update_order_status(order_id: str, marketplace: str, status: str, user_id: int) -> Tuple[bool, str]:
    """
    Actualizar el estado de una orden
    
    Args:
        order_id: ID de la orden
        marketplace: Nombre del marketplace ('paris' o 'ripley')
        status: Nuevo estado de la orden
        user_id: ID del usuario que procesa la orden
        
    Returns:
        Tupla con (éxito, mensaje)
    """
    return call_procedure(
        'update_order_status',
        in_params=[order_id, marketplace, status, user_id],
        out_params={'p_success': False, 'p_message': ''}
    )

def generate_daily_report(report_date: Union[date, datetime, str]) -> Tuple[int, int, int]:
    """
    Generar un reporte diario
    
    Args:
        report_date: Fecha para el reporte
        
    Returns:
        Tupla con (total_orders, total_paris, total_ripley)
    """
    # Convertir a fecha si es string
    if isinstance(report_date, str):
        report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
    
    # Convertir a fecha si es datetime
    if isinstance(report_date, datetime):
        report_date = report_date.date()
    
    return call_procedure(
        'generate_daily_report',
        in_params=[report_date],
        out_params={
            'p_total_orders': 0,
            'p_total_paris': 0,
            'p_total_ripley': 0
        }
    )

# Ejemplo de uso
if __name__ == "__main__":
    print("=== Usando funciones almacenadas ===")
    
    # Obtener estadísticas de marketplace
    paris_count = get_marketplace_stats('paris')
    ripley_count = get_marketplace_stats('ripley')
    
    print(f"Total de órdenes de Paris: {paris_count}")
    print(f"Total de órdenes de Ripley: {ripley_count}")
    print(f"Total general: {paris_count + ripley_count}")
    
    # Estos ejemplos requieren IDs válidos en tu base de datos
    # paris_order_value = calculate_order_value('ORD123456', 'paris')
    # print(f"Valor total de la orden ORD123456 (Paris): ${paris_order_value}")
    
    print("\n=== Usando procedimientos almacenados ===")
    
    # Estos ejemplos requieren IDs válidos en tu base de datos
    # success, message = update_order_status('ORD123456', 'paris', 'PROCESSED', 1)
    # print(f"Actualización: {'Exitosa' if success else 'Fallida'}")
    # print(f"Mensaje: {message}")
    
    # Generar reporte para hoy
    today = datetime.now().date()
    total_orders, total_paris, total_ripley = generate_daily_report(today)
    
    print(f"Reporte diario para {today}:")
    print(f"Total de órdenes: {total_orders}")
    print(f"Total de órdenes de Paris: {total_paris}")
    print(f"Total de órdenes de Ripley: {total_ripley}")
    
    print("\nProceso completado.") 