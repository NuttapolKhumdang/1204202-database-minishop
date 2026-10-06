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
from decimal import Decimal, InvalidOperation
import mysql.connector
import config


def get_connection():
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
    """แปลง error ของ MySQL ที่เจอบ่อยให้เป็น ValueError ภาษาไทย
    (app.py จะส่งข้อความนี้ไปแสดงบนหน้าเว็บ) — คืน None ถ้าเป็น error ที่ไม่รู้จัก"""
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
    if err.errno == 1406:      # ข้อความยาวเกินขนาดคอลัมน์ (เช่น tier / postal_code เป็น VARCHAR(6))
        m = re.search(r"column '(\w+)'", err.msg or "")
        return ValueError(f"ข้อมูลในช่อง '{m.group(1) if m else ''}' ยาวเกินที่กำหนด")
    return None


def run_transaction(work):
    """รันหลายคำสั่งเป็น transaction เดียว: work(cur) จะทำกี่คำสั่งก็ได้
    จบปกติ → commit / เกิด error → rollback ทั้งหมด (ใช้ตอนต้องเขียนหลายตารางพร้อมกัน เช่น customer + address)"""
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
    """ช่องที่ไม่ได้กรอกในฟอร์มจะส่งมาเป็น "" — แปลงเป็น None (= NULL ใน SQL)
    ใช้กับคอลัมน์ที่ว่างได้ เช่น return_date, paid_date  เพราะ MySQL ไม่รับ '' เป็น DATE"""
    return None if value in ("", None) else value


def _todo(name):
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


def _text(value):
    """ข้อความที่ตัดช่องว่างหัวท้ายแล้ว (ว่าง → None)"""
    return None if value is None else blank_to_none(str(value).strip())


def _money(value, default: Decimal | int | str = 0):
    """แปลงค่าที่ส่งมาเป็นตัวเลขทศนิยม (ว่าง → default)"""
    value = blank_to_none(value)
    if value is None:
        if default is None:
            return Decimal("0")
        return Decimal(str(default))
    try:
        return Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"ตัวเลขไม่ถูกต้อง: {value}")


def _build_set(data, skip_blank=(), blank_to_null=()):
    """สร้างส่วน SET ของ UPDATE เฉพาะคอลัมน์ที่ส่งมาใน data → คืน ("a=%s, b=%s", [ค่า a, ค่า b])
      skip_blank   : คอลัมน์ NOT NULL — ถ้าส่งมาเป็นช่องว่างให้ข้าม (ไม่แก้ค่าเดิม)
      blank_to_null: คอลัมน์ที่ว่างได้ — ถ้าส่งมาเป็นช่องว่างให้ตั้งเป็น NULL
    ชื่อคอลัมน์มาจากรายการในโค้ดเท่านั้น (ไม่ได้มาจากผู้ใช้) ส่วนค่าส่งผ่าน %s ตามปกติ จึงปลอดภัย"""
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
# 1 ลูกค้ามีได้หลายที่อยู่ (ตาราง address) — หน้าเว็บแสดง/แก้ "ที่อยู่แรก" (address_id ต่ำสุด) ของลูกค้า
_FIRST_ADDRESS = "a.address_id = (SELECT MIN(a2.address_id) FROM address a2 WHERE a2.cust_id = c.cust_id)"
_ADDRESS_TEXT = "CONCAT_WS(' ', a.line_1, a.line_2, a.province, a.postal_code)"
_ADDRESS_RE = re.compile(r"^(?P<line_1>.+?)\s+(?P<province>\S+)\s+(?P<postal_code>\d{5})$")


