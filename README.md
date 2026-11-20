# 🎓 HỆ CHUYÊN GIA TƯ VẤN CHỌN NGÀNH/NGHỀ THPT 2026

## 1. Giới thiệu dự án

**Career Advisor 2026** là hệ thống hỗ trợ học sinh THPT (lớp 10–12) định hướng và lựa chọn nhóm ngành, ngành học và phương thức xét tuyển đại học phù hợp dựa trên năng lực học tập (điểm học bạ, điểm thi tốt nghiệp THPT), trắc nghiệm tính cách **Holland (RIASEC)**, mức độ quan tâm, ngân sách học phí và các điều kiện ưu tiên.

Hệ thống sử dụng **Hệ chuyên gia dựa trên luật IF–THEN với cơ chế suy diễn tiến (Forward Chaining)** làm lõi tư vấn chính — đáp ứng đầy đủ yêu cầu về cơ sở tri thức luật, xử lý xung đột (Conflict Resolution), hệ số tin cậy (Certainty Factor – MYCIN) và giải trình chuỗi suy diễn (Explanation Trace). Bên cạnh đó, dự án tích hợp quy trình huấn luyện và đối chiếu thực nghiệm với các mô hình **Machine Learning** (LightGBM, HistGradientBoosting, Random Forest, Decision Tree) trên cùng tập dữ liệu kiểm thử.

### Tính năng cốt lõi

- **Cơ sở tri thức SQLite (`kb.sqlite`)**: Quản lý 15 nhóm ngành, 110 ngành học (tham khảo phổ điểm chuẩn công khai theo 3 mốc Top / Trung bình / Cơ bản), tổ hợp xét tuyển và **50 luật IF–THEN** có đầy đủ độ ưu tiên (`priority`) và độ tin cậy (`certainty`).
- **Suy diễn tiến đa vòng (Forward Chaining)**: Thực thi qua 6 pha (`normalize → screen → score → aggregate → admission → warn`); vòng 1 chấm điểm và xác định nhóm ngành dẫn đầu (`top_group`) kèm truy vấn điểm chuẩn thật từ bảng `majors`, vòng 2 đánh giá khả thi, phương thức xét tuyển và cảnh báo.
- **Xử lý xung đột (Conflict Resolution)**: Khi nhiều luật cùng khớp và ghi đè cùng khóa (`set`), hệ thống phân xử theo thứ tự `phase → priority DESC → certainty DESC → rule_id ASC` và ghi nhận rõ luật thắng (`suppressed_by`) vào vết giải trình.
- **Gộp hệ số tin cậy (Certainty Factor – MYCIN)**: Tính song song độ tin cậy tổng hợp (`certainty_cf`) từ các luật ủng hộ/bác bỏ cho từng nhóm ngành.
- **Giải trình chuỗi suy diễn (Explanation Trace)**: Lưu toàn bộ bước suy diễn (cả luật kích hoạt lẫn luật bị đè) vào bảng `sessions` và `trace_steps`, đồng thời hiển thị trực quan trên giao diện web.

## 2. Công nghệ sử dụng

| Thành phần | Công nghệ |
| :--- | :--- |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend & API | Python 3.11+, FastAPI, Uvicorn, Pydantic |
| Cơ sở tri thức & Vết suy diễn | SQLite (`sqlite3`) |
| Machine Learning (Đối chiếu) | LightGBM, Scikit-learn, Joblib |
| Xử lý dữ liệu | Pandas, NumPy |
| Công cụ phát triển | Visual Studio Code |

## 3. Cấu trúc dự án

