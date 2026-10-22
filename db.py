# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
#
#  ปรับให้ตรงกับ schema.sql:
#    - ที่อยู่แยกเป็นตาราง address (customer ไม่มีคอลัมน์ address แล้ว)
#    - product.category เป็น FK → primary_category (เก็บเป็นรหัส ไม่ใช่ชื่อ)
#    - shop_order มี address / sub_total / discount / total (NOT NULL)
# ============================================================
import re
import json
from decimal import Decimal, InvalidOperation

import mysql.connector
import config


def get_connection():
    """เปิดการเชื่อมต่อฐานข้อมูล MySQL (ค่าตั้งต้นอยู่ใน config.py)"""
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


def run_query(sql, params=None):
    """รัน SELECT คืนผลเป็น list ของ dict"""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        conn.close()


# ชื่อ CHECK constraint ใน schema.sql → ข้อความที่แสดงบนหน้าเว็บ
_CHECK_MSG = {
    "chk_cust_tier": "ระดับลูกค้าต้องเป็น normal, silver, gold หรือ vip",
    "chk_product_price": "ราคาสินค้าต้องไม่ติดลบ",
    "chk_product_stock": "จำนวนคงเหลือต้องไม่ติดลบ",
    "chk_order_status": "สถานะออเดอร์ต้องเป็น pending, shipped, complete หรือ cancel",
    "chk_order_sub_total": "ยอดรวมก่อนลดต้องไม่ติดลบ",
    "chk_order_discount": "ส่วนลดต้องไม่ติดลบ",
    "chk_order_total": "ยอดสุทธิต้องไม่ติดลบ (ส่วนลดมากกว่ายอดรวมหรือเปล่า?)",
}


def _friendly(err):
    """แปลง error ของ MySQL ที่เจอบ่อยเป็น ValueError ภาษาไทย (แสดงบนหน้าเว็บ) — ไม่รู้จักคืน None"""
    if err.errno == 1451:      # ลบ/แก้แถวที่ตารางอื่นยังอ้างอิงอยู่ (FK)
        return ValueError("ทำรายการไม่ได้ เพราะยังมีข้อมูลอื่นอ้างอิงอยู่ "
                          "(เช่น ออเดอร์ รายการสินค้า การชำระเงิน หรือรีวิว)")
    if err.errno == 1452:      # ใส่ค่า FK ที่ไม่มีอยู่จริง
        return ValueError("ข้อมูลอ้างอิงไม่ถูกต้อง "
                          "(รหัสลูกค้า / ที่อยู่ / สินค้า / หมวดหมู่ ที่ระบุไม่มีอยู่จริง)")
    if err.errno in (3819, 4025):   # ผิดเงื่อนไข CHECK (MySQL 3819, MariaDB 4025)
        m = re.search(r"[`'](\w+)[`']", err.msg or "")
        name = m.group(1) if m else ""
        return ValueError(_CHECK_MSG.get(name, f"ค่าที่กรอกไม่ผ่านเงื่อนไขของตาราง ({name})"))
    # ข้อความยาวเกินขนาดคอลัมน์ (เช่น tier / postal_code เป็น VARCHAR(6))
    if err.errno == 1406:
        m = re.search(r"column '(\w+)'", err.msg or "")
        return ValueError(f"ข้อมูลในช่อง '{m.group(1) if m else ''}' ยาวเกินที่กำหนด")
    return None


def run_transaction(work):
    """รันหลายคำสั่งเป็น transaction เดียว: สำเร็จ = commit, เกิด error = rollback ทั้งหมด"""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        result = work(cur)
        conn.commit()
        return result
    except mysql.connector.Error as e:
        conn.rollback()
        friendly = _friendly(e)
        if friendly:
            raise friendly from e
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    def work(cur):
        cur.execute(sql, params or ())
        return {"new_id": cur.lastrowid, "affected": cur.rowcount}
    return run_transaction(work)


def blank_to_none(value):
    """แปลงช่องว่าง (สตริงว่าง) ที่ฟอร์มส่งมาเป็น None (= NULL ใน SQL)"""
    return None if value in ("", None) else value


def _todo(name):
    """แจ้งว่าฟังก์ชันยังไม่ได้เขียน (ตอนนี้ไม่มีที่ไหนเรียกใช้แล้ว)"""
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


def _text(value):
    """ข้อความที่ตัดช่องว่างหัวท้ายแล้ว (ว่าง → None)"""
    return None if value is None else blank_to_none(str(value).strip())


def _money(value, default=0):
    """แปลงค่าที่ส่งมาเป็นตัวเลขทศนิยม (ว่าง → default)"""
    value = blank_to_none(value)
    if value is None:
        return Decimal(default)
    try:
        return Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"ตัวเลขไม่ถูกต้อง: {value}")


