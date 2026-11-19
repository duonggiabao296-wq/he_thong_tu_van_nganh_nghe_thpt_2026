import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.db import init_db
from app.inference import run_forward_chaining


def test_knowledge_base_and_forward_chaining():
    conn = init_db()
    n_rules = conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
    assert n_rules >= 25, f"Cần >= 25 luật, hiện có {n_rules}"

    sample_profile = {
        "lop": 12,
        "khu_vuc": "KV2",
        "ngan_sach": 50,
        "the_luc": 4,
        "ielts": 5.5,
        "dgnl_hsa": 100,
        "giai_hsg": 0,
        "holland": {"R": 4.4, "I": 4.6, "A": 2.2, "S": 2.6, "E": 2.9, "C": 3.6},
        "quan_tam": {"CNTT": 5, "KTCN": 5, "KHTN": 4},
        "hb": {"T": 9.0, "L": 8.8, "H": 8.5, "I": 8.8, "A": 7.2, "V": 7.0},
        "thi": {"T": 9.0, "L": 8.75, "H": 8.5, "A": 7.5, "V": 7.0},
    }
    res = run_forward_chaining(sample_profile, conn, save_trace=True)
    assert res["top_groups"][0]["group_code"] in ("CNTT", "KTCN")
    assert res["session_id"] is not None and len(res["trace_preview"]) > 0
    print(f"PASS: {n_rules} rules | Top1={res['top_groups'][0]['group_code']} | Trace steps={len(res['trace_preview'])}")


if __name__ == "__main__":
    test_knowledge_base_and_forward_chaining()
