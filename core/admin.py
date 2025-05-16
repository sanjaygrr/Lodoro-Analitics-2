from django.contrib import admin
from .models import OrderScan, ApiStatus

@admin.register(OrderScan)
class OrderScanAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'marketplace', 'status', 'processed_by', 'processed_at', 'created_at')
    list_filter = ('marketplace', 'status', 'processed_at', 'created_at')
    search_fields = ('order_id', 'notes')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Información de Escaneo', {
            'fields': ('order_id', 'marketplace', 'status', 'created_at')
        }),
        ('Procesamiento', {
            'fields': ('processed_by', 'processed_at', 'notes')
        }),
        ('Referencias', {
            'fields': ('paris_order', 'ripley_order')
        }),
    )

@admin.register(ApiStatus)
class ApiStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'last_check')
    list_filter = ('status', 'last_check')
    search_fields = ('name', 'error_message')
    readonly_fields = ('last_check',)
