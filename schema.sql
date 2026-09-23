-- ============================================================
--  schema.sql — ร้านค้าออนไลน์ (นิสิตออกแบบและเขียนเอง)
--  กติกา: 1 ออเดอร์มีหลายสินค้า (M:N: order × product ผ่าน order_line),
--         รีวิว = M:N (customer × product), การชำระเงิน 1:M จาก shop_order
-- ============================================================

DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS order_line;
DROP TABLE IF EXISTS shop_order
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS customer;


CREATE TABLE customer (
    -- TODO: name, email, address, tier

    cust_id         INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL,
    address         VARCHAR(100) NOT NULL,
    tier            VARCHAR(6) NOT NULL DEFAULT 'normal',

    CONSTRAINT chk_cust_tier CHECK (tier IN ('normal', 'silver', 'gold', 'vip'))
);

CREATE TABLE product (
    -- TODO: name, category, price, stock

    product_id      INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    category        VARCHAR(100),
    price           DECIMAL(7, 2) NOT NULL DEFAULT 0,
    stock           INT DEFAULT 0,

    CONSTRAINT chk_product_price CHECK (price >= 0),
    CONSTRAINT chk_product_stock CHECK (stock >= 0)
);

CREATE TABLE shop_order (
    -- TODO: cust_id (FK), order_date, status

    order_id        INT AUTO_INCREMENT PRIMARY KEY,
    cust_id         INT NOT NULL,
    order_date      DATE NOT NULL DEFAULT (CURRENT_DATE),
    status          VARCHAR(7) DEFAULT 'pending',

    CONSTRAINT chk_order_status CHECK (status IN ('pending', 'shipped', 'cancel')),
    CONSTRAINT fk_order_cust FOREIGN KEY (cust_id) REFERENCES customer (cust_id)
);


CREATE TABLE order_line (         -- M:N: shop_order × product
    -- TODO: order_id (FK), product_id (FK), qty, unit_price ; PRIMARY KEY (order_id, product_id)
    
    order_id        INT,
    product_id      INT,
    qty             INT,
    unit_price      DECIMAL(7, 2),

    CONSTRAINT chk_order_line_qty       CHECK (qty > 0),
    CONSTRAINT chk_order_line_price     CHECK (unit_price > 0),
    CONSTRAINT pk_order_line            PRIMARY KEY (order_id, product_id),
    CONSTRAINT fk_order_line_order      FOREIGN KEY (order_id) REFERENCES shop_order (order_id),
    CONSTRAINT fk_order_line_product    FOREIGN KEY (product_id) REFERENCES product (product_id) 
);

CREATE TABLE review (             -- M:N: customer × product
    -- TODO: cust_id (FK), product_id (FK), rating, comment, review_date ; PRIMARY KEY (cust_id, product_id)
    cust_id         INT, 
    product_id      INT,
    rating          INT,
    comment         VARCHAR(100),
    review_date     DATE DEFAULT (CURRENT_DATE),

    CONSTRAINT chk_review_rating    CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT pk_review            PRIMARY KEY (cust_id, product_id),
    CONSTRAINT fk_review_cust       FOREIGN KEY (cust_id) REFERENCES customer (cust_id),
    CONSTRAINT fk_review_product    FOREIGN KEY (product_id) REFERENCES product (product_id)
);

CREATE TABLE payment (            -- 1:M จาก shop_order
    -- TODO: order_id (FK), method, amount, paid_date

    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    order_id        INT,
    method          VARCHAR(12),
    amount          DECIMAL(7, 2),
    paid_date       DATE DEFAULT (CURRENT_DATE),

    CONSTRAINT chk_payment_method   CHECK (method IN ('cash', 'credit card', 'online')),
    CONSTRAINT fk_payment_order     FOREIGN KEY (order_id) REFERENCES shop_order (order_id)
);

-- TODO: INSERT ข้อมูลตัวอย่างทุกตาราง

