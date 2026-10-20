from faker import Faker
import faker_commerce
from random import random, randrange, choice, choices, sample
from datetime import date
from typing import List, Dict

fake = Faker(['th_TH'])
fake.add_provider(faker_commerce.Provider)

MIN_CUSTOMER_ID = 1
MAX_CUSTOMER_ID = 40

MIN_PRODUCT_ID = 1
MAX_PRODUCT_ID = 20

MIN_ORDER_ID = 1
MAX_ORDER_ID = 10


CATEGORIES = [
    "Books",
    "Movies",
    "Music",
    "Games",
    "Electronics",
    "Computers",
    "Home",
    "Garden",
    "Tools",
    "Grocery",
    "Health",
    "Beauty",
    "Toys",
    "Kids",
    "Baby",
    "Clothing",
    "Shoes",
    "Jewelery",
    "Sports",
    "Outdoors",
    "Automotive",
    "Industrial",
    "Steel",
    "Wooden",
    "Concrete",
    "Plastic",
    "Cotton",
    "Granite",
    "Rubber",
    "Metal",
    "Soft",
    "Fresh",
    "Frozen",
    "Small",
    "Ergonomic",
    "Rustic",
    "Intelligent",
    "Gorgeous",
    "Incredible",
    "Fantastic",
    "Practical",
    "Sleek",
    "Awesome",
    "Generic",
    "Handcrafted",
    "Handmade",
    "Licensed",
    "Refined",
    "Unbranded",
    "Tasty",
    "New",
    "Gently Used",
    "Used",
    "For repair"
]
CUSTOMER_ORDERS = [(14, '2026-10-03', 'complete', 14, 0, 0, 0),
                   (37, '2026-10-01', 'pending', 37, 0, 0, 0),	(15, '2026-10-04',
                                                                'shipped', 15, 0, 0, 0),	(10, '2026-10-03', 'cancel', 10, 0, 0, 0),
                   (29, '2026-10-05', 'shipped', 29, 0, 0, 0),	(31, '2026-10-03',
                                                                'shipped', 31, 0, 0, 0),	(20, '2026-10-01', 'cancel', 20, 0, 0, 0),
                   (37, '2026-10-03', 'cancel', 37, 0, 0, 0),	(16, '2026-10-05',
                                                               'cancel', 16, 0, 0, 0),	(33, '2026-10-03', 'pending', 33, 0, 0, 0),
                   (12, '2026-10-05', 'shipped', 12, 0, 0, 0),	(35, '2026-10-01',
                                                                'pending', 35, 0, 0, 0),	(25, '2026-10-03', 'cancel', 25, 0, 0, 0),
                   (13, '2026-10-02', 'shipped', 13, 0, 0, 0),	(12, '2026-10-05',
                                                                'complete', 12, 0, 0, 0),	(29, '2026-10-02', 'complete', 29, 0, 0, 0),
                   (30, '2026-10-02', 'complete', 30, 0, 0, 0),	(8, '2026-10-04',
                                                                 'cancel', 8, 0, 0, 0),	(6, '2026-10-05', 'cancel', 6, 0, 0, 0),
                   (4, '2026-10-01', 'cancel', 4, 0, 0, 0),	(12, '2026-10-05',
                                                             'shipped', 12, 0, 0, 0),	(33, '2026-10-04', 'complete', 33, 0, 0, 0),
                   (18, '2026-10-04', 'shipped', 18, 0, 0, 0),	(12, '2026-10-02',
                                                                'shipped', 12, 0, 0, 0),	(6, '2026-10-02', 'pending', 6, 0, 0, 0),
                   (31, '2026-10-01', 'shipped', 31, 0, 0, 0),	(28, '2026-10-02',
                                                                'cancel', 28, 0, 0, 0),	(16, '2026-10-04', 'pending', 16, 0, 0, 0),
                   (11, '2026-10-01', 'complete', 11, 0, 0, 0),	(18, '2026-10-03',
                                                                 'cancel', 18, 0, 0, 0),	(35, '2026-10-01', 'pending', 35, 0, 0, 0),
                   (31, '2026-10-05', 'cancel', 31, 0, 0, 0),	(30, '2026-10-01',
                                                               'cancel', 30, 0, 0, 0),	(15, '2026-10-01', 'pending', 15, 0, 0, 0),
                   (24, '2026-10-05', 'complete', 24, 0, 0, 0),	(12, '2026-10-01',
                                                                 'complete', 12, 0, 0, 0),	(27, '2026-10-04', 'cancel', 27, 0, 0, 0),
                   (21, '2026-10-02', 'shipped', 21, 0, 0, 0),	(25, '2026-10-04',
                                                                'complete', 25, 0, 0, 0),	(22, '2026-10-04', 'shipped', 22, 0, 0, 0)
                   ]


