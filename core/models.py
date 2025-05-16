from django.db import models
from django.contrib.auth.models import User
from marketplace.models import ParisOrder, RipleyOrder

# Create your models here.

class OrderScan(models.Model):
    MARKETPLACE_CHOICES = (
        ('PARIS', 'Paris'),
        ('RIPLEY', 'Ripley'),
        ('FALABELLA', 'Falabella'),
    )
    
    STATUS_CHOICES = (
        ('ESCANEADA', 'Escaneada'),
        ('PROCESADA', 'Procesada'),
        ('ERROR', 'Error'),
    )
    
    id = models.AutoField(primary_key=True)
    order_id = models.CharField(max_length=100)
    marketplace = models.CharField(max_length=50, choices=MARKETPLACE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ESCANEADA')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_orders')
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    # Referencias a las órdenes reales, puede ser NULL dependiendo del marketplace
    paris_order = models.ForeignKey(ParisOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='scans')
    ripley_order = models.ForeignKey(RipleyOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='scans')
    
    class Meta:
        verbose_name = 'Escaneo de Orden'
        verbose_name_plural = 'Escaneos de Órdenes'
        db_table = 'lodoro_order_scan'
        
    def __str__(self):
        return f"{self.get_marketplace_display()} - {self.order_id}"

class ApiStatus(models.Model):
    STATUS_CHOICES = (
        ('ACTIVA', 'Activa'),
        ('INACTIVA', 'Inactiva'),
        ('ERROR', 'Error'),
    )
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    last_check = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Estado de API'
        verbose_name_plural = 'Estados de APIs'
        db_table = 'lodoro_api_status'
        
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
