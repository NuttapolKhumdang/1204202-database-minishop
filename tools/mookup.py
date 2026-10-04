from faker import Faker
import faker_commerce
from random import random, randrange, choice, choices
from datetime import date
from typing import List, Dict

fake = Faker(['th_TH'])
fake.add_provider(faker_commerce.Provider)

MIN_CUSTOMER_ID = 1
MAX_CUSTOMER_ID = 40

MIN_PRODUCT_ID = 1
MAX_PRODUCT_ID = 60

MIN_ORDER_ID = 1
MAX_ORDER_ID = 40


PRIMARY_CATEGORIES: List = [
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
    "Industrial"
]
CATEGORIES = [
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


def customer():
    tier = ['normal', 'silver', 'gold', 'vip']
    gender = {'M': 'ชาย', 'F': 'หญิง'}

    addresses: List[str] = []
    for _ in range(MAX_CUSTOMER_ID):
        p = fake.profile()
        sql = f"('{p['name']}', '{p['mail']}', {choice([f"'{gender.get(p['sex'])}'", 'null'])}, '{
            p['birthdate']}', '{choice(tier)}'),"  # type: ignore
        print(sql)

        addresses.append(p['address'])  # type: ignore

    print('\n\n')
    for i, address in enumerate(addresses):
        postal_code = address.split(' ')[-1]
        province = address.split(' ')[-2].replace('จ.', '').replace('จังหวัด', '')
        line_1 = ' '.join(address.split(' ')[:-2])

        try:
            int(postal_code)
        except:
            postal_code = None

        sql = f"('shipping', {i+1}, '{line_1}', '{province}', '{postal_code if postal_code else fake.postcode()}'),"
        print(sql)



def primary_category():
    for i, cate in enumerate(PRIMARY_CATEGORIES):
        sql = f"('{cate}'),"
        print(sql, end="\n" if i % 3 == 0 else "\t")


# primary_category()


def category():
    for i, cate in enumerate(CATEGORIES):
        sql = f"('{cate}'),"
        print(sql, end="\n" if i % 3 == 0 else "\t")

# category()


def product():
    for _ in range(MAX_PRODUCT_ID):
        price = round(random() * randrange(100, 1000), 2)
        stock = randrange(0, 255)
        cate = randrange(1, 22)
        sql = f"('{fake.ecommerce_name()}', {cate}, {price}, {stock}),"
        print(sql)


def shop_order():
    status = ['pending', 'shipped', 'cancel']

    for i in range(MAX_ORDER_ID):
        cust_id = randrange(MIN_CUSTOMER_ID, MAX_CUSTOMER_ID)
        address = cust_id
        ship = choice(status)
        order_date = fake.date_between(start_date=date(
            2020, 1, 1), end_date=date(2026, 1, 1))

        sql = f"({cust_id}, '{order_date}', '{ship}', {address}, 0, 0, 0),"
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