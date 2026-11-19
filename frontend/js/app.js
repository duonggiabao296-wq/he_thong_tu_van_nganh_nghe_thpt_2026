let META = null;

const HOLLAND_LABELS = {
  R: "R - Kỹ thuật / Thực tế",
  I: "I - Nghiên cứu",
  A: "A - Nghệ thuật",
  S: "S - Xã hội",
  E: "E - Quản lý / Kinh doanh",
  C: "C - Nghiệp vụ",
};

function setStatus(ok, text) {
  const el = document.getElementById("statusBadge");
  el.className = "badge " + (ok ? "ok" : "err");
  el.textContent = text;
  document.getElementById("submitBtn").disabled = !ok;
}

function buildSliders(meta) {
  const hBox = document.getElementById("hollandContainer");
  hBox.innerHTML = Object.entries(HOLLAND_LABELS).map(([k, label]) => `
    <div>
      <label>${label}: <span id="val_h_${k}">3.5</span></label>
      <input type="range" id="h_${k}" min="1" max="5" step="0.1" value="${k === "I" ? 4.6 : 3.0}"
             oninput="document.getElementById('val_h_${k}').textContent=this.value" />
    </div>
  `).join("");
  Object.keys(HOLLAND_LABELS).forEach(k => {
    document.getElementById(`val_h_${k}`).textContent = document.getElementById(`h_${k}`).value;
  });

  const qBox = document.getElementById("quanTamContainer");
  qBox.innerHTML = meta.groups.map(g => `
    <div>
      <label>${g.name}: <span id="val_qt_${g.code}">${g.code === "CNTT" ? 5 : 3}</span></label>
      <input type="range" id="qt_${g.code}" min="1" max="5" step="1" value="${g.code === "CNTT" ? 5 : 3}"
             oninput="document.getElementById('val_qt_${g.code}').textContent=this.value" />
    </div>
  `).join("");

  const defaultsHB = { T: 8.8, V: 7.6, A: 8.2, L: 8.5, H: 8.0, I: 9.0, C: 8.4 };
  const defaultsThi = { T: 8.5, V: 7.25, L: 8.25, I: 8.75 };

  document.getElementById("hbContainer").innerHTML = meta.subjects.map(s => `
    <div><label>${s.name}</label><input type="number" step="0.1" min="0" max="10" id="hb_${s.code}" value="${defaultsHB[s.code] ?? ""}" /></div>
  `).join("");

  document.getElementById("thiContainer").innerHTML = meta.subjects.map(s => `
    <div><label>${s.name}</label><input type="number" step="0.25" min="0" max="10" id="thi_${s.code}" value="${defaultsThi[s.code] ?? ""}" /></div>
  `).join("");
}

function collectProfile() {
  const numOrNull = (id) => {
    const v = document.getElementById(id).value;
    return v === "" ? null : parseFloat(v);
  };
  const holland = {};
  Object.keys(HOLLAND_LABELS).forEach(k => holland[k] = parseFloat(document.getElementById(`h_${k}`).value));
  const quan_tam = {};
  META.groups.forEach(g => quan_tam[g.code] = parseInt(document.getElementById(`qt_${g.code}`).value, 10));
  const hb = {}, thi = {};
  META.subjects.forEach(s => {
    hb[s.code] = numOrNull(`hb_${s.code}`);
    thi[s.code] = numOrNull(`thi_${s.code}`);
  });
  return {
    lop: parseInt(document.getElementById("lop").value, 10),
    khu_vuc: document.getElementById("khu_vuc").value,
    ngan_sach: parseFloat(document.getElementById("ngan_sach").value || "50"),
    the_luc: parseInt(document.getElementById("the_luc").value || "4", 10),
    ielts: parseFloat(document.getElementById("ielts").value || "0"),
    dgnl_hsa: parseFloat(document.getElementById("dgnl_hsa").value || "0"),
    giai_hsg: 0,
    holland, quan_tam, hb, thi
  };
}

