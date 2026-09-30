-- ============================================================
--  schema.sql — ร้านค้าออนไลน์ (นิสิตออกแบบและเขียนเอง)
--  กติกา: 1 ออเดอร์มีหลายสินค้า (M:N: order × product ผ่าน order_line),
--         รีวิว = M:N (customer × product), การชำระเงิน 1:M จาก shop_order
-- ============================================================

DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS order_line;
DROP TABLE IF EXISTS product_category;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS shop_order;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS primary_category;
DROP TABLE IF EXISTS address;
DROP TABLE IF EXISTS customer;

CREATE TABLE customer (
    -- TODO: name, email, address, tier

    cust_id         INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL,
    tier            VARCHAR(6) NOT NULL DEFAULT 'normal',

    CONSTRAINT chk_cust_tier CHECK (tier IN ('normal', 'silver', 'gold', 'vip'))
);

CREATE TABLE address (
    address_id      INT AUTO_INCREMENT PRIMARY KEY,
    cust_id         INT,
    title           VARCHAR(36),
    address         VARCHAR(100) NOT NULL,
    postal_code     VARCHAR(6) NOT NULL,
    is_default      BOOLEAN DEFAULT TRUE,

    CONSTRAINT fk_address_custmer FOREIGN KEY (cust_id)
        REFERENCES customer (cust_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE primary_category (
    category_id     INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(50)
);

CREATE TABLE category (
    category_id     INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(50)
);

CREATE TABLE product (
    -- TODO: name, category, price, stock

    product_id      INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    category        INT,
    price           DECIMAL(7, 2) NOT NULL DEFAULT 0,
    stock           INT DEFAULT 0,
    is_active       BOOLEAN DEFAULT TRUE,

    CONSTRAINT chk_product_price CHECK (price >= 0),
    CONSTRAINT chk_product_stock CHECK (stock >= 0),
    CONSTRAINT fk_primary_category FOREIGN KEY (category)
        REFERENCES primary_category (category_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE product_category (
    product_id      INT,
    category_id     INT,

    CONSTRAINT fk_pcate_product FOREIGN KEY (product_id) 
        REFERENCES product (product_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
        
    CONSTRAINT fk_pcate_category FOREIGN KEY (category_id) 
        REFERENCES category (category_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE shop_order (
    -- TODO: cust_id (FK), order_date, status

    order_id        INT AUTO_INCREMENT PRIMARY KEY,
    cust_id         INT NOT NULL,
    order_date      DATE NOT NULL DEFAULT (CURRENT_DATE),
    status          VARCHAR(7) DEFAULT 'pending',

    address         INT,
    sub_total       DECIMAL(9, 2) NOT NULL,
    discount        DECIMAL(9, 2) NOT NULL,
    total           DECIMAL(9, 2) NOT NULL,

    CONSTRAINT chk_order_sub_total      CHECK (sub_total >= 0),
    CONSTRAINT chk_order_discount       CHECK (discount >= 0),
    CONSTRAINT chk_order_total          CHECK (total >= 0),
    CONSTRAINT chk_order_status         CHECK (status IN ('pending', 'shipped', 'complete', 'cancel')),
    CONSTRAINT fk_order_cust            FOREIGN KEY (cust_id) REFERENCES customer (cust_id),
    CONSTRAINT fk_order_address         FOREIGN KEY (address) REFERENCES address (address_id)
);

CREATE TABLE order_line (         -- M:N: shop_order × product
    -- TODO: order_id (FK), product_id (FK), qty, unit_price ; PRIMARY KEY (order_id, product_id)
    
    order_id        INT,
    product_id      INT,
    qty             INT,
    unit_price      DECIMAL(9, 2),

    CONSTRAINT chk_order_line_qty       CHECK (qty > 0),
    CONSTRAINT chk_order_line_price     CHECK (unit_price >= 0),
    CONSTRAINT pk_order_line            PRIMARY KEY (order_id, product_id),
    CONSTRAINT fk_order_line_order      FOREIGN KEY (order_id) REFERENCES shop_order (order_id),
    CONSTRAINT fk_order_line_product    FOREIGN KEY (product_id) REFERENCES product (product_id) 
);

CREATE TABLE review (             -- M:N: customer × product
    -- TODO: cust_id (FK), product_id (FK), rating, comment, review_date ; PRIMARY KEY (cust_id, product_id)
    cust_id         INT, 
    order_id        INT,
    rating          INT,
    comment         VARCHAR(100),
    review_date     DATE DEFAULT (CURRENT_DATE),

    CONSTRAINT chk_review_rating    CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT pk_review            PRIMARY KEY (cust_id, order_id),
    CONSTRAINT fk_review_cust       FOREIGN KEY (cust_id) REFERENCES customer (cust_id),
    CONSTRAINT fk_review_order      FOREIGN KEY (order_id) REFERENCES shop_order (order_id)
);

CREATE TABLE payment (            -- 1:M จาก shop_order
    -- TODO: order_id (FK), method, amount, paid_date

    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    order_id        INT,
    method          VARCHAR(12),
    amount          DECIMAL(9, 2),
    paid_date       DATE DEFAULT (CURRENT_DATE) NOT NULL,

    CONSTRAINT chk_payment_method   CHECK (method IN ('cash', 'credit card', 'online')),
    CONSTRAINT fk_payment_order     FOREIGN KEY (order_id) REFERENCES shop_order (order_id)
);
