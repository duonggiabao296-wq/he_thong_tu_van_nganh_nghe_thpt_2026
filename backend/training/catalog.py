# -*- coding: utf-8 -*-
"""Danh mục nhóm ngành / ngành / tổ hợp dùng cho bộ dữ liệu tư vấn hướng nghiệp THPT 2026."""

SUBJ = ['T', 'V', 'A', 'L', 'H', 'B', 'S', 'D', 'K', 'I', 'C']
SN = {'T': 'Toán', 'V': 'Ngữ văn', 'A': 'Tiếng Anh', 'L': 'Vật lí', 'H': 'Hóa học', 'B': 'Sinh học',
      'S': 'Lịch sử', 'D': 'Địa lí', 'K': 'GD KT&PL', 'I': 'Tin học', 'C': 'Công nghệ'}
SSHORT = {'T': 'Toán', 'V': 'Văn', 'A': 'Anh', 'L': 'Lý', 'H': 'Hóa', 'B': 'Sinh',
          'S': 'Sử', 'D': 'Địa', 'K': 'KTPL', 'I': 'Tin', 'C': 'CN'}
SCOL = {'T': 'toan', 'V': 'van', 'A': 'anh', 'L': 'ly', 'H': 'hoa', 'B': 'sinh',
        'S': 'su', 'D': 'dia', 'K': 'ktpl', 'I': 'tin', 'C': 'cn'}
ELECTIVES = ['L', 'H', 'B', 'S', 'D', 'K', 'I', 'C']

# mã tổ hợp chuẩn (chỉ các mã phổ biến đã ổn định); tổ hợp có Tin/Công nghệ -> 'MOI' (mã do trường quy định)
CODE = {}
for k, v in {'TLH': 'A00', 'TLA': 'A01', 'TLB': 'A02', 'THB': 'B00', 'TBA': 'D08', 'VSD': 'C00', 'TVL': 'C01',
             'TVH': 'C02', 'TVS': 'C03', 'TVD': 'C04', 'TVK': 'C14', 'TVA': 'D01', 'THA': 'D07', 'TSA': 'D09',
             'TDA': 'D10', 'VSA': 'D14', 'VDA': 'D15', 'TBV': 'B03', 'TLD': 'A04', 'TLK': 'A10', 'TSD': 'A07',
             'TSK': 'A08', 'TDK': 'A09', 'THK': 'A11', 'VKA': 'D66', 'VSK': 'C19', 'VDK': 'C20', 'TAK': 'D84'}.items():
    CODE[frozenset(k)] = v

