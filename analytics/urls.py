from django.urls import path
from . import views, views_stored_procs

urlpatterns = [
    # Vistas tradicionales (que utilizan ORM)
    path('dashboard/', views.sales_dashboard, name='sales_dashboard'),
    path('products/', views.product_performance, name='product_performance'),
    path('saved/', views.saved_analytics, name='saved_analytics'),
    
    # Vistas que utilizan procedimientos almacenados
    path('dashboard/sp/', views_stored_procs.sales_dashboard, name='sp_sales_dashboard'),
    path('products/sp/', views_stored_procs.product_performance, name='sp_product_performance'),
] 