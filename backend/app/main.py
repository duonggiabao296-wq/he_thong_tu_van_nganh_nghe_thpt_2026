from __future__ import annotations
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .db import GROUPS, SUBJECTS, init_db
from .inference import run_forward_chaining
from .schemas import AdviseResponse, ProfileInput

app = FastAPI(title="Hệ Chuyên Gia Tư Vấn Ngành Nghề THPT 2026", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONN = init_db()


@app.get("/api/health")
def health():
    n_majors = CONN.execute("SELECT COUNT(*) FROM majors").fetchone()[0]
    n_groups = CONN.execute('SELECT COUNT(*) FROM "groups"').fetchone()[0]
    n_rules = CONN.execute("SELECT COUNT(*) FROM rules WHERE enabled = 1").fetchone()[0]
    return {
        "status": "ok",
        "n_majors": n_majors,
        "n_groups": n_groups,
        "n_rules": n_rules,
        "kb_version": "2026.1-sqlite",
    }


@app.get("/api/meta")
def meta():
    return {
        "subjects": [{"code": c, "name": n} for c, n in SUBJECTS],
        "groups": [{"code": g[0], "name": g[1], "holland": g[2], "min_tuition": g[3]} for g in GROUPS],
        "career_values": [
            {"id": "thu_nhap", "label": "Thu nhập cao"},
            {"id": "on_dinh", "label": "Ổn định lâu dài"},
            {"id": "dam_me", "label": "Đam mê - sở thích"},
            {"id": "cong_hien", "label": "Đóng góp xã hội"},
            {"id": "gan_nha", "label": "Gần gia đình"},
        ],
    }


@app.get("/api/rules")
def list_rules():
    rows = CONN.execute("SELECT * FROM rules ORDER BY phase, priority DESC").fetchall()
    return {"total": len(rows), "rules": [dict(r) for r in rows]}


@app.post("/api/advise", response_model=AdviseResponse)
def advise(profile: ProfileInput, explain: bool = Query(default=True)):
    return run_forward_chaining(profile.model_dump(), CONN, save_trace=explain)


@app.get("/api/sessions/{session_id}/trace")
def get_trace(session_id: str):
    sess = CONN.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
    if not sess:
        raise HTTPException(status_code=404, detail="Không tìm thấy mã phiên suy diễn.")
    steps = CONN.execute(
        "SELECT * FROM trace_steps WHERE session_id = ? ORDER BY step_no", (session_id,)
    ).fetchall()
    return {"session": dict(sess), "steps": [dict(s) for s in steps]}
