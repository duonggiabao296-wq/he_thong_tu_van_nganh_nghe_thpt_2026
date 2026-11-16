# -*- coding: utf-8 -*-
"""
FastAPI backend - Hệ thống Chuyên gia & AI Tư vấn Ngành nghề THPT 2026
Chạy:  uvicorn app.main:app --reload --port 8000     (từ thư mục backend/)
Docs:  http://127.0.0.1:8000/docs
"""
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .engine import CareerExpertSystem2026, DEFAULT_MODEL_PATH
from .schemas import ProfileInput

MODEL_PATH = os.environ.get("MODEL_PATH", DEFAULT_MODEL_PATH)
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(
        f"Không tìm thấy file mô hình: {MODEL_PATH}\n"
        "Hãy chạy: python training/train_model.py --data-dir <thư mục chứa CSV>"
    )

engine = CareerExpertSystem2026(MODEL_PATH)

app = FastAPI(title="Hệ thống Chuyên gia Tư vấn Ngành nghề THPT 2026", version="1.0.0")

# Cho phép frontend (Live Server :5500, http.server :5500/:3000 ...) gọi API khi chạy local.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "n_majors": len(engine.majors), "n_groups": len(engine.groups)}


@app.get("/api/meta")
def meta():
    """Danh mục để frontend dựng form: môn học, nhóm ngành, giá trị ưu tiên, độ chính xác mô hình."""
    return engine.meta()


@app.post("/api/advise")
def advise(req: ProfileInput):
    try:
        return engine.advise(req.model_dump())
    except Exception as exc:  # lỗi dữ liệu đầu vào bất thường
        raise HTTPException(status_code=422, detail=f"Không xử lý được hồ sơ: {exc}")