def _build_set(data, skip_blank=(), blank_to_null=()):
    """สร้างส่วน SET ของ UPDATE เฉพาะคอลัมน์ที่ส่งมา (ชื่อคอลัมน์มาจากโค้ด ค่าส่งผ่าน %s จึงปลอดภัย)"""
    cols, params = [], []
    for col in (*skip_blank, *blank_to_null):
        if col not in data:
            continue
        value = blank_to_none(data[col])
        if value is None and col in skip_blank:
            continue
        cols.append(f"{col}=%s")
        params.append(value)
    return ", ".join(cols), params


# ---------- ลูกค้า (customer) ----------
def search_customers(filters):
    if "name" in filters:
        filters["name"] = f"%{filters["name"]}%"

    if "email" in filters:
        filters["email"] = f"%{filters["email"]}%"

    filter_options = {
        "name": "name LIKE %s",
        "email": "email LIKE %s",
        "tier": "tier = %s",
    }

    filter_string = ""
    args = ()

    for index, key in enumerate(filters.keys()):
        if index == 0:
            filter_string += " WHERE "
        else:
            filter_string += " AND "

        filter_string += filter_options[key]
        args = (*args, filters[key])

    sql = f"""
        SELECT  c.cust_id
            ,   c.name
            ,   c.email
            ,   c.gender
            ,   c.point
            ,   t.tier
            ,   c.join_date
        FROM    customer c
        JOIN    vw_customer_tier t ON t.cust_id = c.cust_id
        {filter_string}
    ORDER BY    cust_id
    """

    return run_query(sql, args)


def get_customer(cust_id):
    sql = f"""
        SELECT c.*
        FROM customer c
        WHERE c.cust_id = %s
    """
    rows = run_query(sql, (cust_id,))
    return rows[0] if rows else None


def create_customer(data):
    name, email = _text(data.get("name")), _text(data.get("email"))
    if not name or not email:
        raise ValueError("กรุณากรอกชื่อและอีเมลของลูกค้า")

    gender = blank_to_none(data.get("gender"))
    birthdate = blank_to_none(data.get("birthdate"))
    point = blank_to_none(data.get("point"))

    return run_command("INSERT INTO customer (name, email, gender, birthdate, point) VALUES (%s, %s, %s, %s, %s)",
                       (name, email, gender, birthdate, point,))


def update_customer(cust_id, data):
    """UPDATE customer (เฉพาะช่องที่ส่งมา) และ UPDATE/INSERT ที่อยู่แรก ใน transaction เดียว"""
    sets, params = _build_set(data, skip_blank=("name", "email", "point"),
                              blank_to_null=("gender", "birthdate"))
    return run_command(f"UPDATE customer SET {sets} WHERE cust_id=%s", (*params, cust_id))


def delete_customer(cust_id):
    """ลบลูกค้า (ที่อยู่ลบตามอัตโนมัติ แต่ถ้ามีออเดอร์/รีวิวอยู่จะลบไม่ได้)"""
    return run_command("DELETE FROM customer WHERE cust_id=%s", (cust_id,))


# ---------- address (address) ----------


def get_customer_address(cust_id):
    sql = f"""
        SELECT a.address_id,
               a.address_type AS ประเภท,
               a.line_1       AS 'บรรทัด 1',
               a.line_2       AS 'บรรทัด 2',
               a.province     AS จังหวัด,
               a.postal_code  AS รหัสไปรษณีย์
        FROM address a
        WHERE a.cust_id = %s
    """
    rows = run_query(sql, (cust_id,))
    return rows


def get_address(address_id):
    sql = f"""
        SELECT *
        FROM address a 
        WHERE a.address_id = %s
    """
    rows = run_query(sql, (address_id,))
    return rows[0] if rows else None


