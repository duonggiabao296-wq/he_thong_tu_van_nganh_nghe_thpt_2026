from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "kb.sqlite"

SUBJECTS: List[Tuple[str, str]] = [
    ("T", "Toán"), ("V", "Ngữ văn"), ("A", "Tiếng Anh"), ("L", "Vật lí"),
    ("H", "Hóa học"), ("B", "Sinh học"), ("S", "Lịch sử"), ("D", "Địa lí"),
    ("K", "GD KT&PL"), ("I", "Tin học"), ("C", "Công nghệ"),
]

GROUPS: List[Tuple[str, str, str, float]] = [
    ("CNTT", "Công nghệ thông tin, AI & Dữ liệu", "I-R-C", 22.0),
    ("KTCN", "Kỹ thuật, Cơ khí, Điện & Tự động hóa", "R-I-C", 20.0),
    ("KHTN", "Khoa học tự nhiên & Toán", "I-R-S", 18.0),
    ("YDUOC", "Y, Dược & Sức khỏe", "I-S-R", 30.0),
    ("KTTCNH", "Kinh tế, Tài chính, Ngân hàng & Kế toán", "C-E-I", 20.0),
    ("QTKD", "Quản trị, Marketing, Thương mại & Logistics", "E-C-S", 22.0),
    ("LUAT", "Luật, Hành chính & Quan hệ quốc tế", "E-S-C", 19.0),
    ("SUPHAM", "Sư phạm & Giáo dục", "S-I-A", 0.0),
    ("NGOAINGU", "Ngôn ngữ & Văn hóa quốc tế", "A-S-E", 20.0),
    ("TT_NT", "Báo chí, Truyền thông, Thiết kế & Nghệ thuật", "A-E-S", 22.0),
    ("KHXH", "Khoa học xã hội & Nhân văn", "S-A-I", 17.0),
    ("NONGLAM", "Nông - Lâm - Thủy sản, Môi trường & Thực phẩm", "R-I-C", 15.0),
    ("DULICH", "Du lịch, Khách sạn & Dịch vụ", "E-S-A", 20.0),
    ("QPAN", "An ninh - Quốc phòng", "R-E-C", 0.0),
    ("KIENTRUC", "Kiến trúc, Xây dựng & Quy hoạch", "R-A-I", 21.0),
]

COMBOS: Dict[str, Tuple[str, str, str]] = {
    "A00": ("T", "L", "H"),
    "A01": ("T", "L", "A"),
    "D01": ("T", "V", "A"),
    "B00": ("T", "H", "B"),
    "B03": ("T", "V", "B"),
    "C00": ("V", "S", "D"),
    "C01": ("T", "V", "L"),
    "C14": ("T", "V", "K"),
    "MOI_TI": ("T", "V", "I"),
}

