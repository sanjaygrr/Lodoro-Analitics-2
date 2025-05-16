#!/usr/bin/env python
"""
Script para verificar si quedan consultas SQL directas en el código
Este script busca patrones comunes de consultas SQL directas en todos los archivos .py
del proyecto y genera un informe.
"""
import os
import re
import sys
from colorama import init, Fore, Style

# Inicializar colorama para formatear la salida en la consola
init()

# Patrones de búsqueda de consultas SQL directas
SQL_PATTERNS = [
    r'\.objects\.raw\(',  # ORM raw query
    r'cursor\.execute\("SELECT',  # Queries SQL directas en cursor.execute
    r'cursor\.execute\("INSERT',
    r'cursor\.execute\("UPDATE',
    r'cursor\.execute\("DELETE',
    r'cursor\.execute\("""SELECT',
    r'cursor\.execute\("""INSERT',
    r'cursor\.execute\("""UPDATE',
    r'cursor\.execute\("""DELETE',
    r'\.extra\(where=',  # Cláusula extra en ORM
    r'cursor.executemany\(',  # Queries masivas
]

# Patrones a excluir (procedimientos almacenados y scripts de migración)
EXCLUDE_PATTERNS = [
    r'cursor\.execute\(\s*"CALL',  # Llamadas a procedimientos almacenados
    r'cursor\.execute\(\s*f"CALL',
    r'cursor\.execute\(\s*"""CALL',
    r'cursor\.execute\(\s*"SET @',  # Configuración de variables MySQL
    r'cursor\.execute\(\s*"CREATE',  # Creación de tablas y procedimientos
    r'cursor\.execute\(\s*"""CREATE',
    r'cursor\.execute\(\s*"DROP',  # Eliminación de tablas y procedimientos
    r'cursor\.execute\(\s*"INSERT INTO system_migrations',  # Registro de migraciones
    r'cursor\.execute\(\s*"""INSERT INTO system_migrations',
    r'create_.*_procedure\.py',  # Scripts de creación de procedimientos
    r'migrate.*\.py',  # Scripts de migración
    r'/migrations/',  # Carpeta de migraciones de Django
]

def should_exclude_file(file_path):
    """Determinar si un archivo debe ser excluido del análisis"""
    exclude_dirs = [
        'venv', 
        '__pycache__', 
        '.git', 
        'migrations'
    ]
    
    # Excluir directorios específicos
    for dir_name in exclude_dirs:
        if f'/{dir_name}/' in file_path or file_path.startswith(f'{dir_name}/'):
            return True
    
    # Excluir archivos de scripts de creación o migración
    for pattern in [r'create_.*_function\.py', r'create_.*_procedure\.py', r'migrate.*\.py']:
        if re.search(pattern, file_path):
            return True
    
    return False

def is_stored_procedure_call(line):
    """Determinar si una línea es una llamada a un procedimiento almacenado"""
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, line):
            return True
    return False

def scan_file(file_path):
    """Escanear un archivo en busca de consultas SQL directas"""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Verificar si la línea contiene una consulta SQL directa
                for pattern in SQL_PATTERNS:
                    if re.search(pattern, line) and not is_stored_procedure_call(line):
                        findings.append({
                            'line_num': line_num,
                            'line': line.strip(),
                            'pattern': pattern
                        })
                        break
    except Exception as e:
        print(f"Error al escanear {file_path}: {str(e)}")
    
    return findings

def scan_directory(directory='.'):
    """Escanear recursivamente un directorio en busca de archivos .py"""
    all_findings = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Comprobar si el archivo debe ser excluido
                if should_exclude_file(file_path):
                    continue
                
                findings = scan_file(file_path)
                if findings:
                    all_findings[file_path] = findings
    
    return all_findings

def format_findings(all_findings):
    """Formatear los hallazgos para la salida en consola"""
    if not all_findings:
        return f"{Fore.GREEN}¡No se encontraron consultas SQL directas en el código!{Style.RESET_ALL}"
    
    output = []
    output.append(f"{Fore.YELLOW}Se encontraron consultas SQL directas en los siguientes archivos:{Style.RESET_ALL}\n")
    
    total_findings = 0
    
    for file_path, findings in all_findings.items():
        output.append(f"{Fore.CYAN}Archivo: {file_path}{Style.RESET_ALL}")
        
        for finding in findings:
            output.append(f"  Línea {finding['line_num']}: {Fore.RED}{finding['line']}{Style.RESET_ALL}")
            total_findings += 1
        
        output.append("")
    
    output.append(f"{Fore.YELLOW}Total de consultas SQL directas encontradas: {total_findings}{Style.RESET_ALL}")
    output.append(f"\n{Fore.WHITE}Recomendación: Reemplazar estas consultas con llamadas a procedimientos almacenados utilizando la clase OrderService o AnalyticsService.{Style.RESET_ALL}")
    
    return "\n".join(output)

def main():
    """Función principal"""
    print(f"{Fore.CYAN}Escaneando el proyecto en busca de consultas SQL directas...{Style.RESET_ALL}")
    
    # Escanear el directorio actual
    all_findings = scan_directory()
    
    # Formatear y mostrar los hallazgos
    print("\n" + format_findings(all_findings))
    
    # Retornar un código de salida basado en si se encontraron consultas directas
    return 1 if all_findings else 0

if __name__ == "__main__":
    sys.exit(main()) 