def add(sql: str, s: str, end: bool | str = False) -> str:
    sql += s + \
        ("\n" if not end else ';\n' if isinstance(
            end, bool) and end == True else end)
    return sql


def customer() -> str:
    name = fake.name()
    email = fake.email()
    gender = choice(['Male', 'Female'])
    point = choices([0, 500, 1000, 5000], k=1, weights=[0.6, 0.2, 0.1, 0.1])[
        0]  # Normal, Silver , Gold, VIP
    birthdate = f"{randrange(2000, 2013 + 1)}-{randrange(1, 12 + 1)}-{randrange(1, 28 + 1)}"
    join_date = f"{randrange(2025, 2026 + 1)}-{randrange(1, 12 + 1)}-{randrange(1, 28 + 1)}"

    return f"('{name}', '{email}', '{gender}', '{birthdate}', {point}, '{join_date}')"


def address(cust_id: int) -> str:
    destination = fake.address()
    postal_code = destination.split(' ')[-1]
    province = destination.split(
        ' ')[-2].replace('จ.', '').replace('จังหวัด', '')
    line_1 = ' '.join(destination.split(' ')[:-2])

    try:
        int(postal_code)
    except:
        postal_code = None

    destination_type = choice(['home', 'work'])
    return f"('{destination_type}', {cust_id}, '{line_1}', '{province}', '{postal_code if postal_code else fake.postcode()}')"


def category() -> str:
    sql = ',\n'.join([f"({i + 1}, '{c}')" for i, c in enumerate(CATEGORIES)])
    return sql


def product() -> str:
    name = fake.ecommerce_name()
    price = randrange(29, 600)
    stock = randrange(10, 200)
    return f"('{name}', {price}, {stock})"


def product_category(pid: int) -> str:
    categories = [CATEGORIES[randrange(
        1, 19 + 1)], *(sample(CATEGORIES[20:], k=randrange(2, 6)))]
    return f", ".join([f"({pid}, {CATEGORIES.index(c)})" for c in categories])


def shop_order(cust_id: int, ) -> str:
    order_date = f"{randrange(2025, 2027)}-{randrange(1, 12)}-{randrange(1, 28 + 1)}"
    status = choices(['pending', 'shipped', 'complete',
                     'cancel'], k=1, weights=[0.6, 0.2, 0.1, 0.1])[0]
    destination = cust_id
    sub_total = 0
    discount = 0
    return f"({cust_id}, '{order_date}', '{status}', {destination}, {sub_total}, {discount})"


def order_line(order_id: int, ) -> str:
    #                   (  order_id,     product_id,                                   qty,              unit_price)
    return ', '.join([f"({order_id}, {pid}, {randrange(1, 5)}, 0)" for pid in sample(range(MIN_PRODUCT_ID, MAX_PRODUCT_ID), randrange(1, 10))])


def payment(order_id: int,) -> str:
    # order_id, method, amount, paid_date
    method = choice(['credit card', 'online banking'])
    paid_date = f"{randrange(2025, 2027)}-{randrange(1, 12)}-{randrange(1, 30)}"

    return f"( {order_id}, '{method}', 0, '{paid_date}')"


def review(cust_id: int, order_id: int, ) -> str:
    product_id = randrange(MIN_PRODUCT_ID, MAX_PRODUCT_ID)
    rating = randrange(1, 5 + 1)
    comment = fake.paragraph()
    return f"({cust_id}, {order_id}, {product_id}, {rating}, '{comment}')"


