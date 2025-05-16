import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
django.setup()

# Importar conexión a la base de datos y modelos
from django.db import connection
from marketplace.models import ParisOrder, RipleyOrder, ParisItem, RipleyOrderLine
from django.db.models import Manager

# Extender el manager de ParisOrder
class ParisOrderManager(Manager):
    def get_queryset(self):
        return super().get_queryset()
    
    def total_orders_by_date(self, date):
        """Obtener el total de órdenes para una fecha específica usando función almacenada"""
        with connection.cursor() as cursor:
            cursor.execute("SET @p_total_orders = 0")
            cursor.execute("SET @p_total_paris = 0")
            cursor.execute("SET @p_total_ripley = 0")
            
            cursor.execute(
                "CALL generate_daily_report(%s, @p_total_orders, @p_total_paris, @p_total_ripley)",
                [date]
            )
            
            cursor.execute("SELECT @p_total_paris")
            return cursor.fetchone()[0]
    
    def calculate_paris_order_value(self, order_id):
        """Calcular el valor de una orden de Paris usando función almacenada"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT calculate_order_value(%s, %s)", [order_id, 'paris'])
            return cursor.fetchone()[0]

# Extender el manager de RipleyOrder
class RipleyOrderManager(Manager):
    def get_queryset(self):
        return super().get_queryset()
    
    def total_orders_by_date(self, date):
        """Obtener el total de órdenes para una fecha específica usando función almacenada"""
        with connection.cursor() as cursor:
            cursor.execute("SET @p_total_orders = 0")
            cursor.execute("SET @p_total_paris = 0")
            cursor.execute("SET @p_total_ripley = 0")
            
            cursor.execute(
                "CALL generate_daily_report(%s, @p_total_orders, @p_total_paris, @p_total_ripley)",
                [date]
            )
            
            cursor.execute("SELECT @p_total_ripley")
            return cursor.fetchone()[0]
    
    def calculate_ripley_order_value(self, order_id):
        """Calcular el valor de una orden de Ripley usando función almacenada"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT calculate_order_value(%s, %s)", [order_id, 'ripley'])
            return cursor.fetchone()[0]

# Aplicar los managers extendidos
def extend_models():
    # Guardar los managers originales
    original_paris_manager = ParisOrder.objects
    original_ripley_manager = RipleyOrder.objects
    
    # Aplicar los nuevos managers
    ParisOrder.objects = ParisOrderManager()
    ParisOrder.stored_objects = ParisOrderManager()
    
    RipleyOrder.objects = RipleyOrderManager()
    RipleyOrder.stored_objects = RipleyOrderManager()
    
    print("Modelos extendidos con funciones almacenadas.")
    
    return original_paris_manager, original_ripley_manager

# Restaurar managers originales
def restore_original_managers(original_paris_manager, original_ripley_manager):
    ParisOrder.objects = original_paris_manager
    RipleyOrder.objects = original_ripley_manager
    
    print("Managers originales restaurados.")

# Ejemplo de uso
if __name__ == "__main__":
    from datetime import datetime
    
    # Extender modelos
    original_managers = extend_models()
    
    try:
        # Usar funciones almacenadas a través de los modelos
        today = datetime.now().date()
        
        # Obtener estadísticas usando funciones almacenadas
        total_paris = ParisOrder.stored_objects.total_orders_by_date(today)
        total_ripley = RipleyOrder.stored_objects.total_orders_by_date(today)
        
        print(f"Total de órdenes Paris hoy: {total_paris}")
        print(f"Total de órdenes Ripley hoy: {total_ripley}")
        
        # Calcular valor de una orden (descomentado cuando tengas IDs válidos)
        # paris_order_id = "ORD123456"
        # paris_order_value = ParisOrder.stored_objects.calculate_paris_order_value(paris_order_id)
        # print(f"Valor de la orden Paris {paris_order_id}: ${paris_order_value}")
        
        # ripley_order_id = "RIP789012"
        # ripley_order_value = RipleyOrder.stored_objects.calculate_ripley_order_value(ripley_order_id)
        # print(f"Valor de la orden Ripley {ripley_order_id}: ${ripley_order_value}")
        
    finally:
        # Restaurar managers originales
        restore_original_managers(*original_managers)
        
    print("\nProceso completado.") 