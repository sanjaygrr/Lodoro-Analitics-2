#!/usr/bin/env python
"""
Script para preparar el entorno para la migración a procedimientos almacenados
Este script:
1. Verifica e instala las dependencias necesarias
2. Ejecuta los scripts de migración en el orden correcto
3. Realiza una comprobación final para asegurar que todo está correctamente configurado
"""
import os
import sys
import subprocess
import time
from datetime import datetime

def print_section(title):
    """Imprime una sección con formato"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def check_dependencies():
    """Verifica e instala las dependencias necesarias"""
    print_section("Verificando dependencias")
    
    try:
        # Intentar importar las dependencias requeridas
        import django
        import MySQLdb
        import colorama
        print("✅ Todas las dependencias están instaladas.")
        return True
    except ImportError as e:
        print(f"❌ Falta una dependencia: {str(e)}")
        
        # Intentar instalar las dependencias
        print("\nInstalando dependencias...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dependencias instaladas correctamente.")
            return True
        except subprocess.CalledProcessError:
            print("❌ No se pudieron instalar las dependencias.")
            return False

def setup_django():
    """Configura Django para poder ejecutar los scripts"""
    print_section("Configurando Django")
    
    # Verificar que existe el archivo de settings
    if not os.path.exists(os.path.join("lodoro_analytics", "settings.py")):
        print("❌ No se encontró el archivo de configuración de Django.")
        return False
    
    # Configurar el entorno de Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lodoro_analytics.settings')
    
    try:
        import django
        django.setup()
        from django.db import connection
        
        # Probar la conexión a la base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        if result and result[0] == 1:
            print("✅ Django configurado y conectado a la base de datos correctamente.")
            return True
        else:
            print("❌ No se pudo establecer una conexión válida con la base de datos.")
            return False
    except Exception as e:
        print(f"❌ Error al configurar Django: {str(e)}")
        return False

def run_migration_scripts():
    """Ejecuta los scripts de migración en el orden correcto"""
    print_section("Ejecutando scripts de migración")
    
    scripts = [
        "complete_migration.py",
    ]
    
    all_success = True
    
    for script in scripts:
        print(f"\nEjecutando {script}...")
        try:
            start_time = time.time()
            result = subprocess.run([sys.executable, script], check=True)
            elapsed_time = time.time() - start_time
            
            print(f"✅ {script} completado en {elapsed_time:.2f} segundos.")
        except subprocess.CalledProcessError:
            print(f"❌ Error al ejecutar {script}.")
            all_success = False
            break
    
    return all_success

def run_verification():
    """Ejecuta el script de verificación para comprobar consultas SQL directas"""
    print_section("Verificando consultas SQL directas")
    
    try:
        result = subprocess.run([sys.executable, "check_sql_queries.py"], check=True)
        print("\n✅ Verificación completada.")
        return True
    except subprocess.CalledProcessError:
        print("\n⚠️ La verificación detectó consultas SQL directas. Revise los resultados.")
        return False

def main():
    """Función principal"""
    print("\n🚀 Iniciando configuración para la migración a procedimientos almacenados...")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Paso 1: Verificar dependencias
    if not check_dependencies():
        print("\n❌ No se pudieron verificar las dependencias. Abortando.")
        return 1
    
    # Paso 2: Configurar Django
    if not setup_django():
        print("\n❌ No se pudo configurar Django. Abortando.")
        return 1
    
    # Paso 3: Ejecutar scripts de migración
    if not run_migration_scripts():
        print("\n❌ Error en los scripts de migración. Abortando.")
        return 1
    
    # Paso 4: Ejecutar verificación
    run_verification()
    
    print_section("Resumen")
    print("✅ La configuración ha sido completada exitosamente.")
    print("""
Próximos pasos:
1. Revise el archivo README_MIGRACION.md para más detalles sobre la implementación
2. Actualice los enlaces en los templates si es necesario
3. Ejecute las pruebas para verificar que todo funciona correctamente

Para ejecutar los procedimientos almacenados, utilice:
- OrderService para operaciones de órdenes
- AnalyticsService para análisis y estadísticas
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 