# 🎓 HỆ THỐNG CHUYÊN GIA & AI TƯ VẤN NGÀNH NGHỀ THPT 2026

## 1. Giới thiệu dự án

**Career Advisor 2026** là hệ thống hỗ trợ học sinh THPT định hướng và lựa chọn ngành nghề phù hợp dựa trên thông tin cá nhân, năng lực học tập, sở thích và định hướng nghề nghiệp.

Dự án kết hợp giữa hệ thống chuyên gia (Expert System) và Machine Learning nhằm phân tích dữ liệu đầu vào và đề xuất các nhóm ngành nghề phù hợp với học sinh.

### Mục tiêu chính

- Hỗ trợ học sinh định hướng nghề nghiệp.
- Phân tích các yếu tố liên quan đến năng lực và sở thích.
- Sử dụng AI để dự đoán nhóm ngành nghề phù hợp.
- Đề xuất Top 3 nhóm ngành có mức độ phù hợp cao.
- Xây dựng giao diện trực quan, dễ sử dụng.

## 2. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Machine Learning | LightGBM, Scikit-learn |
| Xử lý dữ liệu | Pandas, NumPy |
| Lưu trữ mô hình | Joblib |
| API Server | Uvicorn |
| Công cụ phát triển | Visual Studio Code |

## 3. Cấu trúc dự án

```text
career_advisor_2026/
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # Khởi tạo API
│   │   ├── db.py                   # Xử lý dữ liệu
│   │   ├── inference.py            # Dự đoán bằng mô hình AI
│   │   └── schemas.py              # Cấu trúc dữ liệu API
│   │
│   ├── data/                       # Dataset
│   │
│   ├── models/                     # Mô hình đã huấn luyện
│   │
│   ├── training/
│   │   ├── train_lgbm.py           # Huấn luyện LightGBM
│   │   └── train_and_build_expert_model.py
│   │
│   ├── tests/                      # Kiểm thử API
│   │
│   └── requirements.txt            # Thư viện Python
│
├── frontend/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   ├── app.js
│   │   └── config.js
│   │
│   └── index.html                  # Giao diện chính
│
├── .vscode/
│
└── README.md
```

## 4. Hướng dẫn cài đặt và chạy dự án

### Bước 1. Chuẩn bị môi trường

Cài đặt các công cụ cần thiết:

- Python 3.11 trở lên.
- Visual Studio Code.
- Git (nếu tải dự án bằng Git).

Tải source code từ GitHub:

```bash
git clone https://github.com/duonggiabao296-wq/he_thong_tu_van_nganh_nghe_thpt_2026.git
```

Mở thư mục dự án bằng Visual Studio Code.

### Bước 2. Cài đặt Backend

Mở Terminal tại thư mục gốc dự án:

```bash
cd backend
```

Tạo môi trường ảo Python:

```bash
python -m venv .venv
```

Kích hoạt môi trường ảo trên Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Cài đặt thư viện:

```bash
pip install -r requirements.txt
```

Nếu cần huấn luyện LightGBM và thư viện chưa có trong requirements:

```bash
pip install lightgbm
```

### Bước 3. Chuẩn bị dữ liệu và mô hình

Kiểm tra thư mục:

```text
backend/
├── data/
└── models/
```

Đảm bảo các file dataset và mô hình cần thiết đã được đặt đúng vị trí.

Nếu muốn huấn luyện lại mô hình LightGBM, chạy:

```bash
python training/train_lgbm.py
```

Sau khi huấn luyện thành công, các mô hình và bảng đánh giá được lưu trong thư mục `backend/models/`.

Nếu chỉ muốn sử dụng mô hình đã huấn luyện, có thể bỏ qua bước huấn luyện, miễn là các file mô hình cần thiết đã có sẵn.

### Bước 4. Khởi chạy Backend

Tại thư mục `backend`, chạy:

```bash
uvicorn app.main:app --reload --port 8000
```

Nếu khởi chạy thành công, Terminal hiển thị:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

Kiểm tra API bằng trình duyệt:

**http://127.0.0.1:8000/docs**

Đây là giao diện Swagger UI giúp kiểm tra và thử nghiệm các API của hệ thống.

### Bước 5. Khởi chạy Frontend

Giữ nguyên Terminal Backend đang chạy.

Mở Terminal mới tại thư mục gốc dự án:

```bash
cd frontend
```

Khởi chạy máy chủ giao diện:

```bash
python -m http.server 5500
```

Mở trình duyệt tại:

**http://localhost:5500**

Lúc này, hệ thống có thể được sử dụng thông qua giao diện Frontend nếu cấu hình kết nối API chính xác.

## 5. Kết quả huấn luyện Machine Learning

Dự án sử dụng LightGBM để thực hiện bài toán phân loại nhiều lớp (Multi-class Classification), dự đoán nhóm ngành nghề phù hợp dựa trên các đặc trưng đầu vào.

Thông tin lần huấn luyện được ghi nhận:

- Số đặc trưng đầu vào: 83.
- Số nhóm ngành nghề: 15.
- Số mẫu huấn luyện: 42.087.
- Số mẫu kiểm thử: 8.896.

### Kết quả đánh giá mô hình

| Chỉ số | Kết quả |
|---|---:|
| Top-1 Accuracy | 54.36% |
| Top-3 Accuracy | 86.02% |
| Macro-F1 Score | 49.79% |
| Weighted-F1 Score | 53.74% |

**Ý nghĩa:**

- Top-1 Accuracy: Tỷ lệ dự đoán đúng nhóm ngành ở vị trí đầu tiên.
- Top-3 Accuracy: Tỷ lệ mẫu có nhóm ngành thực tế xuất hiện trong 3 đề xuất hàng đầu.
- Macro-F1: Đánh giá hiệu suất trung bình giữa các nhóm ngành, không phụ thuộc nhiều vào số lượng mẫu từng nhóm.
- Weighted-F1: Đánh giá F1 có xét đến số lượng mẫu của từng nhóm ngành.

*Lưu ý: Đây là kết quả của lần huấn luyện và đánh giá được ghi nhận trong quá trình phát triển dự án. Kết quả có thể thay đổi khi dữ liệu hoặc cấu hình huấn luyện thay đổi.*

## 6. Lưu ý khi sử dụng

1. Cần cài đặt đầy đủ thư viện Python trước khi chạy Backend.
2. Không xóa các file mô hình mà chương trình đang sử dụng.
3. Đảm bảo dataset có đúng định dạng và đường dẫn.
4. Backend phải được khởi chạy trước khi sử dụng Frontend.
5. Kiểm tra cấu hình API trong `frontend/js/config.js` nếu giao diện không kết nối được Backend.
6. Không chia sẻ file `.env`, mật khẩu hoặc thông tin cá nhân nhạy cảm lên GitHub.

---

## 7. Thông tin dự án

**Tên dự án:** Hệ thống Chuyên gia & AI Tư vấn Ngành nghề THPT 2026

**Tên tiếng Anh:** Career Advisor 2026

**GitHub Repository:**

https://github.com/duonggiabao296-wq/he_thong_tu_van_nganh_nghe_thpt_2026

**Mục đích:** Nghiên cứu, học tập và xây dựng ứng dụng AI hỗ trợ định hướng nghề nghiệp cho học sinh THPT.

---

⭐ Nếu thấy dự án hữu ích, hãy Star repository để ủng hộ!