# id, tên, vector Holland (R,I,A,S,E,C), môn then chốt, tổ hợp mặc định,
# học phí tối thiểu (triệu/năm), "uy tín xã hội", tag giá trị [thu nhập, ổn định, đam mê, xã hội, tiết kiệm]
GROUPS = [
    ('CNTT', 'Công nghệ thông tin, AI & Dữ liệu', dict(R=.3, I=1, A=.1, S=0, E=.1, C=.5), 'T.4,L.2,I.2,A.2',
     'TLH,TLA,TVA,TLI,TVI,TAI,TLC', 20, .9, [1, 0, .5, 0, 0]),
    ('KTCN', 'Kỹ thuật, Cơ khí, Điện & Tự động hóa', dict(R=1, I=.6, A=.1, S=0, E=.1, C=.3), 'T.35,L.35,H.15,C.15',
     'TLH,TLA,TLC,TLI,THA,TLK', 18, .5, [.8, .5, .4, 0, 0]),
    ('KHTN', 'Khoa học tự nhiên & Toán', dict(R=.2, I=1, A=.1, S=.1, E=0, C=.3), 'T.3,L.25,H.25,B.2',
     'TLH,TLA,TLB,THB,THA,TBA', 15, .3, [.2, .4, 1, .3, .2]),
    ('YDUOC', 'Y, Dược & Sức khỏe', dict(R=.3, I=.7, A=0, S=1, E=.1, C=.2), 'H.35,B.35,T.2,A.1',
     'THB,TLH,THA,TBA,TBV,THK', 30, 1.0, [.8, .9, .3, 1, 0]),
    ('KTTCNH', 'Kinh tế, Tài chính, Ngân hàng & Kế toán', dict(R=0, I=.4, A=0, S=.1, E=.7, C=1), 'T.4,A.25,V.2,L.15',
     'TLH,TLA,TVA,TVL,TVK,TAK,TVI', 20, .8, [1, .7, .2, 0, 0]),
    ('QTKD', 'Quản trị, Marketing, Thương mại & Logistics', dict(R=0, I=.1, A=.3, S=.4, E=1, C=.4), 'T.3,A.3,V.25,K.15',
     'TLH,TLA,TVA,TVK,TVS,TAK,TVI', 20, .7, [1, .3, .4, 0, 0]),
    ('LUAT', 'Luật, Hành chính & Quan hệ quốc tế', dict(R=0, I=.3, A=.1, S=.7, E=.8, C=.5), 'V.35,S.25,K.2,A.2',
     'VSD,TVA,VSK,VDK,VSA,VDA,TVK,TLA', 18, .6, [.6, .9, .3, .6, 0]),
    ('SUPHAM', 'Sư phạm & Giáo dục', dict(R=0, I=.3, A=.3, S=1, E=.2, C=.3), 'T.3,V.3,A.2,S.1,D.1',
     'TLH,TLA,VSD,TVA,THB,VSA,VDA,TVS,TVK', 0, .4, [.2, 1, .5, 1, 1]),
    ('NGOAINGU', 'Ngôn ngữ & Văn hóa quốc tế', dict(R=0, I=.2, A=.7, S=.7, E=.4, C=.2), 'A.5,V.35,S.15',
     'TVA,VSA,VDA,VKA,TSA,TDA', 18, .6, [.6, .3, .9, 0, 0]),
    ('TT_NT', 'Báo chí, Truyền thông, Thiết kế & Nghệ thuật', dict(R=.1, I=.1, A=1, S=.4, E=.5, C=0), 'V.4,A.3,S.15,K.15',
     'TVA,VSD,VSA,VDA,VKA,TVS,VSK', 25, .5, [.4, .2, 1, .2, 0]),
    ('KHXH', 'Khoa học xã hội & Nhân văn', dict(R=0, I=.6, A=.6, S=.8, E=.1, C=.2), 'V.35,S.3,D.2,A.15',
     'VSD,VSA,VDA,VSK,VDK,TVA,VKA,TVS,TVD', 15, .3, [.1, .5, 1, .8, .3]),
    ('NONGLAM', 'Nông - Lâm - Thủy sản, Môi trường & Thực phẩm', dict(R=.9, I=.7, A=0, S=.2, E=.1, C=.2), 'H.3,B.35,T.2,C.15',
     'THB,TLH,THA,TBA,TLB,TLC,TBV', 12, .2, [.3, .5, .4, .4, .8]),
    ('DULICH', 'Du lịch, Khách sạn & Dịch vụ', dict(R=.1, I=0, A=.3, S=.8, E=.9, C=.2), 'A.45,V.3,S.1,D.15',
     'TVA,VSD,VSA,VDA,VKA,TLA,TAK', 20, .4, [.6, .3, .5, 0, .2]),
    ('QPAN', 'An ninh - Quốc phòng', dict(R=.6, I=.2, A=0, S=.5, E=.5, C=.5), 'T.3,V.25,L.2,A.25',
     'TLH,TLA,VSD,TVA,TVL,THB', 0, .6, [.4, 1, .3, 1, 1]),
    ('KIENTRUC', 'Kiến trúc, Xây dựng & Quy hoạch', dict(R=.8, I=.3, A=.7, S=0, E=.1, C=.3), 'T.4,L.3,V.15,A.15',
     'TLH,TLA,TVA,TVL,TLC,TLI', 20, .5, [.7, .4, .8, 0, 0]),
]

