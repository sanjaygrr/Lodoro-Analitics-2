# Instrucciones para Completar la Migración a Procedimientos Almacenados

Este documento proporciona instrucciones paso a paso para completar la migración a procedimientos almacenados en MySQL y limpiar los archivos temporales que ya no son necesarios.

## Paso 1: Preparar el Entorno

Asegúrese de tener todas las dependencias instaladas:

```bash
pip install -r requirements.txt
```

## Paso 2: Actualizar complete_migration.py

Primero, vamos a actualizar el archivo `complete_migration.py` para que contenga todas las funciones necesarias y sea autocontenido:

```bash
python update_complete_migration.py
```

Este script:
1. Hace una copia de seguridad de `complete_migration.py`
2. Extrae todas las funciones de los archivos que se eliminarán
3. Las incorpora en `complete_migration.py`
4. Elimina las referencias a importaciones que ya no serán necesarias

## Paso 3: Verificar que complete_migration.py Funciona Correctamente

Ejecute el script actualizado para asegurarse de que todas las funciones se han incorporado correctamente:

```bash
python complete_migration.py
```

Verifique que todos los procedimientos almacenados se crean sin errores.

## Paso 4: Limpiar Archivos Innecesarios

Una vez que `complete_migration.py` funciona correctamente, puede eliminar los archivos temporales que ya no son necesarios:

```bash
python cleanup_project.py
```

Este script:
1. Identifica los archivos que ya no son necesarios
2. Crea una copia de seguridad de estos archivos en la carpeta `backup_migration_files`
3. Elimina los archivos originales
4. Actualiza `requirements.txt` para mantener solo dependencias esenciales

## Paso 5: Verificar que No Quedan Consultas SQL Directas

Ejecute el script de verificación para asegurarse de que no quedan consultas SQL directas en el código:

```bash
python check_sql_queries.py
```

Este script buscará en todo el proyecto consultas SQL que no utilicen procedimientos almacenados.

## Paso 6: Actualizar los Enlaces en las Plantillas (Opcional)

Si desea cambiar a las vistas que utilizan procedimientos almacenados:

1. Para analytics, actualice los enlaces de:
   - `/analytics/dashboard/` a `/analytics/dashboard/sp/`
   - `/analytics/products/` a `/analytics/products/sp/`

## Estructura Final del Proyecto

Después de completar estos pasos, su proyecto debería tener la siguiente estructura:

1. **Archivos Principales:**
   - `marketplace/order_service.py` - Servicio para operaciones de órdenes
   - `analytics/stored_procedure_service.py` - Servicio para análisis
   - `complete_migration.py` - Script para crear todos los procedimientos almacenados
   - `check_sql_queries.py` - Herramienta para verificar consultas SQL directas

2. **Documentación:**
   - `README_MIGRACION.md` - Documento detallado sobre la implementación
   - `INSTRUCCIONES_FINALES.md` - Este documento

## Solución de Problemas

### Si `update_complete_migration.py` Falla:

Si el script de actualización no puede incorporar las funciones correctamente, puede:

1. Revisar manualmente los archivos `create_order_management_functions.py`, `create_stored_functions.py`, etc.
2. Copiar manualmente las funciones relevantes a `complete_migration.py`
3. Asegurarse de que todas las funciones necesarias estén disponibles

### Si Algún Procedimiento Almacenado No Se Crea Correctamente:

1. Revise el archivo `complete_migration.py`
2. Asegúrese de que la función para crear ese procedimiento esté correctamente definida
3. Ejecute `python complete_migration.py` nuevamente

### Si Necesita Restaurar Archivos Eliminados:

Todos los archivos eliminados se respaldan en la carpeta `backup_migration_files` antes de ser eliminados. Puede copiarlos de vuelta si es necesario. 