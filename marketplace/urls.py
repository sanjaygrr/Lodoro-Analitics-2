from django.urls import path
from . import views

urlpatterns = [
    path('api-configs/', views.api_config_list, name='api_config_list'),
    
    # Paris
    path('paris/', views.paris_orders, name='paris_orders'),
    path('paris/<str:order_id>/', views.paris_order_detail, name='paris_order_detail'),
    
    # Ripley
    path('ripley/', views.ripley_orders, name='ripley_orders'),
    path('ripley/<str:order_id>/', views.ripley_order_detail, name='ripley_order_detail'),
    
    # Resumen
    path('summary/', views.orders_summary, name='orders_summary'),
    
    # Pistolaje
    path('scanning/', views.order_scanning, name='order_scanning'),
] 