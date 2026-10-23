
-- ## CUSTOMER ##
INSERT INTO customer (name, email, gender, birthdate, point, join_date) VALUES
('สุพัตร ทหารแท้', 'sukrstaa28@example.org', 'Male', '2005-9-15', 5000, '2026-6-20'),
('สุธาวี ปรีชากุลเศรษฐ์', 'nathphichaa77@example.org', 'Male', '2010-9-15', 500, '2026-10-9'),
('วาสุเทพ บุญส่ง', 'lnaakhwngs@example.net', 'Male', '2006-12-10', 0, '2026-8-15'),
('ธมลพรรณ ธรรมนิยม', 'nnthkaaycchn32@example.net', 'Female', '2013-3-7', 0, '2026-10-22'),
('ทินพร หอมพิกุล', 'gchamnaaywaad@example.com', 'Female', '2009-6-12', 0, '2026-12-9'),
('สมนึก บุญบำรุง', 'priyyaaaitrbrrph@example.net', 'Male', '2012-11-20', 0, '2025-2-24'),
('พรพิไล ทวีเดช', 'nuttaarniti@example.com', 'Female', '2011-8-20', 0, '2025-10-4'),
('พศร ถมปัด', 'niymsamhrwcchkhdieyaaa@example.com', 'Male', '2002-12-15', 5000, '2025-1-21'),
('กษิดิฐ นิยมธรรม', 'tanthnuchwrprachy@example.net', 'Male', '2004-9-27', 500, '2025-7-1');

-- ## ADDRESS ##
INSERT INTO address (address_type, cust_id, line_1, province, postal_code) VALUES
('home', 1, '8 ถนนนิละทัต ต.บ้านบัวบาน อ.แม่ลาว', 'สกลนคร', '93110'),
('work', 2, '135/4 ถ.เลิศกิ่ง เนินขามใหญ่', 'พระนครศรีอยุธยา', '14490'),
('home', 3, '4/3 ถนนทองแท้ ต.อุ่มเม่าใหญ่ อ.หนอกจอก', 'สุโขทัย', '98070'),
('work', 4, '1 ถ.นาคสุทิน ตำบลบางปะกอก อำเภอหนองบัวแดง', 'ยะลา', '81860'),
('work', 5, '01 หมู่ 4 ถนนนครเทพ ต.วัดบางเล่าใต้ อ.เทิง', 'สงขลา', '54300'),
('home', 6, '7 ถนนพานเกล้า เทพศิรินทร์ บ้านแท่น', 'มุกดาหาร', '95280'),
('home', 7, '46/5 ถ.นครเทพ ต.คลองเขื่อน', 'อ.นาหว้า', '32060'),
('work', 8, '8/5 ถนนตราชู อ.เขาสมิง', 'ตาก', '45080'),
('work', 9, '0 ถนนขันธุลา', 'อุทัยธานี', '28380');

-- ## CATEGORY ##
INSERT INTO category (category_id, name) VALUES
(1, 'Books'),
(2, 'Movies'),
(3, 'Music'),
(4, 'Games'),
(5, 'Electronics'),
(6, 'Computers'),
(7, 'Home'),
(8, 'Garden'),
(9, 'Tools'),
(10, 'Grocery'),
(11, 'Health'),
(12, 'Beauty'),
(13, 'Toys'),
(14, 'Kids'),
(15, 'Baby'),
(16, 'Clothing'),
(17, 'Shoes'),
(18, 'Jewelery'),
(19, 'Sports'),
(20, 'Outdoors'),
(21, 'Automotive'),
(22, 'Industrial'),
(23, 'Steel'),
(24, 'Wooden'),
(25, 'Concrete'),
(26, 'Plastic'),
(27, 'Cotton'),
(28, 'Granite'),
(29, 'Rubber'),
(30, 'Metal'),
(31, 'Soft'),
(32, 'Fresh'),
(33, 'Frozen'),
(34, 'Small'),
(35, 'Ergonomic'),
(36, 'Rustic'),
(37, 'Intelligent'),
(38, 'Gorgeous'),
(39, 'Incredible'),
(40, 'Fantastic'),
(41, 'Practical'),
(42, 'Sleek'),
(43, 'Awesome'),
(44, 'Generic'),
(45, 'Handcrafted'),
(46, 'Handmade'),
(47, 'Licensed'),
(48, 'Refined'),
(49, 'Unbranded'),
(50, 'Tasty'),
(51, 'New'),
(52, 'Gently Used'),
(53, 'Used'),
(54, 'For repair');

