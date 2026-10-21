CREATE OR REPLACE VIEW vw_customer_tier AS
SELECT  cust_id
    ,   CASE WHEN point >= 5000    THEN 'vip'
             WHEN point >= 1000    THEN 'gold'
             WHEN point >= 500     THEN 'silver'
             ELSE 'normal'
        END AS tier
FROM    customer c
;

CREATE OR REPLACE VIEW vw_product_categories AS
SELECT  pc.product_id 
    ,   GROUP_CONCAT(c.name SEPARATOR ', ') as categories
FROM    product_category pc 
JOIN    category c on c.category_id = pc.category_id
GROUP BY product_id
;