// ============================================================
//  app.js  —  ตรรกะหน้าเว็บ (ทำให้เสร็จแล้ว ★ นิสิตไม่ต้องแก้)
//  ปรับช่องค้นหา/ฟอร์มได้ที่ตัวแปร ENTITIES ด้านล่าง
// ============================================================
// ★ ตัวอย่าง dropdown ที่อ่านข้อมูลจากฐานข้อมูล: ฟอร์ม "ออเดอร์" ช่อง cust_id
//   แสดง name แต่ส่งค่าเป็น cust_id (อ่านรายการจาก /api/customers)
//   ช่อง FK อื่น ๆ ทำแบบเดียวกันได้ — เปลี่ยน "type": "number" เป็น select + optionsFrom

let current = Object.keys(ENTITIES);
let editingId = null;
function setStatus(el, msg, cls = "") { el.className = "status " + cls; el.textContent = msg; }
async function api(url, opts) { const res = await fetch(url, opts); return res.json(); }

function fieldHtml(f, prefix, value = "") {
    if (f.type === "heading") return '<div class="form-section">' + f.label + '</div>';
    let input;
    if (f.type === "select") {
        // options เป็นข้อความ "a" หรือ {value, label} ก็ได้
        input = '<select id="' + prefix + f.key + '">' +
            f.options.map(o => {
                const v = typeof o === "object" ? o.value : o;
                const t = typeof o === "object" ? o.label : (o || "ทั้งหมด");
                return '<option value="' + v + '"' + (String(v) === String(value ?? "") ? " selected" : "") + '>' + t + '</option>';
            }).join("") + '</select>';
    } else { input = '<input id="' + prefix + f.key + '" type="' + f.type + '" value="' + (value ?? "") + '">'; }
    return '<div class="field"><label>' + f.label + '</label>' + input + '</div>';
}
// ช่อง select ที่มี optionsFrom → ดึงตัวเลือกจาก API (เช่น รายชื่อหมวดหมู่จากฐานข้อมูล)
async function loadOptions(fields, forSearch) {
    for (const f of fields.filter(f => f.optionsFrom)) {
        const src = f.optionsFrom, r = await api(src.api);
        f.options = r.ok ? (r.data || []).map(row => ({ value: row[src.value], label: row[src.label] }))
            : [{ value: "", label: (r.todo ? "🚧 " : "⚠️ ") + r.error }];
        if (forSearch && r.ok) f.options.unshift({ value: "", label: "ทั้งหมด" });
    }
}
// ช่องในฟอร์มที่ใช้อยู่ตอนนี้ (ช่อง editOnly แสดงเฉพาะตอนแก้ไข)
function formFields() { return ENTITIES.form.filter(f => !f.editOnly || editingId !== null); }

async function openForm(title, data = {}) {
    await loadOptions(formFields(), false);
    $("#modalTitle").textContent = title;
    $("#formFields").innerHTML = formFields().map(f => fieldHtml(f, "f_", data[f.key])).join("");
    $("#modal").classList.remove("hidden");
}
function collectForm() { const d = {}; formFields().filter(f => f.key).forEach(f => d[f.key] = $("#f_" + f.key).value); return d; }
async function editRow(id) {
    const cfg = ENTITIES;
    const r = await api(cfg.api + "/" + id);
    if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
    editingId = id; openForm("แก้ไขข้อมูล", r.data);
}
async function deleteRow(id) {
    if (!confirm("ยืนยันการลบ?")) return;
    const r = await api(ENTITIES.api + "/" + id, { method: "DELETE" });
    if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }

    window.location.reload();
}
async function save() {
    const cfg = ENTITIES, data = collectForm();
    const opts = { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) };
    const r = await api(editingId ? cfg.api + "/" + editingId : cfg.api, opts);
    if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
    $("#modal").classList.add("hidden");

    window.location.reload();
}

$("#btnAdd").onclick = () => { editingId = null; openForm("เพิ่มข้อมูลใหม่"); };
$("#btnSave").onclick = save;
$("#btnCancel").onclick = () => $("#modal").classList.add("hidden");
