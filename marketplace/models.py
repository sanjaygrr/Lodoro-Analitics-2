from django.db import models
from django.contrib.auth.models import User

class ApiConfig(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255, null=True, blank=True)
    api_token = models.CharField(max_length=255, null=True, blank=True)
    api_url = models.CharField(max_length=255)
    marketplace = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_config'
        verbose_name = 'Configuración de API'
        verbose_name_plural = 'Configuraciones de API'
        managed = False

    def __str__(self):
        return f"{self.marketplace} - {self.name}"

class FalabellaProduct(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Falabella_products'
        verbose_name = 'Producto Falabella'
        verbose_name_plural = 'Productos Falabella'
        managed = False

    def __str__(self):
        return f"{self.sku} - {self.name}"

# Modelos para Paris
class ParisOrder(models.Model):
    # Campos actualizados según la estructura real de la tabla
    id = models.CharField(primary_key=True, max_length=36)
    origin = models.CharField(max_length=15, null=True, blank=True)
    originOrderNumber = models.CharField(max_length=15, null=True, blank=True)
    subOrderNumber = models.CharField(max_length=15, unique=True)
    originInvoiceType = models.CharField(max_length=15, null=True, blank=True)
    originOrderDate = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(null=True, blank=True)
    customer_id = models.CharField(max_length=36, null=True, blank=True)
    customer_name = models.CharField(max_length=50, null=True, blank=True)
    customer_email = models.EmailField(max_length=50, null=True, blank=True)
    customer_documentType = models.CharField(max_length=20, null=True, blank=True)
    customer_documentNumber = models.CharField(max_length=20, null=True, blank=True)
    billing_id = models.CharField(max_length=36, null=True, blank=True)
    billing_firstName = models.CharField(max_length=50, null=True, blank=True)
    billing_lastName = models.CharField(max_length=50, null=True, blank=True)
    billing_address1 = models.CharField(max_length=100, null=True, blank=True)
    billing_address2 = models.CharField(max_length=50, null=True, blank=True)
    billing_address3 = models.CharField(max_length=50, null=True, blank=True)
    billing_city = models.CharField(max_length=50, null=True, blank=True)
    billing_stateCode = models.CharField(max_length=50, null=True, blank=True)
    billing_countryCode = models.CharField(max_length=10, null=True, blank=True)
    billing_phone = models.CharField(max_length=30, null=True, blank=True)
    billing_communaCode = models.CharField(max_length=20, null=True, blank=True)
    orden_impresa = models.BooleanField(default=False)
    
    # Campos virtuales para mantener compatibilidad con el código existente
    @property
    def order_id(self):
        return self.originOrderNumber or self.subOrderNumber
    
    @property
    def status(self):
        # Determinar el estado basado en otros campos
        # Por defecto, consideramos NUEVA si no está impresa
        if hasattr(self, 'orden_procesada') and getattr(self, 'orden_procesada', False):
            return 'PROCESADA'
        return 'NUEVA'
    
    @property
    def processed(self):
        # Si existe un campo orden_procesada lo usamos, de lo contrario inferimos
        return getattr(self, 'orden_procesada', False)
    
    @property
    def printed(self):
        return self.orden_impresa
    
    @property
    def total_amount(self):
        # Calcular el total a partir de los items
        from django.db.models import Sum, F
        items = ParisItem.objects.filter(orderId=self.id)
        total = items.aggregate(total=Sum('priceAfterDiscounts'))
        return total['total'] or 0
    
    @property
    def created_at(self):
        return self.createdAt
    
    @property
    def updated_at(self):
        # No hay campo de updated_at, usamos createdAt
        return self.createdAt
    
    @property
    def customer_phone(self):
        return self.billing_phone
    
    class Meta:
        db_table = 'paris_orders'
        verbose_name = 'Orden Paris'
        verbose_name_plural = 'Órdenes Paris'
        managed = False
        
    def __str__(self):
        return f"Orden Paris #{self.order_id}"

class ParisItem(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    sku = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    sellerId = models.CharField(max_length=36, null=True, blank=True)
    jdaSku = models.CharField(max_length=50, null=True, blank=True)
    basePrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    grossPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    priceAfterDiscounts = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taxRate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    sellerSku = models.CharField(max_length=200, null=True, blank=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    taxBasis = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    subOrderNumber = models.CharField(max_length=50, null=True, blank=True)
    reconditioned = models.BooleanField(null=True, blank=True)
    cancellationReasonId = models.IntegerField(null=True, blank=True)
    statusId = models.IntegerField(null=True, blank=True)
    imagePath = models.CharField(max_length=1000, null=True, blank=True)
    itemSize = models.CharField(max_length=20, null=True, blank=True)
    returnId = models.CharField(max_length=36, null=True, blank=True)
    userId = models.CharField(max_length=36, null=True, blank=True)
    shippingCost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    externalCategoryId = models.CharField(max_length=36, null=True, blank=True)
    orderId = models.CharField(max_length=36, null=True, blank=True)
    
    # Propiedades virtuales para mantener compatibilidad
    @property
    def order(self):
        if self.orderId:
            return ParisOrder.objects.filter(id=self.orderId).first()
        return None
    
    @property
    def quantity(self):
        # No hay campo quantity en la tabla real, asumimos 1
        return 1
    
    @property
    def price(self):
        return self.priceAfterDiscounts or self.grossPrice or self.basePrice or 0
    
    class Meta:
        db_table = 'paris_items'
        verbose_name = 'Item Paris'
        verbose_name_plural = 'Items Paris'
        managed = False
        
    def __str__(self):
        return f"{self.sku} - {self.name}"

class ParisSubOrder(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(ParisOrder, on_delete=models.CASCADE, related_name='suborders')
    suborder_id = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'paris_subOrders'
        verbose_name = 'Suborden Paris'
        verbose_name_plural = 'Subórdenes Paris'
        managed = False
        
    def __str__(self):
        return f"Suborden Paris #{self.suborder_id}"

class ParisStatus(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(ParisOrder, on_delete=models.CASCADE, related_name='statuses')
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    
    class Meta:
        db_table = 'paris_statuses'
        verbose_name = 'Estado Paris'
        verbose_name_plural = 'Estados Paris'
        managed = False
        
    def __str__(self):
        return f"{self.order.order_id} - {self.status}"

class ParisPago(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(ParisOrder, on_delete=models.CASCADE, related_name='pagos')
    payment_method = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'paris_pagos'
        verbose_name = 'Pago Paris'
        verbose_name_plural = 'Pagos Paris'
        managed = False
        
    def __str__(self):
        return f"{self.order.order_id} - {self.payment_method}"

class ParisDeliveryOption(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(ParisOrder, on_delete=models.CASCADE, related_name='delivery_options')
    delivery_type = models.CharField(max_length=100)
    address = models.TextField()
    
    class Meta:
        db_table = 'paris_delivery_options'
        verbose_name = 'Opción de Entrega Paris'
        verbose_name_plural = 'Opciones de Entrega Paris'
        managed = False
        
    def __str__(self):
        return f"{self.order.order_id} - {self.delivery_type}"

# Modelos para Ripley
class RipleyOrder(models.Model):
    # Campos actualizados según la estructura real de la tabla
    order_id = models.CharField(primary_key=True, max_length=50)
    commercial_id = models.CharField(max_length=50, null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    last_updated_date = models.DateTimeField(null=True, blank=True)
    acceptance_decision_date = models.DateTimeField(null=True, blank=True)
    customer_debited_date = models.DateTimeField(null=True, blank=True)
    currency_iso_code = models.CharField(max_length=10, null=True, blank=True)
    can_cancel = models.BooleanField(null=True, blank=True)
    has_customer_message = models.BooleanField(null=True, blank=True)
    has_incident = models.BooleanField(null=True, blank=True)
    customer_id = models.CharField(max_length=50, null=True, blank=True)
    leadtime_to_ship = models.IntegerField(null=True, blank=True)
    order_state = models.CharField(max_length=20, null=True, blank=True)
    order_state_reason_code = models.CharField(max_length=50, null=True, blank=True)
    order_state_reason_label = models.CharField(max_length=100, null=True, blank=True)
    payment_type = models.CharField(max_length=50, null=True, blank=True)
    payment_workflow = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipping_type_code = models.CharField(max_length=50, null=True, blank=True)
    shipping_type_label = models.CharField(max_length=255, null=True, blank=True)
    shipping_zone_code = models.CharField(max_length=50, null=True, blank=True)
    shipping_zone_label = models.CharField(max_length=255, null=True, blank=True)
    total_commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    orden_impresa = models.BooleanField(default=False)
    orden_procesada = models.BooleanField(default=False)
    
    # Propiedades virtuales para mantener compatibilidad
    @property
    def status(self):
        # Determinar el estado basado en order_state o orden_procesada
        if self.orden_procesada:
            return 'PROCESADA'
        elif self.order_state == 'SHIPPED':
            return 'ENVIADA'
        elif self.order_state == 'CANCELED':
            return 'CANCELADA'
        return 'NUEVA'
    
    @property
    def total_amount(self):
        return self.total_price or 0
    
    @property
    def created_at(self):
        return self.created_date
    
    @property
    def updated_at(self):
        return self.last_updated_date
    
    @property
    def processed(self):
        return self.orden_procesada
    
    @property
    def printed(self):
        return self.orden_impresa
    
    class Meta:
        db_table = 'ripley_orders'
        verbose_name = 'Orden Ripley'
        verbose_name_plural = 'Órdenes Ripley'
        managed = False
        
    def __str__(self):
        return f"Orden Ripley #{self.order_id}"

class RipleyCustomer(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(RipleyOrder, on_delete=models.CASCADE, related_name='customer')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'ripley_customers'
        verbose_name = 'Cliente Ripley'
        verbose_name_plural = 'Clientes Ripley'
        managed = False
        
    def __str__(self):
        return f"{self.name} - {self.email}"

class RipleyAddress(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(RipleyOrder, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=50)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'ripley_addresses'
        verbose_name = 'Dirección Ripley'
        verbose_name_plural = 'Direcciones Ripley'
        managed = False
        
    def __str__(self):
        return f"{self.order.order_id} - {self.address_type}"

class RipleyOrderLine(models.Model):
    # Campos actualizados según la estructura real de la tabla
    order_line_id = models.CharField(primary_key=True, max_length=50)
    order_id = models.CharField(max_length=50, null=True, blank=True)
    order_line_index = models.IntegerField(null=True, blank=True)
    offer_id = models.IntegerField(null=True, blank=True)
    offer_sku = models.CharField(max_length=100, null=True, blank=True)
    offer_state_code = models.CharField(max_length=20, null=True, blank=True)
    product_sku = models.CharField(max_length=100, null=True, blank=True)
    product_title = models.CharField(max_length=100, null=True, blank=True)
    category_code = models.CharField(max_length=50, null=True, blank=True)
    category_label = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission_rate_vat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission_vat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order_line_state = models.CharField(max_length=50, null=True, blank=True)
    order_line_state_reason_code = models.CharField(max_length=50, null=True, blank=True)
    order_line_state_reason_label = models.CharField(max_length=100, null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    debited_date = models.DateTimeField(null=True, blank=True)
    last_updated_date = models.DateTimeField(null=True, blank=True)
    shipped_date = models.DateTimeField(null=True, blank=True)
    
    # Propiedades virtuales para mantener compatibilidad
    @property
    def order(self):
        if self.order_id:
            return RipleyOrder.objects.filter(order_id=self.order_id).first()
        return None
    
    @property
    def sku(self):
        return self.product_sku or self.offer_sku
    
    @property
    def name(self):
        return self.product_title
    
    class Meta:
        db_table = 'ripley_order_lines'
        verbose_name = 'Línea de Orden Ripley'
        verbose_name_plural = 'Líneas de Orden Ripley'
        managed = False
        
    def __str__(self):
        return f"{self.sku} - {self.name}"

class RipleyRefund(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(RipleyOrder, on_delete=models.CASCADE, related_name='refunds')
    refund_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    created_at = models.DateTimeField()
    
    class Meta:
        db_table = 'ripley_refunds'
        verbose_name = 'Reembolso Ripley'
        verbose_name_plural = 'Reembolsos Ripley'
        managed = False
        
    def __str__(self):
        return f"{self.order.order_id} - {self.refund_id}"
