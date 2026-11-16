# Hệ thống Chuyên gia & AI Tư vấn Ngành nghề THPT 2026

Tách từ notebook Colab thành 2 phần chạy độc lập trên máy tính (VS Code):

```
career-advisor/
├── backend/                     # FastAPI (Python)
│   ├── app/
│   │   ├── main.py              # API: /api/health, /api/meta, /api/advise
│   │   ├── engine.py            # Lõi hệ chuyên gia (CELL 4 của notebook)
│   │   └── schemas.py           # Kiểm tra dữ liệu đầu vào
│   ├── model/ai_expert_model_2026.json   # Mô hình đã huấn luyện sẵn
│   ├── training/
│   │   ├── train_model.py       # Huấn luyện lại (CELL 2 + 3 của notebook)
│   │   ├── catalog.py           # Danh mục 15 nhóm / 110 ngành
│   │   └── data/                # CSV dữ liệu
│   ├── tests/test_engine.py
│   └── requirements.txt
├── frontend/                    # HTML + CSS + JS thuần (không cần build)
│   ├── index.html, css/style.css
│   └── js/config.js (địa chỉ backend), js/app.js
└── .vscode/                     # launch / tasks / extensions
```

Luồng: **Frontend (cổng 5500)** → `POST /api/advise` → **Backend (cổng 8000)** → `engine.advise()` → JSON → Frontend hiển thị.

---

## Chuẩn bị

- **Python 3.10 trở lên** (kiểm tra: `python --version`; macOS/Linux dùng `python3`)
- **VS Code** + extension *Python* (và *Live Server* nếu muốn)

## Bước 1 — Mở project

VS Code → **File → Open Folder…** → chọn thư mục `career-advisor`.
Mở Terminal: **Terminal → New Terminal** (Ctrl+`).

## Bước 2 — Backend: cài môi trường

```bash
cd backend

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
# Nếu PowerShell chặn script:  Set-ExecutionPolicy -Scope Process Bypass

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Trong VS Code: Ctrl+Shift+P → **Python: Select Interpreter** → chọn `backend/.venv`.

## Bước 3 — Backend: (tùy chọn) huấn luyện lại mô hình

File `backend/model/ai_expert_model_2026.json` **đã có sẵn**, bạn có thể bỏ qua bước này.
Muốn huấn luyện lại từ dữ liệu 60.000 học sinh:

1. Copy `dataset_tu_van_nganh_nghe_thpt_2026.csv` vào `backend/training/data/`
   (`danh_muc_nganh_2026.csv` và `catalog.py` đã có sẵn).
2. Chạy (đang ở thư mục `backend/`):

```bash
python training/train_model.py --data-dir training/data
# thêm --gbdt nếu muốn huấn luyện cả mô hình GBDT (scikit-learn)
```

Mất khoảng 15–60 giây, in độ chính xác train/val/test và ghi đè file JSON.
(Kết quả mẫu: 15 nhóm top-1 ≈ 58.9%, top-3 ≈ 90.0%; 110 ngành top-5 ≈ 67.5%.)

## Bước 4 — Backend: chạy server

```bash
# đang ở backend/, venv đã bật
uvicorn app.main:app --reload --port 8000
```

Kiểm tra:
- http://127.0.0.1:8000/api/health → `{"status":"ok",...}`
- http://127.0.0.1:8000/docs → Swagger UI, thử `POST /api/advise` ngay trên trình duyệt

Hoặc bấm **F5** trong VS Code, chọn cấu hình **Backend: FastAPI (uvicorn)** (có thể đặt breakpoint).

## Bước 5 — Frontend: chạy

Mở **một Terminal mới** (giữ terminal backend chạy):

```bash
cd frontend
python -m http.server 5500        # macOS/Linux: python3 -m http.server 5500
```

Mở http://127.0.0.1:5500 — góc phải trên hiện **“Backend OK · 110 ngành”** là thành công.

Cách khác: cài extension **Live Server**, chuột phải `frontend/index.html` → **Open with Live Server**.

> Không nên mở trực tiếp file `index.html` bằng đường dẫn `file://` — hãy dùng một trong hai cách trên.

## Bước 6 — Sử dụng

1. Điền hồ sơ (khối lớp, khu vực, ngân sách, Holland, mức quan tâm, điểm học bạ, điểm thi).
2. Bấm **Chạy tư vấn ngành nghề 2026**.
3. Kết quả: ngành số 1, tổ hợp tối ưu, điểm sau ưu tiên, mức khả thi, phương thức xét tuyển, top 3 nhóm ngành, cảnh báo, top 5 ngành.

Quy ước: ô điểm để **trống hoặc 0** = không học / không thi. Chọn lớp 10–11 thì ô điểm thi tự khóa
(hệ thống ước lượng điểm thi từ học bạ).

---

## Gọi API trực tiếp (không cần frontend)

```bash
curl -X POST http://127.0.0.1:8000/api/advise -H "Content-Type: application/json" -d '{
  "lop": 12, "ngan_sach_hoc_phi_trieu_nam": 35, "uu_tien_dinh_huong": "Thu nhập cao",
  "holland": {"R":3.5,"I":4.8,"A":2.4,"S":2.6,"E":3.2,"C":3.9},
  "quan_tam": {"CNTT":5,"KTCN":4},
  "hb":  {"T":9.0,"V":7.5,"A":8.4,"L":8.6,"H":8.1,"I":9.2,"C":8.5},
  "thi": {"T":8.75,"V":7.25,"L":8.5,"I":9.0}
}'
```

Mã môn: T Toán · V Văn · A Anh · L Lý · H Hóa · B Sinh · S Sử · D Địa · K KTPL · I Tin · C Công nghệ.

## Chạy kiểm thử

```bash
cd backend
python tests/test_engine.py        # in "OK"
```

## Lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| Frontend báo “Backend chưa chạy” | Backend chưa bật, hoặc sai cổng → sửa `frontend/js/config.js` (`API_BASE`) |
| `Không tìm thấy file mô hình` | Chạy `python training/train_model.py ...` (Bước 3) |
| `ModuleNotFoundError: app` | Phải chạy `uvicorn` từ thư mục `backend/`, không phải thư mục gốc |
| `Address already in use` | Đổi cổng: `--port 8001` và sửa `config.js` tương ứng |
| Lỗi CORS trên trình duyệt | Mở frontend qua `http://127.0.0.1:5500` (không dùng `file://`); backend đã bật CORS cho mọi nguồn |
| PowerShell không kích hoạt được venv | `Set-ExecutionPolicy -Scope Process Bypass` rồi kích hoạt lại |

## Ghi chú

- Dữ liệu 60.000 học sinh là **dữ liệu mô phỏng (synthetic)**, xem `backend/training/data/README_tu_dien_du_lieu.md`.
- Mô hình dùng để tham khảo, không thay thế tư vấn tuyển sinh chính thức.
- Mô hình GBDT (CELL 3 trong notebook) chỉ để so sánh; backend chỉ dùng mô hình Hybrid Utility Ranking + luật chuyên gia.
