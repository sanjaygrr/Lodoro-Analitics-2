DELIMITER //

-- 1. Ventas Mensuales Mercado Libre
DROP PROCEDURE IF EXISTS get_mercadolibre_monthly_sales //
CREATE PROCEDURE get_mercadolibre_monthly_sales()
BEGIN
    SELECT
        YEAR(bd.emissionDate) AS anio,
        MONTH(bd.emissionDate) AS mes,
        COUNT(DISTINCT bd.id) AS total_boletas,
        SUM(bd.netAmount) AS venta_neta,
        SUM(bd.taxAmount) AS total_iva,
        SUM(bd.totalAmount) AS venta_total
    FROM mercadolibre_orders mo
    JOIN bsale_references br ON br.number = mo.id
    JOIN bsale_documents bd ON bd.id = br.document_id
    WHERE bd.number IS NOT NULL
    GROUP BY anio, mes
    ORDER BY anio DESC, mes DESC;
END //

-- 2. Estados de Órdenes Mercado Libre
DROP PROCEDURE IF EXISTS get_mercadolibre_monthly_status_stats //
CREATE PROCEDURE get_mercadolibre_monthly_status_stats()
BEGIN
    SELECT
        YEAR(mo.date_created) AS anio,
        MONTH(mo.date_created) AS mes,
        mo.status AS estado,
        COUNT(DISTINCT mo.id) AS total_ordenes
    FROM mercadolibre_orders mo
    GROUP BY anio, mes, estado
    ORDER BY anio DESC, mes DESC;
END //

-- 3. Top 20 Productos Históricos Mercado Libre
DROP PROCEDURE IF EXISTS get_mercadolibre_top_products //
CREATE PROCEDURE get_mercadolibre_top_products()
BEGIN
    SELECT
        bv.barCode AS ean,
        bv.description AS producto,
        bdd.variant_code AS sku_bsale,
        SUM(bdd.quantity) AS cantidad_vendida,
        SUM(bdd.totalAmount) AS total_vendido
    FROM mercadolibre_orders mo
    JOIN bsale_references br ON br.number = mo.id
    JOIN bsale_documents bd ON bd.id = br.document_id
    JOIN bsale_document_details bdd ON bdd.document_id = bd.id
    JOIN bsale_variants bv ON bv.id = bdd.variant_id
    WHERE bd.number IS NOT NULL
    GROUP BY producto, sku_bsale, ean
    ORDER BY cantidad_vendida DESC
    LIMIT 20;
END //

-- 4. Top 20 Productos por Mes Mercado Libre
DROP PROCEDURE IF EXISTS get_mercadolibre_monthly_top_products //
CREATE PROCEDURE get_mercadolibre_monthly_top_products()
BEGIN
    SELECT *
    FROM (
        SELECT
            YEAR(bd.emissionDate) AS anio,
            MONTH(bd.emissionDate) AS mes,
            bv.barCode AS ean,
            bv.description AS producto,
            bdd.variant_code AS sku_bsale,
            SUM(bdd.quantity) AS cantidad_vendida,
            SUM(bdd.totalAmount) AS total_vendido,
            ROW_NUMBER() OVER (
                PARTITION BY YEAR(bd.emissionDate), MONTH(bd.emissionDate)
                ORDER BY SUM(bdd.quantity) DESC
            ) AS fila
        FROM mercadolibre_orders mo
        JOIN bsale_references br ON br.number = mo.id
        JOIN bsale_documents bd ON bd.id = br.document_id
        JOIN bsale_document_details bdd ON bdd.document_id = bd.id
        JOIN bsale_variants bv ON bv.id = bdd.variant_id
        WHERE bd.number IS NOT NULL
        GROUP BY anio, mes, producto, sku_bsale, ean
    ) AS sub
    WHERE sub.fila <= 20
    ORDER BY anio DESC, mes DESC, fila;
END //

DELIMITER ; 