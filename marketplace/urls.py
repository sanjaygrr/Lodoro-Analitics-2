from django.urls import path
from . import views

urlpatterns = [
    path('paris/', views.paris_orders, name='paris_orders'),
    path('ripley/', views.ripley_orders, name='ripley_orders'),
    path('scanning/', views.order_scanning, name='order_scanning'),
    path('print-multiple-boletas/', views.print_multiple_boletas, name='print_multiple_boletas'),
] 