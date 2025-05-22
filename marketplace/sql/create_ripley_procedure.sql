DELIMITER //

DROP PROCEDURE IF EXISTS get_ripley_orders //

CREATE PROCEDURE get_ripley_orders(
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
        ro.order_id AS orden_ripley,
        ro.commercial_id,
        CONCAT(rc.firstname, ' ', rc.lastname) AS cliente,
        ra.street_1 AS calle,
        ra.city AS ciudad,
        ra.state AS region,
        ra.zip_code AS codigo_postal,
        rol.product_title AS producto,
        bd.number AS numero_boleta,
        bd.urlPdf AS url_boleta,
        bdd.variant_code AS sku_bsale,
        bv.barCode AS ean_bsale,
        bd.netAmount AS costo_neto,
        bd.taxAmount AS iva,
        bd.totalAmount AS costo_total,
        ro.shipping_price AS costo_despacho,
        ro.order_state AS estado_despacho,
        ro.created_date AS fecha_creacion,
        ro.last_updated_date AS fecha_actualizacion,
        ro.orden_impresa,
        ro.orden_procesada,
        ro.boleta_impresa,
        ro.orden_despachada
    FROM ripley_orders ro
    JOIN ripley_order_lines rol ON rol.order_id = ro.order_id
    LEFT JOIN ripley_customers rc ON rc.customer_id = ro.customer_id
    LEFT JOIN ripley_addresses ra ON ra.customer_id = ro.customer_id AND ra.type = 'shipping'
    JOIN bsale_references br ON br.number = ro.commercial_id
    JOIN bsale_documents bd ON bd.id = br.document_id
    JOIN bsale_document_details bdd ON bdd.document_id = bd.id
    JOIN bsale_variants bv ON bv.id = bdd.variant_id
    WHERE 1=1
        AND (p_status IS NULL OR ro.order_state = p_status)
        AND (p_processed IS NULL OR ro.orden_procesada = p_processed)
        AND (p_printed IS NULL OR ro.orden_impresa = p_printed)
        AND (p_date_from IS NULL OR ro.created_date >= p_date_from)
        AND (p_date_to IS NULL OR ro.created_date <= p_date_to)
        AND (p_search IS NULL OR 
            ro.order_id LIKE CONCAT('%', p_search, '%') OR
            ro.commercial_id LIKE CONCAT('%', p_search, '%') OR
            CONCAT(rc.firstname, ' ', rc.lastname) LIKE CONCAT('%', p_search, '%') OR
            rol.product_title LIKE CONCAT('%', p_search, '%')
        )
    ORDER BY ro.created_date DESC
    LIMIT p_limit
    OFFSET p_offset;

    -- Obtener total de órdenes y monto total
    SELECT 
        COUNT(DISTINCT ro.order_id),
        COALESCE(SUM(bd.totalAmount), 0)
    INTO p_total_orders, p_total_amount
    FROM ripley_orders ro
    JOIN ripley_order_lines rol ON rol.order_id = ro.order_id
    LEFT JOIN ripley_customers rc ON rc.customer_id = ro.customer_id
    JOIN bsale_references br ON br.number = ro.commercial_id
    JOIN bsale_documents bd ON bd.id = br.document_id
    WHERE 1=1
        AND (p_status IS NULL OR ro.order_state = p_status)
        AND (p_processed IS NULL OR ro.orden_procesada = p_processed)
        AND (p_printed IS NULL OR ro.orden_impresa = p_printed)
        AND (p_date_from IS NULL OR ro.created_date >= p_date_from)
        AND (p_date_to IS NULL OR ro.created_date <= p_date_to)
        AND (p_search IS NULL OR 
            ro.order_id LIKE CONCAT('%', p_search, '%') OR
            ro.commercial_id LIKE CONCAT('%', p_search, '%') OR
            CONCAT(rc.firstname, ' ', rc.lastname) LIKE CONCAT('%', p_search, '%') OR
            rol.product_title LIKE CONCAT('%', p_search, '%')
        );
END //

DELIMITER ; 