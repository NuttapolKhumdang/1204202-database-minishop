from faker import Faker
import faker_commerce
from random import random, randrange, choice
from datetime import date

fake = Faker()
fake.add_provider(faker_commerce.Provider)

MIN_CUSTOMER_ID = 1
MAX_CUSTOMER_ID = 40

MIN_PRODUCT_ID = 1
MAX_PRODUCT_ID = 60

MIN_ORDER_ID = 1
MAX_ORDER_ID = 40

def customer():
    tier = ['normal', 'silver', 'gold', 'vip']

    for _ in range(MAX_CUSTOMER_ID):
        sql = f"('{fake.name()}', '{fake.email()}', '{fake.address().replace('\n', ' ')}', '{choice(tier)}'),"
        print(sql)


def product():
    for _ in range(MAX_PRODUCT_ID):
        price = round(random() * randrange(100, 1000), 2)
        stock = randrange(0, 255)
        sql = f"('{fake.ecommerce_name()}', '{fake.ecommerce_category()}', {price}, {stock}),"
        print(sql)


def shop_order():
    status = ['pending', 'shipped', 'cancel']

    for i in range(MAX_ORDER_ID):
        cust_id = randrange(MIN_CUSTOMER_ID, MAX_CUSTOMER_ID)
        ship = choice(status)
        order_date = fake.date_between(start_date=date(
            2020, 1, 1), end_date=date(2026, 1, 1))

        sql = f"({cust_id}, '{order_date}', '{ship}'),"
        print(sql, end="\n" if i % 3 == 0 else "\t")
    print()


def order_line():
    order_id = list(range(MIN_ORDER_ID, MAX_ORDER_ID))

    items = 0
    for id in order_id:
        use_product = []

        for _ in range(randrange(2, 10)):
            order_id = id

            product_id = randrange(MIN_PRODUCT_ID, MAX_PRODUCT_ID)

            if product_id in use_product:
                continue

            use_product.append(product_id)

            qty = randrange(1, 10)
            sql = f"({order_id}, {product_id}, {qty}, 1),"

            print(sql, end="\n" if items % 5 == 0 else "\t\t")
            items += 1
    print()