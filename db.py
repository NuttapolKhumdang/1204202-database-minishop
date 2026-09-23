# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import mysql.connector
import config


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


def run_query(sql, params=None):
    """รัน SELECT คืนผลเป็น list ของ dict"""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    cur.close(); conn.close(); return rows


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    conn = get_connection(); cur = conn.cursor()
    cur.execute(sql, params or ()); conn.commit()
    out = {"new_id": cur.lastrowid, "affected": cur.rowcount}
    cur.close(); conn.close(); return out


def _todo(name):
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


# ---------- ลูกค้า (customer) ----------
def search_customers(filters):
    """ค้นหา ลูกค้า ตามเงื่อนไข (name, email, tier)
    คำใบ้: เริ่มจาก sql = "SELECT * FROM customer WHERE 1=1"
    แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_customers")


def get_customer(cust_id):
    """ดึง ลูกค้า 1 รายการตาม cust_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM customer WHERE cust_id = %s แล้วคืนแถวเดียว
    _todo("get_customer")


def create_customer(data):
    """เพิ่ม ลูกค้า ใหม่ — data มีคีย์: name, email, address, tier"""
    # TODO: INSERT INTO customer (...) VALUES (%s, ...)
    _todo("create_customer")


def update_customer(cust_id, data):
    """แก้ไข ลูกค้า ตาม cust_id"""
    # TODO: UPDATE customer SET ... WHERE cust_id=%s
    _todo("update_customer")


def delete_customer(cust_id):
    """ลบ ลูกค้า ตาม cust_id"""
    # TODO: DELETE FROM customer WHERE cust_id=%s
    _todo("delete_customer")

# ---------- สินค้า (product) ----------
def search_products(filters):
    """ค้นหา สินค้า ตามเงื่อนไข (name, category)
    คำใบ้: เริ่มจาก sql = "SELECT * FROM product WHERE 1=1"
    แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_products")


def get_product(product_id):
    """ดึง สินค้า 1 รายการตาม product_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM product WHERE product_id = %s แล้วคืนแถวเดียว
    _todo("get_product")


def create_product(data):
    """เพิ่ม สินค้า ใหม่ — data มีคีย์: name, category, price, stock"""
    # TODO: INSERT INTO product (...) VALUES (%s, ...)
    _todo("create_product")


def update_product(product_id, data):
    """แก้ไข สินค้า ตาม product_id"""
    # TODO: UPDATE product SET ... WHERE product_id=%s
    _todo("update_product")


def delete_product(product_id):
    """ลบ สินค้า ตาม product_id"""
    # TODO: DELETE FROM product WHERE product_id=%s
    _todo("delete_product")

# ---------- ออเดอร์ (shop_order) ----------
def search_orders(filters):
    """ค้นหา ออเดอร์ ตามเงื่อนไข (cust_id, status)
    คำใบ้: เริ่มจาก sql = "SELECT * FROM shop_order WHERE 1=1"
    แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_orders")


def get_order(order_id):
    """ดึง ออเดอร์ 1 รายการตาม order_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM shop_order WHERE order_id = %s แล้วคืนแถวเดียว
    _todo("get_order")


def create_order(data):
    """เพิ่ม ออเดอร์ ใหม่ — data มีคีย์: cust_id, order_date, status"""
    # TODO: INSERT INTO shop_order (...) VALUES (%s, ...)
    _todo("create_order")


def update_order(order_id, data):
    """แก้ไข ออเดอร์ ตาม order_id"""
    # TODO: UPDATE shop_order SET ... WHERE order_id=%s
    _todo("update_order")


def delete_order(order_id):
    """ลบ ออเดอร์ ตาม order_id"""
    # TODO: DELETE FROM shop_order WHERE order_id=%s
    _todo("delete_order")


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
# ============================================================
def report_summary():
    """ตัวเลขสรุปบนการ์ด dashboard — คืน dict เช่น {"customers": 10, ...}
    คำใบ้: ใช้ COUNT(*) หลายครั้ง"""
    # TODO: นับจำนวนรวมต่าง ๆ เพื่อแสดงบนการ์ด
    _todo("report_summary")

def report_best_selling():
    """📈 สินค้าขายดี (Best Sellers)
    คำใบ้: JOIN order_line→product, GROUP BY product, SUM(qty), ORDER BY DESC, LIMIT 5"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_best_selling")

def report_customers_above_avg():
    """🏅 ลูกค้าที่ซื้อมากกว่าค่าเฉลี่ย (Above Average)
    คำใบ้: JOIN shop_order→order_line, GROUP BY customer, HAVING SUM(qty*unit_price) > (subquery AVG)"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_customers_above_avg")

def report_high_rated():
    """⭐ สินค้าคะแนนรีวิวเฉลี่ย ≥ 4 (HAVING)
    คำใบ้: JOIN review→product, GROUP BY product, HAVING AVG(rating) >= 4"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_high_rated")