INSERT INTO customer (name, email, address, tier)
VALUES
('Johnny Morgan', 'travishunter@example.org', '3271 Morton Turnpike Apt. 382 South Josephstad, UT 81457', 'silver'),
('Deborah Baird', 'mercedes22@example.net', 'PSC 2011, Box 6331 APO AE 63868', 'gold'),
('Linda Rodriguez', 'karenstephens@example.net', '9639 Ryan Fall Maryberg, WA 01743', 'silver'),
('Catherine Ford', 'erinkelley@example.net', '445 English Divide Duffyview, WV 06489', 'normal'),
('Kevin Morris', 'omoore@example.org', '4361 Morris Burg Suite 499 New Paultown, OK 79793', 'gold'),
('Kenneth Porter', 'jpope@example.net', '5886 Jerry Summit Lake George, SD 62232', 'gold'),
('Kenneth Benson', 'andrewsfelicia@example.net', '250 Ryan Skyway Suite 567 New Joeview, CO 09421', 'vip'),
('James Grant', 'phunter@example.org', '725 Villanueva Walks Port Teresaborough, PR 66091', 'vip'),
('Lori Shaw', 'whitekayla@example.net', '16398 Jacob Point Apt. 970 Diazburgh, MO 28675', 'normal'),
('Nathan King', 'lindseypeterson@example.org', '06090 Martin Row Apt. 873 Lake Christopher, OR 37920', 'gold'),
('Laura Gutierrez', 'nandrews@example.com', '97942 Ferguson Turnpike Colemanborough, VT 08678', 'silver'),
('Donna Davis', 'zvang@example.com', '01700 Cook Plaza Suite 958 North Arthur, OK 03979', 'gold'),
('Tracy Jackson', 'ocochran@example.net', '849 Green Mountain Apt. 751 Millerchester, KY 58581', 'vip'),
('Caroline Thomas', 'matthew71@example.org', 'USNS Nelson FPO AP 14487', 'vip'),
('Billy Velasquez', 'michaelnelson@example.net', '19409 Nicholas Pass Apt. 394 Nguyenside, AR 04934', 'gold'),
('Richard Benson', 'rebeccaperez@example.org', '77697 Espinoza Street Charlesburgh, KS 57206', 'gold'),
('Jessica Oconnell', 'qlee@example.com', '05815 Tucker Place Suite 038 Brooketown, WY 85185', 'silver'),
('Paul Payne', 'zwilliams@example.org', '8287 Terri Stream Lake Randyton, SC 17250', 'normal'),
('Christina Watson', 'qortiz@example.org', '9205 Melanie Street Floresmouth, KS 55561', 'gold'),
('Juan Hayes', 'joshua34@example.net', '808 Sherry Ford Apt. 018 Jeromeside, RI 48406', 'vip'),
('Richard Mcguire', 'christopherwilson@example.net', '14888 Chad Courts Katherineport, MS 88909', 'silver'),
('John Harmon', 'guycosta@example.net', '29822 David Prairie North Sarahstad, AR 10796', 'normal'),
('James Blackwell', 'lpatterson@example.net', '883 Porter Inlet Travisside, NE 85851', 'silver'),
('Mario Martinez', 'gabrielamiller@example.org', '1181 Hill Knolls Port Bryan, AS 47630', 'normal'),
('Tiffany Kirk', 'qgray@example.com', '184 Williams Crest Apt. 589 Port Allisonville, FM 20988', 'gold'),
('Louis Stewart', 'jeffreyrogers@example.org', '723 Campbell Throughway Apt. 359 West Kathleenmouth, ND 81594', 'normal'),
('Maria Mejia', 'jesus79@example.org', '37131 Bethany Mountains Shelbystad, AL 56279', 'normal'),
('Stephen Sanchez', 'oallen@example.org', '13118 Laurie Garden Apt. 842 New Williamshire, VT 79853', 'normal'),
('Victoria Johnson', 'hhardy@example.net', '7954 Mullen Haven Lake David, GU 77859', 'normal'),
('Cheryl Sims', 'ronald64@example.org', '23552 Guerra Grove Tranview, WA 04909', 'vip'),
('Amy Peterson', 'rodriguezjoanne@example.net', 'PSC 4611, Box 5694 APO AA 58730', 'vip'),
('Ashley Johnson', 'christopherramsey@example.net', '061 Cunningham Neck Sarastad, WV 45304', 'normal'),
('Jon Thomas', 'ortegafrancisco@example.com', '9209 Campos Locks South Jennifer, NV 92121', 'normal'),
('Timothy Haynes', 'shawn26@example.net', '4200 Samantha Ways Port Kevin, NY 74075', 'gold'),
('Anthony Benton', 'rebecca85@example.org', '80424 Jones Junctions Lake James, LA 27981', 'vip'),
('Christopher Durham', 'dlarson@example.com', '556 Heather Ramp Suite 834 Hardingshire, HI 49847', 'gold'),
('Miranda Blair', 'bedwards@example.com', '1709 Michael Shore Apt. 499 Jessicafort, OR 64179', 'silver'),
('Justin Sanchez', 'gonzalezmark@example.net', '86457 Kimberly Plains Suite 259 Wheelerfurt, MS 55583', 'vip'),
('Jacqueline Rice', 'thomas20@example.net', '2455 Shannon Parkway Suite 599 Mariahbury, NE 08564', 'gold'),
('Mrs. Amy Gonzalez DDS', 'hfischer@example.com', '9646 Cochran Radial Suite 291 Bishopshire, GU 33499', 'silver');



