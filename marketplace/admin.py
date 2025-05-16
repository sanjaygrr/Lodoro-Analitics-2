from django.contrib import admin
from .models import (
    ApiConfig, FalabellaProduct, 
    ParisOrder, ParisItem, ParisSubOrder, ParisStatus, ParisPago, ParisDeliveryOption,
    RipleyOrder, RipleyCustomer, RipleyAddress, RipleyOrderLine, RipleyRefund
)

@admin.register(ApiConfig)
class ApiConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'marketplace', 'active', 'updated_at')
    list_filter = ('marketplace', 'active')
    search_fields = ('name', 'marketplace')

@admin.register(FalabellaProduct)
class FalabellaProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'name', 'price', 'stock', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('sku', 'name', 'product_id')

# Paris Admin
class ParisItemInline(admin.TabularInline):
    model = ParisItem
    extra = 0
    fk_name = 'orderId'
    fields = ('sku', 'name', 'priceAfterDiscounts')
    readonly_fields = ('sku', 'name', 'priceAfterDiscounts')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(orderId=request.resolver_match.kwargs['object_id'])

class ParisSubOrderInline(admin.TabularInline):
    model = ParisSubOrder
    extra = 0

class ParisStatusInline(admin.TabularInline):
    model = ParisStatus
    extra = 0

class ParisPagoInline(admin.TabularInline):
    model = ParisPago
    extra = 0

class ParisDeliveryOptionInline(admin.TabularInline):
    model = ParisDeliveryOption
    extra = 0

@admin.register(ParisOrder)
class ParisOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_order_id', 'get_customer_name', 'get_total_amount', 'get_status', 'get_created_at', 'get_processed', 'get_printed')
    list_filter = ('orden_impresa', 'createdAt')
    search_fields = ('originOrderNumber', 'subOrderNumber', 'customer_name', 'customer_email')
    readonly_fields = ('createdAt', 'originOrderDate', 'get_order_id', 'get_status', 'get_total_amount', 'get_processed', 'get_printed')
    # Desactivamos los inlines que causan problemas
    # inlines = [ParisItemInline, ParisSubOrderInline, ParisStatusInline, ParisPagoInline, ParisDeliveryOptionInline]
    
    fieldsets = (
        ('Información de Orden', {
            'fields': ('id', 'originOrderNumber', 'subOrderNumber', 'createdAt', 'originOrderDate')
        }),
        ('Cliente', {
            'fields': ('customer_name', 'customer_email', 'billing_phone')
        }),
        ('Detalles', {
            'fields': ('orden_impresa',)
        }),
    )
    
    def get_order_id(self, obj):
        return obj.order_id
    get_order_id.short_description = 'Order ID'
    
    def get_customer_name(self, obj):
        return obj.customer_name
    get_customer_name.short_description = 'Cliente'
    
    def get_total_amount(self, obj):
        return obj.total_amount
    get_total_amount.short_description = 'Total'
    
    def get_status(self, obj):
        return obj.status
    get_status.short_description = 'Estado'
    
    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Creado'
    
    def get_processed(self, obj):
        return obj.processed
    get_processed.short_description = 'Procesada'
    
    def get_printed(self, obj):
        return obj.printed
    get_printed.short_description = 'Impresa'

# Ripley Admin
class RipleyCustomerInline(admin.StackedInline):
    model = RipleyCustomer
    extra = 0

class RipleyAddressInline(admin.StackedInline):
    model = RipleyAddress
    extra = 0

class RipleyOrderLineInline(admin.TabularInline):
    model = RipleyOrderLine
    extra = 0
    fk_name = 'order_id'
    fields = ('product_sku', 'product_title', 'quantity', 'price')
    readonly_fields = ('product_sku', 'product_title', 'quantity', 'price')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(order_id=request.resolver_match.kwargs['object_id'])

class RipleyRefundInline(admin.TabularInline):
    model = RipleyRefund
    extra = 0

@admin.register(RipleyOrder)
class RipleyOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'get_total_amount', 'get_status', 'get_created_at', 'get_processed', 'get_printed')
    list_filter = ('orden_procesada', 'orden_impresa', 'created_date')
    search_fields = ('order_id',)
    readonly_fields = ('created_date', 'last_updated_date', 'get_status', 'get_total_amount', 'get_processed', 'get_printed')
    # Desactivamos los inlines que causan problemas
    # inlines = [RipleyCustomerInline, RipleyAddressInline, RipleyOrderLineInline, RipleyRefundInline]
    
    fieldsets = (
        ('Información de Orden', {
            'fields': ('order_id', 'order_state', 'created_date', 'last_updated_date')
        }),
        ('Detalles', {
            'fields': ('total_price', 'orden_procesada', 'orden_impresa')
        }),
    )
    
    def get_total_amount(self, obj):
        return obj.total_amount
    get_total_amount.short_description = 'Total'
    
    def get_status(self, obj):
        return obj.status
    get_status.short_description = 'Estado'
    
    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Creado'
    
    def get_processed(self, obj):
        return obj.processed
    get_processed.short_description = 'Procesada'
    
    def get_printed(self, obj):
        return obj.printed
    get_printed.short_description = 'Impresa'

# Registrar los modelos de líneas de productos directamente
@admin.register(ParisItem)
class ParisItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'name', 'get_price', 'get_order_id')
    search_fields = ('sku', 'name', 'orderId')
    list_filter = ('statusId',)
    
    def get_price(self, obj):
        return obj.price
    get_price.short_description = 'Precio'
    
    def get_order_id(self, obj):
        if obj.orderId:
            paris_order = ParisOrder.objects.filter(id=obj.orderId).first()
            if paris_order:
                return paris_order.order_id
        return obj.orderId
    get_order_id.short_description = 'Orden'

@admin.register(RipleyOrderLine)
class RipleyOrderLineAdmin(admin.ModelAdmin):
    list_display = ('order_line_id', 'product_sku', 'product_title', 'quantity', 'price', 'order_id')
    search_fields = ('product_sku', 'product_title', 'order_id')
    list_filter = ('order_line_state',)
