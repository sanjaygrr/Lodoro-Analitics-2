#!/usr/bin/env python
"""
Script para limpiar archivos innecesarios después de la migración
Este script elimina los archivos temporales que se utilizaron durante
la migración a procedimientos almacenados pero que ya no son necesarios.
"""
import os
import shutil
import sys

# Lista de archivos a eliminar
FILES_TO_REMOVE = [
    # Scripts de creación de funciones/procedimientos (ya incorporados a complete_migration.py)
    "create_order_management_functions.py",
    "create_stored_functions.py",
    "create_stored_procedures.py",
    "create_tables.py",
    "add_column.py",
    
    # Scripts de migración parcial o utilidades auxiliares
    "migrate_to_stored_procedures.py",
    "use_stored_routines.py",
    "extend_marketplace_models.py",
    "inspect_db.py",
    
    # Archivos de utilidades duplicados (reemplazados por order_service.py)
    "order_db_utils.py",
    "mysql_stored_utils.py"
]

# Lista de archivos esenciales que se deben mantener
ESSENTIAL_FILES = [
    "marketplace/order_service.py",
    "analytics/stored_procedure_service.py",
    "complete_migration.py",
    "check_sql_queries.py",
    "setup_migration.py",
    "cleanup_project.py",
    "README_MIGRACION.md"
]

def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80)

def confirm_action(message):
    """Solicita confirmación al usuario"""
    response = input(f"{message} (s/n): ").lower().strip()
    return response == 's'

def backup_files(files_to_backup):
    """Crea una copia de seguridad de los archivos antes de eliminarlos"""
    backup_dir = "backup_migration_files"
    
    # Crear directorio de backup si no existe
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backed_up = []
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            # Crear subdirectorios en la carpeta de backup si es necesario
            dirname = os.path.dirname(file_path)
            if dirname:
                backup_subdir = os.path.join(backup_dir, dirname)
                if not os.path.exists(backup_subdir):
                    os.makedirs(backup_subdir)
            
            # Copiar archivo a la carpeta de backup
            backup_path = os.path.join(backup_dir, file_path)
            shutil.copy2(file_path, backup_path)
            backed_up.append(file_path)
    
    return backed_up, backup_dir

def remove_files(files_to_remove):
    """Elimina los archivos especificados"""
    removed = []
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                removed.append(file_path)
                print(f"✅ Eliminado: {file_path}")
            except Exception as e:
                print(f"❌ Error al eliminar {file_path}: {str(e)}")
    
    return removed

def update_requirements():
    """Actualiza el archivo requirements.txt para mantener solo dependencias necesarias"""
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            requirements = f.readlines()
        
        # Mantener solo las dependencias necesarias
        essential_deps = []
        for req in requirements:
            package = req.split("==")[0].strip() if "==" in req else req.strip()
            if package and package not in ["colorama"]:  # Colorama solo es necesaria para check_sql_queries.py
                essential_deps.append(req)
        
        # Reescribir el archivo
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.writelines(essential_deps)
        
        print("✅ Archivo requirements.txt actualizado")
        return True
    except Exception as e:
        print(f"❌ Error al actualizar requirements.txt: {str(e)}")
        return False

def main():
    """Función principal"""
    print_header("LIMPIEZA DE ARCHIVOS DE MIGRACIÓN")
    print("\nEste script eliminará los archivos temporales utilizados durante la migración")
    print("a procedimientos almacenados que ya no son necesarios para el proyecto.")
    
    # Verificar los archivos que existen
    existing_files = [f for f in FILES_TO_REMOVE if os.path.exists(f)]
    
    if not existing_files:
        print("\n✅ No se encontraron archivos innecesarios para eliminar.")
        return 0
    
    # Mostrar los archivos que se eliminarán
    print("\nSe eliminarán los siguientes archivos:")
    for file_path in existing_files:
        print(f"  - {file_path}")
    
    # Solicitar confirmación
    if not confirm_action("\n¿Desea continuar con la eliminación de estos archivos?"):
        print("\nOperación cancelada por el usuario.")
        return 0
    
    # Crear backup
    print("\nCreando copia de seguridad de los archivos...")
    backed_up, backup_dir = backup_files(existing_files)
    if backed_up:
        print(f"✅ Se creó una copia de seguridad de {len(backed_up)} archivos en la carpeta '{backup_dir}'")
    else:
        print("⚠️ No se creó ninguna copia de seguridad.")
    
    # Eliminar archivos
    print("\nEliminando archivos innecesarios...")
    removed = remove_files(existing_files)
    
    # Actualizar requirements.txt
    print("\nActualizando requirements.txt...")
    update_requirements()
    
    # Resumen
    print_header("RESUMEN DE LA LIMPIEZA")
    print(f"\nSe eliminaron {len(removed)} archivos innecesarios.")
    print(f"Se creó una copia de seguridad en la carpeta '{backup_dir}'.")
    print("\nLos siguientes archivos son esenciales y se han mantenido:")
    for file_path in ESSENTIAL_FILES:
        if os.path.exists(file_path):
            print(f"  - {file_path}")
    
    print("\n✅ La limpieza ha finalizado exitosamente.")
    print("""
Recomendaciones:
1. Ejecute 'python check_sql_queries.py' para verificar que no haya consultas SQL directas
2. Revise el archivo README_MIGRACION.md para entender la estructura actual
3. Si necesita restaurar algún archivo, puede encontrarlo en la carpeta de backup
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 