MAJORS_SAMPLE = [
    ("7480201", "Công nghệ thông tin", "CNTT", 26.2, 22.5, 19.0, "A00,A01,D01,MOI_TI"),
    ("7480107", "Trí tuệ nhân tạo", "CNTT", 26.8, 23.0, 19.5, "A00,A01,D01,MOI_TI"),
    ("7480101", "Khoa học máy tính", "CNTT", 26.5, 22.8, 19.2, "A00,A01,D01,MOI_TI"),
    ("7520103", "Kỹ thuật cơ khí", "KTCN", 24.5, 21.0, 18.0, "A00,A01,C01"),
    ("7520207", "Kỹ thuật điện tử - viễn thông", "KTCN", 25.0, 21.5, 18.5, "A00,A01,C01"),
    ("7460108", "Khoa học dữ liệu", "KHTN", 25.5, 21.8, 18.5, "A00,A01,D01"),
    ("7720101", "Y khoa", "YDUOC", 27.5, 24.5, 22.0, "B00,B03"),
    ("7340201", "Tài chính - Ngân hàng", "KTTCNH", 25.2, 21.8, 18.5, "A00,A01,D01"),
    ("7340120", "Kinh doanh quốc tế", "QTKD", 25.5, 21.8, 18.8, "A00,A01,D01"),
    ("7340101", "Quản trị kinh doanh", "QTKD", 25.0, 21.2, 18.2, "A00,A01,D01,C14"),
    ("7380101", "Luật", "LUAT", 25.0, 21.5, 18.5, "C00,D01,C14"),
    ("7140201", "Giáo dục Tiểu học", "SUPHAM", 26.0, 22.5, 19.0, "C00,D01"),
    ("7220201", "Ngôn ngữ Anh", "NGOAINGU", 25.0, 21.5, 18.5, "D01"),
    ("7210403", "Thiết kế đồ họa", "TT_NT", 24.0, 20.5, 17.5, "D01,C00"),
    ("7310401", "Tâm lý học", "KHXH", 24.5, 21.0, 18.0, "C00,D01"),
    ("7620105", "Chăn nuôi / Nông nghiệp", "NONGLAM", 20.0, 17.0, 15.0, "B00,A00"),
    ("7810101", "Du lịch", "DULICH", 23.5, 20.0, 17.5, "C00,D01"),
    ("7860100", "An ninh - Quốc phòng", "QPAN", 26.0, 23.0, 20.0, "A00,A01,C00"),
    ("7580101", "Kiến trúc", "KIENTRUC", 24.8, 21.0, 18.0, "A00,A01,C01"),
]