-- ## PRODUCT ##
INSERT INTO product (product_id, name, price, stock) VALUES
(1, 'The Great Gatsby Special Edition', 650.00, 150),
(2, 'Ergonomic Office Chair', 4500.00, 45),
(3, 'Wireless Noise-Canceling Headphones', 9900.00, 120),
(4, 'Handcrafted Wooden Dining Table', 29000.00, 5),
(5, 'Vintage Leather Jacket', 3900.00, 12),
(6, 'Smart LED TV 55-inch', 14900.00, 30),
(7, 'Organic Green Apples', 150.00, 500),
(8, 'Pepperoni Pizza', 199.00, 200),
(9, 'Heavy-Duty Hammer', 490.00, 85),
(10, 'Non-Slip Yoga Mat', 750.00, 110),
(11, 'Broken Gaming Laptop', 1500.00, 2),
(12, 'Mortar and Pestle', 1050.00, 40),
(13, 'Batman Action Figure', 790.00, 300),
(14, 'Basic V-Neck Blank Tee', 299.00, 450),
(15, 'Diamond Pendant Necklace', 6500.00, 8),
(16, 'Large Planter Box', 1350.00, 25),
(17, 'Compact Stroller', 2500.00, 15),
(18, 'Power Drill Set', 4200.00, 60),
(19, 'Sci-Fi Anthology Collection', 390.00, 75),
(20, 'Plush Teddy Bear', 550.00, 250);

-- ## CATEGORY ##
INSERT INTO product_category (product_id, category_id) VALUES
-- 1: Books, New, Fantastic
(1, 1), (1, 51), (1, 40),
-- 2: Home, Ergonomic, New
(2, 7), (2, 35), (2, 51),
-- 3: Electronics, Awesome, New
(3, 5), (3, 43), (3, 51),
-- 4: Home, Wooden, Handcrafted, Rustic
(4, 7), (4, 24), (4, 45), (4, 36),
-- 5: Clothing, Gently Used, Awesome
(5, 16), (5, 52), (5, 43),
-- 6: Electronics, Intelligent, Sleek, New
(6, 5), (6, 37), (6, 42), (6, 51),
-- 7: Grocery, Fresh, Tasty
(7, 10), (7, 32), (7, 50),
-- 8: Grocery, Frozen, Tasty
(8, 10), (8, 33), (8, 50),
-- 9: Tools, Steel, Practical, New
(9, 9), (9, 23), (9, 41), (9, 51),
-- 10: Sports, Rubber, Soft, New
(10, 19), (10, 29), (10, 31), (10, 51),
-- 11: Computers, For repair, Electronics
(11, 6), (11, 54), (11, 5),
-- 12: Home, Granite, Small, Practical
(12, 7), (12, 28), (12, 34), (12, 41),
-- 13: Toys, Kids, Licensed, Plastic
(13, 13), (13, 14), (13, 47), (13, 26),
-- 14: Clothing, Cotton, Unbranded, Generic
(14, 16), (14, 27), (14, 49), (14, 44),
-- 15: Jewelery, Refined, Gorgeous, New
(15, 18), (15, 48), (15, 38), (15, 51),
-- 16: Garden, Concrete, Outdoors, Handmade
(16, 8), (16, 25), (16, 20), (16, 46),
-- 17: Baby, Practical, Sleek, Gently Used
(17, 15), (17, 41), (17, 42), (17, 52),
-- 18: Tools, Industrial, Metal, New
(18, 9), (18, 22), (18, 30), (18, 51),
-- 19: Movies, Incredible, Used
(19, 2), (19, 39), (19, 53),
-- 20: Toys, Kids, Soft, Baby
(20, 13), (20, 14), (20, 31), (20, 15);


