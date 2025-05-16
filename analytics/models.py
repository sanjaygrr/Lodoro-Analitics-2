from django.db import models
from marketplace.models import ParisOrder, RipleyOrder, ParisItem, RipleyOrderLine

class SalesAnalytics(models.Model):
    MARKETPLACE_CHOICES = (
        ('PARIS', 'Paris'),
        ('RIPLEY', 'Ripley'),
        ('FALABELLA', 'Falabella'),
        ('TODOS', 'Todos'),
    )
    
    PERIOD_CHOICES = (
        ('DIA', 'Día'),
        ('SEMANA', 'Semana'),
        ('MES', 'Mes'),
        ('AÑO', 'Año'),
    )
    
    id = models.AutoField(primary_key=True)
    marketplace = models.CharField(max_length=50, choices=MARKETPLACE_CHOICES)
    period = models.CharField(max_length=50, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    total_orders = models.IntegerField()
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Análisis de Ventas'
        verbose_name_plural = 'Análisis de Ventas'
        db_table = 'lodoro_sales_analytics'
        
    def __str__(self):
        return f"{self.get_marketplace_display()} - {self.get_period_display()} - {self.start_date} a {self.end_date}"

class ProductPerformance(models.Model):
    id = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    total_quantity = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    marketplace = models.CharField(max_length=50)
    period_start = models.DateField()
    period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Rendimiento de Producto'
        verbose_name_plural = 'Rendimiento de Productos'
        db_table = 'lodoro_product_performance'
        
    def __str__(self):
        return f"{self.sku} - {self.name} ({self.marketplace})"