def _address_from(data, old=None):
    """อ่านที่อยู่จาก data เพื่อบันทึกลงตาราง address — รับได้ 2 แบบ
      1) แยกช่อง : line_1, line_2, province, postal_code (+ address_type)
      2) ช่องเดียว: address เช่น "99 ถ.สุขุมวิท กรุงเทพฯ 10110"
         (แยก 'จังหวัด รหัสไปรษณีย์' จากท้ายข้อความให้ — ตรงกับที่หน้ารายการลูกค้าแสดง)
    old = แถวที่อยู่เดิมของลูกค้า (ใช้ตอนแก้ไข) เอาไว้เทียบว่าช่องไหน "เปลี่ยนจริง"
    คืน dict (line_1, line_2, province, postal_code, address_type)
    หรือ None = ไม่ต้องแตะที่อยู่ (ไม่ได้กรอก / ไม่ได้เปลี่ยนจากเดิม จึงไม่ต้องบันทึกซ้ำ)"""
    address_type = _text(data.get("address_type"))
    line_1 = _text(data.get("line_1"))
    province = _text(data.get("province"))
    postal_code = _text(data.get("postal_code"))

    if line_1 or province or postal_code:                     # แบบที่ 1: แยกช่อง
        if not (line_1 and province and postal_code):
            raise ValueError("กรุณากรอกที่อยู่ จังหวัด และรหัสไปรษณีย์ให้ครบ")
        new = {"line_1": line_1, "line_2": _text(data.get("line_2")), "province": province,
               "postal_code": postal_code, "address_type": address_type}
        if not old or any(new[k] != old[k] for k in ("line_1", "line_2", "province", "postal_code")):
            return new
        # แยกช่องไม่ต่างจากเดิม → ไปดูต่อว่าช่อง address (ข้อความรวม) ถูกแก้หรือเปล่า

    text = " ".join(str(data.get("address") or "").split())   # แบบที่ 2: ช่องเดียว (ยุบช่องว่างซ้ำ)
    if not text or (old and text == " ".join(old["text"].split())):
        return None
    m = _ADDRESS_RE.match(text)
    if not m:
        raise ValueError('รูปแบบที่อยู่ไม่ถูกต้อง ต้องลงท้ายด้วย "จังหวัด รหัสไปรษณีย์ 5 หลัก" '
                         'เช่น 99 ถ.สุขุมวิท กรุงเทพฯ 10110')
    return {"line_1": m["line_1"], "line_2": None, "province": m["province"],
            "postal_code": m["postal_code"], "address_type": address_type}


def search_customers(filters):
    # JOIN ตาราง address เพื่อดึง line_1, province, postal_code ออกมาแสดงเป็น 'ที่อยู่'
    # (JOIN เฉพาะ "ที่อยู่แรก" ของลูกค้า — ลูกค้าที่มีหลายที่อยู่จะได้ไม่ขึ้นซ้ำหลายแถว)
    # ★ รายการลูกค้าต้องใช้ชื่อคอลัมน์ภาษาอังกฤษ (cust_id, name, email, address, tier) ห้ามตั้ง alias ภาษาไทย
    #   เพราะหน้าเว็บอ่านค่าตามชื่อคีย์เหล่านี้ — cust_id ใช้สร้าง URL ตอนกดแก้ไข/ลบ (/api/customers/<cust_id>)
    #   และ name เป็นข้อความในช่องเลือก "ลูกค้า" ของฟอร์มออเดอร์ (ดึงรายชื่อจาก /api/customers)
    #   ถ้าหาคีย์ไม่เจอ หน้าเว็บจะขึ้นเป็น undefined
    sql = f"""
        SELECT c.cust_id,
               c.name,
               c.email,
               {_ADDRESS_TEXT} AS address,
               c.tier
        FROM customer c
        LEFT JOIN address a ON {_FIRST_ADDRESS}
        WHERE 1=1
    """
    params = []

    if filters.get("name"):
        sql += " AND c.name LIKE %s"
        params.append("%" + filters["name"] + "%")

    if filters.get("email"):
        sql += " AND c.email LIKE %s"
        params.append("%" + filters["email"] + "%")

    if filters.get("address"):
        sql += (" AND (a.line_1 LIKE %s OR a.line_2 LIKE %s"
                " OR a.province LIKE %s OR a.postal_code LIKE %s)")
        search_addr = "%" + filters["address"] + "%"
        params.extend([search_addr] * 4)

    if filters.get("tier"):
        sql += " AND c.tier = %s"
        params.append(filters["tier"])

    sql += " ORDER BY c.cust_id"
    return run_query(sql, tuple(params))