def build_rules_seed() -> List[Dict]:
    '''Sinh tối thiểu 30+ luật IF-THEN có priority & certainty (đáp ứng >= 25 luật).'''
    rules: List[Dict] = []

    # 1. Luật gợi ý cho 15 nhóm ngành dựa trên Holland + Quan tâm (30 luật: mức cao & mức trung bình)
    for gcode, gname, h_code, _ in GROUPS:
        primary_h = h_code.split("-")[0]
        rules.append({
            "rule_id": f"SUIT-{gcode}-HIGH",
            "phase": "score",
            "priority": 80,
            "certainty": 0.85,
            "condition": {
                "all": [
                    {"fact": "holland_top", "op": "==", "value": primary_h},
                    {"fact": f"qt_{gcode}", "op": ">=", "value": 4},
                ]
            },
            "action": {"verb": "set", "key": f"suit_base:{gcode}", "value": 2.4},
            "description": f"Holland chính {primary_h} khớp và quan tâm cao (>=4) nhóm {gname}",
        })
        rules.append({
            "rule_id": f"SUIT-{gcode}-MED",
            "phase": "score",
            "priority": 60,
            "certainty": 0.65,
            "condition": {
                "any": [
                    {"fact": "holland_top", "op": "==", "value": primary_h},
                    {"fact": f"qt_{gcode}", "op": ">=", "value": 4},
                ]
            },
            "action": {"verb": "set", "key": f"suit_base:{gcode}", "value": 1.1},
            "description": f"Holland chính {primary_h} hoặc quan tâm cao nhóm {gname}",
        })

    # 2. Luật năng lực môn học then chốt & ràng buộc đặc thù
    extra_rules = [
        {
            "rule_id": "SUBJ-CNTT-TOAN", "phase": "score", "priority": 82, "certainty": 0.90,
            "condition": {"all": [{"fact": "eff_T", "op": ">=", "value": 8.0}, {"fact": "eff_I", "op": ">=", "value": 8.0}]},
            "action": {"verb": "add", "key": "group_score:CNTT", "value": 1.8},
            "description": "Năng lực Toán >= 8.0 và Tin học >= 8.0 ủng hộ mạnh nhóm CNTT",
        },
        {
            "rule_id": "SUBJ-KTCN-LY", "phase": "score", "priority": 82, "certainty": 0.88,
            "condition": {"all": [{"fact": "eff_T", "op": ">=", "value": 8.0}, {"fact": "eff_L", "op": ">=", "value": 8.0}]},
            "action": {"verb": "add", "key": "group_score:KTCN", "value": 1.8},
            "description": "Năng lực Toán >= 8.0 và Vật lí >= 8.0 ủng hộ nhóm Kỹ thuật",
        },
        {
            "rule_id": "SUBJ-YDUOC-HOASINH", "phase": "score", "priority": 82, "certainty": 0.90,
            "condition": {"all": [{"fact": "eff_H", "op": ">=", "value": 8.0}, {"fact": "eff_B", "op": ">=", "value": 8.0}]},
            "action": {"verb": "add", "key": "group_score:YDUOC", "value": 2.0},
            "description": "Năng lực Hóa >= 8.0 và Sinh >= 8.0 ủng hộ nhóm Y - Dược",
        },
        {
            "rule_id": "SUBJ-NGOAINGU-ANH", "phase": "score", "priority": 80, "certainty": 0.85,
            "condition": {"all": [{"fact": "eff_A", "op": ">=", "value": 8.0}]},
            "action": {"verb": "add", "key": "group_score:NGOAINGU", "value": 1.6},
            "description": "Tiếng Anh >= 8.0 ủng hộ nhóm Ngôn ngữ",
        },
        {
            "rule_id": "PEN-QPAN-THELUC", "phase": "screen", "priority": 90, "certainty": 1.0,
            "condition": {"all": [{"fact": "the_luc", "op": "<=", "value": 2}]},
            "action": {"verb": "add", "key": "group_score:QPAN", "value": -3.0},
            "description": "Thể lực <= 2 bị trừ điểm nặng cho nhóm An ninh - Quốc phòng",
        },
        # 3. Luật khả thi (cố ý cạnh tranh để minh họa conflict resolution bằng 'set')
        {
            "rule_id": "FEA-CAO", "phase": "aggregate", "priority": 80, "certainty": 1.0,
            "condition": {"all": [{"fact": "best_score", "op": ">=", "value": 15.0}, {"fact": "margin_top", "op": ">=", "value": -1.0}]},
            "action": {"verb": "set", "key": "feasibility", "value": "Cao"},
            "description": "Điểm sau ưu tiên >= Điểm chuẩn Top - 1.0 -> Khả thi Cao",
        },
        {
            "rule_id": "FEA-TB", "phase": "aggregate", "priority": 60, "certainty": 1.0,
            "condition": {"all": [{"fact": "best_score", "op": ">=", "value": 15.0}, {"fact": "margin_avg", "op": ">=", "value": 0.0}]},
            "action": {"verb": "set", "key": "feasibility", "value": "Trung bình"},
            "description": "Điểm sau ưu tiên >= Điểm chuẩn Trung bình -> Khả thi Trung bình",
        },
        {
            "rule_id": "FEA-THAP", "phase": "aggregate", "priority": 40, "certainty": 1.0,
            "condition": {"all": [{"fact": "best_score", "op": ">=", "value": 15.0}]},
            "action": {"verb": "set", "key": "feasibility", "value": "Thấp (Cần cân nhắc trường nhóm cơ bản)"},
            "description": "Đạt ngưỡng sàn >= 15.0 nhưng dưới chuẩn trung bình -> Khả thi Thấp",
        },
        {
            "rule_id": "FEA-SAN", "phase": "aggregate", "priority": 100, "certainty": 1.0,
            "condition": {"all": [{"fact": "best_score", "op": "<", "value": 15.0}]},
            "action": {"verb": "set", "key": "feasibility", "value": "Chưa đạt ngưỡng sàn (15.0)"},
            "description": "Tổng điểm tổ hợp tốt nhất < 15.0 -> Chưa đạt ngưỡng sàn",
        },
        # 4. Luật phương thức xét tuyển (cạnh tranh 'set')
        {
            "rule_id": "ADM-HSG", "phase": "admission", "priority": 95, "certainty": 1.0,
            "condition": {"all": [{"fact": "giai_hsg", "op": ">=", "value": 1}]},
            "action": {"verb": "set", "key": "admission_method", "value": "Tuyển thẳng / Ưu tiên xét tuyển"},
            "description": "Có giải HSG -> Ưu tiên cao nhất: Tuyển thẳng",
        },
        {
            "rule_id": "ADM-HSA", "phase": "admission", "priority": 85, "certainty": 1.0,
            "condition": {"all": [{"fact": "lop", "op": "==", "value": 12}, {"fact": "dgnl_hsa", "op": ">=", "value": 90}]},
            "action": {"verb": "set", "key": "admission_method", "value": "Đánh giá năng lực (HSA/TSA)"},
            "description": "Lớp 12 & ĐGNL HSA >= 90 -> Đánh giá năng lực",
        },
        {
            "rule_id": "ADM-IELTS", "phase": "admission", "priority": 75, "certainty": 1.0,
            "condition": {"all": [{"fact": "ielts", "op": ">=", "value": 6.0}]},
            "action": {"verb": "set", "key": "admission_method", "value": "Xét tuyển kết hợp (IELTS + Học bạ/Thi THPT)"},
            "description": "Có chứng chỉ IELTS >= 6.0 -> Xét tuyển kết hợp",
        },
        {
            "rule_id": "ADM-THPT", "phase": "admission", "priority": 20, "certainty": 1.0,
            "condition": {"all": [{"fact": "lop", "op": ">=", "value": 10}]},
            "action": {"verb": "set", "key": "admission_method", "value": "Thi tốt nghiệp THPT / Xét học bạ"},
            "description": "Phương thức xét tuyển mặc định",
        },
        # 5. Luật cảnh báo
        {
            "rule_id": "WRN-BUDGET", "phase": "warn", "priority": 70, "certainty": 1.0,
            "condition": {"all": [{"fact": "budget_gap", "op": "<", "value": 0}]},
            "action": {"verb": "append", "key": "warnings", "value": "Ngân sách dự kiến thấp hơn mức học phí tối thiểu của nhóm ngành."},
            "description": "Cảnh báo khi ngân sách nhỏ hơn học phí tối thiểu",
        },
        {
            "rule_id": "WRN-QPAN", "phase": "warn", "priority": 80, "certainty": 1.0,
            "condition": {"all": [{"fact": "top_group", "op": "==", "value": "QPAN"}, {"fact": "the_luc", "op": "<=", "value": 2}]},
            "action": {"verb": "append", "key": "warnings", "value": "Cần sơ tuyển sức khỏe/thể lực cho nhóm An ninh - Quốc phòng."},
            "description": "Cảnh báo sơ tuyển thể lực cho nhóm QPAN",
        },
        {
            "rule_id": "SUBJ-KTTCNH-TOAN",
            "phase": "score",
            "priority": 80,
            "certainty": 0.85,
            "condition": {
                "all": [
                    {"fact": "eff_T", "op": ">=", "value": 8.0},
                    {"fact": "qt_KTTCNH", "op": ">=", "value": 3},
                ]
            },
            "action": {"verb": "add", "key": "group_score:KTTCNH", "value": 1.5},
            "description": "Điểm Toán >= 8.0 và quan tâm Kinh tế - Tài chính - Ngân hàng",
        },
        {
            "rule_id": "SUBJ-QTKD-TOANANH",
            "phase": "score",
            "priority": 80,
            "certainty": 0.84,
            "condition": {
                "all": [
                    {"fact": "eff_T", "op": ">=", "value": 7.5},
                    {"fact": "eff_A", "op": ">=", "value": 7.5},
                ]
            },
            "action": {"verb": "add", "key": "group_score:QTKD", "value": 1.5},
            "description": "Điểm Toán và Tiếng Anh đều >= 7.5 phù hợp Quản trị - Marketing - Logistics",
        },
        {
            "rule_id": "SUBJ-LUAT-VANANH",
            "phase": "score",
            "priority": 78,
            "certainty": 0.82,
            "condition": {
                "all": [
                    {"fact": "eff_V", "op": ">=", "value": 8.0},
                    {"fact": "qt_LUAT", "op": ">=", "value": 3},
                ]
            },
            "action": {"verb": "add", "key": "group_score:LUAT", "value": 1.5},
            "description": "Điểm Ngữ văn >= 8.0 và quan tâm nhóm Luật - Hành chính",
        },
        {
            "rule_id": "SUBJ-SUPHAM-VANTOAN",
            "phase": "score",
            "priority": 78,
            "certainty": 0.82,
            "condition": {
                "all": [
                    {"fact": "eff_V", "op": ">=", "value": 7.8},
                    {"fact": "qt_SUPHAM", "op": ">=", "value": 3},
                ]
            },
            "action": {"verb": "add", "key": "group_score:SUPHAM", "value": 1.5},
            "description": "Điểm Ngữ văn >= 7.8 và quan tâm nhóm Sư phạm & Giáo dục",
        },
        {
            "rule_id": "SUBJ-KHTN-TOANLY",
            "phase": "score",
            "priority": 82,
            "certainty": 0.88,
            "condition": {
                "all": [
                    {"fact": "eff_T", "op": ">=", "value": 8.5},
                    {"fact": "eff_L", "op": ">=", "value": 8.0},
                ]
            },
            "action": {"verb": "add", "key": "group_score:KHTN", "value": 1.6},
            "description": "Điểm Toán >= 8.5 và Vật lí >= 8.0 phù hợp Khoa học tự nhiên & Toán",
        },
    ]
    rules.extend(extra_rules)
    return rules


