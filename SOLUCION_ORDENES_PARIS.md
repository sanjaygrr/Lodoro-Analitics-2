# Solución para Búsqueda de Órdenes Paris

Este documento detalla la solución implementada para resolver los problemas con la búsqueda de órdenes de Paris, especialmente con órdenes como la 3010245180 que no podían ser encontradas correctamente.

## Problema

Se identificaron los siguientes problemas:

1. No se podían encontrar ciertas órdenes Paris utilizando su número de suborden (subOrderNumber), como por ejemplo la orden 3010245180.
2. Los procedimientos almacenados y métodos de búsqueda no utilizaban coincidencias parciales (LIKE).
3. La función de escaneo (pistolaje) no era lo suficientemente flexible para encontrar órdenes por coincidencias parciales.

## Soluciones Implementadas

### 1. Corrección de Procedimientos Almacenados

Se actualizaron los siguientes procedimientos almacenados:

#### get_paris_order_detail

```sql
CREATE PROCEDURE get_paris_order_detail(
    IN p_order_id VARCHAR(50)
)
BEGIN
    -- Variables para hacer el matching más flexible
    DECLARE order_id_str VARCHAR(50);
    
    -- Convertir a string y limpiar
    SET order_id_str = TRIM(p_order_id);
    
    -- Consulta principal para la orden con búsqueda mejorada
    SELECT 
        po.id,
        po.id as order_id,
        -- [otros campos]
    FROM paris_orders po
    WHERE po.id = order_id_str 
       OR po.originOrderNumber = order_id_str 
       OR po.subOrderNumber = order_id_str
       OR po.originOrderNumber LIKE CONCAT('%', order_id_str, '%')
       OR po.subOrderNumber LIKE CONCAT('%', order_id_str, '%')
    LIMIT 1;
    
    -- Consulta para los items
    -- ...
END;
```

#### get_paris_order_detail_with_bsale

Similar al anterior, pero con campos adicionales de Bsale y se añadieron condiciones LIKE para coincidencias parciales.

#### get_paris_orders

Se actualizó para incluir un parámetro de búsqueda:

```sql
CREATE PROCEDURE get_paris_orders(
    IN p_limit INT,
    IN p_offset INT,
    IN p_status VARCHAR(50),
    IN p_date_from DATE,
    IN p_date_to DATE,
    IN p_search VARCHAR(100),
    OUT p_total_count INT
)
BEGIN
    -- [código existente]
    
    -- Búsqueda por término
    IF p_search IS NOT NULL AND LENGTH(TRIM(p_search)) > 0 THEN
        SET search_clause = CONCAT(" AND (po.originOrderNumber = '", p_search, "' OR po.subOrderNumber = '", p_search, "' OR ",
                                  "po.originOrderNumber LIKE '%", p_search, "%' OR po.subOrderNumber LIKE '%", p_search, "%' OR ",
                                  "po.customer_name LIKE '%", p_search, "%' OR po.customer_email LIKE '%", p_search, "%' OR ",
                                  "po.billing_firstName LIKE '%", p_search, "%' OR po.billing_lastName LIKE '%", p_search, "%') ");
        SET where_clause = CONCAT(where_clause, search_clause);
    END IF;
    
    -- [resto del código]
END;
```

### 2. Función Auxiliar find_paris_order

Se creó una función SQL para facilitar la búsqueda de órdenes:

```sql
CREATE FUNCTION find_paris_order(p_order_id VARCHAR(50)) 
RETURNS VARCHAR(50)
DETERMINISTIC
BEGIN
    DECLARE result_id VARCHAR(50);
    
    -- Limpiar y convertir a string
    SET p_order_id = TRIM(p_order_id);
    
    -- Buscar con coincidencia exacta
    SELECT id INTO result_id
    FROM paris_orders
    WHERE id = p_order_id OR originOrderNumber = p_order_id OR subOrderNumber = p_order_id
    LIMIT 1;
    
    -- Si no se encuentra, intentar con LIKE
    IF result_id IS NULL THEN
        SELECT id INTO result_id
        FROM paris_orders
        WHERE originOrderNumber LIKE CONCAT('%', p_order_id, '%') 
           OR subOrderNumber LIKE CONCAT('%', p_order_id, '%')
        LIMIT 1;
    END IF;
    
    RETURN result_id;
END;
```

### 3. Actualización de OrderService.get_orders

Se mejoró el método `get_orders` en el servicio OrderService para soportar el parámetro de búsqueda:

```python
@staticmethod
def get_orders(marketplace, limit=50, offset=0, status=None, date_from=None, date_to=None, search=None):
    # [código existente]
    
    # Añadir parámetro de búsqueda
    if search:
        params.append(str(search))
    else:
        params.append(None)
    
    # [resto del código]
```

### 4. Mejora en la función order_scanning

Se mejoró la consulta SQL en la función `order_scanning` en `marketplace/views.py`:

```python
cursor.execute("""
    SELECT 
        id, 
        subOrderNumber, 
        originOrderNumber,
        customer_name,
        createdAt
    FROM paris_orders
    WHERE subOrderNumber = %s 
       OR subOrderNumber LIKE %s
       OR originOrderNumber = %s 
       OR originOrderNumber LIKE %s
       OR id = %s
    LIMIT 1
""", [scanned_code_str, f"%{scanned_code_str}%", scanned_code_str, f"%{scanned_code_str}%", scanned_code_str])
```

## Scripts de Solución

Se crearon varios scripts para implementar y probar las soluciones:

1. `test_paris_order_3010245180.py`: Diagnostica el problema con la orden específica.
2. `fix_paris_order_search.py`: Corrige los procedimientos de detalle y crea la función auxiliar.
3. `fix_paris_orders_procedure.py`: Actualiza el procedimiento de listado con soporte de búsqueda.
4. `update_order_service.py`: Muestra cómo actualizar el método get_orders.
5. `test_final_solution.py`: Prueba final para verificar todas las soluciones.

## Cómo Aplicar las Soluciones

Para implementar estas soluciones:

1. Ejecutar los scripts en el siguiente orden:
   ```
   python fix_paris_order_search.py
   python fix_paris_orders_procedure.py
   ```

2. Actualizar manualmente el método `get_orders` en `marketplace/order_service.py` usando el código proporcionado en `update_order_service.py`.

3. Actualizar la vista `paris_orders` en `marketplace/views.py` para pasar el parámetro de búsqueda al método `get_orders`.

4. Actualizar la función `order_scanning` en `marketplace/views.py` para utilizar la consulta SQL mejorada.

5. Ejecutar el script de prueba final:
   ```
   python test_final_solution.py
   ```

## Resultados Esperados

Después de aplicar estas soluciones:

1. La orden problemática 3010245180 podrá ser encontrada tanto en la búsqueda directa como en el escaneo.
2. Se podrán encontrar órdenes por coincidencias parciales en sus números.
3. La función de escaneo (pistolaje) será más robusta para encontrar órdenes.

## Consideraciones Adicionales

Para mejorar aún más el sistema:

1. **Normalización de Datos**: Considerar normalizar los identificadores de órdenes para garantizar coherencia.
2. **Índices en la Base de Datos**: Agregar índices en las columnas `originOrderNumber` y `subOrderNumber` para mejorar el rendimiento de búsqueda.
3. **Registro de Errores**: Implementar un registro de órdenes no encontradas para análisis futuros.
4. **Validación de Datos**: Mejorar la validación de datos para asegurar que los valores ingresados sean correctos antes de realizar las búsquedas. 