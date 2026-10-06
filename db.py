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
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    out = {"new_id": cur.lastrowid, "affected": cur.rowcount}
    cur.close()
    conn.close()
    return out


def blank_to_none(value):
    """ช่องที่ไม่ได้กรอกในฟอร์มจะส่งมาเป็น "" — แปลงเป็น None (= NULL ใน SQL)
    ใช้กับคอลัมน์ที่ว่างได้ เช่น return_date, paid_date  เพราะ MySQL ไม่รับ '' เป็น DATE"""
    return None if value in ("", None) else value


def _todo(name):
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


# ---------- ลูกค้า (customer) ----------
def search_customers(filters):
    sql = "SELECT cust_id as 'รหัสลูกค้า', name as 'ชื่อลูกค้า', " \
        "       email as 'อีเมล', address as 'ที่อยู่', tier as 'ระดับ' FROM customer WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append("%" + filters["name"] + "%")

    if filters.get("email"):
        sql += " AND email LIKE %s"
        params.append("%" + filters["email"] + "%")

    if filters.get("address"):
        sql += " AND address LIKE %s"
        params.append("%" + filters["address"] + "%")
    if filters.get("tier"):
        sql += " AND tier = %s"
        params.append(filters["tier"])

    return run_query(sql, tuple(params))


