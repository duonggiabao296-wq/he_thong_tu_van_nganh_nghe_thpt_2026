# -*- coding: utf-8 -*-
"""Định nghĩa dữ liệu vào cho API (tách từ CELL 7 của notebook, bổ sung kiểm tra giá trị)."""
from typing import Dict, Optional

from pydantic import BaseModel, Field


class ProfileInput(BaseModel):
    lop: int = Field(12, ge=10, le=12, description="Khối lớp 10/11/12")
    diem_uu_tien_khu_vuc: float = Field(0.25, ge=0, le=2.75)
    ngan_sach_hoc_phi_trieu_nam: float = Field(35.0, ge=0, le=500)
    uu_tien_dinh_huong: str = "Thu nhập cao"
    gia_dinh_goi_y_nhom_nganh: str = "Không"
    du_dinh_nhom_nganh_cua_hoc_sinh: str = ""
    the_luc: int = Field(3, ge=1, le=5)
    ielts: Optional[float] = Field(None, ge=0, le=9)
    dgnl_hsa_150: Optional[float] = Field(None, ge=0, le=150)
    giai_hsg: str = "Không"
    holland: Dict[str, float] = {"R": 3.0, "I": 3.0, "A": 3.0, "S": 3.0, "E": 3.0, "C": 3.0}
    quan_tam: Dict[str, int] = {}
    hb: Dict[str, Optional[float]] = {}
    thi: Dict[str, Optional[float]] = {}
