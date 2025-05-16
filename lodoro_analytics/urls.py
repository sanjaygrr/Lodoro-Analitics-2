"""
URL configuration for lodoro_analytics project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from core.views import login_view, logout_view, home_view, api_status_view, scan_order_view, order_detail_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core URLs
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', home_view, name='home'),
    path('api-status/', api_status_view, name='api_status'),
    path('scan-order/', scan_order_view, name='scan_order'),
    path('order/<int:scan_id>/', order_detail_view, name='order_detail'),
    
    # Marketplace URLs
    path('marketplace/', include('marketplace.urls')),
    
    # Analytics URLs
    path('analytics/', include('analytics.urls')),
]