```text
he_thong_tu_van_nganh_nghe_thpt_2026/
│
├── backend/
│   ├── app/
│   │   ├── main.py                       # Khởi tạo FastAPI và các REST API endpoints
│   │   ├── db.py                         # Khởi tạo SQLite kb.sqlite, danh mục ngành và 50 luật IF–THEN
│   │   ├── inference.py                  # Bộ suy diễn tiến đa vòng, xử lý xung đột & gộp CF MYCIN
│   │   └── schemas.py                    # Kiểm tra dữ liệu đầu vào/đầu ra (Pydantic)
│   │
│   ├── data/
│   │   ├── danh_muc_nganh_2026.csv       # Danh mục 15 nhóm ngành, 110 ngành & 3 mốc điểm chuẩn
│   │   ├── dataset_tu_van_nganh_nghe_thpt_2026.csv  # Bộ dữ liệu 60.000 hồ sơ học sinh
│   │   └── kb.sqlite                     # Cơ sở tri thức SQLite (tự khởi tạo nếu chưa có)
│   │
│   ├── models/
│   │   ├── lgbm_nhom_nganh.joblib        # Mô hình LightGBM đã huấn luyện
│   │   ├── label_encoder.joblib          # Bộ mã hóa 15 nhóm ngành
│   │   ├── feature_columns.joblib        # Danh sách đặc trưng đầu vào
│   │   ├── cat_columns.joblib            # Danh sách cột phân loại
│   │   ├── model_comparison.csv          # Bảng đối chiếu Hệ chuyên gia vs 4 mô hình ML
│   │   └── lgbm_classification_report.csv
│   │
│   ├── training/
│   │   ├── train_lgbm.py                 # Huấn luyện LightGBM & 3 mô hình baseline (DT, RF, HGB)
│   │   └── evaluate_expert.py            # Đánh giá Hệ chuyên gia Forward Chaining trên tập Test
│   │
│   ├── tests/
│   │   └── test_api.py                   # Kiểm thử tích hợp các endpoint API
│   │
│   └── requirements.txt                  # Danh sách thư viện Python
│
├── frontend/
│   ├── css/
│   │   └── style.css                     # Giao diện responsive, hỗ trợ Dark mode
│   ├── js/
│   │   ├── config.js                     # Cấu hình địa chỉ Backend API
│   │   └── app.js                        # Gọi API, hiển thị Top ngành & Chuỗi suy diễn/Xung đột
│   └── index.html                        # Trang giao diện chính
│
├── .gitignore
└── README.md
```

## 4. Danh sách API Endpoints

| Endpoint | Phương thức | Mô tả |
| :--- | :--- | :--- |
| `/api/health` | `GET` | Kiểm tra trạng thái Backend và số lượng ngành, nhóm, luật trong `kb.sqlite` |
| `/api/meta` | `GET` | Trả danh mục 11 môn học, 15 nhóm ngành, tổ hợp xét tuyển và giá trị ưu tiên |
| `/api/rules` | `GET` | Liệt kê toàn bộ 50 luật IF–THEN kèm pha, `priority`, `certainty`, điều kiện và hành động |
| `/api/advise?explain=true` | `POST` | Chạy suy diễn tiến tư vấn ngành nghề, trả Top 3 nhóm ngành (`certainty_cf`), Top 5 ngành, khả thi, phương thức xét tuyển, cảnh báo và `trace_preview` |
| `/api/sessions/{session_id}/trace` | `GET` | Truy xuất toàn bộ chuỗi suy diễn và các luật bị đè (`suppressed_by`) của một phiên tư vấn |

## 5. Hướng dẫn cài đặt và chạy dự án (Windows / VS Code)

### Bước 1. Tải mã nguồn

```powershell
git clone https://github.com/duonggiabao296-wq/he_thong_tu_van_nganh_nghe_thpt_2026.git
cd he_thong_tu_van_nganh_nghe_thpt_2026
```

### Bước 2. Tạo môi trường ảo và cài thư viện Backend

Mở Terminal trong VS Code tại thư mục gốc dự án:

```powershell
cd backend
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install lightgbm scikit-learn pandas numpy joblib
```

### Bước 3. Khởi tạo lại cơ sở tri thức & chạy đánh giá (Tùy chọn)

Nếu bạn vừa chỉnh sửa bộ luật trong `backend/app/db.py` hoặc muốn chạy lại toàn bộ thực nghiệm so sánh:

```powershell
# Xóa kb.sqlite cũ để hệ thống nạp lại 50 luật mới nhất
Remove-Item .\data\kb.sqlite -ErrorAction SilentlyContinue

# Huấn luyện lại LightGBM + 3 mô hình baseline (đã loại cột rò rỉ nhãn & 7 cột nhạy cảm)
python .\training\train_lgbm.py

# Đánh giá Hệ chuyên gia Forward Chaining trên cùng tập Test (8.896 học sinh)
python .\training\evaluate_expert.py
```

### Bước 4. Khởi chạy Backend FastAPI (Cổng 8000)

Tại Terminal đang kích hoạt `(.venv)` trong thư mục `backend`:

```powershell
uvicorn app.main:app --reload --port 8000
```

Khi Terminal hiện `Uvicorn running on http://127.0.0.1:8000` là Backend đã sẵn sàng. Có thể kiểm tra nhanh tại:

- **Swagger UI (tài liệu API):** `http://127.0.0.1:8000/docs`
- **Danh sách 50 luật:** `http://127.0.0.1:8000/api/rules`

