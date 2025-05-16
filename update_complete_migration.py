#!/usr/bin/env python
"""
Script para actualizar complete_migration.py con todas las funciones necesarias
Este script incorpora las funciones de create_order_management_functions.py y otros 
archivos dentro de complete_migration.py para que sea autocontenido.
"""
import os
import sys
import re
import shutil
from datetime import datetime

def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80)

def backup_file(file_path):
    """Crea una copia de seguridad del archivo"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"✅ Copia de seguridad creada: {backup_path}")
        return backup_path
    return None

def extract_functions(file_path, function_pattern=r"def\s+([a-zA-Z0-9_]+)\s*\(.*?\):\s*(?:\"\"\".*?\"\"\"\s*)?(.+?)(?=\ndef|\Z)", flags=re.DOTALL):
    """Extrae las funciones de un archivo Python"""
    if not os.path.exists(file_path):
        print(f"⚠️ El archivo {file_path} no existe.")
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todas las definiciones de funciones
    functions = {}
    for match in re.finditer(function_pattern, content, flags):
        function_name = match.group(1)
        function_code = match.group(0)
        functions[function_name] = function_code
    
    return functions

def update_complete_migration():
    """Actualiza el archivo complete_migration.py con las funciones necesarias"""
    # Archivos a procesar
    source_files = [
        "create_order_management_functions.py",
        "create_stored_functions.py",
        "create_stored_procedures.py"
    ]
    
    target_file = "complete_migration.py"
    
    # Hacer backup del archivo original
    backup_path = backup_file(target_file)
    if not backup_path:
        print(f"❌ No se pudo hacer backup de {target_file}. Abortando.")
        return False
    
    # Leer el archivo original
    with open(target_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Extraer funciones de los archivos fuente
    all_functions = {}
    for file_path in source_files:
        if os.path.exists(file_path):
            print(f"Procesando {file_path}...")
            functions = extract_functions(file_path)
            print(f"  Se encontraron {len(functions)} funciones.")
            all_functions.update(functions)
    
    # Verificar si ya existen estas funciones en complete_migration.py
    existing_functions = extract_functions(target_file)
    new_functions = {k: v for k, v in all_functions.items() if k not in existing_functions}
    
    if not new_functions:
        print("⚠️ No se encontraron nuevas funciones para agregar.")
        return False
    
    print(f"Se agregarán {len(new_functions)} nuevas funciones a {target_file}:")
    for func_name in new_functions:
        print(f"  - {func_name}")
    
    # Encontrar el punto de inserción (justo antes de main())
    import_pattern = r"from create_order_management_functions import \(.*?\)"
    main_pattern = r"def main\(\):"
    import_match = re.search(import_pattern, original_content, re.DOTALL)
    main_match = re.search(main_pattern, original_content)
    
    if not main_match:
        print(f"❌ No se pudo encontrar la función main() en {target_file}. Abortando.")
        return False
    
    # Modificar el contenido
    new_content = original_content
    
    # Eliminar la importación de funciones
    if import_match:
        new_content = new_content.replace(import_match.group(0), "# Todas las funciones necesarias están incluidas en este archivo")
    
    # Insertar las nuevas funciones antes de main()
    insertion_point = main_match.start()
    functions_to_insert = "\n\n".join(new_functions.values())
    new_content = new_content[:insertion_point] + functions_to_insert + "\n\n" + new_content[insertion_point:]
    
    # Guardar el archivo modificado
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ El archivo {target_file} ha sido actualizado con {len(new_functions)} nuevas funciones.")
    return True

def main():
    """Función principal"""
    print_header("ACTUALIZACIÓN DE COMPLETE_MIGRATION.PY")
    print("\nEste script actualizará complete_migration.py para incluir todas las funciones")
    print("necesarias desde los scripts que serán eliminados posteriormente.")
    
    # Actualizar complete_migration.py
    success = update_complete_migration()
    
    if success:
        print_header("PROCESO COMPLETADO")
        print("""
Ahora puede ejecutar:
1. python complete_migration.py - Para verificar que todo funciona correctamente
2. python cleanup_project.py - Para eliminar los archivos innecesarios
""")
    else:
        print_header("PROCESO INCOMPLETO")
        print("""
No se pudieron incorporar nuevas funciones a complete_migration.py.
Verifique manualmente si:
1. Las funciones ya están incluidas
2. El archivo tiene un formato diferente al esperado
""")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 