def main():
    # CUSTOMER

    sql = ""
    sql = add(sql, "")
    sql = add(sql, "-- ## CUSTOMER ##")
    sql = add(
        sql, "INSERT INTO customer (name, email, gender, birthdate, point, join_date) VALUES")
    for id in range(MIN_CUSTOMER_ID, MAX_CUSTOMER_ID):
        sql = add(sql, customer(), ",\n" if id !=
                  MAX_CUSTOMER_ID - 1 else True)

    sql = add(sql, "")
    sql = add(sql, "-- ## ADDRESS ##")
    sql = add(
        sql, "INSERT INTO address (address_type, cust_id, line_1, province, postal_code) VALUES")
    for id in range(MIN_CUSTOMER_ID, MAX_CUSTOMER_ID):
        sql = add(sql, address(id), ",\n" if id !=
                  MAX_CUSTOMER_ID - 1 else True)

    sql = add(sql, "")
    sql = add(sql, "-- ## CATEGORY ##")
    sql = add(sql, "INSERT INTO category (category_id, name) VALUES")
    sql = add(sql, category(), True)

    sql = add(sql, "")
    sql = add(sql, "-- ## PRODUCT ##")
    sql = add(sql, "INSERT INTO product (name, price, stock) VALUES")
    for id in range(MIN_PRODUCT_ID, MAX_PRODUCT_ID):
        sql = add(sql, product(), ",\n" if id != MAX_PRODUCT_ID - 1 else True)

    sql = add(sql, "")
    sql = add(sql, "-- ## PRODUCT CATEGORIES ##")
    sql = add(sql, "INSERT INTO product_category (product_id, category_id) VALUES")
    for id in range(MIN_PRODUCT_ID, MAX_PRODUCT_ID):
        sql = add(sql, product_category(id), ",\n" if id !=
                  MAX_PRODUCT_ID - 1 else True)

    sql = add(sql, "")
    sql = add(sql, "-- ## SHOP ORDER ##")
    sql = add(
        sql, "INSERT INTO shop_order (cust_id, order_date, status, address_id, sub_total, discount) VALUES")
    for id in range(MIN_ORDER_ID, MAX_ORDER_ID):
        sql = add(sql, shop_order(id), ",\n" if id !=
                  MAX_ORDER_ID - 1 else True)

    sql = add(sql, "")
    sql = add(sql, "-- ## ORDER LINE ##")
    sql = add(
        sql, "INSERT INTO order_line(order_id, product_id, qty, unit_price) VALUES")
    for id in range(MIN_ORDER_ID, MAX_ORDER_ID):
        sql = add(sql, order_line(id), ",\n" if id !=
                  MAX_ORDER_ID - 1 else True)

    sql = add(sql, "")
    sql = add(sql, "-- ## REVIEW ##")
    sql = add(
        sql, "INSERT INTO review (cust_id, order_id, product_id, rating, comment) VALUES")
    for id in range(MIN_ORDER_ID, MAX_ORDER_ID):
        sql = add(sql, review(randrange(MIN_CUSTOMER_ID, MAX_CUSTOMER_ID), id), ",\n" if id !=
                  MAX_ORDER_ID - 1 else True)

    sql = add(sql, "")
    sql = add(sql, "-- ## PAYMENT ##")
    sql = add(
        sql, "INSERT INTO payment (order_id, method, amount, paid_date) VALUES")
    for id in range(MIN_ORDER_ID, MAX_ORDER_ID):
        sql = add(sql, payment(id), ",\n" if id !=
                  MAX_ORDER_ID - 1 else True)

    sql = add(sql, "")
    sql = add(sql, "-- ## UPDATE ORDER LINE unit_price ##")
    sql = add(sql, "UPDATE order_line")
    sql = add(sql, "SET unit_price = (SELECT p.price FROM product p WHERE p.product_id = order_line.product_id)", True)

    sql = add(sql, "")
    sql = add(sql, "-- ## UPDATE SHOP ORDER sub_total ##")
    sql = add(sql, "UPDATE shop_order")
    sql = add(
        sql, "SET sub_total = COALESCE((SELECT SUM(ol.qty * ol.unit_price)")
    sql = add(sql, "FROM order_line ol")
    sql = add(sql, "WHERE ol.order_id = shop_order.order_id), 0)", True)

    sql = add(sql, "")
    sql = add(sql, "-- ## UPDATE SHOP ORDER discount ##")
    sql = add(sql, """UPDATE shop_order
JOIN    vw_customer_tier ON vw_customer_tier.cust_id = shop_order.cust_id
SET		discount = IFNULL(sub_total * (
        CASE 
            WHEN vw_customer_tier.tier = 'vip' THEN 0.15
            WHEN vw_customer_tier.tier = 'gold' AND sub_total >= 500 THEN 0.10
            WHEN vw_customer_tier.tier = 'silver' AND sub_total >= 500 THEN 0.05
            WHEN vw_customer_tier.tier = 'normal' THEN 0
        END), 0)""", True)

    sql = add(sql, "")
    sql = add(sql, "-- ## UPDATE PAYMENT amount ##")
    sql = add(sql, "UPDATE payment")
    sql = add(sql, "SET amount = (SELECT sub_total - discount FROM shop_order WHERE shop_order.order_id = payment.order_id)", ",\n")
    sql = add(sql, " paid_date = (SELECT order_date FROM shop_order WHERE shop_order.order_id = payment.order_id)", True)

    sql = add(sql, "")
    sql = add(sql, "-- ## UPDATE REVIEW review_date ##")
    sql = add(sql, "UPDATE review")
    sql = add(sql, "JOIN shop_order ON shop_order.order_id = review.order_id")
    sql = add(sql, "SET review.review_date = shop_order.order_date", True)

    print(sql)


if __name__ == '__main__':
    main()