def get_customer(cust_id):
    """ข้อมูลลูกค้า + ที่อยู่แรก  (address = ข้อความรวม 'ที่อยู่ จังหวัด รหัสไปรษณีย์' ใช้เติมช่องในฟอร์ม)"""
    sql = f"""
        SELECT c.*, a.address_id, a.address_type, a.line_1, a.line_2, a.province, a.postal_code,
               {_ADDRESS_TEXT} AS address
        FROM customer c
        LEFT JOIN address a ON {_FIRST_ADDRESS}
        WHERE c.cust_id = %s
    """
    rows = run_query(sql, (cust_id,))
    return rows[0] if rows else None


def create_customer(data):
    """INSERT customer แล้ว INSERT address (ถ้ากรอกที่อยู่) ใน transaction เดียว"""
    name, email = _text(data.get("name")), _text(data.get("email"))
    if not name or not email:
        raise ValueError("กรุณากรอกชื่อและอีเมลของลูกค้า")
    addr = _address_from(data)          # ตรวจรูปแบบที่อยู่ก่อนเริ่มบันทึก

    def work(cur):
        cur.execute(
            "INSERT INTO customer (name, email, gender, birthdate, tier) VALUES (%s, %s, %s, %s, %s)",
            (name, email, blank_to_none(data.get("gender")), blank_to_none(data.get("birthdate")),
             blank_to_none(data.get("tier")) or "normal"))
        cust_id = cur.lastrowid
        if addr:
            cur.execute(
                "INSERT INTO address (cust_id, address_type, line_1, line_2, province, postal_code) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (cust_id, addr["address_type"] or "shipping", addr["line_1"], addr["line_2"],
                 addr["province"], addr["postal_code"]))
        return {"new_id": cust_id, "affected": 1}

    return run_transaction(work)


def update_customer(cust_id, data):
    """UPDATE customer (เฉพาะช่องที่ส่งมา) และ UPDATE/INSERT ที่อยู่แรก ใน transaction เดียว"""
    sets, params = _build_set(data, skip_blank=("name", "email", "tier"),
                              blank_to_null=("gender", "birthdate"))

    def work(cur):
        cur.execute("SELECT cust_id FROM customer WHERE cust_id = %s", (cust_id,))
        if not cur.fetchall():
            raise ValueError(f"ไม่พบลูกค้ารหัส {cust_id}")
        affected = 0
        if sets:
            cur.execute(f"UPDATE customer SET {sets} WHERE cust_id=%s", (*params, cust_id))
            affected += cur.rowcount

        cur.execute(f"SELECT a.address_id, a.line_1, a.line_2, a.province, a.postal_code, "
                    f"{_ADDRESS_TEXT} AS text FROM address a "
                    "WHERE a.cust_id = %s ORDER BY a.address_id LIMIT 1", (cust_id,))
        old = cur.fetchone()
        addr = _address_from(data, old)
        if addr and old:
            cur.execute(
                "UPDATE address SET address_type=COALESCE(%s, address_type), line_1=%s, line_2=%s, "
                "province=%s, postal_code=%s WHERE address_id=%s",
                (addr["address_type"], addr["line_1"], addr["line_2"],
                 addr["province"], addr["postal_code"], old["address_id"]))
            affected += cur.rowcount
        elif addr:                      # ลูกค้ายังไม่มีที่อยู่เลย → เพิ่มใหม่
            cur.execute(
                "INSERT INTO address (cust_id, address_type, line_1, line_2, province, postal_code) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (cust_id, addr["address_type"] or "shipping", addr["line_1"], addr["line_2"],
                 addr["province"], addr["postal_code"]))
            affected += cur.rowcount
        return {"new_id": None, "affected": affected}

    return run_transaction(work)


