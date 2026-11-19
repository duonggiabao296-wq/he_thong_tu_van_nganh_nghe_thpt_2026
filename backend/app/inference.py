from __future__ import annotations
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from .db import COMBOS, GROUPS, SUBJECTS

PHASE_ORDER = {"normalize": 1, "screen": 2, "score": 3, "aggregate": 4, "admission": 5, "warn": 6}
GROUP_NAME_MAP = {g[0]: g[1] for g in GROUPS}
GROUP_TUITION_MAP = {g[0]: g[3] for g in GROUPS}
KV_BONUS = {"KV1": 0.75, "KV2-NT": 0.50, "KV2": 0.25, "KV3": 0.0}


def eval_condition(cond: Dict[str, Any], facts: Dict[str, Any]) -> bool:
    if "all" in cond:
        return all(eval_condition(c, facts) for c in cond["all"])
    if "any" in cond:
        return any(eval_condition(c, facts) for c in cond["any"])
    if "not" in cond:
        return not eval_condition(cond["not"], facts)
    val = facts.get(cond["fact"])
    target = cond["value"]
    op = cond["op"]
    if val is None:
        return False
    if op == "==":
        return val == target
    if op == "!=":
        return val != target
    if op == ">=":
        return val >= target
    if op == "<=":
        return val <= target
    if op == ">":
        return val > target
    if op == "<":
        return val < target
    return False


def build_facts(profile: Dict[str, Any], conn: sqlite3.Connection) -> Dict[str, Any]:
    facts: Dict[str, Any] = {
        "lop": profile.get("lop", 12),
        "the_luc": profile.get("the_luc", 4),
        "ielts": profile.get("ielts", 0.0),
        "dgnl_hsa": profile.get("dgnl_hsa", 0.0),
        "giai_hsg": profile.get("giai_hsg", 0),
        "ngan_sach": profile.get("ngan_sach", 50.0),
        "warnings": [],
    }
    holland = profile.get("holland", {})
    facts["holland_top"] = max(holland, key=holland.get) if holland else "I"

    for gcode in GROUP_NAME_MAP:
        facts[f"qt_{gcode}"] = profile.get("quan_tam", {}).get(gcode, 3)
        facts[f"group_score:{gcode}"] = float(facts[f"qt_{gcode}"]) * 0.4

    hb = profile.get("hb", {})
    thi = profile.get("thi", {})
    for code, _ in SUBJECTS:
        h = hb.get(code)
        t = thi.get(code)
        if facts["lop"] == 12 and t is not None and h is not None:
            eff = 0.6 * t + 0.4 * h
        elif t is not None:
            eff = t
        elif h is not None:
            eff = h
        else:
            eff = 0.0
        facts[f"eff_{code}"] = round(eff, 2)

    # Tính tổ hợp tốt nhất
    best_combo = "D01"
    best_score = 0.0
    for cid, (s1, s2, s3) in COMBOS.items():
        v1 = thi.get(s1) if (facts["lop"] == 12 and thi.get(s1) is not None) else hb.get(s1)
        v2 = thi.get(s2) if (facts["lop"] == 12 and thi.get(s2) is not None) else hb.get(s2)
        v3 = thi.get(s3) if (facts["lop"] == 12 and thi.get(s3) is not None) else hb.get(s3)
        if v1 is not None and v2 is not None and v3 is not None:
            tot = float(v1) + float(v2) + float(v3)
            if tot > best_score:
                best_score = tot
                best_combo = cid

    bonus = KV_BONUS.get(profile.get("khu_vuc", "KV2"), 0.0)
    if best_score >= 22.5:
        bonus = ((30.0 - best_score) / 7.5) * bonus
    best_ut = round(best_score + bonus, 2)

    facts["best_combo"] = best_combo
    facts["best_score"] = round(best_score, 2)
    facts["best_score_ut"] = best_ut
    facts["margin_top"] = round(best_ut - 25.5, 2)
    facts["margin_avg"] = round(best_ut - 21.5, 2)
    facts["budget_gap"] = round(facts["ngan_sach"] - 20.0, 2)
    return facts