INSERT INTO product(name, category, price, stock)
VALUES
('Fish', 'Outdoors', 1.58, 244),
('Gently Used Car', 'Electronics', 105.13, 46),
('Bacon', 'Health', 3.23, 213),
('Pants', 'Books', 193.31, 117),
('Handcrafted Granite Cheese', 'Baby', 52.63, 155),
('For repair Cotton Chair', 'Computers', 506.88, 181),
('Handcrafted Rubber Chair', 'Movies', 16.08, 53),
('Frozen Chips', 'Kids', 83.17, 141),
('Soft Fish', 'Home', 122.91, 70),
('Generic Ball', 'Garden', 447.05, 92),
('Keyboard', 'Shoes', 74.89, 80),
('Frozen Car', 'Games', 243.08, 134),
('Unbranded Plastic Gloves', 'Automotive', 216.14, 5),
('Frozen Bacon', 'Industrial', 131.14, 63),
('Fantastic Shirt', 'Outdoors', 318.88, 135),
('Concrete Car', 'Health', 772.61, 15),
('Pants', 'Automotive', 61.99, 241),
('Pizza', 'Beauty', 63.25, 92),
('Licensed Cotton Keyboard', 'Kids', 584.77, 178),
('Practical Metal Pants', 'Industrial', 65.3, 74),
('Gently Used Concrete Chair', 'Sports', 847.57, 33),
('Sleek Wooden Gloves', 'Tools', 177.56, 161),
('Soft Chicken', 'Tools', 327.62, 107),
('Handcrafted Cheese', 'Outdoors', 59.34, 125),
('Wooden Chair', 'Home', 124.14, 47),
('Pants', 'Toys', 493.08, 251),
('Unbranded Wooden Chips', 'Beauty', 267.27, 93),
('Rubber Chicken', 'Kids', 104.35, 103),
('Computer', 'Industrial', 838.9, 233),
('Ergonomic Granite Tuna', 'Electronics', 310.67, 228),
('Intelligent Frozen Chicken', 'Outdoors', 103.88, 19),
('Tuna', 'Clothing', 587.64, 91),
('Chicken', 'Kids', 438.69, 36),
('Shoes', 'Sports', 486.07, 232),
('Gorgeous Metal Sausages', 'Grocery', 557.65, 63),
('Ergonomic Computer', 'Baby', 692.79, 142),
('Fantastic Concrete Fish', 'Outdoors', 176.42, 79),
('Fish', 'Grocery', 33.85, 156),
('Soft Car', 'Movies', 542.33, 138),
('Used Steel Soap', 'Baby', 298.76, 58),
('Metal Hat', 'Electronics', 144.94, 76),
('Handcrafted Concrete Chair', 'Electronics', 424.56, 93),
('Metal Bacon', 'Sports', 392.23, 171),
('For repair Frozen Gloves', 'Games', 781.22, 146),
('Hat', 'Baby', 89.56, 163),
('Frozen Fish', 'Games', 94.17, 208),
('Wooden Chair', 'Home', 334.07, 249),
('Chicken', 'Beauty', 126.38, 43),
('Cheese', 'Kids', 454.9, 52),
('Practical Concrete Table', 'Outdoors', 86.05, 62),
('Sleek Chair', 'Clothing', 88.14, 85),
('Sleek Salad', 'Movies', 38.23, 106),
('Gorgeous Soap', 'Kids', 145.98, 91),
('Cotton Table', 'Games', 648.11, 228),
('Computer', 'Outdoors', 784.53, 173),
('For repair Rubber Shoes', 'Automotive', 136.57, 88),
('Bike', 'Music', 36.61, 129),
('Cheese', 'Games', 308.7, 132),
('Steel Shoes', 'Clothing', 9.47, 244),
('Ball', 'Books', 432.86, 203);


