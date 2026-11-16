# Bộ dữ liệu tư vấn chọn ngành/nghề cho học sinh THPT Việt Nam – mùa tuyển sinh 2026

**Đây là dữ liệu mô phỏng (synthetic), không phải dữ liệu thật của học sinh.** Mục đích: huấn luyện/kiểm thử hệ thống chuyên gia hoặc mô hình tư vấn ngành nghề.

- `dataset_tu_van_nganh_nghe_thpt_2026.csv`: 60.000 học sinh × 111 cột (UTF-8 có BOM, mở được bằng Excel). Lớp 10: 17.924 · lớp 11: 17.958 · lớp 12: 24.118.
- `danh_muc_nganh_2026.csv`: 110 ngành thuộc 15 nhóm ngành – tri thức nền cho phần luật của hệ chuyên gia (hồ sơ Holland, môn then chốt, tổ hợp xét tuyển, 3 mức điểm chuẩn, học phí tối thiểu).
- `generate.py` + `catalog.py`: script sinh dữ liệu, chạy lại với `python3 generate.py <số_dòng> <thư_mục_ra>` để tạo bộ lớn hơn (seed cố định, tái lập được).

## 1. Cơ sở hiệu chỉnh theo thực tế 2026

| Nguồn | Dùng để |
|---|---|
| VnExpress – phổ điểm các tổ hợp 2026 | Điểm trung bình tổ hợp: A00 19,41 · D01 19,01 · A01 18,41 · C00 17,23 · B00 16,69; ngưỡng sàn 15 điểm |
| Xây dựng chính sách (Chính phủ) – phổ điểm thi TN THPT 2026 | Tỷ lệ dưới trung bình / ≥8 từng môn (Toán 42,34%, Văn 15,2%, Lý 42,69%, Hóa 24,44%, Sinh 34,7%, Sử 32,84%, Địa >50%, Anh 55,6%, Tin 27,83%…) → suy ra trung bình và độ lệch chuẩn từng môn |
| Báo Chính phủ – điểm chuẩn ĐH 2026 | Neo điểm chuẩn nhóm trường top cho một số ngành (KH dữ liệu & AI 29,54; Kiểm toán 28,84; Y khoa 27,43; SP Toán 27,55; Logistics 28,5; Luật kinh tế 24,83…) |
| Tuổi Trẻ – hướng dẫn quy đổi điểm 2026 | Cột `phan_vi_to_hop_de_xuat` (bách phân vị trong cùng tổ hợp) và không quy đổi "bắc cầu" giữa tổ hợp |

Kết quả kiểm tra trên 24.118 học sinh lớp 12 (tính trên thí sinh của từng môn): tỷ lệ dưới 5 điểm sai lệch so với mục tiêu ≤ 3 điểm phần trăm (Toán 40,2% vs 42,3%; Lý 40,5% vs 42,7%; Hóa 24,2% vs 24,4%; Sinh 33,4% vs 34,7%; Anh 53,8% vs 55,6%; Tin 27,3% vs 27,8%); điểm trung bình tổ hợp sai lệch ≤ 0,6 điểm (A00 19,03; D01 18,37; A01 18,98; C00 17,76; B00 16,80).

**Giả định do mình đặt (bài báo không cung cấp):** phân phối chuẩn xấp xỉ cho từng môn; Hóa, Sử dùng độ lệch chuẩn giả định; Công nghệ (TB 6,5) hoàn toàn giả định; điểm chuẩn "trung bình hệ thống" = 15 + 0,65 × (điểm chuẩn top − 15) và "nhóm cơ bản" = trung bình − 3 (không phải số liệu công bố); toàn bộ danh mục ngành là ước tính, không phải danh sách chính thức. Mã tổ hợp chỉ gán cho các mã đã ổn định (A00, A01, B00, C00, D01…); tổ hợp có Tin học/Công nghệ ghi `MOI` vì mã do từng trường quy định.

## 2. Cột dữ liệu

**Định danh & chia tập:** `ma_hoc_sinh`, `tap` (train 70% / val 15% / test 15%), `lop` (10/11/12).

**Nhân khẩu – gia đình:** `gioi_tinh`, `tinh_thanh` (34 tỉnh/thành sau sắp xếp 2025), `vung_mien` (6 vùng), `khu_vuc_cu_tru`, `loai_truong`, `dan_toc_thieu_so`, `khu_vuc_uu_tien` (KV1/KV2-NT/KV2/KV3), `diem_uu_tien_khu_vuc`, `nghe_cha`, `nghe_me`, `hoc_van_cha_me_cao_nhat` (1–5), `muc_thu_nhap_gia_dinh` (1–5), `ngan_sach_hoc_phi_trieu_nam`, `san_sang_hoc_xa_nha`, `muon_du_hoc`, `uu_tien_dinh_huong` (thu nhập / ổn định / đam mê / đóng góp / gần nhà), `gia_dinh_goi_y_nhom_nganh`.

