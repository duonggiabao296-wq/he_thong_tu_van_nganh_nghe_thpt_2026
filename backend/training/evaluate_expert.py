from __future__ import annotations
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db import GROUPS, init_db
from app.inference import run_forward_chaining

DATA_PATH = ROOT / "data" / "dataset_tu_van_nganh_nghe_thpt_2026.csv"
COMPARISON_PATH = ROOT / "models" / "model_comparison.csv"

GROUP_CODES = [g[0] for g in GROUPS]
GROUP_NAME_TO_CODE = {g[1]: g[0] for g in GROUPS}

# Ánh xạ cột CSV -> mã môn trong app/db.py (chỉnh nếu mã môn trong db.py khác)
SUBJ_COL_MAP = {
    "T": "toan",
    "V": "van",
    "A": "anh",
    "L": "ly",
    "H": "hoa",
    "B": "sinh",
    "I": "tin",
    "S": "su",
    "D": "dia",
    "K": "ktpl",
    "C": "cn",
}


def _safe_float(val, default=None):
    if pd.isna(val):
        return default
    v = float(val)
    return None if v <= 0 else v


def _normalize_giai_hsg(val):
    if pd.isna(val):
        return 0
    try:
        return int(val)
    except (TypeError, ValueError):
        label = str(val).strip().casefold()
        if label == "không":
            return 0
        if label in {"cấp tỉnh/thành", "quốc gia/quốc tế"}:
            return 1
        raise ValueError(f"Giá trị giai_hsg không hợp lệ: {val!r}")


def row_to_profile(row: pd.Series) -> dict:
    lop = int(row.get("lop", 12)) if not pd.isna(row.get("lop", 12)) else 12
    holland = {
        k: float(row.get(f"holland_{k}", row.get(f"holland_{k.lower()}", 3.0)))
        if not pd.isna(row.get(f"holland_{k}", row.get(f"holland_{k.lower()}", 3.0)))
        else 3.0
        for k in ["R", "I", "A", "S", "E", "C"]
    }
    quan_tam = {}
    for gc in GROUP_CODES:
        col_lower = f"qt_{gc.lower()}"
        col_upper = f"qt_{gc}"
        col_alt = f"quan_tam_{gc.lower()}"
        val = row.get(col_lower, row.get(col_upper, row.get(col_alt, 3)))
        quan_tam[gc] = int(round(float(val))) if not pd.isna(val) else 3

    hb = {code: _safe_float(row.get(f"hb_{cname}")) for code, cname in SUBJ_COL_MAP.items()}
    thi = {code: _safe_float(row.get(f"thi_{cname}")) for code, cname in SUBJ_COL_MAP.items()}

    return {
        "lop": lop,
        "khu_vuc": str(row.get("khu_vuc_uu_tien", row.get("khu_vuc", "KV2"))),
        "ngan_sach": float(row.get("ngan_sach_hoc_phi_trieu_nam", row.get("ngan_sach", 40.0)))
        if not pd.isna(row.get("ngan_sach_hoc_phi_trieu_nam", row.get("ngan_sach", 40.0)))
        else 40.0,
        "the_luc": int(row.get("the_luc", 4)) if not pd.isna(row.get("the_luc", 4)) else 4,
        "ielts": float(row.get("ielts", 0.0)) if not pd.isna(row.get("ielts", 0.0)) else 0.0,
        "dgnl_hsa": float(row.get("dgnl_hsa_150", row.get("dgnl_hsa", 0.0)))
        if not pd.isna(row.get("dgnl_hsa_150", row.get("dgnl_hsa", 0.0)))
        else 0.0,
        "giai_hsg": _normalize_giai_hsg(row.get("giai_hsg", 0)),
        "holland": holland,
        "quan_tam": quan_tam,
        "hb": hb,
        "thi": thi,
    }


def main():
    df = pd.read_csv(DATA_PATH)
    test_df = df[df["tap"] == "test"].reset_index(drop=True)

    db_path = ROOT / "data" / "kb.sqlite"
    conn = None
    try:
        res = init_db()
        if isinstance(res, sqlite3.Connection):
            conn = res
    except TypeError:
        try:
            res = init_db(db_path)
            if isinstance(res, sqlite3.Connection):
                conn = res
        except Exception:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            init_db(conn)
    if conn is None:
        conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    y_true, y_pred_top1, top3_hits, latencies_ms = [], [], [], []
    lop12_mask = []

    for _, row in test_df.iterrows():
        target = str(row.get("ma_nhom_nganh_top1", ""))
        if not target or target == "nan":
            target = GROUP_NAME_TO_CODE.get(str(row.get("nhom_nganh_top1", "")), "CNTT")

        profile = row_to_profile(row)
        t0 = time.perf_counter()
        res = run_forward_chaining(profile, conn, save_trace=False)
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)

        top_codes = [g["group_code"] for g in res["top_groups"]]
        y_true.append(target)
        y_pred_top1.append(top_codes[0] if top_codes else "CNTT")
        top3_hits.append(1 if target in top_codes[:3] else 0)
        lop12_mask.append(profile["lop"] == 12)

    lop12_idx = [i for i, is12 in enumerate(lop12_mask) if is12]
    y_true_12 = [y_true[i] for i in lop12_idx]
    y_pred_12 = [y_pred_top1[i] for i in lop12_idx]
    top3_12 = [top3_hits[i] for i in lop12_idx]

    row_metrics = {
        "Model": "ExpertSystem_ForwardChaining",
        "Train_Acc(%)": "-",
        "Val_Acc(%)": "-",
        "Test_Top1(%)": round(accuracy_score(y_true, y_pred_top1) * 100, 2),
        "Train-Val(%)": "-",
        "Test_Top3(%)": round(float(np.mean(top3_hits)) * 100, 2),
        "Macro_P(%)": round(precision_score(y_true, y_pred_top1, average="macro", zero_division=0) * 100, 2),
        "Macro_R(%)": round(recall_score(y_true, y_pred_top1, average="macro", zero_division=0) * 100, 2),
        "Macro_F1(%)": round(f1_score(y_true, y_pred_top1, average="macro", zero_division=0) * 100, 2),
        "Weighted_F1(%)": round(f1_score(y_true, y_pred_top1, average="weighted", zero_division=0) * 100, 2),
        "LogLoss": "-",
        "MRR": "-",
        "NDCG@3": "-",
        "Lop12_Top1(%)": round(accuracy_score(y_true_12, y_pred_12) * 100, 2) if y_true_12 else 0.0,
        "Lop12_Top3(%)": round(float(np.mean(top3_12)) * 100, 2) if top3_12 else 0.0,
        "Latency_Med(ms)": round(float(np.median(latencies_ms)), 2),
        "Latency_p95(ms)": round(float(np.percentile(latencies_ms, 95)), 2),
        "Batch(us/mau)": "-",
        "CV_3Fold(%)": "-",
    }

    print("=== KẾT QUẢ HỆ CHUYÊN GIA (FORWARD CHAINING) TRÊN TẬP TEST ===")
    for k, v in row_metrics.items():
        print(f"  {k}: {v}")

    if COMPARISON_PATH.exists():
        comp_df = pd.read_csv(COMPARISON_PATH)
        comp_df = comp_df[comp_df["Model"] != "ExpertSystem_ForwardChaining"]
        comp_df = pd.concat([comp_df, pd.DataFrame([row_metrics])], ignore_index=True)
        comp_df.to_csv(COMPARISON_PATH, index=False)
        print(f"Đã cập nhật bảng so sánh tại: {COMPARISON_PATH}")


if __name__ == "__main__":
    main()