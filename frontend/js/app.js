// Frontend tư vấn ngành nghề — gọi Backend FastAPI: GET /api/meta, POST /api/advise
const API = (window.API_BASE || "http://127.0.0.1:8000").replace(/\/$/, "");
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// Giá trị mặc định (lấy từ ví dụ trong notebook)
const DEF = {
  holland: { R: 3.4, I: 4.6, A: 2.5, S: 2.8, E: 3.1, C: 3.8 },
  hollandName: { R: "R - Thực tế", I: "I - Nghiên cứu", A: "A - Nghệ thuật", S: "S - Xã hội", E: "E - Quản lý", C: "C - Nghiệp vụ" },
  interest: { CNTT: 5, KTCN: 4, KHTN: 4, KTTCNH: 3, QTKD: 3, YDUOC: 2, SUPHAM: 2, NGOAINGU: 3, TT_NT: 2 },
  hb: { T: 8.8, V: 7.6, A: 8.2, L: 8.5, H: 8.0, I: 9.0, C: 8.4 },
  thi: { T: 8.5, V: 7.25, L: 8.25, I: 8.75 },
};

let META = null;

function setStatus(kind, text) {
  const el = $("status");
  el.className = "pill pill-" + kind;
  el.textContent = text;
}

function fillSelect(sel, items, selected) {
  sel.innerHTML = "";
  items.forEach(([value, label]) => {
    const o = document.createElement("option");
    o.value = value; o.textContent = label;
    if (value === selected) o.selected = true;
    sel.appendChild(o);
  });
}

function numField(id, label, value) {
  return `<label>${esc(label)}<input id="${id}" type="number" step="0.05" min="0" max="10" value="${value ?? ""}"></label>`;
}

function buildForm(meta) {
  fillSelect($("values"), meta.values.map((v) => [v, v]), "Thu nhập cao");
  fillSelect($("family"), [["Không", "Không"], ...meta.groups.map((g) => [g.code, `${g.code} - ${g.name}`])], "Không");
  fillSelect($("intent"), meta.groups.map((g) => [g.name, g.name]), meta.groups[0]?.name);

  $("holland").innerHTML = meta.holland.map((t) => `
    <label>${esc(DEF.hollandName[t] || t)}: <b id="hol_${t}_v">${DEF.holland[t]}</b>
      <input id="hol_${t}" type="range" min="1" max="5" step="0.1" value="${DEF.holland[t]}">
    </label>`).join("");
  meta.holland.forEach((t) => $("hol_" + t).addEventListener("input", (e) => ($("hol_" + t + "_v").textContent = e.target.value)));

  $("interest").innerHTML = meta.groups.map((g) => {
    const v = DEF.interest[g.code] ?? 3;
    return `<label title="${esc(g.name)}">${esc(g.name)}: <b id="qt_${g.code}_v">${v}</b>
      <input id="qt_${g.code}" type="range" min="1" max="5" step="1" value="${v}"></label>`;
  }).join("");
  meta.groups.forEach((g) => $("qt_" + g.code).addEventListener("input", (e) => ($("qt_" + g.code + "_v").textContent = e.target.value)));

  $("hb").innerHTML = meta.subjects.map((s) => numField("hb_" + s.code, "HB " + s.name, DEF.hb[s.code])).join("");
  $("thi").innerHTML = meta.subjects.map((s) => numField("thi_" + s.code, "Thi " + s.name, DEF.thi[s.code])).join("");

  ["budget", "the_luc"].forEach((id) => $(id).addEventListener("input", (e) => ($(id + "_v").textContent = e.target.value)));
  $("lop").addEventListener("change", syncGrade);
  syncGrade();

  const m = meta.metrics?.test;
  if (m) {
    $("metrics").hidden = false;
    $("metrics_body").innerHTML = `15 nhóm: top-1 <b>${m.group_top1}%</b>, top-3 <b>${m.group_top3}%</b><br>
      110 ngành: top-1 <b>${m.major_top1}%</b>, top-3 <b>${m.major_top3}%</b>, top-5 <b>${m.major_top5}%</b>`;
  }
}

function syncGrade() {
  const is12 = $("lop").value === "12";
  META.subjects.forEach((s) => ($("thi_" + s.code).disabled = !is12));
  $("dgnl").disabled = !is12;
}

// Ô trống / 0 / không hợp lệ -> null (môn không học / không thi)
function num(id) {
  const v = $(id).value.trim();
  if (v === "") return null;
  const n = parseFloat(v);
  return Number.isFinite(n) && n > 0 ? n : null;
}

function collectProfile() {
  const is12 = $("lop").value === "12";
  const profile = {
    lop: parseInt($("lop").value, 10),
    diem_uu_tien_khu_vuc: parseFloat($("kv").value),
    ngan_sach_hoc_phi_trieu_nam: parseFloat($("budget").value),
    uu_tien_dinh_huong: $("values").value,
    gia_dinh_goi_y_nhom_nganh: $("family").value,
    du_dinh_nhom_nganh_cua_hoc_sinh: $("intent").value,
    the_luc: parseInt($("the_luc").value, 10),
    ielts: num("ielts"),
    dgnl_hsa_150: is12 ? num("dgnl") : null,
    giai_hsg: $("hsg").value,
    holland: {}, quan_tam: {}, hb: {}, thi: {},
  };
  META.holland.forEach((t) => (profile.holland[t] = parseFloat($("hol_" + t).value)));
  META.groups.forEach((g) => (profile.quan_tam[g.code] = parseInt($("qt_" + g.code).value, 10)));
  META.subjects.forEach((s) => {
    profile.hb[s.code] = num("hb_" + s.code);
    profile.thi[s.code] = is12 ? num("thi_" + s.code) : null;
  });
  return profile;
}

