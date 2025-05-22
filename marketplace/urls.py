from django.urls import path
from . import views
from .views import procesar_orden

urlpatterns = [
    path('paris/', views.paris_orders, name='paris_orders'),
    path('ripley/', views.ripley_orders, name='ripley_orders'),
    path('falabella/', views.falabella_orders, name='falabella_orders'),
    path('mercadolibre/', views.mercadolibre_orders, name='mercadolibre_orders'),
    path('ripley/order/<str:order_id>/', views.ripley_order_detail, name='ripley_order_detail'),
    path('falabella/order/<str:order_id>/', views.falabella_order_detail, name='falabella_order_detail'),
    path('mercadolibre/order/<str:order_id>/', views.mercadolibre_order_detail, name='mercadolibre_order_detail'),
    path('scanning/', views.order_scanning, name='order_scanning'),
    path('print-multiple-boletas/', views.print_multiple_boletas, name='print_multiple_boletas'),
    path('print-picking/', views.print_picking, name='print_picking'),
    path('print-packing/', views.print_packing, name='print_packing'),
    path('paris/order/<str:order_id>/', views.paris_order_detail, name='paris_order_detail'),
    path('unir-boletas/', views.unir_boletas, name='unir_boletas'),
    path('ripley/print-picking/', views.print_ripley_picking, name='print_ripley_picking'),
    path('ripley/print-packing/', views.print_ripley_packing, name='print_ripley_packing'),
    path('marketplace/falabella/orders/', views.falabella_orders, name='falabella_orders'),
    path('marketplace/falabella/orders/print-picking/', views.print_falabella_picking, name='print_falabella_picking'),
    path('marketplace/falabella/orders/print-packing/', views.print_falabella_packing, name='print_falabella_packing'),
    path('mercadolibre/orders/<str:order_id>/', views.mercadolibre_order_detail, name='mercadolibre_order_detail'),
    path('mercadolibre/picking/', views.print_mercadolibre_picking, name='print_mercadolibre_picking'),
    path('mercadolibre/packing/', views.print_mercadolibre_packing, name='print_mercadolibre_packing'),
    path('scan-order/', views.scan_order, name='scan_order'),
    path('procesar-orden/', procesar_orden, name='procesar_orden'),
] 