def create_address(cust_id, data):
    sql = f"""
        INSERT INTO address (cust_id, address_type, line_1, line_2, province, postal_code)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    rows = run_command(sql, (cust_id, data['address_type'], data['line_1'],
                       data['line_2'], data['province'], data['postal_code']))
    return rows


def update_address(address_id, data):
    sets, params = _build_set(data, skip_blank=(
        "address_type", "line_1", "line_2", "province", "postal_code"))

    return run_command(f"UPDATE address SET {sets} WHERE address_id = %s", (*params, address_id))


def delete_address(address_id):
    sql = f"""
        DELETE FROM address
        WHERE address_id = %s
    """

    rows = run_command(sql, (address_id,))
    return rows

# -- Product


def search_products(filters):
    sql = """
        SELECT  p.product_id
            ,   p.name
            ,   p.price
            ,   p.stock
            ,   vpc.categories
        FROM    product p
        JOIN    vw_product_categories vpc ON vpc.product_id = p.product_id
        WHERE 1=1
    """

    PRODUCT_STATUS = {
        'เลิกขาย': 0,
        'ใช้งานอยู่': 1,
        'ทั้งหมด': -1,
    }

    params = []

    if filters.get("category"):
        query = [q.strip() for q in filters.get("category").split(',')]
        mapped_query = [f"%{q}%" for q in query]
        mapped_parameter = ' '.join(
            ['or c.name like %s' for _ in mapped_query])

        for q in mapped_query:
            params.append(q)

        sql = f"""
        SELECT  p.product_id
            ,   p.name
            ,   p.price
            ,   p.stock
            ,   vpc.categories
        FROM    product p
        JOIN    vw_product_categories vpc ON vpc.product_id = p.product_id
        WHERE	p.product_id IN (
            SELECT 	pc.product_id
            FROM	product_category pc
            WHERE 	pc.category_id IN (
                SELECT 	c.category_id 
                FROM 	category c
                WHERE	1 <> 1
                    {mapped_parameter}
            )
        )
        """

    if not filters.get("is_active"):
        sql += " AND p.is_active = 1"

    elif filters.get("is_active") and str(filters.get("is_active")).lower() != 'all':
        sql += " AND p.is_active = %s"
        if filters.get("is_active") in PRODUCT_STATUS:
            params.append(PRODUCT_STATUS[filters['is_active']])

        if (filters.get("is_active") in ['0', '1']):
            params.append(filters['is_active'])

    if filters.get("name"):
        sql += " AND p.name LIKE %s"
        params.append("%" + filters["name"] + "%")

    if filters.get("min_price"):
        sql += " AND p.price >= %s"
        params.append(filters["min_price"])

    if filters.get("max_price"):
        sql += " AND p.price <= %s"
        params.append(filters["max_price"])

    sql += " ORDER BY p.product_id"
    return run_query(sql, tuple(params))


def get_product(product_id):
    """ดึงสินค้า 1 รายการ (category = รหัสหมวดหมู่, category_name = ชื่อหมวดหมู่)"""
    sql = """
        SELECT p.*
        FROM product p
        WHERE p.product_id = %s
    """
    rows = run_query(sql, (product_id,))
    return rows[0] if rows else None


def get_product_category(product_id):
    sql = """
        SELECT c.category_id, c.name
        FROM product_category pc
        INNER JOIN category c       ON c.category_id = pc.category_id
        WHERE pc.product_id = %s
    """
    return run_query(sql, (product_id,))


def create_product(data):
    """เพิ่มสินค้าใหม่ (หมวดหมู่ใส่เป็นรหัสหรือชื่อก็ได้)"""

    print("data:", data)
    name = _text(data.get("name"))
    if not name:
        raise ValueError("กรุณากรอกชื่อสินค้า")

    sql = "INSERT INTO product (name, price, stock) VALUES (%s, %s, %s)"
    params = (name, blank_to_none(data.get("price"))
              or 0, blank_to_none(data.get("stock")) or 0)
    product = run_command(sql, params)

    if "category" in data:
        category = json.loads(data['category'])
        for c in category:
            run_command(f"""
            INSERT INTO product_category (product_id, category_id) 
            VALUES (%s, %s) 
        """, (product["new_id"], c,))


def update_product(product_id, data):
    """แก้ไขสินค้าเฉพาะช่องที่ส่งมา"""
    data = dict(data)

    if "category" in data:
        category = json.loads(data['category'])
        run_command(f"""
            DELETE FROM product_category 
            WHERE product_id = %s AND category_id NOT IN ({', '.join([str(int(c)) for c in category])}) 
        """, (product_id,))

        exited_category = [c["category_id"] for c in run_query(  # type:ignore
            "SELECT * FROM product_category WHERE product_id = %s", (product_id,))]

        for c in category:
            if c in exited_category:
                continue

            run_command(f"""
            INSERT INTO product_category (product_id, category_id) 
            VALUES (%s, %s) 
        """, (product_id, c,))

    sets, params = _build_set(data, skip_blank=(
        "name", "price", "stock", "is_active"))
    if not sets:
        return {"new_id": None, "affected": 0}
    return run_command(f"UPDATE product SET {sets} WHERE product_id=%s", (*params, product_id))


def delete_product(product_id):
    """ลบสินค้า (ถ้าเคยถูกสั่งซื้อแล้วจะลบไม่ได้ — ให้ตั้ง is_active = FALSE แทน)"""
    return run_command("DELETE FROM product WHERE product_id=%s", (product_id,))


def get_category(filters):
    sql = """
        SELECT *
        FROM category 
        WHERE 1=1 
    """

    params = []
    if filters.get('name'):
        sql += " AND name LIKE %s"
        params.append(f"%{filters["name"]}%")

    return run_query(sql, (params))


# ---------- ออเดอร์ (shop_order) ----------
def search_orders(filters):
    sql = """
        SELECT  o.order_id
            ,   c.cust_id                   AS 'รหัสลูกค้า'
            ,   c.name                      AS 'ชื่อลูกค้า'
            ,   o.order_date                AS 'วันที่สั่งซื้อ'
            ,   o.status                    AS 'สถานะ'
            ,   (o.sub_total - o.discount)  AS 'ยอดสุทธิ'
            ,   SUM(p.amount)                    AS 'ชำระแล้ว'
        FROM    shop_order o 
        JOIN    customer c ON c.cust_id = o.cust_id
    LEFT JOIN   payment  p ON p.order_id = o.order_id
        WHERE 1=1"""

    params = []
    if filters.get("cust_id"):
        sql += " AND c.cust_id = %s"
        params.append(filters["cust_id"])

    if filters.get("status"):
        sql += " AND status = %s"
        params.append(filters["status"])

    if filters.get("start_date"):
        sql += " AND order_date >= %s"
        params.append(filters["start_date"])

    if filters.get("end_date"):
        sql += " AND order_date <= %s"
        params.append(filters["end_date"])

    sql += " GROUP BY    o.order_id, 'รหัสลูกค้า', 'ชื่อลูกค้า', 'วันที่สั่งซื้อ', 'สถานะ', 'ยอดสุทธิ'"
    sql += " ORDER BY order_id"
    return run_query(sql, tuple(params))


def get_order(order_id):
    """ดึงออเดอร์ 1 รายการ"""
    sql = """
        SELECT  c.cust_id
            ,   c.name
            ,   so.*
        FROM shop_order so
        JOIN customer c     ON c.cust_id = so.cust_id
        WHERE order_id = %s
    """
    rows = run_query(sql, (order_id,))
    return rows[0] if rows else None


def check_can_ship(order_id):
    """ตรวจว่าออเดอร์จัดส่งได้ไหม (pending, มีสินค้า, เปิดขาย, stock พอ) → คืน (True/False, ข้อความ)"""
    rows = run_query(
        "SELECT status FROM shop_order WHERE order_id = %s", (order_id,))
    if not rows:
        return False, f"ไม่พบออเดอร์นี้: {order_id}"

    status = rows[0]["status"]  # type: ignore
    if status != "pending":
        return False, f"ออเดอร์นี้ไม่สามารถจัดส่งได้ (สถานะปัจจุบัน: {status})"

    lines = run_query("""
        SELECT p.name, p.stock, p.is_active, ol.qty
        FROM order_line ol
        JOIN product p ON p.product_id = ol.product_id
        WHERE ol.order_id = %s""", (order_id,))
    if not lines:
        return False, "ออเดอร์นี้ไม่สามารถจัดส่งได้ (ไม่มีรายการสินค้า)"

    problems = [f"{l['name']} (สั่ง {l['qty']} / คงเหลือ {l['stock'] or 0})"  # type: ignore
                for l in lines
                # type: ignore
                if l["is_active"] == 0 or (l["stock"] or 0) < l["qty"]] # type: ignore
    if problems:
        return False, "ออเดอร์นี้ไม่สามารถจัดส่งได้ (สินค้าไม่พร้อม: " + ", ".join(problems) + ")"
    return True, "จัดส่งได้"


def create_order(data):
    """เพิ่มออเดอร์ใหม่ (ไม่กรอก: วันที่ = วันนี้, สถานะ = pending, ที่อยู่ = ที่อยู่แรกของลูกค้า)"""
    cust_id = blank_to_none(data.get("cust_id"))
    if cust_id is None:
        raise ValueError("กรุณาระบุรหัสลูกค้า")

    sql = """
        INSERT INTO shop_order (cust_id, order_date, status, sub_total, discount)
        VALUES (%s, %s, %s, 0, 0)
    """

    params = (
        cust_id,
        blank_to_none(data.get("order_date")),
        blank_to_none(data.get("status"))
    )

    return run_command(sql, params)


def update_order(order_id, data):
    """แก้ไขออเดอร์เฉพาะช่องที่ส่งมา (เปลี่ยนเป็น shipped ต้องผ่าน check_can_ship ก่อน)"""
    current = get_order(order_id)
    if not current:
        raise ValueError(f"ไม่พบออเดอร์รหัส {order_id}")

    # เปลี่ยนสถานะเป็น shipped ต้องผ่านการตรวจสต็อกก่อน (ดู check_can_ship)
    # type: ignore
    if blank_to_none(data.get("status")) == "shipped" and current["status"] != "shipped": # type: ignore
        ok, msg = check_can_ship(order_id)
        if not ok:
            raise ValueError(msg)

    # อัปเดตเฉพาะช่องที่ส่งมา (ช่องว่าง = ไม่แก้)
    sets, params = _build_set(data, skip_blank=(
        "order_date", "status", "address_id"))

    if not sets:
        return {"new_id": None, "affected": 0}
    return run_command(f"UPDATE shop_order SET {sets} WHERE order_id=%s", (*params, order_id))


def delete_order(order_id):
    """ลบออเดอร์พร้อมรายการสินค้าใน transaction เดียว (ถ้ามีการชำระเงิน/รีวิวจะลบไม่ได้)"""
    def work(cur):
        cur.execute("DELETE FROM order_line WHERE order_id=%s", (order_id,))
        cur.execute("DELETE FROM shop_order WHERE order_id=%s", (order_id,))
        return {"new_id": None, "affected": cur.rowcount}
    return run_transaction(work)


def get_order_line(order_id):
    sql = """
        SELECT  *
        FROM    order_line ol
        JOIN    product p       ON p.product_id = ol.product_id
        WHERE   order_id = %s
    """

    rows = run_query(sql, (order_id,))
    return rows


def create_order_line(order_id, data):
    def work(cur):
        cur.execute(
            "SELECT stock FROM product WHERE product_id = %s", (data["product_id"], ))
        stock = cur.fetchone()["stock"]

        avaliable_stock = int(stock) - int(data['qty'])  # type: ignore
        if avaliable_stock >= 0:
            cur.execute("UPDATE product SET stock = %s WHERE product_id = %s",
                        (avaliable_stock, data['product_id'],))
        else:
            raise ValueError("จำนวนคำสั่งซื้อมากกว่าสินค้าในคลัง")

        cur.execute("""
            INSERT INTO order_line (order_id, product_id, qty, unit_price)
            VALUES (%s, %s, %s, 0)
        """, (order_id, data['product_id'], data['qty']))

        cur.execute("""
            UPDATE order_line
            SET unit_price = (SELECT price FROM product WHERE product_id = order_line.product_id)
            WHERE order_id = %s AND product_id = %s
        """, (order_id, data['product_id']))

        cur.execute("""
            UPDATE  shop_order
            SET     sub_total = IFNULL(COALESCE(
                            (   SELECT SUM(ol.qty * ol.unit_price)
                                FROM    order_line ol
                                WHERE   ol.order_id = shop_order.order_id
                            ), 0), 0)
            WHERE   order_id = %s
        """, (order_id, ))

        cur.execute("""
            UPDATE 	shop_order
            JOIN 	vw_customer_tier ON vw_customer_tier.cust_id = shop_order.cust_id
            SET		discount = IFNULL(sub_total * (
                    CASE 
                        WHEN vw_customer_tier.tier = 'vip' 								THEN 0.15
                        WHEN vw_customer_tier.tier = 'gold' 	AND sub_total >= 500 	THEN 0.10
                        WHEN vw_customer_tier.tier = 'silver' 	AND sub_total >= 500 	THEN 0.05
                        WHEN vw_customer_tier.tier = 'normal' 							THEN 0
                    END), 0)
            WHERE 	order_id = %s;
        """, (order_id, ))
    return run_transaction(work)


def delete_order_line(order_id, pid):
    def work(cur):
        cur.execute("""	526.30
            SELECT qty FROM order_line
            WHERE       order_id = %s AND product_id = %s
        """, (order_id, pid, ))

        qty = cur.fetchone()['qty']

        cur.execute("""
            DELETE FROM order_line
            WHERE       order_id = %s AND product_id = %s
        """, (order_id, pid, ))

        cur.execute("""
            UPDATE product SET stock = stock + %s
            WHERE  product_id = %s
        """, (qty, pid, ))

        cur.execute("""
            UPDATE  shop_order
            SET     sub_total = IFNULL(COALESCE(
                            (   SELECT SUM(ol.qty * ol.unit_price)
                                FROM    order_line ol
                                WHERE   ol.order_id = shop_order.order_id
                            ), 0), 0)
            WHERE   order_id = %s
        """, (order_id, ))

        cur.execute("""
            UPDATE 	shop_order
            JOIN 	vw_customer_tier ON vw_customer_tier.cust_id = shop_order.cust_id
            SET		discount = IFNULL(sub_total * (
                    CASE 
                        WHEN vw_customer_tier.tier = 'vip' 								THEN 0.15
                        WHEN vw_customer_tier.tier = 'gold' 	AND sub_total >= 500 	THEN 0.10
                        WHEN vw_customer_tier.tier = 'silver' 	AND sub_total >= 500 	THEN 0.05
                        WHEN vw_customer_tier.tier = 'normal' 							THEN 0
                    END), 0)
            WHERE 	order_id = %s;
        """, (order_id, ))
    return run_transaction(work)


# --  Payment

def search_payment(filters):
    sql = """
        SELECT  p.payment_id
            ,   so.order_id
            ,   c.name          AS customer_name
            ,   p.amount
            ,   p.method
            ,   p.paid_date
        FROM    payment p
        JOIN    shop_order so   ON so.order_id = p.order_id
        JOIN    customer c      ON c.cust_id = so.cust_id
        WHERE 1=1
    """

    params = []

    if filters.get('payment_id'):
        sql += " AND payment_id = %s"
        params.append(filters['order_id'])

    if filters.get('order_id'):
        sql += " AND so.order_id = %s"
        params.append(filters['order_id'])

    if filters.get('cust_id'):
        sql += " AND so.cust_id = %s"
        params.append(filters['cust_id'])

    if filters.get('paid_date'):
        sql += " AND paid_date = %s"
        params.append(filters['paid_date'])

    sql += " ORDER BY payment_id"
    return run_query(sql, (*params, ))


def get_payment(payment_id):
    row = run_query(
        "SELECT * FROM payment WHERE payment_id = %s", (payment_id,))
    return row[0] if row else None


def create_payment(data):
    ORDER_POINT_MULTIPLYER = {
        '<1000': 0.05,
        '>=1000': 0.10
    }

    order_id = data['order_id']
    method = data['method']
    amount = data['amount']
    paid_date = data['paid_date']

    def work(cur):
        sql = """INSERT INTO payment (order_id, method, amount, paid_date) VALUES (%s, %s, %s, %s)"""
        cur.execute(sql, (order_id, method, amount, paid_date,))

        cur.execute("""
            SELECT  so.cust_id
                ,   so.sub_total - so.discount  AS total
                ,   SUM(amount)                 AS paided
            FROM    shop_order so
        LEFT JOIN   payment p ON p.order_id = so.order_id
            WHERE   so.order_id=%s
        GROUP BY    so.cust_id, total
            """, (order_id, ))
        order = cur.fetchone()

        if float(order['total']) == float(order['paided']):
            total = float(order['total'])
            point = round(
                total * (ORDER_POINT_MULTIPLYER[">=1000"] if total >= 1000 else ORDER_POINT_MULTIPLYER["<1000"]))
            cur.execute("""UPDATE customer SET point = point + %s WHERE cust_id = %s""",
                        (point, order['cust_id'], ))

    return run_transaction(work)


def update_payment(payment_id, data):
    sets, params = _build_set(data, skip_blank=(
        "order_id", "method", "amount", "paid_date"))
    sql = f"""UPDATE payment SET {sets} WHERE payment_id = %s"""
    return run_command(sql, (*params, payment_id))


def delete_payment(payment_id):
    return run_command("DELETE FROM payment WHERE payment_id = %s", (payment_id,))


# --  Review

def search_review(filters):
    sql = """
        SELECT  r.review_id
            ,   r.review_date
            ,   c.name                  AS customer_name
            ,   p.name                  AS product_name
            ,   r.rating
            ,   r.comment
        FROM    review r
        JOIN    shop_order so ON so.order_id = r.order_id
        JOIN    customer c ON c.cust_id     = so.cust_id
        JOIN    product  p ON p.product_id  = r.product_id
        WHERE 1=1
    """

    params = []

    if filters.get('review_id'):
        sql += " AND r.review_id = %s"
        params.append(filters['review_id'])

    if filters.get('cust_id'):
        sql += " AND c.cust_id = %s"
        params.append(filters['cust_id'])

    if filters.get('product_id'):
        sql += " AND p.product_id = %s"
        params.append(filters['product_id'])

    if filters.get('rating'):
        sql += " AND r.rating = %s"
        params.append(filters['rating'])

    return run_query(sql, (*params, ))


def get_review(review_id):
    row = run_query("SELECT * FROM review WHERE review_id = %s", (review_id,))
    return row[0] if row else None


def create_review(data):
    sql = """INSERT INTO review (cust_id, order_id, product_id, rating, comment) VALUES (%s, %s, %s, %s, %s)"""

    cust_id = data['cust_id']
    order_id = data['order_id']
    product_id = data['product_id']
    rating = data['rating']
    comment = data['comment']

    return run_command(sql, (cust_id, order_id, product_id, rating, comment, ))


def update_review(review_id, data):
    sets, params = _build_set(data, skip_blank=(
        "order_id", "method", "amount", "paid_date"))
    sql = f"""UPDATE review SET {sets} WHERE review_id = %s"""
    return run_command(sql, (*params, review_id))


def delete_review(review_id):
    return run_command("DELETE FROM review WHERE review_id = %s", (review_id,))


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ — ใช้ AS 'ชื่อภาษาไทย' ได้
#  ★ ORDER BY ชื่อ alias ต้องครอบด้วย backtick (`ชื่อ`) ห้ามใช้ 'ชื่อ' เพราะ MySQL จะมองเป็นข้อความคงที่ (ไม่เรียงจริง)
# ============================================================
interval_map = {
    "1d": "1 DAY",
    "7d": "7 DAY",
    "1m": "1 MONTH",
    "6m": "6 MONTH",
    "1y": "1 YEAR",
    "all": None,
}


def _since(column, range_val):
    interval = interval_map.get(range_val)
    if not interval:
        return ""          # all / ไม่ระบุ / ไม่รู้จัก → ไม่กรอง
    return f"AND {column} >= CURRENT_DATE - INTERVAL {interval}"


def summary_summary(filters):
    """สรุปตัวเลขรวมของร้านตามช่วงเวลา filters['range'] = 1d, 7d, 1m, 6m, 1y, all (ไม่ระบุ = ทั้งหมด) — คืน 1 แถว"""
    range_val = filters.get("range") if isinstance(filters, dict) else filters

    sql = f"""SELECT
        (
            SELECT COUNT(*) FROM customer
            WHERE 1=1
                {_since("join_date", range_val)}
        ) AS 'ลูกค้า',

        (
            SELECT COUNT(*) FROM product
            WHERE 1=1 
                {_since("added_date", range_val)}
        ) AS 'สินค้า',

        (
            SELECT  COUNT(*) FROM shop_order
            WHERE   1=1
                {_since("order_date", range_val)}
        ) AS 'ออเดอร์',

        (
            SELECT  COUNT(*) FROM review
            WHERE   1=1
                {_since("review_date", range_val)}
        ) AS 'รีวิว',   

        ( 
            SELECT  SUM(sub_total - discount) 
            FROM    shop_order
            WHERE   status IN ('pending', 'shipped', 'complete')
                {_since("order_date", range_val)}
        ) AS 'ยอดขายรวม (บาท)',

        ( 
            SELECT  SUM(amount) 
            FROM    payment
            WHERE   1=1
                {_since("paid_date", range_val)}
        ) AS 'รายรับ (บาท)',

        (
            SELECT  ROUND(AVG(rating), 2) FROM review
            WHERE   1=1
                {_since("review_date", range_val)}
        ) AS 'คะแนนรีวิวเฉลี่ย'
        """
    return run_query(sql)[0]


def summary_best_selling(filters):
    """สินค้าขายดี 5 อันดับ ตามช่วงเวลา filters['range'] = 1d, 7d, 1m, 6m, 1y, all (ไม่ระบุ = ทั้งหมด)"""
    range_val = filters.get("range") if isinstance(filters, dict) else filters

    sql = f"""
    SELECT p.product_id AS 'รหัสสินค้า',
           p.name AS 'ชื่อสินค้า',
           SUM(ol.qty) AS 'จำนวนที่ขาย',
           SUM(ol.qty * ol.unit_price) AS 'ยอดขายรวม'
    FROM order_line AS ol
    INNER JOIN product AS p ON ol.product_id = p.product_id
    INNER JOIN shop_order AS so ON ol.order_id = so.order_id
    WHERE 1=1 {_since("so.order_date", range_val)}
    GROUP BY p.product_id, p.name
    ORDER BY SUM(ol.qty) DESC, p.product_id 
    LIMIT 5
    """
    return run_query(sql)


def summary_customers_above_avg(filters):
    """ลูกค้าที่ยอดซื้อสูงกว่าค่าเฉลี่ย ตามช่วงเวลา filters['range'] = 1d, 7d, 1m, 6m, 1y, all (ไม่ระบุ = ทั้งหมด)"""
    range_val = filters.get("range") if isinstance(filters, dict) else filters

    sql = f"""
     SELECT c.cust_id as 'รหัสลูกค้า', c.name as 'ชื่อลูกค้า',
           SUM(ol.qty * ol.unit_price) AS 'ยอดซื้อรวม'
    FROM customer AS c
    INNER JOIN shop_order AS so
        ON c.cust_id = so.cust_id
    INNER JOIN order_line AS ol
        ON so.order_id = ol.order_id
    WHERE 1=1 {_since("so.order_date", range_val)}
    GROUP BY c.cust_id, c.name
    HAVING SUM(ol.qty * ol.unit_price) > (
        SELECT AVG(customer_total)
        FROM (
            SELECT SUM(ol2.qty * ol2.unit_price) AS customer_total
            FROM shop_order AS so2
            INNER JOIN order_line AS ol2
                ON so2.order_id = ol2.order_id
            WHERE 1=1 {_since("so2.order_date", range_val)}
            GROUP BY so2.cust_id
        ) AS totals
    )
    ORDER BY `ยอดซื้อรวม` DESC
    """

    return run_query(sql)


def summary_high_rated(filters):
    """สินค้าที่คะแนนรีวิวเฉลี่ย ≥ 4 (รีวิวผูกกับออเดอร์ จึงนับให้ทุกสินค้าในออเดอร์นั้น)"""
    range_val = filters.get("range") if isinstance(filters, dict) else filters

    sql = f"""
    SELECT p.product_id as 'รหัสสินค้า', p.name as 'ชื่อสินค้า',
           ROUND(AVG(r.rating), 1) AS 'คะแนนเฉลี่ย',
           COUNT(r.rating) AS 'จำนวนรีวิว'
    FROM review AS r
    INNER JOIN order_line AS ol
        ON r.order_id = ol.order_id
    INNER JOIN product AS p
        ON ol.product_id = p.product_id
    WHERE 1=1 {_since("r.review_date", range_val)}
    GROUP BY p.product_id, p.name
    HAVING AVG(r.rating) >= 4
    ORDER BY `คะแนนเฉลี่ย` DESC 
    """
    return run_query(sql)


def summary_low_rated(filters):
    range_val = filters.get("range") if isinstance(filters, dict) else filters

    sql = f"""
    SELECT p.product_id as 'รหัสสินค้า', p.name as 'ชื่อสินค้า',
           ROUND(AVG(r.rating), 1) AS 'คะแนนเฉลี่ย',
           COUNT(r.rating) AS 'จำนวนรีวิว'
    FROM review AS r
    INNER JOIN order_line AS ol
        ON r.order_id = ol.order_id
    INNER JOIN product AS p
        ON ol.product_id = p.product_id
    WHERE 1=1 {_since("r.review_date", range_val)}
    GROUP BY p.product_id, p.name
    HAVING AVG(r.rating) < 2
    ORDER BY `คะแนนเฉลี่ย` DESC 
    """
    return run_query(sql)


def summary_most_interactive_customer(filters):
    range_val = filters.get("range") if isinstance(filters, dict) else filters

    sql = f"""    
    SELECT  c.cust_id
        ,   c.name              AS customer_name
        ,   c.email
        ,   COUNT(c.cust_id)    AS review_count
        ,   ROUND(AVG(r.rating), 2) AS average_review_rating
    FROM    customer c
    JOIN    shop_order so ON so.cust_id = c.cust_id
    JOIN    review r    ON r.order_id = so.order_id
    WHERE c.cust_id IN (
        SELECT 	so2.cust_id
        FROM 	review r2
        JOIN    shop_order so2 ON so2.order_id = r2.order_id
        WHERE	1=1 {_since("r2.review_date", range_val)}
        GROUP BY cust_id 
        HAVING  COUNT(cust_id) = (	
            SELECT MAX(review_count)
            FROM (
                SELECT 	COUNT(so3.cust_id) AS review_count
                FROM 	review r3
                JOIN    shop_order so3 ON so3.order_id = r3.order_id
                WHERE	1=1 {_since("r3.review_date", range_val)}
                GROUP BY cust_id
            ) AS max_review_count
        )
    ) {_since("review_date", range_val)}
    GROUP BY cust_id, customer_name, email
    ORDER BY cust_id
    """
    return run_query(sql)


# ============================================================
#  รายการรายงานที่แสดงบนหน้า /report  (เรียงตามลำดับที่แสดง)
#  ★ วิธีเพิ่มรายงานใหม่ (ไม่ต้องแก้ไฟล์อื่น):
#    1) เขียนฟังก์ชัน report_xxx() ด้านบน ให้ return run_query(sql)
#    2) เพิ่ม 1 บรรทัดในรายการนี้:  ("ชื่อใน-url", "หัวข้อที่แสดง", ชื่อฟังก์ชัน)
#  ★ รายการนี้ต้องอยู่ท้ายไฟล์ (หลังฟังก์ชันทั้งหมด) ไม่งั้น Python หาชื่อฟังก์ชันไม่เจอ
#  ★ ห้ามตั้งชื่อ url ว่า "summary" (ใช้แล้วสำหรับการ์ดสรุป)
# ============================================================
SUMMARY = [
    ("best-selling",  " สินค้าขายดี (Best Sellers) 📈", summary_best_selling),
    ("top-customers", " ลูกค้าที่ซื้อมากกว่าค่าเฉลี่ย (Above Average) 🏅",
     summary_customers_above_avg),
    ("most-interactive",    "💬 ลูกค้าที่มีส่วนร่วมรีวิวสูงสุด (Top Reviewers)",
     summary_most_interactive_customer),
    ("high-rated",    "⭐ สินค้าคะแนนรีวิวเฉลี่ย ≥ 4", summary_high_rated),
    ("lowest-rated",    "⭐ สินค้าคะแนนรีวิวเฉลี่ย < 2", summary_low_rated),
]