def run_forward_chaining(profile: Dict[str, Any], conn: sqlite3.Connection, save_trace: bool = False) -> Dict[str, Any]:
    facts = build_facts(profile, conn)
    rows = conn.execute("SELECT * FROM rules WHERE enabled = 1").fetchall()
    rules = [
        {
            "rule_id": r["rule_id"],
            "phase": r["phase"],
            "priority": r["priority"],
            "certainty": r["certainty"],
            "condition": json.loads(r["condition_json"]),
            "action": json.loads(r["action_json"]),
            "description": r["description"],
        }
        for r in rows
    ]

    fired_ids: set[str] = set()
    trace: List[Dict[str, Any]] = []
    step_no = 0
    n_iterations = 0

    for iteration in range(1, 7):
        matched = [r for r in rules if r["rule_id"] not in fired_ids and eval_condition(r["condition"], facts)]
        if not matched:
            break
        n_iterations = iteration

        # Giải quyết xung đột: pha tăng dần -> priority giảm dần -> certainty giảm dần -> rule_id
        matched.sort(key=lambda r: (PHASE_ORDER.get(r["phase"], 9), -r["priority"], -r["certainty"], r["rule_id"]))

        set_winners: Dict[str, Dict] = {}
        for r in matched:
            step_no += 1
            act = r["action"]
            verb, key, val = act["verb"], act["key"], act["value"]

            if verb == "set" and key in set_winners:
                w = set_winners[key]
                fired_ids.add(r["rule_id"])
                trace.append({
                    "step_no": step_no,
                    "iteration": iteration,
                    "rule_id": r["rule_id"],
                    "phase": r["phase"],
                    "fired": 0,
                    "suppressed_by": w["rule_id"],
                    "priority": r["priority"],
                    "certainty": r["certainty"],
                    "explanation": f"Bị đè bởi {w['rule_id']} (priority {w['priority']} > {r['priority']})",
                })
                continue

            if verb == "set":
                set_winners[key] = r
                facts[key] = val
            elif verb == "add":
                facts[key] = round(float(facts.get(key, 0.0)) + float(val), 2)
            elif verb == "append":
                facts.setdefault(key, []).append(val)

            fired_ids.add(r["rule_id"])
            trace.append({
                "step_no": step_no,
                "iteration": iteration,
                "rule_id": r["rule_id"],
                "phase": r["phase"],
                "fired": 1,
                "suppressed_by": None,
                "priority": r["priority"],
                "certainty": r["certainty"],
                "explanation": r["description"],
            })

        # Sau khi chấm điểm xong vòng 1, cập nhật top_group để luật cảnh báo vòng 2 dùng
        group_scores = [
            (k.replace("group_score:", ""), float(v))
            for k, v in facts.items()
            if k.startswith("group_score:")
        ]
        group_scores.sort(key=lambda x: -x[1])
        if group_scores:
            top_g = group_scores[0][0]
            facts["top_group"] = top_g
            facts["budget_gap"] = round(facts["ngan_sach"] - GROUP_TUITION_MAP.get(top_g, 20.0), 2)

    group_scores = sorted(
        [(k.replace("group_score:", ""), float(v)) for k, v in facts.items() if k.startswith("group_score:")],
        key=lambda x: -x[1],
    )
    total_pos = sum(max(0.1, s) for _, s in group_scores[:3]) or 1.0
    top_groups = [
        {
            "group_code": gc,
            "group_name": GROUP_NAME_MAP[gc],
            "group_score": round(sc, 2),
            "confidence_pct": round(max(0.1, sc) / total_pos * 100, 1),
        }
        for gc, sc in group_scores[:3]
    ]

    top_code = top_groups[0]["group_code"] if top_groups else "CNTT"
    majors = conn.execute("SELECT * FROM majors WHERE group_code = ? LIMIT 5", (top_code,)).fetchall()
    top_majors = [
        {
            "major_id": m["major_id"],
            "major_name": m["major_name"],
            "group_name": GROUP_NAME_MAP[m["group_code"]],
            "best_combo": facts["best_combo"],
            "score_ut": facts["best_score_ut"],
            "dc_top": m["dc_top"],
            "dc_avg": m["dc_avg"],
            "dc_basic": m["dc_basic"],
            "suitability_score": min(99.0, round(60.0 + group_scores[0][1] * 5.0, 1)),
        }
        for m in majors
    ]

    session_id = None
    if save_trace:
        session_id = uuid.uuid4().hex
        conn.execute(
            "INSERT INTO sessions(session_id, created_at, top_group, top_major) VALUES (?, ?, ?, ?)",
            (session_id, datetime.now(timezone.utc).isoformat(), top_code, top_majors[0]["major_name"] if top_majors else ""),
        )
        conn.executemany(
            '''INSERT INTO trace_steps(session_id, step_no, iteration, rule_id, phase, fired, suppressed_by, priority, certainty, explanation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            [
                (
                    session_id, t["step_no"], t["iteration"], t["rule_id"], t["phase"],
                    t["fired"], t["suppressed_by"], t["priority"], t["certainty"], t["explanation"],
                )
                for t in trace
            ],
        )
        conn.commit()

    return {
        "engine_mode": "forward_chaining_sqlite" if save_trace else "standard",
        "top_groups": top_groups,
        "top_majors": top_majors,
        "feasibility": facts.get("feasibility", "Trung bình"),
        "admission_method": facts.get("admission_method", "Thi tốt nghiệp THPT"),
        "warnings": facts.get("warnings", []),
        "best_combo": facts["best_combo"],
        "best_score": facts["best_score"],
        "best_score_ut": facts["best_score_ut"],
        "session_id": session_id,
        "n_iterations": n_iterations,
        "n_fired": sum(1 for t in trace if t["fired"] == 1),
        "trace_preview": trace[:15] if save_trace else [],
    }
