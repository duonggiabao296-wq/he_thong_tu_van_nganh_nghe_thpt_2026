from __future__ import annotations
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict

VALID_SUBJECTS = {"T", "V", "A", "L", "H", "B", "S", "D", "K", "I", "C"}
VALID_HOLLAND = {"R", "I", "A", "S", "E", "C"}
VALID_GROUPS = {
    "CNTT", "KTCN", "KHTN", "YDUOC", "KTTCNH", "QTKD", "LUAT",
    "SUPHAM", "NGOAINGU", "TT_NT", "KHXH", "NONGLAM", "DULICH", "QPAN", "KIENTRUC"
}


class ProfileInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    lop: int = Field(default=12, ge=10, le=12, description="Khối lớp (10, 11, 12)")
    khu_vuc: str = Field(default="KV2", description="Khu vực ưu tiên (KV1, KV2-NT, KV2, KV3)")
    ngan_sach: float = Field(default=50.0, ge=0, le=500, description="Ngân sách học phí (triệu/năm)")
    uu_tien: str = Field(default="dam_me", description="Giá trị ưu tiên số 1")
    gia_dinh_goi_y: str = Field(default="", description="Nhóm ngành gia đình định hướng")
    du_dinh_ban_than: str = Field(default="", description="Dự định nhóm ngành của bản thân")
    the_luc: int = Field(default=4, ge=1, le=5, description="Thể lực (1-5)")
    ielts: float = Field(default=0.0, ge=0.0, le=9.0)
    dgnl_hsa: float = Field(default=0.0, ge=0.0, le=150.0)
    giai_hsg: int = Field(default=0, ge=0, le=3)

    holland: Dict[str, float]
    quan_tam: Dict[str, int]
    hb: Dict[str, Optional[float]] = Field(default_factory=dict)
    thi: Dict[str, Optional[float]] = Field(default_factory=dict)

    @field_validator("holland")
    @classmethod
    def check_holland(cls, v: Dict[str, float]) -> Dict[str, float]:
        if set(v.keys()) != VALID_HOLLAND:
            raise ValueError("holland phải chứa đủ 6 khóa: R, I, A, S, E, C")
        for k, val in v.items():
            if not (1.0 <= float(val) <= 5.0):
                raise ValueError(f"holland[{k}] phải nằm trong [1.0, 5.0]")
        return {k: float(val) for k, val in v.items()}

    @field_validator("quan_tam")
    @classmethod
    def check_quan_tam(cls, v: Dict[str, int]) -> Dict[str, int]:
        for k, val in v.items():
            if k not in VALID_GROUPS:
                raise ValueError(f"Mã nhóm ngành không hợp lệ trong quan_tam: {k}")
            if not (1 <= int(val) <= 5):
                raise ValueError(f"quan_tam[{k}]={val} ngoài miền [1, 5]")
        return {k: int(val) for k, val in v.items()}

    @field_validator("hb", "thi")
    @classmethod
    def check_scores(cls, v: Dict[str, Optional[float]]) -> Dict[str, Optional[float]]:
        cleaned: Dict[str, Optional[float]] = {}
        for k, val in v.items():
            if k not in VALID_SUBJECTS:
                raise ValueError(f"Mã môn học không hợp lệ: {k}")
            if val is None or float(val) == 0.0:
                cleaned[k] = None
            else:
                fval = float(val)
                if not (0.0 <= fval <= 10.0):
                    raise ValueError(f"Điểm môn {k}={fval} phải nằm trong [0, 10]")
                cleaned[k] = fval
        return cleaned

    @field_validator("du_dinh_ban_than", "gia_dinh_goi_y")
    @classmethod
    def check_group_code(cls, v: str) -> str:
        if v and v not in VALID_GROUPS:
            raise ValueError(f"Mã nhóm ngành '{v}' không hợp lệ")
        return v


class AdviseResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    engine_mode: str
    top_groups: List[Dict[str, Any]]
    top_majors: List[Dict[str, Any]]
    feasibility: str
    admission_method: str
    warnings: List[str]
    session_id: Optional[str] = None
    n_iterations: Optional[int] = None
    n_fired: Optional[int] = None
