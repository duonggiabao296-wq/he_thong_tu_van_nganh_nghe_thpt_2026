"""
================================================================================
HỆ CHUYÊN GIA & AI TƯ VẤN CHỌN NGÀNH / NGHỀ CHO HỌC SINH THPT (2026)
Pipeline Step-by-Step: Tiền xử lý -> Luật IF-THEN & CF -> Huấn luyện Hybrid & ML
Áp dụng đầy đủ kiến thức từ Báo cáo BaiTapLon_AI.docx (Chương 1 - Chương 5)
================================================================================
Hướng dẫn chạy trên máy cá nhân (Windows / Linux / macOS):
  1. Giải nén file `dataset_tu_van_nganh_nghe_thpt_2026.rar` vào thư mục `data/`
     (sao cho có file `data/dataset_tu_van_nganh_nghe_thpt_2026.csv`).
  2. Cài đặt thư viện cần thiết:
       pip install pandas numpy scikit-learn joblib
  3. Chạy từng bước tự động:
       python train_and_build_expert_model.py --csv data/dataset_tu_van_nganh_nghe_thpt_2026.csv
================================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pickle
try:
    import joblib
except ImportError:
    joblib = None
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from sklearn.tree import DecisionTreeClassifier


# ==============================================================================
# CẤU HÌNH CỘT DỮ LIỆU THEO BÁO CÁO (CHƯƠNG 1 & CHƯƠNG 4)
# ==============================================================================
# 22 cột đầu ra phải khóa để chống rò rỉ nhãn (Data Leakage Guard)
LEAKAGE_COLS = [
    "ma_nhom_nganh_top1", "nhom_nganh_top1", "nganh_goi_y_1", "nganh_goi_y_2",
    "nganh_goi_y_3", "diem_phu_hop_1", "diem_phu_hop_2", "diem_phu_hop_3",
    "to_hop_de_xuat", "diem_to_hop_de_xuat", "diem_sau_uu_tien",
    "diem_chuan_top", "diem_chuan_tb", "diem_chuan_cb",
    "muc_kha_thi", "phuong_thuc_xet_tuyen", "canh_bao",
    "top_nhom_1", "top_nhom_2", "top_nhom_3", "ma_nganh_1", "xep_hang_1",
]

# 8 cột định danh & nhạy cảm phải loại để đảm bảo công bằng (Fairness Guard)
SENSITIVE_COLS = [
    "student_id", "ma_hoc_sinh", "tap", "gioi_tinh", "dan_toc",
    "tinh_thanh", "vung_mien", "khu_vuc_cu_tru", "loai_truong",
]

HOLLAND_COLS = ["holland_r", "holland_i", "holland_a", "holland_s", "holland_e", "holland_c"]

MON_HOC_11 = [
    "toan", "van", "anh", "ly", "hoa", "sinh", "su", "dia", "ktpl", "tin", "cn"
]


# ==============================================================================
# BƯỚC 1: NẠP DỮ LIỆU & KIỂM TRA CẤU TRÚC
# ==============================================================================
def step1_load_dataset(csv_path: str) -> pd.DataFrame:
    print("\n[BƯỚC 1] Nạp và kiểm tra bộ dữ liệu...")
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy '{csv_path}'. Hãy giải nén dataset_tu_van_nganh_nghe_thpt_2026.rar "
            "bằng WinRAR/7-Zip vào thư mục data/ trước khi chạy."
        )

    df = pd.read_csv(path)
    print(f"  -> Đã nạp {len(df):,} dòng × {df.shape[1]} cột.")
    if "tap" in df.columns:
        print("  -> Phân bố cột 'tap':", df["tap"].value_counts().to_dict())
    return df


# ==============================================================================
# BƯỚC 2: TIỀN XỬ LÝ DỮ LIỆU (CHƯƠNG 1: CLEANING -> SCALING -> ENCODING)
# ==============================================================================
def step2_preprocess_data(
    df: pd.DataFrame,
    target_col: str = "ma_nhom_nganh_top1",
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str], LabelEncoder, Dict[str, Any]]:
    print("\n[BƯỚC 2] Tiền xử lý dữ liệu (Làm sạch -> Chuẩn hóa -> Mã hóa)...")

    if target_col not in df.columns:
        # Dự phòng nếu tên cột nhãn là nhom_nganh_top1 hoặc Target_Career_Group
        for alt in ["nhom_nganh_top1", "Target_Career_Group"]:
            if alt in df.columns:
                target_col = alt
                break
        else:
            raise KeyError(f"Không tìm thấy cột nhãn mục tiêu '{target_col}' trong CSV.")

    # Giai đoạn 1: Làm sạch dữ liệu (loại dòng thiếu nhãn & giá trị ngoại lai điểm ngoài [0, 10])
    df_clean = df.dropna(subset=[target_col]).copy()
    for m in MON_HOC_11:
        for prefix in ("hb_", "thi_"):
            col = f"{prefix}{m}"
            if col in df_clean.columns:
                df_clean.loc[(df_clean[col] < 0) | (df_clean[col] > 10), col] = np.nan

    # Chống rò rỉ nhãn & loại cột nhạy cảm
    drop_cols = set(LEAKAGE_COLS + SENSITIVE_COLS + [target_col])
    feature_cols = [c for c in df_clean.columns if c not in drop_cols]

    # Chỉ giữ các cột số hoặc phân loại ít mức để mã hóa One-Hot
    num_cols = df_clean[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [
        c for c in feature_cols
        if c not in num_cols and df_clean[c].nunique(dropna=True) <= 30
    ]

    X_df = df_clean[num_cols + cat_cols].copy()

    # Giai đoạn 3 (trên đặc trưng phân loại): One-Hot Encoding cho các cột chữ (ví dụ exam_block, gia_dinh_goi_y...)
    if cat_cols:
        X_df = pd.get_dummies(X_df, columns=cat_cols, dummy_na=False)
    final_feature_names = X_df.columns.tolist()

    # Mã hóa nhãn đầu ra (Label Encoding)
    le = LabelEncoder()
    y_all = le.fit_transform(df_clean[target_col].astype(str))

    # Chia tập Train / Val / Test theo cột 'tap' (hoặc 70/15/15 nếu không có cột 'tap')
    if "tap" in df_clean.columns:
        tap_lower = df_clean["tap"].astype(str).str.lower()
        train_mask = tap_lower == "train"
        val_mask = tap_lower.isin(["val", "validation"])
        test_mask = tap_lower == "test"
    else:
        rng = np.random.default_rng(42)
        idx = rng.permutation(len(df_clean))
        n_train = int(0.70 * len(df_clean))
        n_val = int(0.15 * len(df_clean))
        train_mask = np.zeros(len(df_clean), dtype=bool)
        val_mask = np.zeros(len(df_clean), dtype=bool)
        test_mask = np.zeros(len(df_clean), dtype=bool)
        train_mask[idx[:n_train]] = True
        val_mask[idx[n_train:n_train + n_val]] = True
        test_mask[idx[n_train + n_val:]] = True

    X_train_raw = X_df.loc[train_mask].to_numpy(dtype=np.float32)
    X_val_raw = X_df.loc[val_mask].to_numpy(dtype=np.float32)
    X_test_raw = X_df.loc[test_mask].to_numpy(dtype=np.float32)

    y_train, y_val, y_test = y_all[train_mask], y_all[val_mask], y_all[test_mask]

    # Giai đoạn 1b & 2: Điền khuyết bằng Median + Chuẩn hóa (fit trên Train để tránh rò rỉ dữ liệu)
    imputer = SimpleImputer(strategy="median")
    scaler = MinMaxScaler()  # Có thể đổi sang StandardScaler() cho Z-score

    X_train = scaler.fit_transform(imputer.fit_transform(X_train_raw))
    X_val = scaler.transform(imputer.transform(X_val_raw))
    X_test = scaler.transform(imputer.transform(X_test_raw))

    artifacts = {
        "imputer": imputer,
        "scaler": scaler,
        "num_cols": num_cols,
        "cat_cols": cat_cols,
        "feature_names": final_feature_names,
    }
    print(f"  -> Số đặc trưng sau One-Hot: {len(final_feature_names)} | Số lớp: {len(le.classes_)}")
    print(f"  -> Kích thước Train / Val / Test: {len(y_train):,} / {len(y_val):,} / {len(y_test):,}")
    return X_train, X_val, X_test, y_train, y_val, y_test, final_feature_names, le, artifacts


# ==============================================================================
# BƯỚC 3: HỆ CHUYÊN GIA LUẬT IF-THEN, HỆ SỐ TIN CẬY CF & SUY DIỄN TIẾN
# ==============================================================================
@dataclass
class Rule:
    rule_id: str
    phase: int               # Tầng suy diễn (1..4)
    priority: int            # Độ ưu tiên giải quyết xung đột
    cf_rule: float           # Hệ số tin cậy MYCIN [-1.0, +1.0]
    target_key: str          # Khóa kết luận trong Working Memory
    conclusion: Any          # Giá trị kết luận
    mode: str                # 'cf_merge' (cộng dồn CF) hoặc 'set' (ghi đè có phân xử)
    description: str
    condition_fn: Any        # Hàm kiểm tra trên Working Memory -> (bool, cf_premise)


def combine_cf(cf_a: float, cf_b: float) -> float:
    """Công thức gộp hệ số tin cậy MYCIN (Chương 2, mục 2.1.4)."""
    if cf_a >= 0 and cf_b >= 0:
        return cf_a + cf_b * (1.0 - cf_a)
    if cf_a < 0 and cf_b < 0:
        return cf_a + cf_b * (1.0 + cf_a)
    denom = 1.0 - min(abs(cf_a), abs(cf_b))
    return (cf_a + cf_b) / denom if denom > 1e-9 else 0.0


@dataclass
class ForwardChainingExpertSystem:
    """Bộ suy diễn tiến (Recognize-Act) kèm Conflict Resolution & Explanation Trace."""
    rules: List[Rule] = field(default_factory=list)

    @staticmethod
    def build_default_rules() -> "ForwardChainingExpertSystem":
        # Tập luật mẫu theo Bảng 3 (Chương 2) và cơ chế phân xử xung đột (Chương 5)
        rules = [
            # Tầng 1: Trừu tượng hóa dữ liệu
            Rule(
                "T1-HOLLAND", phase=1, priority=90, cf_rule=1.0,
                target_key="holland_top", conclusion=None, mode="set",
                description="Xác định mã Holland nổi trội nhất",
                condition_fn=lambda wm: (bool(wm.get("holland")), 1.0),
            ),
            # Tầng 2: Luật gợi ý nhóm ngành (CF từ tập dữ liệu 60.000 HS)
            Rule(
                "R01", phase=2, priority=80, cf_rule=0.31,
                target_key="cf_group:CNTT", conclusion="CNTT", mode="cf_merge",
                description="Lớp 12 & đủ khối A01 & Toán thi >= 8.0 & Holland chính = I -> CNTT",
                condition_fn=lambda wm: (
                    wm.get("lop") == 12
                    and wm.get("thi_toan", 0) >= 8.0
                    and wm.get("thi_ly", 0) > 0
                    and wm.get("thi_anh", 0) > 0
                    and wm.get("holland_top") == "I",
                    1.0,
                ),
            ),
            Rule(
                "R02", phase=2, priority=75, cf_rule=0.30,
                target_key="cf_group:CNTT", conclusion="CNTT", mode="cf_merge",
                description="Holland chính = I & quan tâm CNTT >= 4 & học bạ Toán >= 8.0 -> CNTT",
                condition_fn=lambda wm: (
                    wm.get("holland_top") == "I"
                    and wm.get("qt_CNTT", 0) >= 4
                    and wm.get("hb_toan", 0) >= 8.0,
                    1.0,
                ),
            ),
            Rule(
                "R03", phase=2, priority=75, cf_rule=0.36,
                target_key="cf_group:KTCN", conclusion="KTCN", mode="cf_merge",
                description="Holland = R & quan tâm KTCN >= 4 & HB Toán >= 8 & HB Lý >= 8 -> KTCN",
                condition_fn=lambda wm: (
                    wm.get("holland_top") == "R"
                    and wm.get("qt_KTCN", 0) >= 4
                    and wm.get("hb_toan", 0) >= 8.0
                    and wm.get("hb_ly", 0) >= 8.0,
                    1.0,
                ),
            ),
            Rule(
                "R05", phase=2, priority=75, cf_rule=0.32,
                target_key="cf_group:QTKD", conclusion="QTKD", mode="cf_merge",
                description="Holland = E & quan tâm QTKD >= 4 & HB Toán >= 7.5 -> QTKD",
                condition_fn=lambda wm: (
                    wm.get("holland_top") == "E"
                    and wm.get("qt_QTKD", 0) >= 4
                    and wm.get("hb_toan", 0) >= 7.5,
                    1.0,
                ),
            ),
            Rule(
                "R07", phase=2, priority=70, cf_rule=0.33,
                target_key="cf_group:TT_NT", conclusion="TT_NT", mode="cf_merge",
                description="Holland = A & quan tâm Truyền thông - Nghệ thuật >= 4 -> TT_NT",
                condition_fn=lambda wm: (
                    wm.get("holland_top") == "A"
                    and wm.get("qt_TT_NT", 0) >= 4,
                    1.0,
                ),
            ),
            Rule(
                "R08", phase=2, priority=70, cf_rule=0.29,
                target_key="cf_group:SUPHAM", conclusion="SUPHAM", mode="cf_merge",
                description="Holland = S & quan tâm Sư phạm >= 4 -> SUPHAM",
                condition_fn=lambda wm: (
                    wm.get("holland_top") == "S"
                    and wm.get("qt_SUPHAM", 0) >= 4,
                    1.0,
                ),
            ),
            # Tầng 3: Bằng chứng âm / Ràng buộc điều chỉnh
            Rule(
                "R09", phase=3, priority=85, cf_rule=-0.75,
                target_key="cf_group:QPAN", conclusion="QPAN", mode="cf_merge",
                description="Thể lực <= 2 -> giảm mạnh độ phù hợp An ninh - Quốc phòng",
                condition_fn=lambda wm: (wm.get("the_luc", 5) <= 2, 1.0),
            ),
            # Tầng 4: Quy chế khả thi, phương thức xét tuyển & cảnh báo (có xung đột 'set')
            Rule(
                "R11-CAO", phase=4, priority=80, cf_rule=1.0,
                target_key="feasibility", conclusion="Cao", mode="set",
                description="Điểm tổ hợp >= 15 và >= Điểm chuẩn top - 1.0 -> Khả thi Cao",
                condition_fn=lambda wm: (
                    wm.get("best_score", 0) >= 15.0
                    and wm.get("best_score_ut", 0) >= wm.get("dc_top", 26.0) - 1.0,
                    1.0,
                ),
            ),
            Rule(
                "R11-TB", phase=4, priority=60, cf_rule=1.0,
                target_key="feasibility", conclusion="Trung bình", mode="set",
                description="Điểm tổ hợp >= 15 (chưa đạt mốc Cao) -> Khả thi Trung bình",
                condition_fn=lambda wm: (wm.get("best_score", 0) >= 15.0, 1.0),
            ),
            Rule(
                "R13", phase=4, priority=95, cf_rule=1.0,
                target_key="admission_method", conclusion="Tuyển thẳng / Ưu tiên xét tuyển", mode="set",
                description="Có giải HSG Quốc gia/Quốc tế -> Tuyển thẳng",
                condition_fn=lambda wm: (bool(wm.get("giai_hsg", 0)), 1.0),
            ),
            Rule(
                "R12", phase=4, priority=85, cf_rule=1.0,
                target_key="admission_method", conclusion="Đánh giá năng lực (HSA/TSA)", mode="set",
                description="Lớp 12 & điểm ĐGNL HSA >= 90 -> Phương thức Đánh giá năng lực",
                condition_fn=lambda wm: (
                    wm.get("lop") == 12 and wm.get("dgnl_hsa", 0) >= 90,
                    1.0,
                ),
            ),
            Rule(
                "R12-DEFAULT", phase=4, priority=20, cf_rule=1.0,
                target_key="admission_method", conclusion="Thi tốt nghiệp THPT", mode="set",
                description="Phương thức mặc định: Thi tốt nghiệp THPT",
                condition_fn=lambda wm: (True, 1.0),
            ),
            Rule(
                "R14", phase=4, priority=70, cf_rule=1.0,
                target_key="warning_budget", conclusion="Ngân sách thấp hơn học phí dự kiến", mode="set",
                description="Ngân sách < học phí tối thiểu (20 triệu/năm) -> Cảnh báo học phí",
                condition_fn=lambda wm: (wm.get("ngan_sach", 100) < wm.get("min_tuition", 20), 1.0),
            ),
        ]
        return ForwardChainingExpertSystem(rules=rules)

    def infer(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Vòng lặp suy diễn tiến Recognize -> Resolve -> Act kèm vết giải trình."""
        wm = dict(profile)
        if "holland" in wm and isinstance(wm["holland"], dict):
            wm["holland_top"] = max(wm["holland"], key=wm["holland"].get)

        fired: set[str] = set()
        trace_steps: List[Dict[str, Any]] = []
        step_no = 0

        for iteration in range(1, 7):
            # 1. MATCH
            agenda: List[Tuple[Rule, float]] = []
            for r in self.rules:
                if r.rule_id in fired:
                    continue
                ok, cf_prem = r.condition_fn(wm)
                if ok and cf_prem >= 0.2:
                    agenda.append((r, cf_prem))

            if not agenda:
                break

            # 2. CONFLICT RESOLUTION: phase tăng dần, priority giảm dần, |cf_rule| giảm dần, rule_id
            agenda.sort(key=lambda x: (x[0].phase, -x[0].priority, -abs(x[0].cf_rule), x[0].rule_id))

            # Xử lý xung đột cho các luật cùng target_key ở chế độ 'set'
            winners_by_set_key: Dict[str, Rule] = {}
            for r, cf_prem in agenda:
                step_no += 1
                if r.mode == "set" and r.target_key in winners_by_set_key:
                    winner = winners_by_set_key[r.target_key]
                    fired.add(r.rule_id)  # Đánh dấu đã xét (refraction)
                    trace_steps.append({
                        "step_no": step_no,
                        "iteration": iteration,
                        "rule_id": r.rule_id,
                        "status": "suppressed",
                        "suppressed_by": winner.rule_id,
                        "reason": f"Bị đè bởi {winner.rule_id} (priority {winner.priority} > {r.priority})",
                    })
                    continue

                if r.mode == "set":
                    winners_by_set_key[r.target_key] = r
                    if r.rule_id != "T1-HOLLAND":
                        wm[r.target_key] = r.conclusion
                elif r.mode == "cf_merge":
                    cf_contrib = r.cf_rule * cf_prem
                    prev_cf = wm.get(r.target_key, 0.0)
                    wm[r.target_key] = combine_cf(prev_cf, cf_contrib)

                fired.add(r.rule_id)
                trace_steps.append({
                    "step_no": step_no,
                    "iteration": iteration,
                    "rule_id": r.rule_id,
                    "status": "fired",
                    "suppressed_by": None,
                    "priority": r.priority,
                    "cf_rule": r.cf_rule,
                    "output_key": r.target_key,
                    "output_value": wm.get(r.target_key),
                    "description": r.description,
                })

        group_scores = {
            k.replace("cf_group:", ""): round(v, 4)
            for k, v in wm.items()
            if k.startswith("cf_group:")
        }
        ranked_groups = sorted(group_scores.items(), key=lambda x: -x[1])
        return {
            "top_groups": ranked_groups,
            "feasibility": wm.get("feasibility", "Chưa xác định"),
            "admission_method": wm.get("admission_method", "Thi tốt nghiệp THPT"),
            "warning": wm.get("warning_budget"),
            "trace_steps": trace_steps,
        }


