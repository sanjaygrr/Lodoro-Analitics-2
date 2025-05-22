DELIMITER //

DROP PROCEDURE IF EXISTS get_paris_orders //

CREATE PROCEDURE get_paris_orders(
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
        po.subOrderNumber,
        pi.sku AS paris_sku,
        pi.name AS producto_nombre,
        bdd.variant_code AS bsale_sku,
        bv.barCode AS ean,
        bd.number AS numero_boleta,
        bd.urlPdf AS url_boleta,
        bd.netAmount AS costo_neto,
        bd.taxAmount AS iva,
        bd.totalAmount AS costo_total,
        pi.shippingCost AS costo_despacho,
        po.customer_name AS nombre_cliente,
        po.customer_documentNumber AS rut_cliente,
        CONCAT_WS(', ', po.billing_address1, po.billing_address2, po.billing_address3, po.billing_city) AS direccion_envio,
        po.billing_phone AS telefono,
        po.originOrderDate AS fecha_creacion,
        po.createdAt AS fecha_registro,
        po.orden_impresa,
        po.orden_procesada,
        po.orden_despachada,
        po.boleta_impresa,
        ps.carrier AS transportista,
        ps.trackingNumber AS numero_seguimiento,
        ps.labelUrl AS label_url,
        pst.translate AS estado_despacho
    FROM paris_orders po
    LEFT JOIN paris_items pi ON pi.subOrderNumber = po.subOrderNumber
    LEFT JOIN paris_subOrders ps ON ps.subOrderNumber = po.subOrderNumber
    LEFT JOIN paris_statuses pst ON pst.id = ps.statusId
    LEFT JOIN bsale_references br ON br.number = po.subOrderNumber
    LEFT JOIN bsale_documents bd ON bd.id = br.document_id
    LEFT JOIN bsale_document_details bdd ON bdd.document_id = bd.id
    LEFT JOIN bsale_variants bv ON bv.id = bdd.variant_id
    WHERE 1=1
        AND (p_status IS NULL OR pst.translate = p_status)
        AND (p_processed IS NULL OR po.orden_procesada = p_processed)
        AND (p_printed IS NULL OR po.orden_impresa = p_printed)
        AND (p_date_from IS NULL OR po.originOrderDate >= p_date_from)
        AND (p_date_to IS NULL OR po.originOrderDate <= p_date_to)
        AND (p_search IS NULL OR 
            po.subOrderNumber LIKE CONCAT('%', p_search, '%') OR
            po.customer_name LIKE CONCAT('%', p_search, '%') OR
            pi.name LIKE CONCAT('%', p_search, '%')
        )
    ORDER BY po.originOrderDate DESC
    LIMIT p_limit
    OFFSET p_offset;

    -- Obtener total de órdenes y monto total
    SELECT 
        COUNT(DISTINCT po.subOrderNumber),
        COALESCE(SUM(bd.totalAmount), 0)
    INTO p_total_orders, p_total_amount
    FROM paris_orders po
    LEFT JOIN paris_items pi ON pi.subOrderNumber = po.subOrderNumber
    LEFT JOIN paris_subOrders ps ON ps.subOrderNumber = po.subOrderNumber
    LEFT JOIN paris_statuses pst ON pst.id = ps.statusId
    LEFT JOIN bsale_references br ON br.number = po.subOrderNumber
    LEFT JOIN bsale_documents bd ON bd.id = br.document_id
    WHERE 1=1
        AND (p_status IS NULL OR pst.translate = p_status)
        AND (p_processed IS NULL OR po.orden_procesada = p_processed)
        AND (p_printed IS NULL OR po.orden_impresa = p_printed)
        AND (p_date_from IS NULL OR po.originOrderDate >= p_date_from)
        AND (p_date_to IS NULL OR po.originOrderDate <= p_date_to)
        AND (p_search IS NULL OR 
            po.subOrderNumber LIKE CONCAT('%', p_search, '%') OR
            po.customer_name LIKE CONCAT('%', p_search, '%') OR
            pi.name LIKE CONCAT('%', p_search, '%')
        );
END //

DELIMITER ; 