def delete_customer(cust_id):
    # address ถูกลบตามอัตโนมัติ (ON DELETE CASCADE) แต่ถ้าลูกค้ามีออเดอร์/รีวิวอยู่ จะลบไม่ได้ (FK)
    return run_command("DELETE FROM customer WHERE cust_id=%s", (cust_id,))


# ---------- สินค้า (product) ----------
def _category_id(value):
    """product.category เป็น FK → primary_category
    รับได้ทั้งรหัส (เช่น 5) หรือชื่อ (เช่น 'Electronics') แล้วคืนรหัสหมวดหมู่ (ว่าง → None)"""
    value = _text(value)
    if value is None:
        return None
    if value.isdigit():
        return int(value)
    rows = run_query("SELECT category_id FROM primary_category WHERE name = %s", (value,))
    if not rows:
        raise ValueError(f"ไม่พบหมวดหมู่ '{value}'")
    return rows[0]["category_id"] # type: ignore


def search_products(filters):
    # JOIN primary_category เพื่อแสดง 'ชื่อ' หมวดหมู่ (ในตาราง product เก็บเป็นรหัส)
    # ★ คอลัมน์รหัส (product_id) ต้องใช้ชื่อจริงของคอลัมน์ ห้ามตั้ง alias ภาษาไทย
    #   เพราะหน้าเว็บอ่านค่านี้ไปสร้าง URL ตอนกดแก้ไข/ลบ (/api/products/<product_id>)
    #   ถ้าหาไม่เจอจะได้ /api/products/undefined (404)
    sql = """
        SELECT p.product_id, p.name AS 'ชื่อสินค้า',
               pc.name AS 'หมวดหมู่', p.price AS 'ราคา', p.stock AS 'จำนวนคงเหลือ'
        FROM product p
        LEFT JOIN primary_category pc ON p.category = pc.category_id
        WHERE 1=1
    """
    params = []
    if filters.get("name"):
        sql += " AND p.name LIKE %s"
        params.append("%" + filters["name"] + "%")

    if filters.get("category"):            # กรองด้วยรหัสหรือชื่อหมวดหมู่ก็ได้
        if str(filters["category"]).isdigit():
            sql += " AND p.category = %s"
        else:
            sql += " AND pc.name = %s"
        params.append(filters["category"])

    if filters.get("min_price"):
        sql += " AND p.price >= %s"
        params.append(filters["min_price"])

    if filters.get("max_price"):
        sql += " AND p.price <= %s"
        params.append(filters["max_price"])

    sql += " ORDER BY p.product_id"
    return run_query(sql, tuple(params))


def get_product(product_id):
    # category = รหัสหมวดหมู่ (เหมือนในตาราง), category_name = ชื่อหมวดหมู่
    sql = """
        SELECT p.*, pc.name AS category_name
        FROM product p
        LEFT JOIN primary_category pc ON p.category = pc.category_id
        WHERE p.product_id = %s
    """
    rows = run_query(sql, (product_id,))
    return rows[0] if rows else None


def create_product(data):
    name = _text(data.get("name"))
    if not name:
        raise ValueError("กรุณากรอกชื่อสินค้า")
    sql = "INSERT INTO product (name, category, price, stock) VALUES (%s, %s, %s, %s)"
    params = (name, _category_id(data.get("category")),
              blank_to_none(data.get("price")) or 0, blank_to_none(data.get("stock")) or 0)
    return run_command(sql, params)


def update_product(product_id, data):
    data = dict(data)
    if "category" in data:
        data["category"] = _category_id(data["category"])
    sets, params = _build_set(data, skip_blank=("name", "price", "stock"),
                              blank_to_null=("category",))
    if not sets:
        return {"new_id": None, "affected": 0}
    return run_command(f"UPDATE product SET {sets} WHERE product_id=%s", (*params, product_id))


def delete_product(product_id):
    # สินค้าที่เคยถูกสั่งซื้อ (มีใน order_line) จะลบไม่ได้ (FK) — ถ้าไม่อยากให้ขายอีก ให้ตั้ง is_active = FALSE แทน
    return run_command("DELETE FROM product WHERE product_id=%s", (product_id,))


