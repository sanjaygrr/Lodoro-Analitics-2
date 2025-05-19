from django.contrib import admin
from .models import ParisOrder, RipleyOrder

@admin.register(ParisOrder)
class ParisOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'origin_order_number', 'customer_name', 'total_amount', 'is_processed', 'is_printed')
    list_filter = ('is_processed', 'is_printed')
    search_fields = ('order_id', 'origin_order_number', 'customer_name')

@admin.register(RipleyOrder)
class RipleyOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'commercial_id', 'customer_id', 'total_price', 'is_processed', 'is_printed')
    list_filter = ('is_processed', 'is_printed')
    search_fields = ('order_id', 'commercial_id', 'customer_id')
