DELIMITER //

DROP PROCEDURE IF EXISTS get_falabella_orders //

CREATE PROCEDURE get_falabella_orders(
    IN p_status VARCHAR(50),
    IN p_processed TINYINT,
    IN p_printed TINYINT,
    IN p_date_from DATETIME,
    IN p_date_to DATETIME,
    IN p_search VARCHAR(255),
    IN p_limit INT,
    IN p_offset INT,
    OUT p_total_orders INT,
    OUT p_total_amount DECIMAL(10,2)
)
BEGIN
    -- Consulta principal
    SELECT DISTINCT
        fo.order_number AS orden_falabella,
        CONCAT(fo.customer_first_name, ' ', fo.customer_last_name) AS cliente,
        fosa.address1 AS calle,
        fosa.city AS ciudad,
        fosa.region AS region,
        foi.name AS producto,
        bd.number AS numero_boleta,
        bd.urlPdf AS url_boleta,
        bdd.variant_code AS sku_bsale,
        bv.barCode AS ean_bsale,
        bd.netAmount AS costo_neto,
        bd.taxAmount AS iva,
        bd.totalAmount AS costo_total,
        fo.shipping_fee_total AS costo_despacho,
        fo.status AS estado_despacho,
        fo.created_at AS fecha_creacion,
        fo.updated_at AS fecha_actualizacion,
        fo.printed AS orden_impresa,
        fo.processed AS orden_procesada,
        fo.dispatched AS orden_despachada,
        fo.invoice_printed AS boleta_impresa
    FROM falabella_orders fo
    JOIN falabella_order_items foi ON foi.order_id = fo.order_id
    LEFT JOIN falabella_orders_shipping_address fosa ON fosa.order_id = fo.order_id
    JOIN bsale_references br ON br.number = fo.order_number
    JOIN bsale_documents bd ON bd.id = br.document_id
    JOIN bsale_document_details bdd ON bdd.document_id = bd.id
    JOIN bsale_variants bv ON bv.id = bdd.variant_id
    WHERE 1=1
        AND (p_status IS NULL OR fo.status COLLATE utf8mb4_unicode_ci = p_status COLLATE utf8mb4_unicode_ci)
        AND (p_processed IS NULL OR fo.processed = p_processed)
        AND (p_printed IS NULL OR fo.printed = p_printed)
        AND (p_date_from IS NULL OR fo.created_at >= p_date_from)
        AND (p_date_to IS NULL OR fo.created_at <= p_date_to)
        AND (
            p_search IS NULL 
            OR fo.order_number COLLATE utf8mb4_unicode_ci LIKE CONCAT('%', p_search, '%') COLLATE utf8mb4_unicode_ci
            OR CONCAT(fo.customer_first_name, ' ', fo.customer_last_name) COLLATE utf8mb4_unicode_ci LIKE CONCAT('%', p_search, '%') COLLATE utf8mb4_unicode_ci
            OR foi.name COLLATE utf8mb4_unicode_ci LIKE CONCAT('%', p_search, '%') COLLATE utf8mb4_unicode_ci
        )
    ORDER BY fo.created_at DESC
    LIMIT p_limit OFFSET p_offset;

    -- Obtener total de órdenes y monto total
    SELECT 
        COUNT(DISTINCT fo.order_number) AS total_orders,
        COALESCE(SUM(bd.totalAmount), 0) AS total_amount
    INTO p_total_orders, p_total_amount
    FROM falabella_orders fo
    JOIN falabella_order_items foi ON foi.order_id = fo.order_id
    LEFT JOIN falabella_orders_shipping_address fosa ON fosa.order_id = fo.order_id
    JOIN bsale_references br ON br.number = fo.order_number
    JOIN bsale_documents bd ON bd.id = br.document_id
    JOIN bsale_document_details bdd ON bdd.document_id = bd.id
    JOIN bsale_variants bv ON bv.id = bdd.variant_id
    WHERE 1=1
        AND (p_status IS NULL OR fo.status COLLATE utf8mb4_unicode_ci = p_status COLLATE utf8mb4_unicode_ci)
        AND (p_processed IS NULL OR fo.processed = p_processed)
        AND (p_printed IS NULL OR fo.printed = p_printed)
        AND (p_date_from IS NULL OR fo.created_at >= p_date_from)
        AND (p_date_to IS NULL OR fo.created_at <= p_date_to)
        AND (
            p_search IS NULL 
            OR fo.order_number COLLATE utf8mb4_unicode_ci LIKE CONCAT('%', p_search, '%') COLLATE utf8mb4_unicode_ci
            OR CONCAT(fo.customer_first_name, ' ', fo.customer_last_name) COLLATE utf8mb4_unicode_ci LIKE CONCAT('%', p_search, '%') COLLATE utf8mb4_unicode_ci
            OR foi.name COLLATE utf8mb4_unicode_ci LIKE CONCAT('%', p_search, '%') COLLATE utf8mb4_unicode_ci
        );
END //

DELIMITER ; 