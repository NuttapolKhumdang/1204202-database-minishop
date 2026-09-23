// ============================================================
//  app.js  —  ตรรกะหน้าเว็บ (ทำให้เสร็จแล้ว ★ นิสิตไม่ต้องแก้)
//  ปรับช่องค้นหา/ฟอร์มได้ที่ตัวแปร ENTITIES ด้านล่าง
// ============================================================
const ENTITIES = {
  "customers": {
    "label": "ลูกค้า",
    "api": "/api/customers",
    "idKey": "cust_id",
    "search": [
      {
        "key": "name",
        "label": "ชื่อ",
        "type": "text"
      },
      {
        "key": "email",
        "label": "อีเมล",
        "type": "text"
      },
      {
        "key": "tier",
        "label": "ระดับ",
        "type": "select",
        "options": [
          "",
          "normal",
          "vip"
        ]
      }
    ],
    "form": [
      {
        "key": "name",
        "label": "ชื่อ",
        "type": "text"
      },
      {
        "key": "email",
        "label": "อีเมล",
        "type": "text"
      },
      {
        "key": "address",
        "label": "ที่อยู่",
        "type": "text"
      },
      {
        "key": "tier",
        "label": "ระดับ",
        "type": "select",
        "options": [
          "normal",
          "vip"
        ]
      }
    ]
  },
  "products": {
    "label": "สินค้า",
    "api": "/api/products",
    "idKey": "product_id",
    "search": [
      {
        "key": "name",
        "label": "ชื่อสินค้า",
        "type": "text"
      },
      {
        "key": "category",
        "label": "หมวดหมู่",
        "type": "text"
      }
    ],
    "form": [
      {
        "key": "name",
        "label": "ชื่อสินค้า",
        "type": "text"
      },
      {
        "key": "category",
        "label": "หมวดหมู่",
        "type": "text"
      },
      {
        "key": "price",
        "label": "ราคา",
        "type": "number"
      },
      {
        "key": "stock",
        "label": "สต็อก",
        "type": "number"
      }
    ]
  },
  "orders": {
    "label": "ออเดอร์",
    "api": "/api/orders",
    "idKey": "order_id",
    "search": [
      {
        "key": "cust_id",
        "label": "รหัสลูกค้า",
        "type": "number"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "",
          "pending",
          "shipped"
        ]
      }
    ],
    "form": [
      {
        "key": "cust_id",
        "label": "รหัสลูกค้า",
        "type": "number"
      },
      {
        "key": "order_date",
        "label": "วันที่สั่ง",
        "type": "date"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "pending",
          "shipped"
        ]
      }
    ]
  }
};

let current = Object.keys(ENTITIES)[0];
let editingId = null;
const $ = (s) => document.querySelector(s);
function setStatus(el, msg, cls = "") { el.className = "status " + cls; el.textContent = msg; }
async function api(url, opts) { const res = await fetch(url, opts); return res.json(); }

function fieldHtml(f, prefix, value = "") {
  let input;
  if (f.type === "select") {
    input = '<select id="' + prefix + f.key + '">' +
      f.options.map(o => '<option value="' + o + '"' + (o === value ? " selected" : "") + '>' + (o || "ทั้งหมด") + '</option>').join("") + '</select>';
  } else { input = '<input id="' + prefix + f.key + '" type="' + f.type + '" value="' + (value ?? "") + '">'; }
  return '<div class="field"><label>' + f.label + '</label>' + input + '</div>';
}
function buildSearch() {
  const cfg = ENTITIES[current];
  $("#searchTitle").textContent = cfg.label;
  $("#searchFields").innerHTML = cfg.search.map(f => fieldHtml(f, "s_")).join("");
}
async function doSearch() {
  const cfg = ENTITIES[current];
  const params = new URLSearchParams();
  cfg.search.forEach(f => { const v = $("#s_" + f.key).value; if (v) params.append(f.key, v); });
  setStatus($("#status"), "กำลังค้นหา...");
  renderTable(await api(cfg.api + "?" + params.toString()));
}
function renderTable(r) {
  const head = $("#tableHead"), body = $("#tableBody"), st = $("#status");
  head.innerHTML = ""; body.innerHTML = "";
  if (!r.ok) { setStatus(st, (r.todo ? "🚧 " : "⚠️ ") + r.error, r.todo ? "todo" : "err"); return; }
  const rows = r.data || [];
  if (rows.length === 0) { setStatus(st, "ไม่พบข้อมูล"); return; }
  setStatus(st, "พบ " + rows.length + " รายการ");
  const cols = Object.keys(rows[0]);
  head.innerHTML = cols.map(c => "<th>" + c + "</th>").join("") + "<th>จัดการ</th>";
  body.innerHTML = rows.map(row => {
    const id = row[ENTITIES[current].idKey];
    return "<tr>" + cols.map(c => "<td>" + (row[c] ?? "—") + "</td>").join("") +
      '<td><button class="btn sm" onclick="editRow(' + id + ')">แก้ไข</button> ' +
      '<button class="btn sm del" onclick="deleteRow(' + id + ')">ลบ</button></td></tr>';
  }).join("");
}
function openForm(title, data = {}) {
  const cfg = ENTITIES[current];
  $("#modalTitle").textContent = title;
  $("#formFields").innerHTML = cfg.form.map(f => fieldHtml(f, "f_", data[f.key])).join("");
  $("#modal").classList.remove("hidden");
}
function collectForm() { const cfg = ENTITIES[current], d = {}; cfg.form.forEach(f => d[f.key] = $("#f_" + f.key).value); return d; }
async function editRow(id) {
  const cfg = ENTITIES[current];
  const r = await api(cfg.api + "/" + id);
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  editingId = id; openForm("แก้ไขข้อมูล", r.data);
}
async function deleteRow(id) {
  if (!confirm("ยืนยันการลบ?")) return;
  const r = await api(ENTITIES[current].api + "/" + id, { method: "DELETE" });
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  doSearch();
}
async function save() {
  const cfg = ENTITIES[current], data = collectForm();
  const opts = { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) };
  const r = await api(editingId ? cfg.api + "/" + editingId : cfg.api, opts);
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  $("#modal").classList.add("hidden"); doSearch();
}
document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  t.classList.add("active"); current = t.dataset.entity;
  buildSearch(); $("#tableHead").innerHTML = ""; $("#tableBody").innerHTML = "";
  setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');
}));
$("#btnSearch").onclick = doSearch;
$("#btnClear").onclick = () => buildSearch();
$("#btnAdd").onclick = () => { editingId = null; openForm("เพิ่มข้อมูลใหม่"); };
$("#btnSave").onclick = save;
$("#btnCancel").onclick = () => $("#modal").classList.add("hidden");
buildSearch();
setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');