**Chương trình GDPT 2018:** `to_hop_mon_chon` (4 môn học sâu, 16 gói phổ biến), `chon_ly … chon_cn` (cờ 0/1).

**Học bạ:** `hb_toan … hb_cn` (điểm TB từng môn; trống nếu không học), `gpa_hoc_ba`, `hoc_luc` (Tốt/Khá/Đạt/Chưa đạt theo quy tắc TT22), `hanh_kiem`.

**Hướng nghiệp:** `holland_R/I/A/S/E/C` (thang 1–5), `ma_holland_3`, `ky_nang_*` (1–5), `the_luc` (1–5), `quan_tam_<nhóm ngành>` ×15 (1–5).

**Chứng chỉ – thành tích:** `ielts` (trống nếu không có), `dgnl_hsa_150` (chỉ lớp 12, thang 150), `giai_hsg`, `mon_hsg`.

**Điểm thi tốt nghiệp THPT 2026 (chỉ lớp 12, bước 0,25):** `mon_thi_tu_chon_1/2`, `thi_toan … thi_cn` (trống nếu không thi), `tong_4_mon_thi`.

**Nhãn tư vấn (đầu ra của "chuyên gia"):**
- `nhom_nganh_top1/2/3`, `ma_nhom_nganh_top1` – 15 lớp; `nganh_goi_y_1/2/3` – 110 lớp.
- `diem_phu_hop_top1` (0–100), `do_tin_cay_nhom_top1` (0–1).
- `to_hop_xet_tuyen_de_xuat`, `ma_to_hop_de_xuat`, `tong_diem_to_hop_de_xuat` (lớp 12: điểm thi thật; lớp 10/11: điểm dự kiến từ học bạ), `tong_diem_sau_uu_tien` (ưu tiên khu vực quy đổi giảm dần khi tổng ≥ 22,5).
- `diem_chuan_nhom_truong_top_top1`, `diem_chuan_trung_binh_top1`, `diem_chuan_nhom_co_ban_top1`, `chenh_lech_diem_so_voi_trung_binh_nganh`.
- `muc_do_kha_thi_top1`: Cao / Trung bình / Thấp - chỉ nhóm trường cơ bản / Rất thấp / Dưới ngưỡng sàn 15 điểm / Chưa đủ tổ hợp.
- `phan_vi_to_hop_de_xuat` (lớp 12), `phuong_thuc_xet_tuyen_de_xuat` (lớp 12: thi THPT / học bạ / ĐGNL / IELTS kết hợp / tuyển thẳng).
- `canh_bao` (nhiều cảnh báo nối bằng " | ", hoặc "Không").
- `du_dinh_nhom_nganh_cua_hoc_sinh` (dự định tự thân, chịu ảnh hưởng gia đình nhiều hơn năng lực), `khop_du_dinh_voi_tu_van` (khoảng 27% khớp – dùng để huấn luyện mô hình phát hiện lệch hướng).

## 3. Cách nhãn được tạo

Với mỗi học sinh và mỗi ngành, điểm phù hợp = độ khớp Holland + mức quan tâm + năng lực ở các môn then chốt + khả năng đạt điểm so với điểm chuẩn + yếu tố thị trường + ngân sách + gia đình gợi ý + giá trị ưu tiên, trừ phạt khi không đủ tổ hợp, cộng nhiễu Gumbel để mô phỏng sự khác biệt giữa các chuyên gia. Ngành điểm cao nhất là `nganh_goi_y_1`. **Đây là nhãn luật + nhiễu, không phải nhãn từ tư vấn viên thật.** Mô hình baseline (gradient boosting) đạt top-1 ≈ 55% và top-3 ≈ 87% cho 15 nhóm ngành (đoán theo lớp đông nhất chỉ 12%), nghĩa là dữ liệu học được nhưng không tầm thường.

## 4. Lưu ý khi huấn luyện

- **Rò rỉ nhãn:** khi dự đoán `nhom_nganh_top1` hay `nganh_goi_y_*`, không đưa vào đặc trưng các cột nhãn khác (`tong_diem_*`, `diem_chuan_*`, `muc_do_kha_thi_top1`, `canh_bao`, `phuong_thuc_*`, `phan_vi_*`, `to_hop_xet_tuyen_de_xuat`, `diem_phu_hop_top1`…).
- **Công bằng:** có tương quan giới tính nhẹ ở Holland (R cao hơn ở nam, S/A cao hơn ở nữ) và chênh lệch điểm theo vùng/trường để phản ánh thực tế khảo sát. Nên loại `gioi_tinh`, `dan_toc_thieu_so`, `tinh_thanh` khỏi đặc trưng của mô hình tư vấn.
- Điểm thi chỉ có ở lớp 12; lớp 10/11 dùng học bạ. Có thể huấn luyện riêng theo `lop`.
- Số liệu phân phối là mô phỏng hiệu chỉnh theo thống kê tổng hợp trên báo, **không** thay thế được dữ liệu điểm thi thật khi cần độ chính xác thống kê.