### Bước 5. Khởi chạy Frontend (Cổng 5500)

Giữ nguyên Terminal Backend đang chạy, mở **Terminal thứ 2** tại thư mục gốc dự án:

```powershell
cd frontend
python -m http.server 5500
```

Mở trình duyệt truy cập **`http://127.0.0.1:5500`**. Khi góc trên bên phải hiển thị nhãn xanh **Backend OK**, hệ thống đã kết nối thành công.

### Bước 6. Chạy kiểm thử tự động (Tùy chọn)

Khi Backend đang chạy ở cổng 8000, mở thêm Terminal tại `backend` (đã bật `.venv`) và chạy:

```powershell
python .\tests\test_api.py
```

## 6. Kết quả thực nghiệm & Đối chiếu (Tập Test: 8.896 học sinh, 15 nhóm ngành)

Tập dữ liệu gồm 60.000 hồ sơ học sinh chia thành **Train (42.087) / Val (9.017) / Test (8.896)**. Toàn bộ 22 cột đầu ra cùng các cột điểm chuẩn đều bị khóa để chống rò rỉ nhãn (`DROP_LEAKAGE`), đồng thời loại bỏ 7 cột nhạy cảm (`gioi_tinh`, `dan_toc_thieu_so`, `dan_toc`, `tinh_thanh`, `vung_mien`, `khu_vuc_cu_tru`, `loai_truong`) để đảm bảo tính công bằng (`DROP_FAIRNESS`).

| Mô hình | Test Top-1 (%) | Test Top-3 (%) | Macro-F1 (%) | Weighted-F1 (%) | Lớp 12 Top-1 (%) | Độ trễ trung vị (ms) | Giải trình luật |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **ExpertSystem_ForwardChaining** (50 luật SQLite) | 31.08 | 65.85 | 27.04 | 29.94 | 27.64 | **0.52** | Đầy đủ (Trace + Xung đột + CF) |
| **LightGBM** | **54.36** | **86.02** | **49.79** | **53.74** | **56.10** | 3.45 | Không (Hộp đen) |
| **HistGradientBoosting** | 52.59 | 85.24 | 48.05 | 52.01 | 54.65 | 13.39 | Không (Hộp đen) |
| **RandomForest** | 48.01 | 80.53 | 40.06 | 45.99 | 48.32 | 33.65 | Khó giải thích |
| **DecisionTree** | 39.01 | 63.60 | 32.28 | 37.36 | 38.90 | 4.10 | Trích xuất nhánh cây |

**Nhận xét chính:**

- **Hệ chuyên gia Forward Chaining** có tốc độ phản hồi nhanh nhất (**0.52 ms/hồ sơ**, nhanh gấp ~6.6 lần LightGBM và ~64 lần Random Forest), hoàn toàn không bị quá khớp (Overfitting), dễ cập nhật quy chế tuyển sinh trong SQLite mà không cần huấn luyện lại, và cung cấp đầy đủ chuỗi giải trình kèm xử lý xung đột.
- **Các mô hình Machine Learning** (dẫn đầu là LightGBM với Top-3 đạt 86.02%) khai thác tốt các quan hệ phi tuyến từ dữ liệu lớn nhưng có hiện tượng quá khớp (Random Forest lệch Train–Val > 50 điểm %) và không tự giải trình được theo quy chế tuyển sinh.

## 7. Lưu ý khi sử dụng & đóng góp

1. Không đẩy thư mục môi trường ảo `.venv/`, `__pycache__/` hoặc tệp tạm lên GitHub (đã được cấu hình chặn trong `.gitignore`).
2. Luôn chạy Backend ở cổng `8000` trước khi mở giao diện Frontend ở cổng `5500`.
3. Khi sửa luật trong `backend/app/db.py`, cần xóa `backend/data/kb.sqlite` rồi khởi động lại Backend để nạp lại cơ sở tri thức mới.
4. Nếu đổi cổng Backend, cập nhật lại địa chỉ API trong `frontend/js/config.js`.

## 8. Thông tin dự án

- **Đề tài:** Hệ chuyên gia tư vấn chọn ngành/nghề cho học sinh THPT (2026)
- **Repository:** `https://github.com/duonggiabao296-wq/he_thong_tu_van_nganh_nghe_thpt_2026`
- **Mục đích:** Bài tập lớn môn Trí tuệ nhân tạo — Trường Đại học Giao thông Vận tải TP. Hồ Chí Minh (UTH).