def get_customer(cust_id):
    rows = run_query("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
    return rows[0] if rows else None


def create_customer(data):
    sql = "INSERT INTO customer (name, email, address, tier) VALUES (%s, %s, %s, %s)"
    params = (data["name"], data["email"], data["address"], data["tier"])
    return run_command(sql, params)


def update_customer(cust_id, data):
    sql = "UPDATE customer SET name=%s, email=%s, address=%s, tier=%s WHERE cust_id=%s"
    params = (data["name"], data["email"],
              data["address"], data["tier"], cust_id)
    return run_command(sql, params)


def delete_customer(cust_id):
    return run_command("DELETE FROM customer WHERE cust_id=%s", (cust_id,))

# ---------- สินค้า (product) ----------


def search_products(filters):
    sql = "SELECT product_id as 'รหัสสินค้า', name as 'ชื่อสินค้า', " \
          "category as 'หมวดหมู่', price as 'ราคา', stock as 'จำนวนคงเหลือ' FROM product WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append("%" + filters["name"] + "%")

    if filters.get("category"):
        sql += " AND category = %s"
        params.append(filters["category"])

    if filters.get("min_price"):
        sql += " AND price >= %s"
        params.append(filters["min_price"])

    if filters.get("max_price"):
        sql += " AND price <= %s"
        params.append(filters["max_price"])

    return run_query(sql, tuple(params))


def get_product(product_id):
    sql = "SELECT * FROM product WHERE product_id = %s"
    rows = run_query(sql, (product_id,))
    return rows[0] if rows else None


def create_product(data):
    sql = "INSERT INTO product (name, category, price, stock) VALUES (%s, %s, %s, %s)"
    params = (data["name"], data["category"], data["price"], data["stock"])
    return run_command(sql, params)


def update_product(product_id, data):
    sql = "UPDATE product SET name=%s, category=%s, price=%s, stock=%s WHERE product_id=%s"
    params = (data["name"], data["category"],
              data["price"], data["stock"], product_id)
    return run_command(sql, params)


def delete_product(product_id):
    return run_command("DELETE FROM product WHERE product_id=%s", (product_id,))

# ---------- ออเดอร์ (shop_order) ----------


def search_orders(filters):
    sql = "SELECT order_id as 'รหัสออเดอร์', cust_id as 'รหัสลูกค้า', " \
          "order_date as 'วันที่สั่งซื้อ', status as 'สถานะ' FROM shop_order WHERE 1=1"
    params = []
    if filters.get("cust_id"):
        sql += " AND cust_id = %s"
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

    return run_query(sql, tuple(params))


def get_order(order_id):
    sql = "SELECT * FROM shop_order WHERE order_id = %s"
    rows = run_query(sql, (order_id,))
    return rows[0] if rows else None


def check_can_ship(order_id):
    rows = run_query(
        "SELECT status FROM shop_order WHERE order_id = %s", (order_id,))
    if not rows:
        return False, f"ไม่พบออเดอร์นี้: {order_id}"

    status = rows[0]["status"]  # type: ignore
    if status != "pending":
        return False, f"ออเดอร์นี้ไม่สามารถจัดส่งได้ (สถานะปัจจุบัน: {status})"

    sql = """SELECT b.order_id as 'รหัสออเดอร์', b.cust_id as 'รหัสลูกค้า', b.order_date as 'วันที่สั่งซื้อ', 
                    b.status as 'สถานะ', a.product_id as 'รหัสสินค้า', a.qty as 'จำนวน', a.unit_price as 'ราคาต่อหน่วย'

              FROM order_line a
              JOIN shop_order b ON a.order_id = b.order_id
              WHERE b.order_id = %s""", (order_id,)

    rows = run_query(sql, (order_id,))
    if not rows:
        return False, f"ออเดอร์นี้ไม่สามารถจัดส่งได้ (ไม่มีรายการสินค้า)"

    available = rows[0]["available"]  # type: ignore
    if not available:
        return False, f"ออเดอร์นี้ไม่สามารถจัดส่งได้ (สินค้าไม่พร้อม)"


def create_order(data):
    sql = "INSERT INTO shop_order (cust_id, order_date, status) VALUES (%s, %s, %s)"
    params = (data["cust_id"], data["order_date"], data["status"])
    return run_command(sql, params)


def update_order(order_id, data):
    sql = "UPDATE shop_order SET cust_id=%s, order_date=%s, status=%s WHERE order_id=%s"
    params = (data["cust_id"], data["order_date"], data["status"], order_id)
    return run_command(sql, params)


def delete_order(order_id):
    return run_command("DELETE FROM shop_order WHERE order_id=%s", (order_id,))


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ — ใช้ AS 'ชื่อภาษาไทย' ได้
# ============================================================
def report_summary():
    sql = """SELECT
          (SELECT COUNT(*) FROM customer) AS 'ลูกค้า',
          (SELECT COUNT(*) FROM product) AS 'สินค้า',
          (SELECT COUNT(*) FROM shop_order) AS 'ออเดอร์',
          (SELECT COUNT(*) FROM review) AS 'รีวิว',
          (SELECT SUM(qty * unit_price) FROM order_line) AS 'ยอดขายรวม (บาท)',
          (SELECT ROUND(AVG(rating), 2) FROM review) AS 'คะแนนรีวิวเฉลี่ย'
          """
    return run_query(sql)[0]


def report_best_selling():
    """📈 สินค้าขายดี (Best Sellers)
    คำใบ้: JOIN order_line→product, GROUP BY product, SUM(qty), ORDER BY DESC, LIMIT 5"""
    sql = """
    SELECT p.product_id as 'รหัสสินค้า', p.name as 'ชื่อสินค้า', p.category as 'หมวดหมู่',
           SUM(ol.qty) AS 'จำนวนที่ขาย',
           SUM(ol.qty * ol.unit_price) AS 'ยอดขายรวม'
    FROM order_line AS ol
    INNER JOIN product AS p ON ol.product_id = p.product_id
    GROUP BY p.product_id, p.name, p.category
    ORDER BY 'จำนวนที่ขาย' DESC
    LIMIT 5
    """
    return run_query(sql)


def report_customers_above_avg():
    """🏅 ลูกค้าที่ซื้อมากกว่าค่าเฉลี่ย (Above Average)"""
    sql = """
    SELECT c.cust_id as 'รหัสลูกค้า', c.name as 'ชื่อลูกค้า',
           SUM(ol.qty * ol.unit_price) AS 'ยอดซื้อรวม'
    FROM customer AS c
    INNER JOIN shop_order AS so
        ON c.cust_id = so.cust_id
    INNER JOIN order_line AS ol
        ON so.order_id = ol.order_id
    GROUP BY c.cust_id, c.name
    HAVING SUM(ol.qty * ol.unit_price) > (
        SELECT AVG(customer_total)
        FROM (
            SELECT SUM(ol2.qty * ol2.unit_price) AS customer_total
            FROM shop_order AS so2
            INNER JOIN order_line AS ol2
                ON so2.order_id = ol2.order_id
            GROUP BY so2.cust_id
        ) AS totals
    )
    ORDER BY 'ยอดซื้อรวม' DESC
    """
    return run_query(sql)


def report_high_rated():
    """⭐ สินค้าคะแนนรีวิวเฉลี่ย ≥ 4 (HAVING)"""
    sql = """
    SELECT p.product_id as 'รหัสสินค้า', p.name as 'ชื่อสินค้า',
           ROUND(AVG(r.rating), 1) AS 'คะแนนเฉลี่ย',
           COUNT(*) AS 'จำนวนรีวิว'
    FROM review AS r
    INNER JOIN product AS p
        ON r.product_id = p.product_id
    GROUP BY p.product_id, p.name
    HAVING AVG(r.rating) >= 4
    ORDER BY 'คะแนนเฉลี่ย' DESC
    """
    return run_query(sql)


def summary_best_selling(filters):
    # range: 1d, 7d, 1m, 6m, 1y
    print(filters)
    _todo('Query Summary')


# ============================================================
#  รายการรายงานที่แสดงบนหน้า /report  (เรียงตามลำดับที่แสดง)
#  ★ วิธีเพิ่มรายงานใหม่ (ไม่ต้องแก้ไฟล์อื่น):
#    1) เขียนฟังก์ชัน report_xxx() ด้านบน ให้ return run_query(sql)
#    2) เพิ่ม 1 บรรทัดในรายการนี้:  ("ชื่อใน-url", "หัวข้อที่แสดง", ชื่อฟังก์ชัน)
#  ★ รายการนี้ต้องอยู่ท้ายไฟล์ (หลังฟังก์ชันทั้งหมด) ไม่งั้น Python หาชื่อฟังก์ชันไม่เจอ
#  ★ ห้ามตั้งชื่อ url ว่า "summary" (ใช้แล้วสำหรับการ์ดสรุป)
# ============================================================
REPORTS = [
    ("best-selling",  " สินค้าขายดี (Best Sellers) 📈",  report_best_selling),
    ("top-customers", " ลูกค้าที่ซื้อมากกว่าค่าเฉลี่ย (Above Average) 🏅",
     report_customers_above_avg),
    ("high-rated",    "⭐ สินค้าคะแนนรีวิวเฉลี่ย ≥ 4 (HAVING)", report_high_rated)
]

SUMMARY = [
    ("best-selling",  " สินค้าขายดี (Best Sellers) 📈", summary_best_selling),
]
