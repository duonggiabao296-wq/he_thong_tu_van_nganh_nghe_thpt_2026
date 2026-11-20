import time
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import importlib

try:
    lgb = importlib.import_module("lightgbm")
except ImportError as exc:
    raise ImportError(
        "Thiếu thư viện 'lightgbm'. Hãy cài bằng lệnh: "
        "python -m pip install lightgbm"
    ) from exc

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    top_k_accuracy_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier

# Bật True để so sánh thêm Decision Tree, Random Forest, HistGradientBoosting
RUN_BASELINES = True

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "dataset_tu_van_nganh_nghe_thpt_2026.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print(f"Đang đọc dữ liệu từ: {DATA_PATH}")
df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

TARGET_COL = "nhom_nganh_top1"
DROP_LEAKAGE = [
    "ma_hoc_sinh", "tap",
    "nhom_nganh_top1", "nhom_nganh_top2", "nhom_nganh_top3", "ma_nhom_nganh_top1",
    "nganh_goi_y_1", "nganh_goi_y_2", "nganh_goi_y_3",
    "diem_phu_hop_top1", "do_tin_cay_nhom_top1",
    "to_hop_xet_tuyen_de_xuat", "ma_to_hop_de_xuat",
    "tong_diem_to_hop_de_xuat", "tong_diem_sau_uu_tien",
    "chenh_lech_diem_so_voi_trung_binh_nganh", "muc_do_kha_thi_top1",
    "phan_vi_to_hop_de_xuat", "phuong_thuc_xet_tuyen_de_xuat", "canh_bao",
    "du_dinh_nhom_nganh_cua_hoc_sinh", "khop_du_dinh_voi_tu_van",
]
DROP_LEAKAGE += [c for c in df.columns if c.startswith("diem_chuan_")]
DROP_FAIRNESS = [
    "gioi_tinh",
    "dan_toc_thieu_so",
    "dan_toc",
    "tinh_thanh",
    "vung_mien",
    "khu_vuc_cu_tru",
    "loai_truong",
]
COLS_TO_DROP = list(set(DROP_LEAKAGE + DROP_FAIRNESS))

train_df = df[df["tap"] == "train"].copy()
val_df = df[df["tap"] == "val"].copy()
test_df = df[df["tap"] == "test"].copy()

feature_cols = [c for c in df.columns if c not in COLS_TO_DROP]
cat_cols = [
    c for c in feature_cols
    if not pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])
]
num_cols = [c for c in feature_cols if c not in cat_cols]

for col in cat_cols:
    categories = df[col].fillna("MISSING").astype(str).unique().tolist()
    for split_df in (train_df, val_df, test_df):
        split_df[col] = pd.Categorical(
            split_df[col].fillna("MISSING").astype(str),
            categories=categories,
        )

X_train, X_val, X_test = train_df[feature_cols], val_df[feature_cols], test_df[feature_cols]

le = LabelEncoder()
y_train = le.fit_transform(train_df[TARGET_COL])
y_val = le.transform(val_df[TARGET_COL])
y_test = le.transform(test_df[TARGET_COL])
labels_idx = np.arange(len(le.classes_))
mask_lop12_test = (test_df["lop"] == 12).values


def compute_mrr_and_ndcg3(y_true: np.ndarray, y_proba: np.ndarray):
    order = np.argsort(-y_proba, axis=1)
    mrr_list, ndcg3_list = [], []
    for i, true_lbl in enumerate(y_true):
        rank = int(np.where(order[i] == true_lbl)[0][0]) + 1
        mrr_list.append(1.0 / rank)
        ndcg3_list.append((1.0 / np.log2(rank + 1)) if rank <= 3 else 0.0)
    return float(np.mean(mrr_list)), float(np.mean(ndcg3_list))


def measure_latency(model_obj, X_sample: pd.DataFrame, n_single: int = 300):
    rng = np.random.default_rng(42)
    idxs = rng.choice(len(X_sample), size=min(n_single, len(X_sample)), replace=False)
    times_ms = []
    for idx in idxs:
        row = X_sample.iloc[[idx]]
        t0 = time.perf_counter()
        model_obj.predict_proba(row)
        times_ms.append((time.perf_counter() - t0) * 1000.0)

    t0 = time.perf_counter()
    model_obj.predict_proba(X_sample)
    batch_us = ((time.perf_counter() - t0) * 1e6) / len(X_sample)
    return float(np.median(times_ms)), float(np.percentile(times_ms, 95)), float(batch_us)