# ---------- ออเดอร์ (shop_order) ----------
def search_orders(filters):
    # ★ คอลัมน์รหัส (order_id) ต้องใช้ชื่อจริงของคอลัมน์ ห้ามตั้ง alias ภาษาไทย
    #   เพราะหน้าเว็บอ่านค่านี้ไปสร้าง URL ตอนกดแก้ไข/ลบ (/api/orders/<order_id>)
    #   ถ้าหาไม่เจอจะได้ /api/orders/undefined (404)
    sql = "SELECT order_id, cust_id as 'รหัสลูกค้า', " \
          "order_date as 'วันที่สั่งซื้อ', status as 'สถานะ', total as 'ยอดสุทธิ' " \
          "FROM shop_order WHERE 1=1"
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

    sql += " ORDER BY order_id"
    return run_query(sql, tuple(params))


def get_order(order_id):
    sql = "SELECT * FROM shop_order WHERE order_id = %s"
    rows = run_query(sql, (order_id,))
    return rows[0] if rows else None


def check_can_ship(order_id):
    """ตรวจว่าออเดอร์จัดส่งได้ไหม → คืน (True/False, ข้อความ)
    เงื่อนไข: มีออเดอร์นี้ / สถานะต้องเป็น pending / มีรายการสินค้าอย่างน้อย 1 รายการ /
              สินค้าทุกรายการยังเปิดขาย (is_active) และ stock พอตามจำนวนที่สั่ง"""
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

    problems = [f"{l['name']} (สั่ง {l['qty']} / คงเหลือ {l['stock'] or 0})" # type: ignore
                for l in lines
                if l["is_active"] == 0 or (l["stock"] or 0) < l["qty"]]  # type: ignore
    if problems:
        return False, "ออเดอร์นี้ไม่สามารถจัดส่งได้ (สินค้าไม่พร้อม: " + ", ".join(problems) + ")"
    return True, "จัดส่งได้"


def create_order(data):
    # sub_total / discount / total เป็น NOT NULL และไม่มีค่า default → ต้องส่งค่าเสมอ
    # (ไม่ได้กรอกมา = 0, ออเดอร์ใหม่ยังไม่มีรายการสินค้า) / ไม่กรอกวันที่ = วันนี้ / ไม่กรอกสถานะ = pending
    # ไม่กรอกที่อยู่จัดส่ง = ใช้ที่อยู่แรกของลูกค้าคนนั้น
    cust_id = blank_to_none(data.get("cust_id"))
    if cust_id is None:
        raise ValueError("กรุณาระบุรหัสลูกค้า")
    sub_total = _money(data.get("sub_total"))
    discount = _money(data.get("discount"))
    total = _money(data.get("total"), default=sub_total - discount)

    sql = """
        INSERT INTO shop_order (cust_id, order_date, status, address, sub_total, discount, total)
        VALUES (%s, COALESCE(%s, CURRENT_DATE), COALESCE(%s, 'pending'),
                COALESCE(%s, (SELECT MIN(address_id) FROM address WHERE cust_id = %s)),
                %s, %s, %s)
    """
    params = (cust_id, blank_to_none(data.get("order_date")), blank_to_none(data.get("status")),
              blank_to_none(data.get("address")), cust_id, sub_total, discount, total)
    return run_command(sql, params)


def update_order(order_id, data):
    current = get_order(order_id)
    if not current:
        raise ValueError(f"ไม่พบออเดอร์รหัส {order_id}")
    if not isinstance(current, dict):
        raise ValueError(f"ข้อมูลออเดอร์รหัส {order_id} ไม่ถูกต้อง")

    # เปลี่ยนสถานะเป็น shipped ต้องผ่านการตรวจสต็อกก่อน (ดู check_can_ship)
    current_status = current.get("status")
    if blank_to_none(data.get("status")) == "shipped" and current_status != "shipped":
        ok, msg = check_can_ship(order_id)
        if not ok:
            raise ValueError(msg)

    # อัปเดตเฉพาะช่องที่ส่งมา (ช่องว่าง = ไม่แก้)
    sets, params = _build_set(data, skip_blank=("cust_id", "order_date", "status", "address",
                                                "sub_total", "discount", "total"))
    if not sets:
        return {"new_id": None, "affected": 0}
    return run_command(f"UPDATE shop_order SET {sets} WHERE order_id=%s", (*params, order_id))