-- ## SHOP ORDER ##
INSERT INTO shop_order (order_id, cust_id, order_date, status, address_id, sub_total, discount) VALUES
(1, 1, '2025-09-03', 'complete', 1, 5150.00, 0.00),
(2, 2, '2025-09-05', 'shipped',  2, 499.00, 0.00),
(3, 3, '2025-09-10', 'pending',  3, 9900.00, 500.00),
(4, 4, '2025-09-12', 'complete', 4, 4690.00, 190.00),
(5, 5, '2025-09-15', 'cancel',   5, 6500.00, 0.00);

-- ## ORDER LINE ##
INSERT INTO order_line (order_id, product_id, qty, unit_price) VALUES
(1, 1, 1, 650.00),
(1, 2, 1, 4500.00),
(2, 7, 2, 150.00),
(2, 8, 1, 199.00),
(3, 3, 1, 9900.00),
(4, 9, 1, 490.00),
(4, 18, 1, 4200.00),
(5, 15, 1, 6500.00);
-- ## REVIEW ##
-- Note: The (order_id, product_id) combination MUST exist in order_line because of the fk_review_order_line constraint.
INSERT INTO review (order_id, product_id, rating, comment, review_date) VALUES
(1, 1, 5, 'Great book, arrived in perfect condition.', '2025-09-07'),
(1, 2, 4, 'Very comfortable chair, but assembly took a while.', '2025-09-08'),
(4, 18, 5, 'Powerful drill, gets the job done easily.', '2025-09-16');

-- ## PAYMENT ##
-- Note: The amount should logically equal (sub_total - discount) from the shop_order table.
INSERT INTO payment (order_id, method, amount, paid_date) VALUES
(1, 'credit card', 5150.00, '2025-09-03'),
(2, 'online banking', 499.00, '2025-09-05'),
(3, 'credit card', 9400.00, '2025-09-10'),
(4, 'online banking', 4500.00, '2025-09-12'),
(5, 'credit card', 6500.00, '2025-09-15');

-- ## UPDATE ORDER LINE unit_price ##
UPDATE order_line
SET unit_price = (SELECT p.price FROM product p WHERE p.product_id = order_line.product_id);

-- ## UPDATE SHOP ORDER sub_total ##
UPDATE shop_order
SET sub_total = COALESCE((SELECT SUM(ol.qty * ol.unit_price)
FROM order_line ol
WHERE ol.order_id = shop_order.order_id), 0);

-- ## UPDATE SHOP ORDER discount ##
UPDATE shop_order
JOIN    vw_customer_tier ON vw_customer_tier.cust_id = shop_order.cust_id
SET		discount = IFNULL(sub_total * (
        CASE 
            WHEN vw_customer_tier.tier = 'vip' THEN 0.15
            WHEN vw_customer_tier.tier = 'gold' AND sub_total >= 500 THEN 0.10
            WHEN vw_customer_tier.tier = 'silver' AND sub_total >= 500 THEN 0.05
            WHEN vw_customer_tier.tier = 'normal' THEN 0
        END), 0);

-- ## UPDATE PAYMENT amount ##
UPDATE payment
JOIN shop_order ON shop_order.order_id = payment.order_id
SET amount = shop_order.sub_total - shop_order.discount,
 paid_date = shop_order.order_date;

-- ## UPDATE REVIEW review_date ##
UPDATE review
JOIN shop_order ON shop_order.order_id = review.order_id
SET review.review_date = shop_order.order_date;

