DELIMITER //

DROP PROCEDURE IF EXISTS get_mercadolibre_orders //

CREATE PROCEDURE get_mercadolibre_orders(
    IN p_status VARCHAR(50),
    IN p_processed VARCHAR(50),
    IN p_printed VARCHAR(50),
    IN p_date_from DATE,
    IN p_date_to DATE,
    IN p_search VARCHAR(255),
    IN p_limit INT,
    IN p_offset INT,
    OUT p_total_orders INT,
    OUT p_total_amount DECIMAL(10,2)
)
BEGIN
    -- Consulta principal
    SELECT DISTINCT
        mo.id AS orden_mercadolibre,
        mo.buyer_nickname AS cliente,
        mo.status AS estado_orden,
        mo.paid_amount AS total_pagado,
        mo.total_amount AS total_orden,
        mo.currency_id AS moneda,
        mo.cancel_detail AS detalle_anulacion,
        mo.tags AS etiquetas_meli,

        GROUP_CONCAT(DISTINCT moi.title SEPARATOR ' | ') AS productos,
        GROUP_CONCAT(DISTINCT moi.seller_sku SEPARATOR ' | ') AS sku_meli,
        GROUP_CONCAT(DISTINCT moi.quantity SEPARATOR ' | ') AS cantidades,
        GROUP_CONCAT(DISTINCT moi.unit_price SEPARATOR ' | ') AS precio_unitario,

        GROUP_CONCAT(DISTINCT bdd.variant_code SEPARATOR ' | ') AS sku_bsale,
        GROUP_CONCAT(DISTINCT bv.barCode SEPARATOR ' | ') AS ean_bsale,
        GROUP_CONCAT(DISTINCT bv.description SEPARATOR ' | ') AS descripcion_bsale,

        bd.number AS numero_boleta,
        bd.urlPdf AS url_boleta,
        bd.netAmount AS costo_neto,
        bd.taxAmount AS iva,
        bd.totalAmount AS costo_total,
        bd.emissionDate AS fecha_emision_boleta,
        bd.address AS direccion_cliente,
        bd.city AS ciudad_cliente,

        mo.date_created AS fecha_creacion,
        mo.last_updated AS fecha_actualizacion,

        mo.orden_impresa,
        mo.orden_procesada,
        mo.orden_despachada,
        mo.boleta_impresa
    FROM mercadolibre_orders mo
    LEFT JOIN mercadolibre_order_items moi ON moi.order_id = mo.id
    JOIN bsale_references br ON br.number = mo.id
    JOIN bsale_documents bd ON bd.id = br.document_id
    JOIN bsale_document_details bdd ON bdd.document_id = bd.id
    JOIN bsale_variants bv ON bv.id = bdd.variant_id
    WHERE 1=1
        AND (p_status IS NULL OR mo.status = p_status)
        AND (p_processed IS NULL OR mo.orden_procesada = p_processed)
        AND (p_printed IS NULL OR mo.orden_impresa = p_printed)
        AND (p_date_from IS NULL OR mo.date_created >= p_date_from)
        AND (p_date_to IS NULL OR mo.date_created <= p_date_to)
        AND (p_search IS NULL OR 
            mo.id LIKE CONCAT('%', p_search, '%') OR
            mo.buyer_nickname LIKE CONCAT('%', p_search, '%') OR
            moi.title LIKE CONCAT('%', p_search, '%')
        )
    GROUP BY mo.id
    ORDER BY mo.date_created DESC
    LIMIT p_limit
    OFFSET p_offset;

    -- Obtener total de órdenes y monto total
    SELECT 
        COUNT(DISTINCT mo.id),
        COALESCE(SUM(bd.totalAmount), 0)
    INTO p_total_orders, p_total_amount
    FROM mercadolibre_orders mo
    LEFT JOIN mercadolibre_order_items moi ON moi.order_id = mo.id
    JOIN bsale_references br ON br.number = mo.id
    JOIN bsale_documents bd ON bd.id = br.document_id
    WHERE 1=1
        AND (p_status IS NULL OR mo.status = p_status)
        AND (p_processed IS NULL OR mo.orden_procesada = p_processed)
        AND (p_printed IS NULL OR mo.orden_impresa = p_printed)
        AND (p_date_from IS NULL OR mo.date_created >= p_date_from)
        AND (p_date_to IS NULL OR mo.date_created <= p_date_to)
        AND (p_search IS NULL OR 
            mo.id LIKE CONCAT('%', p_search, '%') OR
            mo.buyer_nickname LIKE CONCAT('%', p_search, '%') OR
            moi.title LIKE CONCAT('%', p_search, '%')
        );
END //

DELIMITER ; 