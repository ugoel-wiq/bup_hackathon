WITH base as (
SELECT *
FROM `gcp-wow-rwds-ai-search-dev.99_temp.facets_products_hackathon`
), 

details AS 
(
  SELECT articlenumber, 
        MAX(IF(name = 'name', COALESCE(attributevalueoverride, attributevalue), NULL)) AS name, 
        MAX(IF(name = 'ProductName', COALESCE(attributevalueoverride, attributevalue), NULL)) AS product_name, 
        MAX(IF(name = 'Online Product Name', COALESCE(attributevalueoverride, attributevalue), NULL)) AS online_product_name, 
        MAX(IF(name = 'PlainTextDescription', COALESCE(attributevalueoverride, attributevalue), NULL)) AS text_description, 
        MAX(IF(name = 'description', COALESCE(attributevalueoverride, attributevalue), NULL)) AS description, 
        MAX(IF(name = 'ShortDescription', COALESCE(attributevalueoverride, attributevalue), NULL)) AS short_description, 
        MAX(IF(name = 'Brand', attributevalue, NULL)) AS brand, 
        MAX(IF(name = 'Sub-Brand', attributevalue, NULL)) AS sub_brand, 
        --COALESCE(articlenumber IN (SELECT * FROM b2b_articles), FALSE) AS is_b2b 
    FROM `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_online_view_smkt.pies_smkt_attribute_value_v` AS a 
    INNER JOIN `gcp-wow-ent-im-wowx-cust-prod.adp_wowx_dm_online_view_smkt.pies_smkt_attribute_metadata_v` AS b 
    ON a.attributemetadataid = b.id 
    WHERE ((attributemetadataid IN (1088, 835, 1002, 1003, 735, 976, 427, 1087, 50, 897)) -- including B2B products 
        OR (attributemetadataid = 3753 AND upper(attributevalue) = upper('True'))) 
        AND salesorganisationid = 1005 AND a.isactive = true 
      GROUP BY 1
)

SELECT A.*, b.online_product_name, b.description, b.brand,
FROM BASE a
LEFT JOIN details b 
ON a.product_nbr = b.articlenumber
order by original_term, kw; 