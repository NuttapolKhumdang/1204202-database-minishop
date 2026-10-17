CREATE OR REPLACE VIEW vw_customer_tier AS
SELECT  cust_id
    ,   point
    ,   CASE WHEN point > 5000    THEN 'vip'
             WHEN point > 1000    THEN 'gold'
             WHEN point > 500     THEN 'silver'
             ELSE 'normal'
        END AS tier
FROM    customer c
;