function renderResult(res) {
  const t = res.top_majors[0];
  const pct = t.percentile_g12 != null ? `Top ${(100 - t.percentile_g12).toFixed(1)}%` : "Dành cho lớp 12";
  const groups = res.top_groups.map((g) => `
    <div class="row"><span>${g.rank}. ${esc(g.group_name)}</span><b>${g.confidence_pct}%</b>
      <div class="bar"><i style="width:${Math.min(100, g.confidence_pct)}%"></i></div></div>`).join("");
  const warns = res.warnings.length
    ? res.warnings.map((w) => `<div class="warn">⚠ ${esc(w)}</div>`).join("")
    : `<p class="muted">Không có cảnh báo.</p>`;
  const align = res.intention_aligned
    ? "Khớp định hướng cá nhân."
    : `Lệch định hướng (dự định: ${esc(res.student_intention)} · chuyên gia: ${esc(res.top_groups[0].group_name)}).`;
  const rows = res.top_majors.map((m, i) => `
    <tr><td>#${i + 1}</td><td><b>${esc(m.major_name)}</b><br><span class="muted">${esc(m.group_name)}</span></td>
      <td>${m.fit_score}</td><td>${esc(m.combo_code)}<br><span class="muted">${esc(m.combo_name)}</span></td>
      <td>${m.adj_score ?? "–"}</td><td>${m.dc_top} / ${m.dc_avg} / ${m.dc_basic}</td><td>${esc(m.feasibility)}</td></tr>`).join("");

  $("out").innerHTML = `
    <div class="hero">
      <div class="k">Ngành khuyến nghị số 1</div>
      <div class="v">${esc(t.major_name)}</div>
      <div class="muted">${esc(t.group_name)}</div>
      <div class="score">${t.fit_score}<small class="muted"> / 100</small></div>
    </div>
    <dl class="kv">
      <dt>Tổ hợp tối ưu</dt><dd>${esc(t.combo_code)} (${esc(t.combo_name)})</dd>
      <dt>Điểm sau ưu tiên</dt><dd>${t.adj_score ?? "–"} <span class="muted">(gốc ${t.raw_score ?? "–"})</span></dd>
      <dt>Bách phân vị</dt><dd>${pct}</dd>
      <dt>Khả thi 2026</dt><dd><span class="tag">${esc(t.feasibility)}</span>
        <span class="muted">ĐC Top ${t.dc_top} · TB ${t.dc_avg} · CB ${t.dc_basic}</span></dd>
      <dt>Phương thức</dt><dd>${esc(res.admission_method)}</dd>
      <dt>Định hướng</dt><dd>${align}</dd>
    </dl>
    <h3>Top 3 nhóm ngành</h3><div class="bars">${groups}</div>
    <h3>Cảnh báo chuyên gia</h3>${warns}
    <h3>Top 5 ngành khuyến nghị</h3>
    <div style="overflow-x:auto"><table>
      <thead><tr><th>Hạng</th><th>Ngành</th><th>Phù hợp</th><th>Tổ hợp</th><th>Điểm ƯT</th><th>ĐC Top/TB/CB</th><th>Khả thi</th></tr></thead>
      <tbody>${rows}</tbody></table></div>`;
}

async function onSubmit(e) {
  e.preventDefault();
  const btn = $("submit");
  btn.disabled = true; btn.textContent = "Đang tính…";
  try {
    const r = await fetch(`${API}/api/advise`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(collectProfile()),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}: ${(await r.text()).slice(0, 300)}`);
    renderResult(await r.json());
  } catch (err) {
    $("out").innerHTML = `<div class="err">Không gọi được backend (${esc(err.message)}).<br>
      Kiểm tra backend đang chạy tại <b>${esc(API)}</b>.</div>`;
  } finally {
    btn.disabled = false; btn.textContent = "Chạy tư vấn ngành nghề 2026";
  }
}

async function init() {
  $("form").addEventListener("submit", onSubmit);
  try {
    const r = await fetch(`${API}/api/meta`);
    if (!r.ok) throw new Error("HTTP " + r.status);
    META = await r.json();
    buildForm(META);
    setStatus("ok", `Backend OK · ${META.n_majors} ngành`);
    $("submit").disabled = false;
    $("form").requestSubmit();   // tự chạy 1 lần với dữ liệu mẫu
  } catch (err) {
    setStatus("bad", "Backend chưa chạy");
    $("submit").disabled = true;
    $("out").innerHTML = `<div class="err">Không kết nối được backend tại <b>${esc(API)}</b>.<br>
      Hãy chạy backend trước (xem README), sau đó tải lại trang.</div>`;
  }
}
init();
