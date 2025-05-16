from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from datetime import datetime, timedelta

from marketplace.models import ParisOrder, RipleyOrder, ParisItem, RipleyOrderLine
from .models import ApiStatus, OrderScan

def login_view(request):
    """Vista para el login de usuarios"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    """Vista principal del dashboard"""
    # Obtener conteos para el panel de control
    today = datetime.today()
    this_month_start = datetime(today.year, today.month, 1)
    
    # Órdenes París
    paris_orders_total = ParisOrder.objects.count()
    paris_orders_new = sum(1 for order in ParisOrder.objects.all() if order.status == 'NUEVA')
    paris_orders_processed = sum(1 for order in ParisOrder.objects.all() if order.processed)
    paris_orders_this_month = ParisOrder.objects.filter(createdAt__gte=this_month_start).count()
    
    # Órdenes Ripley
    ripley_orders_total = RipleyOrder.objects.count()
    ripley_orders_new = sum(1 for order in RipleyOrder.objects.all() if order.status == 'NUEVA')
    ripley_orders_processed = RipleyOrder.objects.filter(orden_procesada=True).count()
    ripley_orders_this_month = RipleyOrder.objects.filter(created_date__gte=this_month_start).count()
    
    # Estado de APIs - Manejar el caso en que la tabla no exista o esté vacía
    try:
        api_status = ApiStatus.objects.all()
        apis_active = api_status.filter(status='ACTIVA').count()
        apis_inactive = api_status.filter(status='INACTIVA').count()
        apis_error = api_status.filter(status='ERROR').count()
    except Exception:
        # Si hay algún error, inicializar con valores predeterminados
        apis_active = 0
        apis_inactive = 0
        apis_error = 0
        
        # Crear algunos registros de ejemplo en la tabla ApiStatus
        try:
            ApiStatus.objects.create(name='API Paris', status='ACTIVA', last_check=datetime.now())
            ApiStatus.objects.create(name='API Ripley', status='ACTIVA', last_check=datetime.now())
            ApiStatus.objects.create(name='API Falabella', status='INACTIVA', last_check=datetime.now(), error_message='API no configurada')
            messages.info(request, 'Se han creado registros de ejemplo para el estado de las APIs.')
        except Exception as e:
            messages.error(request, f'Error al crear registros de ejemplo para las APIs: {str(e)}')
    
    # Productos más vendidos este mes (París)
    try:
        top_paris_products = ParisItem.objects.filter(
            orderId__in=ParisOrder.objects.filter(createdAt__gte=this_month_start).values_list('id', flat=True)
        ).values('sku', 'name').annotate(
            total_quantity=Count('id'),
            total_revenue=Sum('priceAfterDiscounts')
        ).order_by('-total_quantity')[:5]
    except Exception:
        top_paris_products = []
    
    # Productos más vendidos este mes (Ripley)
    try:
        top_ripley_products = RipleyOrderLine.objects.filter(
            order_id__in=RipleyOrder.objects.filter(created_date__gte=this_month_start).values_list('order_id', flat=True)
        ).values('product_sku', 'product_title').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_quantity')[:5]
        
        # Adaptar los resultados de Ripley para mantener la compatibilidad con las plantillas
        adapted_ripley_products = []
        for product in top_ripley_products:
            adapted_ripley_products.append({
                'sku': product['product_sku'],
                'name': product['product_title'],
                'total_quantity': product['total_quantity'],
                'total_revenue': product['total_revenue']
            })
    except Exception:
        adapted_ripley_products = []
    
    context = {
        'paris_orders_total': paris_orders_total,
        'paris_orders_new': paris_orders_new,
        'paris_orders_processed': paris_orders_processed,
        'paris_orders_this_month': paris_orders_this_month,
        
        'ripley_orders_total': ripley_orders_total,
        'ripley_orders_new': ripley_orders_new,
        'ripley_orders_processed': ripley_orders_processed,
        'ripley_orders_this_month': ripley_orders_this_month,
        
        'apis_active': apis_active,
        'apis_inactive': apis_inactive,
        'apis_error': apis_error,
        
        'top_paris_products': top_paris_products,
        'top_ripley_products': adapted_ripley_products,
    }
    
    return render(request, 'core/home.html', context)

@login_required
def api_status_view(request):
    """Vista para mostrar el estado de las APIs"""
    try:
        apis = ApiStatus.objects.all().order_by('name')
    except Exception:
        apis = []
        messages.error(request, 'No se pudo acceder a la información de estado de las APIs.')
    
    return render(request, 'core/api_status.html', {'apis': apis})

@login_required
def scan_order_view(request):
    """Vista para escanear órdenes"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        marketplace = request.POST.get('marketplace')
        
        if not order_id or not marketplace:
            messages.error(request, 'Debe proporcionar el ID de la orden y el marketplace')
            return redirect('scan_order')
        
        # Buscar la orden en la base de datos
        order_found = False
        
        if marketplace == 'PARIS':
            try:
                # Buscar por originOrderNumber o subOrderNumber
                paris_order = ParisOrder.objects.filter(
                    Q(originOrderNumber=order_id) | Q(subOrderNumber=order_id)
                ).first()
                
                if paris_order:
                    # Crear o actualizar el escaneo
                    scan, created = OrderScan.objects.get_or_create(
                        order_id=order_id,
                        marketplace=marketplace,
                        defaults={'paris_order': paris_order}
                    )
                    
                    if not created:
                        scan.status = 'ESCANEADA'
                        scan.processed_by = None
                        scan.processed_at = None
                        scan.save()
                    
                    order_found = True
                    return redirect('order_detail', scan_id=scan.id)
            except ParisOrder.DoesNotExist:
                pass
        
        elif marketplace == 'RIPLEY':
            try:
                ripley_order = RipleyOrder.objects.get(order_id=order_id)
                
                # Crear o actualizar el escaneo
                scan, created = OrderScan.objects.get_or_create(
                    order_id=order_id,
                    marketplace=marketplace,
                    defaults={'ripley_order': ripley_order}
                )
                
                if not created:
                    scan.status = 'ESCANEADA'
                    scan.processed_by = None
                    scan.processed_at = None
                    scan.save()
                
                order_found = True
                return redirect('order_detail', scan_id=scan.id)
            except RipleyOrder.DoesNotExist:
                pass
        
        if not order_found:
            # Crear un escaneo con error
            scan = OrderScan.objects.create(
                order_id=order_id,
                marketplace=marketplace,
                status='ERROR',
                notes='Orden no encontrada en la base de datos'
            )
            messages.error(request, f'Orden {order_id} no encontrada en {marketplace}')
            return redirect('scan_order')
    
    # Obtener escaneos recientes para mostrar en la página
    try:
        recent_scans = OrderScan.objects.order_by('-created_at')[:10]
    except Exception:
        recent_scans = []
        messages.warning(request, 'No se pudo acceder a los escaneos recientes.')
    
    return render(request, 'core/scan_order.html', {'recent_scans': recent_scans})