function renderResult(data) {
  const box = document.getElementById("resultArea");
  const top1 = data.top_majors[0];
  const warns = (data.warnings || []).map(w => `<div class="warn-box">${w}</div>`).join("");
  const bars = data.top_groups.map(g => `
    <div class="bar-wrap">
      <div class="bar-head"><span>${g.group_name}</span><span>${g.confidence_pct}% (điểm ${g.group_score})</span></div>
      <div class="bar-bg"><div class="bar-fill" style="width:${g.confidence_pct}%"></div></div>
    </div>
  `).join("");
  const majors = data.top_majors.map(m => `
    <tr><td><b>${m.major_name}</b></td><td>${m.best_combo}</td><td>${m.dc_top}</td><td>${m.suitability_score}</td></tr>
  `).join("");
  const trace = (data.trace_preview || []).map(t => `
    <div class="trace-item ${t.fired ? "" : "suppressed"}">
      <b>#${t.step_no} [${t.rule_id}]</b> (pha <i>${t.phase}</i>, P=${t.priority}, CF=${t.certainty}) — ${t.explanation}
    </div>
  `).join("");

  box.innerHTML = `
    <p><b>Ngành khuyến nghị số 1:</b> ${top1 ? top1.major_name : "Đang cập nhật"}<br/>
       <b>Tổ hợp tối ưu:</b> ${data.best_combo} (${data.best_score_ut} đ sau ưu tiên)<br/>
       <b>Khả thi 2026:</b> ${data.feasibility} · <b>Phương thức:</b> ${data.admission_method}</p>
    ${warns}
    <h3>Top 3 nhóm ngành phù hợp</h3>
    ${bars}
    <h3>Top ngành gợi ý</h3>
    <table><thead><tr><th>Ngành</th><th>Khối</th><th>ĐC Top</th><th>Điểm</th></tr></thead><tbody>${majors}</tbody></table>
    <h3>Chuỗi suy diễn & Xử lý xung đột (${data.n_fired} luật kích hoạt, ${data.n_iterations} vòng)</h3>
    ${trace}
  `;
}

async function runAdvise() {
  const btn = document.getElementById("submitBtn");
  btn.disabled = true;
  btn.textContent = "Đang suy diễn...";
  try {
    const res = await fetch(`${API_BASE}/api/advise?explain=true`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectProfile()),
    });
    if (!res.ok) throw new Error(await res.text());
    renderResult(await res.json());
  } catch (err) {
    document.getElementById("resultArea").innerHTML = `<div class="warn-box">Lỗi: ${err.message}</div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = "Chạy tư vấn ngành nghề 2026";
  }
}

async function init() {
  try {
    const [hRes, mRes] = await Promise.all([fetch(`${API_BASE}/api/health`), fetch(`${API_BASE}/api/meta`)]);
    const health = await hRes.json();
    META = await mRes.json();
    buildSliders(META);
    setStatus(true, `Backend OK · ${health.n_majors} ngành · ${health.n_rules} luật`);
    runAdvise();
  } catch {
    setStatus(false, "Backend chưa chạy");
    document.getElementById("resultArea").innerHTML = `<div class="warn-box">Không kết nối được backend tại ${API_BASE}. Hãy chạy uvicorn trước.</div>`;
  }
}

document.getElementById("adviseForm").addEventListener("submit", (e) => { e.preventDefault(); runAdvise(); });
document.getElementById("fillA").addEventListener("click", () => {
  document.getElementById("h_R").value = 4.4; document.getElementById("h_I").value = 4.6;
  document.getElementById("qt_CNTT").value = 5; document.getElementById("qt_KTCN").value = 5;
  document.getElementById("hb_T").value = 9.0; document.getElementById("hb_L").value = 8.8; document.getElementById("hb_H").value = 8.5;
  runAdvise();
});
document.getElementById("fillB").addEventListener("click", () => {
  document.getElementById("h_I").value = 3.2; document.getElementById("h_E").value = 4.5;
  document.getElementById("qt_CNTT").value = 2; document.getElementById("qt_QTKD").value = 5;
  document.getElementById("hb_T").value = 7.8; document.getElementById("hb_V").value = 8.4; document.getElementById("hb_A").value = 8.8;
  runAdvise();
});

init();
