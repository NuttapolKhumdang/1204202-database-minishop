CREATE OR REPLACE VIEW vw_customer_detail AS
SELECT  cust_id
    ,   name
    ,   email
    ,   birthdate
    ,   gender
    ,   point
    ,   CASE WHEN point > 1000    THEN 'vip'
             WHEN point > 500     THEN 'gold'
             WHEN point > 250     THEN 'silver'
             ELSE 'normal'
        END AS tier
FROM    customer c
;