def init_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.executescript(
        '''
        CREATE TABLE IF NOT EXISTS subjects (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS "groups" (
            group_code TEXT PRIMARY KEY,
            group_name TEXT NOT NULL,
            holland_profile TEXT NOT NULL,
            min_tuition REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS majors (
            major_id TEXT PRIMARY KEY,
            major_name TEXT NOT NULL,
            group_code TEXT NOT NULL REFERENCES "groups"(group_code),
            dc_top REAL NOT NULL,
            dc_avg REAL NOT NULL,
            dc_basic REAL NOT NULL CHECK (dc_basic >= 15.0 AND dc_basic <= dc_avg),
            combos_csv TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rules (
            rule_id TEXT PRIMARY KEY,
            phase TEXT NOT NULL,
            priority INTEGER NOT NULL,
            certainty REAL NOT NULL,
            condition_json TEXT NOT NULL,
            action_json TEXT NOT NULL,
            description TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            top_group TEXT,
            top_major TEXT
        );
        CREATE TABLE IF NOT EXISTS trace_steps (
            session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
            step_no INTEGER NOT NULL,
            iteration INTEGER NOT NULL,
            rule_id TEXT NOT NULL,
            phase TEXT NOT NULL,
            fired INTEGER NOT NULL,
            suppressed_by TEXT,
            priority INTEGER NOT NULL,
            certainty REAL NOT NULL,
            explanation TEXT NOT NULL,
            PRIMARY KEY (session_id, step_no)
        );
        '''
    )

    if conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0] == 0:
        conn.executemany("INSERT INTO subjects(code, name) VALUES (?, ?)", SUBJECTS)
        conn.executemany(
            'INSERT INTO "groups"(group_code, group_name, holland_profile, min_tuition) VALUES (?, ?, ?, ?)',
            GROUPS,
        )
        conn.executemany(
            "INSERT INTO majors(major_id, major_name, group_code, dc_top, dc_avg, dc_basic, combos_csv) VALUES (?, ?, ?, ?, ?, ?, ?)",
            MAJORS_SAMPLE,
        )
        for r in build_rules_seed():
            conn.execute(
                "INSERT INTO rules(rule_id, phase, priority, certainty, condition_json, action_json, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    r["rule_id"], r["phase"], r["priority"], r["certainty"],
                    json.dumps(r["condition"], ensure_ascii=False),
                    json.dumps(r["action"], ensure_ascii=False),
                    r["description"],
                ),
            )
        conn.commit()
    return conn