def delete_order(order_id):
    # รายการสินค้า (order_line) เป็นส่วนหนึ่งของออเดอร์ → ลบพร้อมกันใน transaction เดียว
    # แต่ถ้าออเดอร์มีการชำระเงิน/รีวิวอยู่ จะลบไม่ได้ (FK) และ rollback ทั้งหมด
    def work(cur):
        cur.execute("DELETE FROM order_line WHERE order_id=%s", (order_id,))
        cur.execute("DELETE FROM shop_order WHERE order_id=%s", (order_id,))
        return {"new_id": None, "affected": cur.rowcount}
    return run_transaction(work)


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ — ใช้ AS 'ชื่อภาษาไทย' ได้
#  ★ ORDER BY ชื่อ alias ต้องครอบด้วย backtick (`ชื่อ`) ห้ามใช้ 'ชื่อ' เพราะ MySQL จะมองเป็นข้อความคงที่ (ไม่เรียงจริง)
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
    SELECT p.product_id as 'รหัสสินค้า', p.name as 'ชื่อสินค้า', pc.name as 'หมวดหมู่',
           SUM(ol.qty) AS 'จำนวนที่ขาย',
           SUM(ol.qty * ol.unit_price) AS 'ยอดขายรวม'
    FROM order_line AS ol
    INNER JOIN product AS p ON ol.product_id = p.product_id
    LEFT JOIN primary_category AS pc ON p.category = pc.category_id
    GROUP BY p.product_id, p.name, pc.name
    ORDER BY `จำนวนที่ขาย` DESC, p.product_id
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
    ORDER BY `ยอดซื้อรวม` DESC
    """
    return run_query(sql)


def report_high_rated():
    """⭐ สินค้าคะแนนรีวิวเฉลี่ย ≥ 4 (HAVING)
    (review ผูกกับ 'ออเดอร์' → คะแนนของออเดอร์นั้นนับให้ทุกสินค้าในออเดอร์ผ่าน order_line)"""
    sql = """
    SELECT p.product_id as 'รหัสสินค้า', p.name as 'ชื่อสินค้า',
           ROUND(AVG(r.rating), 1) AS 'คะแนนเฉลี่ย',
           COUNT(r.rating) AS 'จำนวนรีวิว'
    FROM review AS r
    INNER JOIN order_line AS ol
        ON r.order_id = ol.order_id
    INNER JOIN product AS p
        ON ol.product_id = p.product_id
    GROUP BY p.product_id, p.name
    HAVING AVG(r.rating) >= 4
    ORDER BY `คะแนนเฉลี่ย` DESC
    """
    return run_query(sql)


def summary_best_selling(filters):
    # range: 1d, 7d, 1m, 6m, 1y
    range_val = filters.get("range") if isinstance(filters, dict) else filters

    # แมปช่วงเวลาเป็น SQL INTERVAL
    interval_map = {
        "1d": "1 DAY",
        "7d": "7 DAY",
        "1m": "1 MONTH",
        "6m": "6 MONTH",
        "1y": "1 YEAR"
    }

    sql = """
    SELECT p.product_id AS 'รหัสสินค้า',
           p.name AS 'ชื่อสินค้า',
           pc.name AS 'หมวดหมู่',
           SUM(ol.qty) AS 'จำนวนที่ขาย',
           SUM(ol.qty * ol.unit_price) AS 'ยอดขายรวม'
    FROM order_line AS ol
    INNER JOIN product AS p ON ol.product_id = p.product_id
    INNER JOIN shop_order AS so ON ol.order_id = so.order_id
    LEFT JOIN primary_category AS pc ON p.category = pc.category_id
    WHERE 1=1
    """
    params = []

    if range_val in interval_map:
        sql += f" AND so.order_date >= CURRENT_DATE - INTERVAL {interval_map[range_val]}"

    sql += """
    GROUP BY p.product_id, p.name, pc.name
    ORDER BY SUM(ol.qty) DESC, p.product_id
    LIMIT 5
    """

    return run_query(sql, tuple(params))

def summary_customers_above_avg(filters):
    # range: 1d, 7d, 1m, 6m, 1y
    range_val = filters.get("range") if isinstance(filters, dict) else filters

    # แมปช่วงเวลาเป็น SQL INTERVAL
    interval_map = {
        "1d": "1 DAY",
        "7d": "7 DAY",
        "1m": "1 MONTH",
        "6m": "6 MONTH",
        "1y": "1 YEAR"
    }

    interval = None
    if range_val in interval_map:
        interval = interval_map[range_val]

    sql = f"""
     SELECT c.cust_id as 'รหัสลูกค้า', c.name as 'ชื่อลูกค้า',
           SUM(ol.qty * ol.unit_price) AS 'ยอดซื้อรวม'
    FROM customer AS c
    INNER JOIN shop_order AS so
        ON c.cust_id = so.cust_id
    INNER JOIN order_line AS ol
        ON so.order_id = ol.order_id
    WHERE so.order_date >= CURRENT_DATE - INTERVAL {interval}
    GROUP BY c.cust_id, c.name
    HAVING SUM(ol.qty * ol.unit_price) > (
        SELECT AVG(customer_total)
        FROM (
            SELECT SUM(ol2.qty * ol2.unit_price) AS customer_total
            FROM shop_order AS so2
            INNER JOIN order_line AS ol2
                ON so2.order_id = ol2.order_id
            WHERE so2.order_date >= CURRENT_DATE - INTERVAL {interval}
            GROUP BY so2.cust_id
        ) AS totals
    )
    ORDER BY `ยอดซื้อรวม` DESC
    """

    return run_query(sql)


def summary_high_rated(filters):
    range_val = filters.get("range") if isinstance(filters, dict) else filters

    # แมปช่วงเวลาเป็น SQL INTERVAL
    interval_map = {
        "1d": "1 DAY",
        "7d": "7 DAY",
        "1m": "1 MONTH",
        "6m": "6 MONTH",
        "1y": "1 YEAR"
    }

    interval = None
    if range_val in interval_map:
        interval = interval_map[range_val]

    sql = f"""
    SELECT p.product_id as 'รหัสสินค้า', p.name as 'ชื่อสินค้า',
           ROUND(AVG(r.rating), 1) AS 'คะแนนเฉลี่ย',
           COUNT(r.rating) AS 'จำนวนรีวิว'
    FROM review AS r
    INNER JOIN order_line AS ol
        ON r.order_id = ol.order_id
    INNER JOIN product AS p
        ON ol.product_id = p.product_id
    WHERE r.review_date >= CURRENT_DATE - INTERVAL {interval}
    GROUP BY p.product_id, p.name
    HAVING AVG(r.rating) >= 4
    ORDER BY `คะแนนเฉลี่ย` DESC
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
REPORTS = [
    ("best-selling",  " สินค้าขายดี (Best Sellers) 📈",  report_best_selling),
    ("top-customers", " ลูกค้าที่ซื้อมากกว่าค่าเฉลี่ย (Above Average) 🏅",
     report_customers_above_avg),
    ("high-rated",    "⭐ สินค้าคะแนนรีวิวเฉลี่ย ≥ 4 (HAVING)", report_high_rated)
]

SUMMARY = [
    ("best-selling",  " สินค้าขายดี (Best Sellers) 📈", summary_best_selling),
    ("top-customers", " ลูกค้าที่ซื้อมากกว่าค่าเฉลี่ย (Above Average) 🏅",
         summary_customers_above_avg),
        ("high-rated",    "⭐ สินค้าคะแนนรีวิวเฉลี่ย ≥ 4 (HAVING)", summary_high_rated)
]