# ==============================================================================
# BƯỚC 4: HUẤN LUYỆN & ĐỐI CHIẾU CÁC MÔ HÌNH HỌC MÁY (CHƯƠNG 3 & CHƯƠNG 4)
# ==============================================================================
def top_k_accuracy(y_true: np.ndarray, y_proba: np.ndarray, k: int = 3) -> float:
    k_eff = min(k, y_proba.shape[1])
    top_k_preds = np.argsort(y_proba, axis=1)[:, -k_eff:]
    hits = [y_true[i] in top_k_preds[i] for i in range(len(y_true))]
    return float(np.mean(hits))


def step4_train_and_evaluate_models(
    X_train: np.ndarray,
    X_val: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_val: np.ndarray,
    y_test: np.ndarray,
    use_grid_search: bool = False,
) -> Tuple[Dict[str, Any], pd.DataFrame]:
    print("\n[BƯỚC 4] Huấn luyện & đánh giá đối chiếu các mô hình Học máy...")

    if use_grid_search:
        # Tinh chỉnh siêu tham số theo Bảng 6 (Chương 4) trên mẫu con 12.000 dòng để tiết kiệm thời gian
        n_sub = min(12_000, len(X_train))
        dt_search = GridSearchCV(
            DecisionTreeClassifier(random_state=42),
            param_grid={"max_depth": [6, 10, 12, 16], "min_samples_leaf": [5, 20]},
            cv=3, n_jobs=-1,
        )
        dt_search.fit(X_train[:n_sub], y_train[:n_sub])
        dt_model = dt_search.best_estimator_
    else:
        dt_model = DecisionTreeClassifier(max_depth=12, min_samples_leaf=20, random_state=42)

    models = {
        "DecisionTree": dt_model,
        "RandomForest": RandomForestClassifier(
            n_estimators=200, max_depth=16, min_samples_leaf=2, n_jobs=-1, random_state=42
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            max_iter=150, learning_rate=0.08, max_depth=8, random_state=42
        ),
    }

    results = []
    trained_models: Dict[str, Any] = {}

    for name, clf in models.items():
        t0 = time.perf_counter()
        clf.fit(X_train, y_train)
        train_sec = time.perf_counter() - t0

        t_inf = time.perf_counter()
        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)
        inf_ms_per_sample = (time.perf_counter() - t_inf) * 1000.0 / len(y_test)

        acc_train = accuracy_score(y_train, clf.predict(X_train)) * 100
        acc_val = accuracy_score(y_val, clf.predict(X_val)) * 100
        acc_test = accuracy_score(y_test, y_pred) * 100
        f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0) * 100
        f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0) * 100
        prec_macro = precision_score(y_test, y_pred, average="macro", zero_division=0) * 100
        rec_macro = recall_score(y_test, y_pred, average="macro", zero_division=0) * 100
        top3 = top_k_accuracy(y_test, y_proba, k=3) * 100

        results.append({
            "Model": name,
            "Train_Acc(%)": round(acc_train, 2),
            "Val_Acc(%)": round(acc_val, 2),
            "Test_Acc(%)": round(acc_test, 2),
            "Precision_Macro(%)": round(prec_macro, 2),
            "Recall_Macro(%)": round(rec_macro, 2),
            "F1_Macro(%)": round(f1_macro, 2),
            "F1_Weighted(%)": round(f1_weighted, 2),
            "Top3_Acc(%)": round(top3, 2),
            "Train_Time(s)": round(train_sec, 2),
            "Inf_ms_per_sample": round(inf_ms_per_sample, 4),
        })
        trained_models[name] = clf
        print(f"  -> {name}: Test Acc={acc_test:.2f}% | F1-Macro={f1_macro:.2f}% | Top-3={top3:.2f}%")

    metrics_df = pd.DataFrame(results)
    return trained_models, metrics_df