@login_required
def order_detail_view(request, scan_id):
    """Vista para ver detalles de una orden escaneada"""
    scan = get_object_or_404(OrderScan, id=scan_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'process':
            # Marcar la orden como procesada
            scan.status = 'PROCESADA'
            scan.processed_by = request.user
            scan.processed_at = datetime.now()
            scan.save()
            
            # Actualizar estado en la orden original
            if scan.marketplace == 'PARIS' and scan.paris_order:
                # Intentar agregar el campo orden_procesada si no existe
                try:
                    scan.paris_order.orden_procesada = True
                    scan.paris_order.save(update_fields=['orden_procesada'])
                except:
                    # Si no existe el campo, solo actualizamos el campo orden_impresa
                    scan.paris_order.orden_impresa = True
                    scan.paris_order.save(update_fields=['orden_impresa'])
            elif scan.marketplace == 'RIPLEY' and scan.ripley_order:
                scan.ripley_order.orden_procesada = True
                scan.ripley_order.save(update_fields=['orden_procesada'])
                
            messages.success(request, f'Orden {scan.order_id} marcada como procesada')
        
        elif action == 'print':
            # Marcar la orden como impresa
            if scan.marketplace == 'PARIS' and scan.paris_order:
                scan.paris_order.orden_impresa = True
                scan.paris_order.save(update_fields=['orden_impresa'])
            elif scan.marketplace == 'RIPLEY' and scan.ripley_order:
                scan.ripley_order.orden_impresa = True
                scan.ripley_order.save(update_fields=['orden_impresa'])
                
            messages.success(request, f'Orden {scan.order_id} marcada como impresa')
        
        return redirect('order_detail', scan_id=scan.id)
    
    # Obtener detalles de la orden según el marketplace
    order_details = None
    order_items = None
    
    if scan.marketplace == 'PARIS' and scan.paris_order:
        order_details = scan.paris_order
        order_items = ParisItem.objects.filter(orderId=scan.paris_order.id)
    elif scan.marketplace == 'RIPLEY' and scan.ripley_order:
        order_details = scan.ripley_order
        order_items = RipleyOrderLine.objects.filter(order_id=scan.ripley_order.order_id)
    
    context = {
        'scan': scan,
        'order_details': order_details,
        'order_items': order_items,
    }
    
    return render(request, 'core/order_detail.html', context)
