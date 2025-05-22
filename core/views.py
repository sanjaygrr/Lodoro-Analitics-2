from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def dashboard(request):
    """Vista para el dashboard principal"""
    return render(request, 'core/dashboard.html')

@login_required
def profile(request):
    """Vista para el perfil del usuario"""
    return render(request, 'core/profile.html')

@login_required
def settings(request):
    """Vista para la configuración del sistema"""
    return render(request, 'core/settings.html') 