INSERT INTO shop_order (cust_id, order_date, status)
VALUES
(13, '2021-04-13', 'shipped'),
(18, '2024-12-23', 'pending'),	(6, '2024-09-21', 'pending'),	(9, '2021-04-02', 'shipped'),
(6, '2024-07-23', 'cancel'),	(2, '2020-12-19', 'pending'),	(13, '2024-03-05', 'cancel'),
(1, '2021-05-26', 'cancel'),	(4, '2021-05-17', 'pending'),	(15, '2024-12-25', 'cancel'),
(2, '2025-01-12', 'cancel'),	(10, '2022-12-16', 'shipped'),	(7, '2022-04-30', 'cancel'),
(18, '2020-06-25', 'pending'),	(7, '2025-02-07', 'shipped'),	(9, '2025-02-15', 'pending'),
(17, '2024-03-13', 'cancel'),	(18, '2021-10-28', 'shipped'),	(10, '2020-01-26', 'shipped'),
(15, '2025-02-20', 'pending'),	(13, '2023-11-28', 'pending'),	(17, '2020-07-02', 'pending'),
(15, '2024-07-26', 'shipped'),	(1, '2022-04-22', 'cancel'),	(19, '2020-10-04', 'shipped'),
(13, '2020-01-23', 'shipped'),	(10, '2023-09-09', 'shipped'),	(3, '2023-06-13', 'cancel'),
(13, '2020-06-26', 'pending'),	(19, '2020-03-06', 'cancel'),	(19, '2023-04-10', 'shipped'),
(14, '2022-06-17', 'pending'),	(8, '2025-12-31', 'shipped'),	(2, '2021-09-06', 'shipped'),
(13, '2022-09-26', 'pending'),	(16, '2021-04-02', 'shipped'),	(4, '2025-12-02', 'pending'),
(10, '2021-02-11', 'cancel'),	(15, '2023-03-01', 'cancel'),	(3, '2020-03-18', 'shipped');