# nhóm|ngành|điểm chuẩn tham khảo (thang 30, mức trung bình các trường)|chỉnh Holland|môn then chốt|tổ hợp
NGANH_TXT = """
CNTT|Khoa học máy tính|26.0|I+.2||
CNTT|Trí tuệ nhân tạo|26.5|I+.3|T.45,L.2,I.2,A.15|
CNTT|Khoa học dữ liệu|25.5|I+.2,C+.1|T.5,A.2,I.15,L.15|
CNTT|Kỹ thuật phần mềm|25.0|C+.1||
CNTT|An toàn thông tin|24.5|R+.1,C+.2||
CNTT|Mạng máy tính & Truyền thông dữ liệu|23.0|R+.2||
CNTT|Công nghệ chip bán dẫn & Vi mạch|23.5|R+.4,I+.1|T.35,L.4,H.1,I.15|TLH,TLA,TLI,TLC
CNTT|Hệ thống thông tin quản lý|23.5|E+.3,C+.2|T.35,A.25,V.15,I.25|TLA,TVA,TLH,TVI,TAI
KTCN|Kỹ thuật điều khiển & Tự động hóa|26.0|I+.2||
KTCN|Kỹ thuật điện - Điện tử|24.0|||
KTCN|Cơ khí & Cơ điện tử|24.0|R+.2||
KTCN|Kỹ thuật ô tô|24.5|R+.2||
KTCN|Kỹ thuật hóa học & Vật liệu|22.5|I+.3|T.3,H.4,L.2,B.1|THB,TLH,THA
KTCN|Kỹ thuật hàng không - Vũ trụ|25.5|R+.1,I+.2||
KTCN|Công nghệ kỹ thuật nhiệt & Điện lạnh|21.0|R+.2||
KTCN|Kỹ thuật robot & Mô hình hóa|25.0|I+.3,C+.1|T.4,L.3,I.2,C.1|TLH,TLA,TLI,TLC
KHTN|Toán học & Toán ứng dụng|24.0|C+.2||
KHTN|Vật lý & Kỹ thuật hạt nhân|22.5|R+.2|T.3,L.5,H.2|TLH,TLA,TLC
KHTN|Hóa học|22.0||T.3,H.5,B.2|THB,TLH,THA
KHTN|Sinh học & Công nghệ sinh học|22.5|S+.1|T.2,B.5,H.3|THB,TBA,TBV,TLB
KHTN|Thống kê & Phân tích dữ liệu|24.0|C+.3|T.5,A.2,I.2,L.1|TLA,TVA,TLH,TVI,TAI
KHTN|Khoa học vật liệu & Công nghệ nano|21.5|R+.2||
YDUOC|Y khoa|27.0|S+.2||THB,TBA,THA
YDUOC|Răng - Hàm - Mặt|27.0|R+.3,A+.1||THB,TBA,THA
YDUOC|Dược học|25.5|I+.2|H.4,T.3,B.2,L.1|TLH,THB,THA
YDUOC|Y học cổ truyền|23.0|S+.1||THB,TBA
YDUOC|Điều dưỡng|20.0|S+.3,I-.1|||
YDUOC|Kỹ thuật xét nghiệm y học|22.0|I+.2,C+.2|||
YDUOC|Y tế công cộng & Dinh dưỡng|19.0|S+.2,E+.1|||
YDUOC|Kỹ thuật phục hồi chức năng|19.5|S+.3,R+.2|||
KTTCNH|Kế toán|24.5|C+.3||
KTTCNH|Kiểm toán|27.0|C+.3,I+.1||
KTTCNH|Tài chính - Ngân hàng|25.5|E+.1,C+.1||
KTTCNH|Kinh tế học|25.0|I+.2||
KTTCNH|Kinh tế quốc tế & Kinh tế đối ngoại|27.0|E+.1,S+.1|T.3,A.35,V.2,L.15|TLA,TVA,TAK,TLH
KTTCNH|Bảo hiểm & Quản trị rủi ro|22.0|C+.1||
KTTCNH|Công nghệ tài chính (Fintech)|25.0|I+.3,C+.2|T.45,A.2,I.2,L.15|TLA,TLH,TVA,TAI,TLI
QTKD|Quản trị kinh doanh|24.0|||
QTKD|Marketing|25.0|A+.3||
QTKD|Kinh doanh quốc tế|25.5|S+.1||
QTKD|Logistics & Quản lý chuỗi cung ứng|26.0|C+.2,R+.1||
QTKD|Thương mại điện tử|24.0|I+.1,A+.1||
QTKD|Quản trị nhân lực|23.0|S+.3||
QTKD|Kinh doanh thương mại|22.5|||
QTKD|Quản lý công nghiệp & Kỹ thuật hệ thống|21.0|R+.4,I+.1|T.4,L.3,A.2,H.1|TLH,TLA,TVA
LUAT|Luật|24.0|||
LUAT|Luật kinh tế|24.8|E+.1,C+.1||
LUAT|Luật quốc tế & Thương mại quốc tế|24.5|A+.1|V.3,A.3,S.2,K.2|TVA,VSA,VKA,VSK
LUAT|Quản lý nhà nước & Hành chính công|21.0|C+.2||
LUAT|Quan hệ quốc tế|26.0|S+.1,A+.1|V.3,A.35,S.2,K.15|VSA,TVA,VDA,VKA
LUAT|Chính trị học & Lý luận chính trị|19.0|I+.1,S+.2|V.3,S.35,K.25,D.1|VSD,VSK,VDK,VSA
SUPHAM|Sư phạm Toán học|26.5|I+.3,C+.1|T.55,L.2,H.1,A.15|TLH,TLA,TVA
SUPHAM|Sư phạm Tin học|22.0|I+.1|T.4,L.2,I.3,A.1|TLA,TLH,TLI,TVI
SUPHAM|Sư phạm Vật lí|25.0|I+.3|T.3,L.5,H.1,A.1|TLH,TLA
SUPHAM|Sư phạm Hóa học|25.5|I+.3|T.25,H.5,L.15,B.1|THB,TLH,THA
SUPHAM|Sư phạm Sinh học|23.5|I+.2|B.45,H.3,T.25|THB,TBA,TBV
SUPHAM|Sư phạm Ngữ văn|25.5|A+.4|V.6,S.2,A.2|VSD,VSA,TVA,VDA
SUPHAM|Sư phạm Lịch sử & Địa lí|24.5|A+.2|V.3,S.35,D.35|VSD,VSA,VDA,VSK
SUPHAM|Sư phạm tiếng Anh|27.0|A+.3|A.6,V.25,T.15|TVA,VSA,VDA
SUPHAM|Giáo dục Tiểu học|24.0|A+.2|V.3,T.3,A.2,S.1,D.1|TVA,VSD,TLA,TLH,VSA
SUPHAM|Giáo dục Mầm non|20.0|A+.3|V.35,T.15,A.2,S.15,K.15|VSD,TVA,VSA,VKA
SUPHAM|Giáo dục Chính trị & Pháp luật|23.0|E+.1|V.3,S.3,K.3,D.1|VSD,VSK,VDK,VSA
SUPHAM|Tâm lý học giáo dục & Quản lý giáo dục|22.5|I+.3,E+.1|V.3,T.2,A.2,S.15,B.15|TVA,VSA,THB,VSD
NGOAINGU|Ngôn ngữ Anh|25.5|||
NGOAINGU|Ngôn ngữ Trung Quốc|26.0|C+.1||
NGOAINGU|Ngôn ngữ Nhật Bản|24.5|C+.1||
NGOAINGU|Ngôn ngữ Hàn Quốc|25.5|A+.2||
NGOAINGU|Ngôn ngữ Pháp, Đức, Nga|22.5|I+.2||
NGOAINGU|Biên - phiên dịch & Đông phương học|24.5|A+.2,I+.1||
TT_NT|Báo chí|25.0|A+.1,E+.1||
TT_NT|Truyền thông đa phương tiện|25.5|A+.2,I+.1||
TT_NT|Quan hệ công chúng|25.5|E+.4||
TT_NT|Thiết kế đồ họa & Mỹ thuật ứng dụng|23.0|A+.5,E-.2,I+.1|V.3,A.3,T.2,S.1,K.1|TVA,VSA,VDA,VKA,TVS
TT_NT|Công nghệ truyền thông & Sản xuất nội dung số|24.0|I+.2,R+.1,A+.1|T.25,V.25,A.3,I.2|TVA,TVI,TLA,VSA
TT_NT|Thiết kế thời trang & Nội thất|21.0|A+.6,R+.2,E-.3|||
TT_NT|Âm nhạc, Sân khấu - Điện ảnh|20.0|A+.8,E+.1,C-.3|V.4,A.2,S.2,D.2|VSD,VSA,VDA,TVA
TT_NT|Thiết kế game & Hoạt hình kỹ thuật số|22.0|A+.4,I+.3,R+.1|T.3,V.2,A.2,I.3|TVA,TVI,TLA,TLI
KHXH|Lịch sử & Khảo cổ|22.0|I+.2||
KHXH|Văn học & Ngôn ngữ học|22.5|A+.3||
KHXH|Xã hội học & Nhân học|22.0|S+.1||
KHXH|Tâm lý học|25.0|S+.2,I+.1||
KHXH|Công tác xã hội|19.0|S+.4||
KHXH|Địa lý học & Quy hoạch vùng|20.0|R+.3||
KHXH|Thông tin - Thư viện & Lưu trữ|18.5|C+.5,A-.2||
KHXH|Triết học & Tôn giáo học|19.0|I+.2|V.3,S.3,K.25,D.15|VSD,VSK,VSA
NONGLAM|Nông học & Khoa học cây trồng|17.5|||
NONGLAM|Chăn nuôi - Thú y|21.0|S+.1||
NONGLAM|Công nghệ thực phẩm|22.5|I+.2,C+.1||
NONGLAM|Công nghệ sinh học nông nghiệp|21.0|I+.3||
NONGLAM|Quản lý tài nguyên & Môi trường|19.5|S+.1,E+.1||
NONGLAM|Lâm nghiệp & Quản lý rừng|16.0|R+.2||
NONGLAM|Nuôi trồng & Khai thác thủy sản|16.5|R+.2||
NONGLAM|Khoa học môi trường & Biến đổi khí hậu|19.0|I+.3||
DULICH|Du lịch & Lữ hành|22.5|||
DULICH|Quản trị khách sạn|23.5|C+.1||
DULICH|Quản trị nhà hàng & Dịch vụ ăn uống|21.5|R+.2||
DULICH|Quản trị sự kiện & Tổ chức hội nghị|22.0|E+.1,A+.2||
DULICH|Dịch vụ vận tải hàng không|24.0|C+.2||
DULICH|Việt Nam học & Hướng dẫn viên|20.0|S+.1,A+.2||
QPAN|An ninh nhân dân & Điều tra hình sự|24.0|I+.3||
QPAN|Cảnh sát (Giao thông, PCCC, Cơ động)|24.0|R+.3||
QPAN|Chỉ huy - Tham mưu (Quân đội)|23.0|E+.2||
QPAN|Kỹ thuật quân sự & Hậu cần|21.5|R+.4,I+.2|T.3,L.4,H.1,A.2|TLH,TLA
QPAN|Biên phòng & Hải quân|21.0|R+.4||
KIENTRUC|Kiến trúc|24.0|A+.4||
KIENTRUC|Quy hoạch đô thị & Vùng|21.0|S+.1,A+.2||
KIENTRUC|Xây dựng dân dụng & Công nghiệp|22.5|C+.1||
KIENTRUC|Xây dựng cầu đường & Hạ tầng giao thông|21.0|R+.2||
KIENTRUC|Quản lý xây dựng & Bất động sản|21.5|E+.3,C+.2||
KIENTRUC|Kỹ thuật cấp thoát nước & Môi trường|19.5|I+.2||
"""

