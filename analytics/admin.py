from django.contrib import admin
from .models import SalesAnalytics, ProductPerformance

@admin.register(SalesAnalytics)
class SalesAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('id', 'marketplace', 'period', 'start_date', 'end_date', 'total_sales', 'total_orders', 'average_order_value')
    list_filter = ('marketplace', 'period', 'start_date', 'end_date')
    search_fields = ('marketplace',)
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Filtros', {
            'fields': ('marketplace', 'period', 'start_date', 'end_date')
        }),
        ('Métricas', {
            'fields': ('total_sales', 'total_orders', 'average_order_value')
        }),
    )

@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'name', 'marketplace', 'total_quantity', 'total_revenue', 'period_start', 'period_end')
    list_filter = ('marketplace', 'period_start', 'period_end')
    search_fields = ('sku', 'name', 'marketplace')
    date_hierarchy = 'period_start'
