# -*- coding: utf-8 -*-
"""
File: app/engine.py (tách từ CELL 4 của notebook Colab)
Chức năng: Lõi Suy diễn Hệ Chuyên Gia kết hợp Trọng số AI
"""
import os
import json
import numpy as np

DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'model', 'ai_expert_model_2026.json'
)

SUBJ = ['T', 'V', 'A', 'L', 'H', 'B', 'S', 'D', 'K', 'I', 'C']
SN = {
    'T': 'Toán', 'V': 'Ngữ văn', 'A': 'Tiếng Anh', 'L': 'Vật lí', 'H': 'Hóa học',
    'B': 'Sinh học', 'S': 'Lịch sử', 'D': 'Địa lí', 'K': 'GD KT&PL', 'I': 'Tin học', 'C': 'Công nghệ'
}
HT = ['R', 'I', 'A', 'S', 'E', 'C']


class CareerExpertSystem2026:
    def __init__(self, artifact_path=DEFAULT_MODEL_PATH):
        with open(artifact_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.w_feat = np.array(self.data['weights']['w_feat'], dtype=float)
        self.b_major = np.array(self.data['weights']['b_major'], dtype=float)
        self.ex_mean = self.data['weights']['ex_mean']
        self.ex_std = self.data['weights']['ex_std']
        self.groups = self.data['groups']
        self.majors = self.data['majors']
        self.combos_catalog = self.data['combos_catalog']
        self.values = self.data['values']
        self.group_code_to_idx = {g['code']: i for i, g in enumerate(self.groups)}

    def meta(self) -> dict:
        """Dữ liệu danh mục cho frontend dựng form (nhóm ngành, giá trị, môn học, metrics...)."""
        return {
            'subjects': [{'code': s, 'name': SN[s]} for s in SUBJ],
            'holland': HT,
            'values': self.values,
            'groups': [{'code': g['code'], 'name': g['name']} for g in self.groups],
            'n_majors': len(self.majors),
            'metrics': self.data.get('metrics', {}),
        }

    @staticmethod
    def calc_priority_adjusted_score(raw_total, pri_bonus):
        if raw_total is None or raw_total <= 0:
            return 0.0
        if raw_total >= 22.5:
            eff_bonus = max(0.0, (30.0 - raw_total) / 7.5 * pri_bonus)
        else:
            eff_bonus = pri_bonus
        return round(raw_total + eff_bonus, 2)

    def estimate_combo_percentile(self, combo_key, raw_total):
        if combo_key not in self.combos_catalog or raw_total is None or raw_total <= 0:
            return None
        qs = self.combos_catalog[combo_key]['percentiles']
        for i in range(len(qs) - 1):
            if raw_total <= qs[i + 1]:
                span = max(0.01, qs[i + 1] - qs[i])
                frac = max(0.0, min(1.0, (raw_total - qs[i]) / span))
                return round((i + frac) * 5.0, 1)
        return 99.5

    def advise(self, profile: dict) -> dict:
        lop = int(profile.get('lop', 12))
        is_g12 = (lop == 12)
        pri = float(profile.get('diem_uu_tien_khu_vuc', 0.25))
        budget = float(profile.get('ngan_sach_hoc_phi_trieu_nam', 30))
        val_str = profile.get('uu_tien_dinh_huong', 'Thu nhập cao')
        val_idx = self.values.index(val_str) if val_str in self.values else 0
        fam_sug = profile.get('gia_dinh_goi_y_nhom_nganh', 'Không')
        du_dinh = profile.get('du_dinh_nhom_nganh_cua_hoc_sinh', '')
        the_luc = int(profile.get('the_luc', 3))
        ielts = profile.get('ielts', None)
        dgnl = profile.get('dgnl_hsa_150', None)
        giai_hsg = profile.get('giai_hsg', 'Không')

        hb = profile.get('hb', {})
        thi = profile.get('thi', {})
        holland = profile.get('holland', {t: 3.0 for t in HT})
        quan_tam = profile.get('quan_tam', {g['code']: 3 for g in self.groups})

        zperf, score_use, avail_subj, hb_vals = {}, {}, {}, []
        for s in SUBJ:
            h_val = hb.get(s, None)
            e_val = thi.get(s, None) if is_g12 else None
            has_h = h_val is not None and not np.isnan(h_val)
            has_e = e_val is not None and not np.isnan(e_val)

            if has_h:
                hb_vals.append(float(h_val))
            zh = (float(h_val) - 7.7) / 0.95 if has_h else None
            ze = (float(e_val) - self.ex_mean[s]) / self.ex_std[s] if has_e else None

            if has_e and has_h:
                zperf[s] = 0.6 * ze + 0.4 * zh
            elif has_h:
                zperf[s] = 0.75 * zh
            else:
                zperf[s] = None

            if is_g12:
                avail_subj[s] = has_e
                score_use[s] = float(e_val) if has_e else None
            else:
                avail_subj[s] = has_h
                score_use[s] = (self.ex_mean[s] + self.ex_std[s] * 0.8 * zh) if has_h else None

        gpa_hb = round(float(np.mean(hb_vals)), 2) if hb_vals else 7.5

        combo_totals = {}
        for ckey, cinfo in self.combos_catalog.items():
            subjs = cinfo['subjects']
            if all(avail_subj.get(s, False) for s in subjs):
                combo_totals[ckey] = round(sum(score_use[s] for s in subjs), 2)
            else:
                combo_totals[ckey] = None

        ri_vec = np.array([float(holland.get(t, 3.0)) for t in HT])
        rc_vec = ri_vec - ri_vec.mean()

        fit_g = []
        for g in self.groups:
            hv = np.array([float(g['holland'][t]) for t in HT])
            fit_g.append(float(np.dot(rc_vec, hv / max(hv.sum(), 1e-9))))
        fit_g = np.array(fit_g)

        K = len(self.majors)
        U_scores = np.zeros(K)
        major_details = []

        for k, m in enumerate(self.majors):
            g_obj = self.groups[m['group_idx']]
            hk = np.array([float(m['holland'][t]) for t in HT])
            f_hol = float(np.dot(rc_vec, hk / max(hk.sum(), 1e-9)))
            f_int = float(quan_tam.get(m['group_code'], 3)) - 3.0

            num, den = 0.0, 0.0
            for s, w in m['key_weights'].items():
                if zperf.get(s) is not None:
                    num += zperf[s] * float(w)
                    den += float(w)
            f_apt = float(np.clip(num / den if den > 0 else 0.0, -2.5, 2.5))

            best_ckey, best_raw = None, -1e9
            for ckey in m['combos']:
                tot_c = combo_totals.get(ckey)
                if tot_c is not None and tot_c > best_raw:
                    best_raw = tot_c
                    best_ckey = ckey

            is_elig = best_ckey is not None
            raw_tot = round(best_raw, 2) if is_elig else 0.0
            adj_tot = self.calc_priority_adjusted_score(raw_tot, pri) if is_elig else 0.0
            reach_diff = round(adj_tot - m['dc_avg'], 2) if is_elig else -9.9
            f_reach = float(np.clip((reach_diff + 1.0) / 3.0, -2.5, 0.4)) if is_elig else -2.5

            f_bud = -min(1.5, max(0.0, float(m['min_tuition']) - budget) / 12.0)
            f_fam = 1.0 if (fam_sug == m['group_code']) else 0.0
            f_val = float(g_obj['value_tags'][val_idx])
            f_elig = 0.0 if is_elig else -3.0
            f_qp = -1.0 if (m['group_code'] == 'QPAN' and the_luc <= 2) else 0.0

            feat_vec = np.array([f_hol, f_int, f_apt, f_reach, f_bud, f_fam, f_val, f_elig, f_qp])
            u_val = float(np.dot(feat_vec, self.w_feat) + self.b_major[k])
            u_scaled = u_val / 2.65
            fit_pct = round(100.0 / (1.0 + np.exp(-(u_scaled - 1.6) / 1.4)), 1)
            U_scores[k] = u_scaled

            if not is_elig:
                feas = 'Chưa đủ tổ hợp'
            elif raw_tot < 15.0:
                feas = 'Dưới ngưỡng sàn 15 điểm'
            elif adj_tot >= m['dc_top'] - 1.0:
                feas = 'Cao'
            elif adj_tot >= m['dc_avg']:
                feas = 'Trung bình'
            elif adj_tot >= m['dc_basic']:
                feas = 'Thấp - chỉ nhóm trường cơ bản'
            else:
                feas = 'Rất thấp'

            c_info = self.combos_catalog.get(best_ckey, {'code': '', 'name': 'Chưa có'}) if is_elig else {'code': '', 'name': 'Chưa có'}
            pct_rank = self.estimate_combo_percentile(best_ckey, raw_tot) if (is_g12 and is_elig) else None

            major_details.append({
                'major_id': k,
                'major_name': m['name'],
                'group_code': m['group_code'],
                'group_name': m['group_name'],
                'fit_score': fit_pct,
                'combo_code': c_info['code'],
                'combo_name': c_info['name'],
                'raw_score': raw_tot if is_elig else None,
                'adj_score': adj_tot if is_elig else None,
                'dc_top': m['dc_top'],
                'dc_avg': m['dc_avg'],
                'dc_basic': m['dc_basic'],
                'diff_vs_avg': reach_diff if is_elig else None,
                'feasibility': feas,
                'percentile_g12': pct_rank,
                'min_tuition': m['min_tuition'],
                'nang_khieu': m['nang_khieu'],
                'holland_profile': m['holland'],
                '_f_apt': f_apt
            })

        G_max = np.full(len(self.groups), -1e9)
        for j in range(len(self.groups)):
            g_indices = [k for k, m in enumerate(self.majors) if m['group_idx'] == j]
            G_max[j] = U_scores[g_indices].max()

        exp_g = np.exp(G_max - G_max.max())
        probs_g = exp_g / exp_g.sum()
        g_order = np.argsort(-G_max)

        top_groups = [
            {
                'rank': int(r + 1),
                'group_code': self.groups[j]['code'],
                'group_name': self.groups[j]['name'],
                'confidence_pct': round(float(probs_g[j] * 100), 1)
            }
            for r, j in enumerate(g_order)
        ]

        m_order = np.argsort(-U_scores)
        top_majors = []
        for k in m_order[:5]:
            item = dict(major_details[int(k)])
            item.pop('_f_apt', None)
            top_majors.append(item)

        top1 = major_details[int(m_order[0])]
        top1_group_code = top1['group_code']

        kc_ok = top1_group_code in ['CNTT', 'KTTCNH', 'QTKD', 'NGOAINGU', 'TT_NT', 'LUAT', 'DULICH', 'KHXH']
        dg_ok = top1_group_code in ['CNTT', 'KTCN', 'KHTN', 'KTTCNH', 'QTKD', 'YDUOC', 'KIENTRUC']
        if not is_g12:
            admission_method = 'Chưa áp dụng (lớp 10/11 - tập trung tối ưu điểm Học bạ & chọn tổ hợp môn)'
        else:
            admission_method = 'Thi tốt nghiệp THPT'
            if (gpa_hb * 3.0 >= top1['dc_avg'] + 1.0) and (top1['diff_vs_avg'] is not None and top1['diff_vs_avg'] < 0):
                admission_method = 'Xét học bạ (kết hợp thi THPT)'
            if dgnl is not None and float(dgnl) >= 90.0 and dg_ok:
                admission_method = 'Đánh giá năng lực (HSA/TSA)'
            if ielts is not None and float(ielts) >= 6.0 and gpa_hb >= 7.5 and kc_ok:
                admission_method = 'Xét tuyển kết hợp (IELTS + học bạ/thi THPT)'
            if giai_hsg == 'Quốc gia/Quốc tế':
                admission_method = 'Tuyển thẳng/Ưu tiên xét tuyển (HSG quốc gia)'

        warnings = []
        if top1['raw_score'] is None:
            warnings.append('Thiếu tổ hợp xét tuyển phù hợp')
        if budget < top1['min_tuition']:
            warnings.append('Ngân sách thấp hơn học phí dự kiến')
        if top1['raw_score'] is not None:
            if top1['raw_score'] < 15.0:
                warnings.append('Tổng điểm tổ hợp dưới ngưỡng sàn 15 điểm')
            elif top1['adj_score'] < top1['dc_basic']:
                warnings.append('Điểm dự kiến thấp hơn cả nhóm trường cơ bản')
            elif top1['adj_score'] < top1['dc_avg']:
                warnings.append('Điểm dự kiến thấp hơn điểm chuẩn trung bình ngành')

        top1_g_idx = self.group_code_to_idx[top1_group_code]
        if fit_g[top1_g_idx] > (fit_g.mean() + fit_g.std()) and top1['_f_apt'] < -0.5:
            warnings.append('Lệch giữa sở thích và năng lực')
        if top1['nang_khieu']:
            warnings.append('Cần thi năng khiếu/đánh giá riêng')
        if top1_group_code == 'QPAN':
            w_qp = 'Cần sơ tuyển (sức khỏe, lý lịch)'
            if the_luc <= 2:
                w_qp += ' - thể lực chưa đáp ứng'
            warnings.append(w_qp)

        intention_aligned = (du_dinh == top_groups[0]['group_name']) or (du_dinh == top_groups[0]['group_code'])

        return {
            'student_grade': lop,
            'gpa_hoc_ba': gpa_hb,
            'top_groups': top_groups[:3],
            'top_majors': top_majors,
            'admission_method': admission_method,
            'warnings': warnings,
            'warning_string': ' | '.join(warnings) if warnings else 'Không',
            'student_intention': du_dinh,
            'intention_aligned': bool(intention_aligned),
        }