def evaluate_model(name: str, model_obj):
    train_acc = accuracy_score(y_train, model_obj.predict(X_train))
    val_acc = accuracy_score(y_val, model_obj.predict(X_val))

    y_proba = model_obj.predict_proba(X_test)
    y_pred = np.argmax(y_proba, axis=1)
    mrr, ndcg3 = compute_mrr_and_ndcg3(y_test, y_proba)
    med_ms, p95_ms, batch_us = measure_latency(model_obj, X_test)

    acc_12 = accuracy_score(y_test[mask_lop12_test], y_pred[mask_lop12_test])
    top3_12 = top_k_accuracy_score(
        y_test[mask_lop12_test], y_proba[mask_lop12_test], k=3, labels=labels_idx
    )

    return {
        "Model": name,
        "Train_Acc(%)": round(train_acc * 100, 2),
        "Val_Acc(%)": round(val_acc * 100, 2),
        "Test_Top1(%)": round(accuracy_score(y_test, y_pred) * 100, 2),
        "Train-Val(%)": round((train_acc - val_acc) * 100, 2),
        "Test_Top3(%)": round(top_k_accuracy_score(y_test, y_proba, k=3, labels=labels_idx) * 100, 2),
        "Macro_P(%)": round(precision_score(y_test, y_pred, average="macro", zero_division=0) * 100, 2),
        "Macro_R(%)": round(recall_score(y_test, y_pred, average="macro", zero_division=0) * 100, 2),
        "Macro_F1(%)": round(f1_score(y_test, y_pred, average="macro", zero_division=0) * 100, 2),
        "Weighted_F1(%)": round(f1_score(y_test, y_pred, average="weighted", zero_division=0) * 100, 2),
        "LogLoss": round(log_loss(y_test, y_proba, labels=labels_idx), 4),
        "MRR": round(mrr, 4),
        "NDCG@3": round(ndcg3, 4),
        "Lop12_Top1(%)": round(acc_12 * 100, 2),
        "Lop12_Top3(%)": round(top3_12 * 100, 2),
        "Latency_Med(ms)": round(med_ms, 2),
        "Latency_p95(ms)": round(p95_ms, 2),
        "Batch(us/mau)": round(batch_us, 2),
    }, y_pred


results = []

# 1. Huấn luyện LightGBM chính
print("\n[1/2] Đang huấn luyện LightGBM...")
lgbm_params = dict(
    objective="multiclass",
    num_class=len(le.classes_),
    n_estimators=1000,
    learning_rate=0.05,
    num_leaves=63,
    subsample_for_bin=50000,
    colsample_bytree=0.8,
    subsample=0.8,
    random_state=20261111,
    n_jobs=-1,
    verbose=-1,
)
lgbm_model = lgb.LGBMClassifier(**lgbm_params)
lgbm_model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)],
)
lgbm_metrics, lgbm_pred = evaluate_model("LightGBM", lgbm_model)

# 3-Fold CV cho LightGBM trên tập Train để đo độ ổn định
skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=20261111)
cv_scores = []
best_trees = max(lgbm_model.best_iteration_ or 200, 50)
for tr_idx, va_idx in skf.split(X_train, y_train):
    cv_clf = lgb.LGBMClassifier(**{**lgbm_params, "n_estimators": best_trees})
    cv_clf.fit(X_train.iloc[tr_idx], y_train[tr_idx])
    cv_scores.append(accuracy_score(y_train[va_idx], cv_clf.predict(X_train.iloc[va_idx])))
lgbm_metrics["CV_3Fold(%)"] = f"{np.mean(cv_scores)*100:.2f} ± {np.std(cv_scores)*100:.2f}"
results.append(lgbm_metrics)

# 2. Chạy các mô hình đối chiếu (Decision Tree, Random Forest, HistGradientBoosting)
if RUN_BASELINES:
    print("[2/2] Đang chạy các mô hình đối chiếu (DT, RF, HGB)...")
    prep_tree = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="constant", fill_value=-1.0), num_cols),
            ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cat_cols),
        ]
    )
    baselines = [
        ("DecisionTree", Pipeline([
            ("prep", prep_tree),
            ("clf", DecisionTreeClassifier(max_depth=12, min_samples_leaf=20, random_state=42)),
        ])),
        ("RandomForest", Pipeline([
            ("prep", prep_tree),
            ("clf", RandomForestClassifier(n_estimators=200, max_depth=None, min_samples_leaf=2, n_jobs=-1, random_state=42)),
        ])),
        ("HistGradientBoosting", HistGradientBoostingClassifier(
            max_iter=150, categorical_features="from_dtype", random_state=42
        )),
    ]
    for b_name, b_model in baselines:
        print(f"  -> Đang train {b_name}...")
        b_model.fit(X_train, y_train)
        b_metrics, _ = evaluate_model(b_name, b_model)
        b_metrics["CV_3Fold(%)"] = "-"
        results.append(b_metrics)

# 3. In bảng tổng hợp và xuất file CSV
summary_df = pd.DataFrame(results)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
print("\n=== BẢNG SO SÁNH ĐẦY ĐỦ CÁC CHỈ SỐ (TẬP TEST) ===")
print(summary_df.to_string(index=False))

summary_df.to_csv(MODEL_DIR / "model_comparison.csv", index=False, encoding="utf-8-sig")

cls_report_dict = classification_report(
    y_test, lgbm_pred, target_names=le.classes_, output_dict=True, zero_division=0
)
cls_report_df = pd.DataFrame(cls_report_dict).transpose()
cls_report_df.to_csv(MODEL_DIR / "lgbm_classification_report.csv", encoding="utf-8-sig")

print("\n=== F1-SCORE TỪNG NHÓM NGÀNH (LightGBM) ===")
print(classification_report(y_test, lgbm_pred, target_names=le.classes_, digits=4, zero_division=0))

# 4. Lưu model LightGBM để dùng cho Backend API
joblib.dump(lgbm_model, MODEL_DIR / "lgbm_nhom_nganh.joblib")
joblib.dump(le, MODEL_DIR / "label_encoder.joblib")
joblib.dump(feature_cols, MODEL_DIR / "feature_columns.joblib")
joblib.dump(cat_cols, MODEL_DIR / "cat_columns.joblib")
print(f"\nĐã lưu toàn bộ model và bảng chỉ số vào: {MODEL_DIR}")