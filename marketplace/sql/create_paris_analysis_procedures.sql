DELIMITER //

-- Procedimiento para obtener top 20 productos históricos
DROP PROCEDURE IF EXISTS get_paris_top_products //
CREATE PROCEDURE get_paris_top_products()
BEGIN
    SELECT
        bv.barCode AS ean,
        bv.description AS producto,
        bdd.variant_code AS sku_bsale,
        SUM(bdd.quantity) AS cantidad_vendida,
        SUM(bdd.totalAmount) AS total_vendido
    FROM paris_orders po
    JOIN paris_items pi ON pi.subOrderNumber = po.subOrderNumber
    LEFT JOIN bsale_references br ON br.number = po.subOrderNumber
    LEFT JOIN bsale_documents bd ON bd.id = br.document_id
    LEFT JOIN bsale_document_details bdd ON bdd.document_id = bd.id
    LEFT JOIN bsale_variants bv ON bv.id = bdd.variant_id
    WHERE bd.number IS NOT NULL
    GROUP BY producto, sku_bsale, ean
    ORDER BY cantidad_vendida DESC
    LIMIT 20;
END //

-- Procedimiento para obtener top 20 productos por mes
DROP PROCEDURE IF EXISTS get_paris_monthly_top_products //
CREATE PROCEDURE get_paris_monthly_top_products()
BEGIN
    SELECT *
    FROM (
        SELECT
            DATE_FORMAT(bd.emissionDate, '%Y-%m') AS periodo,
            bv.id AS variant_id,
            bv.description AS producto,
            bv.barCode AS ean,
            bdd.variant_code AS sku_bsale,
            SUM(bdd.quantity) AS cantidad_vendida,
            SUM(bdd.totalAmount) AS total_vendido,
            ROW_NUMBER() OVER (
                PARTITION BY YEAR(bd.emissionDate), MONTH(bd.emissionDate)
                ORDER BY SUM(bdd.quantity) DESC
            ) AS fila
        FROM paris_orders po
        JOIN paris_items pi ON pi.subOrderNumber = po.subOrderNumber
        LEFT JOIN bsale_references br ON br.number = po.subOrderNumber
        LEFT JOIN bsale_documents bd ON bd.id = br.document_id
        LEFT JOIN bsale_document_details bdd ON bdd.document_id = bd.id
        LEFT JOIN bsale_variants bv ON bv.id = bdd.variant_id
        WHERE bd.number IS NOT NULL
        GROUP BY periodo, variant_id, producto, sku_bsale, ean
    ) AS sub
    WHERE sub.fila <= 20
    ORDER BY periodo DESC, fila;
END //

-- Procedimiento para obtener estadísticas por estado mensual
DROP PROCEDURE IF EXISTS get_paris_monthly_status_stats //
CREATE PROCEDURE get_paris_monthly_status_stats()
BEGIN
    SELECT
        YEAR(po.originOrderDate) AS anio,
        MONTH(po.originOrderDate) AS mes,
        pst.translate AS estado,
        COUNT(DISTINCT po.subOrderNumber) AS total_ordenes,
        COUNT(*) AS total_productos_aprox,
        SUM(pi.grossPrice) AS monto_estimado
    FROM paris_orders po
    JOIN paris_items pi ON pi.subOrderNumber = po.subOrderNumber
    LEFT JOIN paris_subOrders ps ON ps.subOrderNumber = po.subOrderNumber
    LEFT JOIN paris_statuses pst ON pst.id = ps.statusId
    GROUP BY anio, mes, estado
    ORDER BY anio DESC, mes DESC, estado;
END //

-- Procedimiento para obtener ventas mensuales
DROP PROCEDURE IF EXISTS get_paris_monthly_sales //
CREATE PROCEDURE get_paris_monthly_sales()
BEGIN
    SELECT
        YEAR(bd.emissionDate) AS anio,
        MONTH(bd.emissionDate) AS mes,
        COUNT(DISTINCT bd.id) AS total_boletas,
        SUM(bd.netAmount) AS venta_neta,
        SUM(bd.taxAmount) AS total_iva,
        SUM(bd.totalAmount) AS venta_total
    FROM paris_orders po
    LEFT JOIN bsale_references br ON br.number = po.subOrderNumber
    LEFT JOIN bsale_documents bd ON bd.id = br.document_id
    WHERE bd.number IS NOT NULL
    GROUP BY anio, mes
    ORDER BY anio DESC, mes DESC;
END //

DELIMITER ; 