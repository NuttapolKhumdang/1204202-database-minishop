async function api(url) { return (await fetch(url)).json(); }
function fillTable(tableSel, statusSel, r, e = false) {
    const t = $(tableSel), st = $(statusSel);
    const thead = t.querySelector("thead"), tbody = t.querySelector("tbody");
    thead.innerHTML = ""; tbody.innerHTML = "";
    if (!r.ok) { st.className = "status " + (r.todo ? "todo" : "err"); st.textContent = (r.todo ? "🚧" : "⚠️ ") + r.error; return; }

    const rows = r.data || [];
    if (!rows.length) { st.className = "status"; st.textContent = "ไม่มีข้อมูล"; return; }
    st.textContent = "";

    console.log(rows);

    const cols = Object.keys(rows[0]);
    thead.innerHTML = "<tr>"
        + cols.map(c => "<th>" + c + "</th>").join("")
        + (e ? `<th>จัดการ</th>` : "")
        + "</tr>";

    tbody.innerHTML = rows.map(row => "<tr>"
        + cols.map(c => "<td>" + (row[c] ?? "—") + "</td>").join("")
        + (e ? `<td>
            <button class="btn sm" onclick="editRow(${row[ENTITIES.idKey]})">แก้ไข</button>
            <button class="btn sm del" onclick="deleteRow(${row[ENTITIES.idKey]})">ลบ</button>
            </td>` : "")
        + "</tr>").join("");
}

async function createTable(container, url, ediable = false) {
    fillTable('#' + container, "#" + container + "_status", await api(url), ediable);
}