NANG_KHIEU = {'Thiết kế đồ họa & Mỹ thuật ứng dụng', 'Thiết kế thời trang & Nội thất', 'Âm nhạc, Sân khấu - Điện ảnh',
              'Kiến trúc', 'Giáo dục Mầm non', 'Thiết kế game & Hoạt hình kỹ thuật số', 'Quy hoạch đô thị & Vùng'}

PACKAGES = [  # các tổ hợp 4 môn lựa chọn học sâu (GDPT 2018) phổ biến ở trường THPT
    'LHBI', 'LHIC', 'LHBC', 'LHDI', 'LIDK', 'LICK', 'HBIK', 'HBSD', 'BDKI', 'SDKI', 'SDKC', 'SDKB', 'SDBI', 'LSDK', 'LHSK',
    'DKIC']

JOBS = ['Nông - lâm - ngư nghiệp', 'Công nhân - lao động phổ thông', 'Buôn bán - kinh doanh', 'Công chức - viên chức',
        'Giáo viên', 'Y tế', 'Kỹ sư - IT - chuyên môn', 'Lực lượng vũ trang', 'Lao động tự do', 'Nội trợ - hưu trí - khác']

VALUES = ['Thu nhập cao', 'Ổn định - an toàn', 'Đam mê - sở thích', 'Đóng góp xã hội', 'Gần nhà - tiết kiệm']


def _parse_w(s):
    d = {}
    if s:
        for p in s.split(','):
            d[p[0]] = float(p[1:])
    return d


def build():
    gid = {g[0]: i for i, g in enumerate(GROUPS)}
    rows = []
    for line in NGANH_TXT.strip().splitlines():
        p = line.split('|')
        g, name, dc, tw, key, comb = p[0], p[1], float(p[2]), p[3], p[4] if len(p) > 4 else '', p[5] if len(p) > 5 else ''
        G = GROUPS[gid[g]]
        w = dict(G[2])
        for t in (tw.split(',') if tw else []):
            w[t[0]] = max(0.0, min(1.3, w[t[0]] + float(t[1:])))
        rows.append(dict(group=g, gi=gid[g], name=name, dc_mid=dc, hol=w,
                         key=_parse_w(key or G[3]), combos=(comb or G[4]).split(','),
                         nang_khieu=name in NANG_KHIEU))
    return gid, rows