# ==============================================================================
# BƯỚC 5: ĐÓNG GÓI MÔ HÌNH & CHẠY DEMO SUY DIỄN HỒ SƠ MẪU (HS035884)
# ==============================================================================
def step5_save_and_demo(
    out_dir: str,
    trained_models: Dict[str, Any],
    label_encoder: LabelEncoder,
    preprocess_artifacts: Dict[str, Any],
    metrics_df: pd.DataFrame,
) -> None:
    print("\n[BƯỚC 5] Lưu model đã huấn luyện & chạy demo Hệ chuyên gia...")
    os.makedirs(out_dir, exist_ok=True)

    # Lưu gói model Học máy (dùng cho Backend FastAPI đối chiếu)
    bundle_path = Path(out_dir) / "sklearn_models_2026.pkl"
    payload = {
        "models": trained_models,
        "label_encoder": label_encoder,
        "preprocess": preprocess_artifacts,
        "metrics": metrics_df.to_dict(orient="records"),
    }
    if joblib is not None:
        joblib.dump(payload, bundle_path)
    else:
        with open(bundle_path, "wb") as f:
            pickle.dump(payload, f)
    metrics_csv = Path(out_dir) / "model_comparison_metrics.csv"
    metrics_df.to_csv(metrics_csv, index=False, encoding="utf-8-sig")

    # Lưu cấu hình trọng số chuẩn của Hệ chuyên gia (Bảng 7, Chương 4)
    expert_config = {
        "version": "2026.1",
        "hybrid_weights": {
            "f1_holland_match": 3.67,
            "f2_interest_level": 1.69,
            "f3_key_subjects": 2.45,
            "f4_cutoff_feasibility": 3.78,
            "f5_tuition_budget": 2.80,
            "f6_family_suggestion": 0.95,
            "f7_career_values": 1.24,
            "f8_combo_eligibility": 2.38,
            "f9_physical_qpan": 2.09,
        },
        "scale_factor": 2.65,
    }
    expert_json_path = Path(out_dir) / "expert_weights_2026.json"
    expert_json_path.write_text(json.dumps(expert_config, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"  -> Đã lưu ML bundle: {bundle_path}")
    print(f"  -> Đã lưu bảng đánh giá: {metrics_csv}")
    print(f"  -> Đã lưu trọng số Hệ chuyên gia: {expert_json_path}")

    # Chạy minh họa suy diễn tiến trên hồ sơ mẫu HS035884 (Bảng 4, Chương 2)
    sample_hs035884 = {
        "lop": 12,
        "holland": {"R": 2.1, "I": 5.0, "A": 2.7, "S": 2.4, "E": 3.5, "C": 2.0},
        "qt_CNTT": 5,
        "hb_toan": 9.9,
        "thi_toan": 10.0,
        "thi_anh": 9.25,
        "thi_ly": 6.75,
        "the_luc": 4,
        "ngan_sach": 65,
        "min_tuition": 20,
        "best_score": 27.25,
        "best_score_ut": 27.34,
        "dc_top": 26.0,
        "dgnl_hsa": 0,
        "giai_hsg": 0,
    }
    es = ForwardChainingExpertSystem.build_default_rules()
    advise = es.infer(sample_hs035884)
    print("\n  -> Kết quả suy diễn tiến trên hồ sơ mẫu HS035884:")
    print(f"     * Top nhóm ngành (CF gộp): {advise['top_groups']}")
    print(f"     * Mức khả thi: {advise['feasibility']}")
    print(f"     * Phương thức xét tuyển: {advise['admission_method']}")
    print(f"     * Số bước giải trình (trace): {len(advise['trace_steps'])} bước")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline xây dựng mô hình Tư vấn Ngành nghề THPT 2026")
    parser.add_argument(
        "--csv",
        default="data/dataset_tu_van_nganh_nghe_thpt_2026.csv",
        help="Đường dẫn tới file CSV đã giải nén từ dataset_tu_van_nganh_nghe_thpt_2026.rar",
    )
    parser.add_argument("--out-dir", default="saved_models", help="Thư mục lưu model đầu ra")
    parser.add_argument("--grid-search", action="store_true", help="Bật GridSearchCV cho Decision Tree")
    args = parser.parse_args()

    df = step1_load_dataset(args.csv)
    X_train, X_val, X_test, y_train, y_val, y_test, _, le, prep = step2_preprocess_data(df)
    trained_models, metrics_df = step4_train_and_evaluate_models(
        X_train, X_val, X_test, y_train, y_val, y_test, use_grid_search=args.grid_search
    )
    step5_save_and_demo(args.out_dir, trained_models, le, prep, metrics_df)


if __name__ == "__main__":
    main()