INSERT INTO order_line(order_id, product_id, qty, unit_price)
VALUES
(1, 16, 9, 1),
(1, 53, 5, 1),		(1, 30, 1, 1),		(2, 8, 5, 1),		(2, 48, 5, 1),		(3, 36, 9, 1),
(3, 28, 7, 1),		(3, 23, 1, 1),		(3, 45, 5, 1),		(3, 57, 9, 1),		(3, 42, 1, 1),
(4, 6, 3, 1),		(4, 1, 8, 1),		(5, 46, 5, 1),		(5, 35, 8, 1),		(5, 51, 9, 1),
(5, 47, 7, 1),		(5, 56, 5, 1),		(5, 18, 3, 1),		(5, 37, 6, 1),		(5, 2, 6, 1),
(5, 55, 6, 1),		(6, 23, 5, 1),		(6, 17, 4, 1),		(6, 12, 9, 1),		(6, 49, 7, 1),
(6, 1, 4, 1),		(6, 3, 1, 1),		(7, 55, 4, 1),		(7, 34, 9, 1),		(7, 38, 4, 1),
(7, 31, 8, 1),		(7, 58, 4, 1),		(7, 22, 8, 1),		(7, 47, 4, 1),		(7, 12, 4, 1),
(8, 53, 5, 1),		(8, 54, 9, 1),		(8, 25, 8, 1),		(8, 42, 5, 1),		(8, 1, 1, 1),
(8, 13, 2, 1),		(9, 27, 7, 1),		(9, 46, 9, 1),		(9, 40, 6, 1),		(9, 2, 2, 1),
(9, 50, 1, 1),		(10, 22, 7, 1),		(10, 26, 9, 1),		(10, 59, 9, 1),		(10, 40, 7, 1),
(10, 42, 2, 1),		(10, 20, 3, 1),		(11, 52, 7, 1),		(11, 24, 7, 1),		(11, 39, 3, 1),
(12, 31, 1, 1),		(12, 13, 6, 1),		(12, 30, 4, 1),		(13, 33, 6, 1),		(13, 53, 5, 1),
(13, 3, 1, 1),		(13, 31, 8, 1),		(14, 18, 6, 1),		(14, 44, 4, 1),		(14, 1, 9, 1),
(14, 22, 4, 1),		(14, 35, 4, 1),		(14, 29, 9, 1),		(14, 41, 4, 1),		(14, 4, 1, 1),
(15, 47, 6, 1),		(15, 35, 4, 1),		(15, 32, 2, 1),		(16, 1, 8, 1),		(16, 52, 3, 1),
(16, 44, 5, 1),		(16, 18, 9, 1),		(16, 13, 6, 1),		(16, 33, 8, 1),		(16, 20, 2, 1),
(17, 59, 3, 1),		(17, 48, 1, 1),		(18, 47, 6, 1),		(18, 2, 3, 1),		(18, 13, 9, 1),
(18, 20, 5, 1),		(18, 33, 8, 1),		(19, 56, 5, 1),		(19, 48, 3, 1),		(19, 1, 2, 1),
(19, 6, 6, 1),		(19, 18, 6, 1),		(20, 34, 9, 1),		(20, 11, 2, 1),		(20, 22, 5, 1),
(20, 24, 1, 1),		(21, 19, 5, 1),		(21, 6, 2, 1),		(21, 57, 7, 1),		(21, 37, 2, 1),
(21, 43, 5, 1),		(21, 49, 4, 1),		(21, 53, 5, 1),		(21, 24, 3, 1),		(22, 48, 8, 1),
(22, 29, 9, 1),		(22, 18, 5, 1),		(22, 23, 9, 1),		(23, 30, 6, 1),		(23, 55, 1, 1),
(23, 1, 1, 1),		(23, 53, 1, 1),		(23, 51, 5, 1),		(23, 16, 8, 1),		(24, 52, 7, 1),
(24, 51, 9, 1),		(24, 40, 8, 1),		(25, 39, 4, 1),		(25, 9, 8, 1),		(25, 47, 1, 1),
(25, 34, 4, 1),		(25, 54, 4, 1),		(25, 10, 8, 1),		(26, 50, 4, 1),		(26, 11, 8, 1),
(26, 4, 1, 1),		(26, 30, 6, 1),		(26, 24, 6, 1),		(26, 28, 4, 1),		(26, 5, 4, 1),
(26, 25, 9, 1),		(27, 42, 9, 1),		(27, 58, 8, 1),		(27, 12, 5, 1),		(27, 49, 1, 1),
(27, 44, 1, 1),		(28, 13, 1, 1),		(28, 43, 4, 1),		(29, 32, 2, 1),		(29, 33, 1, 1),
(30, 24, 4, 1),		(30, 3, 1, 1),		(30, 45, 2, 1),		(30, 19, 6, 1),		(30, 52, 4, 1),
(30, 44, 9, 1),		(31, 17, 8, 1),		(31, 24, 7, 1),		(31, 55, 9, 1),		(31, 49, 3, 1),
(31, 33, 5, 1),		(31, 56, 8, 1),		(31, 48, 1, 1),		(31, 28, 4, 1),		(31, 7, 8, 1),
(32, 20, 6, 1),		(32, 40, 6, 1),		(32, 49, 5, 1),		(32, 8, 8, 1),		(32, 5, 9, 1),
(33, 10, 1, 1),		(33, 26, 8, 1),		(34, 44, 3, 1),		(34, 17, 9, 1),		(34, 15, 8, 1),
(34, 28, 7, 1),		(34, 50, 2, 1),		(34, 7, 4, 1),		(34, 56, 9, 1),		(35, 15, 6, 1),
(35, 58, 9, 1),		(35, 18, 3, 1),		(35, 2, 7, 1),		(35, 25, 1, 1),		(35, 46, 3, 1),
(35, 17, 9, 1),		(36, 5, 8, 1),		(36, 36, 9, 1),		(36, 59, 6, 1),		(36, 28, 3, 1),
(36, 41, 2, 1),		(36, 57, 3, 1),		(36, 49, 3, 1),		(36, 21, 9, 1),		(37, 47, 7, 1),
(37, 2, 1, 1),		(37, 19, 2, 1),		(37, 49, 5, 1),		(37, 15, 7, 1),		(38, 13, 4, 1),
(38, 23, 7, 1),		(38, 2, 8, 1),		(38, 44, 8, 1),		(38, 32, 7, 1),		(38, 8, 1, 1),
(39, 27, 1, 1),		(39, 26, 1, 1),		(39, 11, 8, 1),		(39, 2, 3, 1),		(39, 35, 5, 1),
(39, 28, 1, 1),		(39, 33, 9, 1);

-- Update order_line unit_price

UPDATE  order_line
JOIN    product p ON p.product_id = order_line.product_id
SET     unit_price = p.price;