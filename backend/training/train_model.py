# -*- coding: utf-8 -*-
"""
train_model.py - Huấn luyện mô hình & xuất ai_expert_model_2026.json
(Tách từ CELL 2 + CELL 3 của notebook Colab.)

Cách chạy (từ thư mục backend/):
    python training/train_model.py --data-dir training/data
    python training/train_model.py --data-dir training/data --gbdt     # huấn luyện thêm GBDT (tùy chọn)

Cần có trong --data-dir:
    dataset_tu_van_nganh_nghe_thpt_2026.csv   (60.000 học sinh, ~51 MB)
    danh_muc_nganh_2026.csv
"""
import argparse
import json
import os
import sys
from statistics import NormalDist

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # để import được catalog.py nằm cạnh file này
from catalog import SUBJ, SN, SSHORT, SCOL, CODE, GROUPS, PACKAGES, VALUES, build  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default=os.path.join(HERE, 'data'))
    ap.add_argument('--out', default=os.path.join(os.path.dirname(HERE), 'model', 'ai_expert_model_2026.json'))
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--gbdt', action='store_true', help='huấn luyện thêm HistGradientBoosting và lưu sklearn_models.pkl')
    args = ap.parse_args()

    data_csv = os.path.join(args.data_dir, 'dataset_tu_van_nganh_nghe_thpt_2026.csv')
    if not os.path.exists(data_csv):
        sys.exit(f'Không tìm thấy {data_csv}\nHãy copy file CSV 60.000 học sinh vào thư mục --data-dir.')

    # ---------------------------------------------------------------- CELL 2: đọc dữ liệu
    df = pd.read_csv(data_csv)
    gid, NG = build()
    print(f'Dữ liệu: {df.shape[0]:,} học sinh x {df.shape[1]} cột')
    print(df['tap'].value_counts().to_string())

    # ---------------------------------------------------------------- CELL 3: đặc trưng
    K = len(NG)
    NGp = len(GROUPS)
    HT = ['R', 'I', 'A', 'S', 'E', 'C']
    SI = {s: i for i, s in enumerate(SUBJ)}

    train_mask = (df['tap'] == 'train').values
    val_mask = (df['tap'] == 'val').values
    test_mask = (df['tap'] == 'test').values
    g12_all = (df['lop'].values == 12)

    hb_cols = [f'hb_{SCOL[s]}' for s in SUBJ]
    thi_cols = [f'thi_{SCOL[s]}' for s in SUBJ]
    qt_cols = [f'quan_tam_{G[0].lower()}' for G in GROUPS]

    HB_all = df[hb_cols].values.astype(float)
    EX_all = df[thi_cols].values.astype(float)

    ex_mean = np.nanmean(EX_all[train_mask & g12_all], axis=0)
    ex_std = np.nanstd(EX_all[train_mask & g12_all], axis=0)

    ZHB = (HB_all - 7.7) / 0.95
    zexam = (EX_all - ex_mean) / ex_std
    has_hb = ~np.isnan(ZHB)
    has_ex = ~np.isnan(zexam)
    zperf = np.where(has_ex & has_hb, 0.6 * zexam + 0.4 * ZHB, np.where(has_hb, 0.75 * ZHB, np.nan))

    proj = ex_mean + ex_std * 0.8 * ZHB
    studied = has_hb
    taken = has_ex & g12_all[:, None]
    SCORE = np.where(g12_all[:, None], EX_all, np.where(studied, proj, np.nan))
    AVc = np.where(g12_all[:, None], taken, studied)

    ALLC = sorted(
        {frozenset(c) for G in GROUPS for c in G[4].split(',')} |
        {frozenset(c) for n in NG for c in n['combos']},
        key=lambda s: ''.join(sorted(s))
    )
    CI = {c: i for i, c in enumerate(ALLC)}
    NEG = -1e9
    N = len(df)
    TOT = np.full((N, len(ALLC)), NEG)
    for i, c in enumerate(ALLC):
        idx = [SI[x] for x in c]
        ok = AVc[:, idx].all(1)
        TOT[:, i] = np.where(ok, np.nansum(SCORE[:, idx], 1), NEG)

    pri = df['diem_uu_tien_khu_vuc'].values.astype(float)

    def adj_score(t, p):
        p_arr = p[:, None] if t.ndim == 2 else p
        return t + np.where(t >= 22.5, (30.0 - t) / 7.5 * p_arr, p_arr)

    RI = df[[f'holland_{t}' for t in HT]].values.astype(float)
    rc = RI - RI.mean(1, keepdims=True)
    HK = np.array([[n['hol'][t] for t in HT] for n in NG])
    fit_k = rc @ (HK / HK.sum(1, keepdims=True)).T

    def keymat(keys):
        M = np.zeros((len(keys), 11))
        for i, d in enumerate(keys):
            for s, w in d.items():
                M[i, SI[s]] = w
        return M

    def apt_of(M, z_mat):
        Zf = np.nan_to_num(z_mat)
        A = (~np.isnan(z_mat)).astype(float)
        num = Zf @ M.T
        den = A @ M.T
        return np.where(den > 0, num / np.maximum(den, 1e-9), 0.0)

    KM = keymat([n['key'] for n in NG])
    apt_k = np.clip(apt_of(KM, zperf), -2.5, 2.5)

    gi = np.array([n['gi'] for n in NG])
    DCk = np.array([n['dc_mid'] for n in NG])
    DCm = 15.0 + (DCk - 15.0) * 0.65
    DCb = np.maximum(15.0, DCm - 3.0)

    best_tot = np.full((N, K), NEG)
    for k, n in enumerate(NG):
        ci = [CI[frozenset(c)] for c in n['combos']]
        best_tot[:, k] = TOT[:, ci].max(1)

    elig = best_tot > NEG / 2
    tot_adj = np.where(elig, adj_score(np.where(elig, best_tot, 0.0), pri), 0.0)
    reach_raw = tot_adj - DCm
    reach_k = np.clip((reach_raw + 1.0) / 3.0, -2.5, 0.4)

    MINC = np.array([G[5] for G in GROUPS], float)
    TAG = np.array([G[7] for G in GROUPS], float)
    budget = df['ngan_sach_hoc_phi_trieu_nam'].values.astype(float)
    bud_pen_k = -np.minimum(1.5, np.maximum(0.0, MINC[gi][None, :] - budget[:, None]) / 12.0)

    val_map = {v: i for i, v in enumerate(VALUES)}
    value_idx = np.array([val_map[v] for v in df['uu_tien_dinh_huong'].values])
    val_k = TAG[gi][:, value_idx].T

    GN = [G[0] for G in GROUPS]
    fam_raw = df['gia_dinh_goi_y_nhom_nganh'].values
    fam_k = np.zeros((N, K), dtype=float)
    for j, gcode in enumerate(GN):
        fam_k[:, gi == j] = (fam_raw == gcode)[:, None].astype(float)

    quan_tam = df[qt_cols].values.astype(float)
    int_k = (quan_tam[:, gi] - 3.0)

    the_luc = df['the_luc'].values.astype(float)
    qp_pen_k = np.where((gi == gid['QPAN'])[None, :] & (the_luc[:, None] <= 2), -1.0, 0.0)
    elig_pen_k = np.where(elig, 0.0, -3.0)

    # ---------------------------------------------------------------- Mô hình 1: Hybrid Utility Ranking
    print(f'\nHuấn luyện Mô hình 1: Hybrid Utility Ranking ({int(train_mask.sum()):,} HS tập train)...')
    y_group = np.array([gid[m] for m in df['ma_nhom_nganh_top1'].values])
    nganh_to_idx = {n['name']: k for k, n in enumerate(NG)}
    y_major = np.array([nganh_to_idx[m] for m in df['nganh_goi_y_1'].values])

    F_list = [fit_k, int_k, apt_k, reach_k, bud_pen_k, fam_k, val_k, elig_pen_k, qp_pen_k]
    X_tr = np.stack([f[train_mask] for f in F_list], axis=-1)
    y_maj_tr = y_major[train_mask]

    w_feat = np.ones(9, dtype=np.float64)
    b_major = np.zeros(K, dtype=np.float64)
    lr = 0.05
    m_w, v_w = np.zeros_like(w_feat), np.zeros_like(w_feat)
    m_b, v_b = np.zeros_like(b_major), np.zeros_like(b_major)
    batch_size = 4096
    n_tr = X_tr.shape[0]
    rng_tr = np.random.default_rng(42)

    for epoch in range(1, args.epochs + 1):
        perm = rng_tr.permutation(n_tr)
        for start in range(0, n_tr, batch_size):
            idx = perm[start:start + batch_size]
            xb = X_tr[idx]
            yb = y_maj_tr[idx]
            B_len = len(idx)

            logits = np.tensordot(xb, w_feat, axes=([2], [0])) + b_major[None, :]
            exp_l = np.exp(logits - logits.max(axis=1, keepdims=True))
            probs = exp_l / exp_l.sum(axis=1, keepdims=True)

            grad_logits = probs.copy()
            grad_logits[np.arange(B_len), yb] -= 1.0
            grad_logits /= B_len

            gw = np.einsum('bkf,bk->f', xb, grad_logits) + 2e-4 * w_feat
            gb = grad_logits.sum(axis=0)

            m_w = 0.9 * m_w + 0.1 * gw
            v_w = 0.999 * v_w + 0.001 * (gw ** 2)
            m_b = 0.9 * m_b + 0.1 * gb
            v_b = 0.999 * v_b + 0.001 * (gb ** 2)

            w_feat -= lr * (m_w / (1 - 0.9 ** epoch)) / (np.sqrt(v_w / (1 - 0.999 ** epoch)) + 1e-8)
            b_major -= lr * (m_b / (1 - 0.9 ** epoch)) / (np.sqrt(v_b / (1 - 0.999 ** epoch)) + 1e-8)
        if epoch % 10 == 0:
            print(f'  epoch {epoch}/{args.epochs}')

    X_all_feat = np.stack(F_list, axis=-1)
    U_pred = np.tensordot(X_all_feat, w_feat, axes=([2], [0])) + b_major[None, :]
    G_pred = np.full((N, NGp), -1e9)
    for j in range(NGp):
        G_pred[:, j] = U_pred[:, gi == j].max(axis=1)

    def eval_split(mask, name):
        g_top3 = np.argsort(-G_pred[mask], axis=1)[:, :3]
        yg = y_group[mask]
        g_acc1 = np.mean(g_top3[:, 0] == yg) * 100
        g_acc3 = np.mean(np.any(g_top3 == yg[:, None], axis=1)) * 100
        m_top5 = np.argsort(-U_pred[mask], axis=1)[:, :5]
        ym = y_major[mask]
        m_acc1 = np.mean(m_top5[:, 0] == ym) * 100
        m_acc3 = np.mean(np.any(m_top5[:, :3] == ym[:, None], axis=1)) * 100
        m_acc5 = np.mean(np.any(m_top5 == ym[:, None], axis=1)) * 100
        print(f'  [{name.upper():8s}] 15 nhóm -> Top-1 {g_acc1:.2f}% | Top-3 {g_acc3:.2f}% || '
              f'110 ngành -> Top-1 {m_acc1:.2f}% | Top-3 {m_acc3:.2f}% | Top-5 {m_acc5:.2f}%')
        return {'group_top1': round(float(g_acc1), 2), 'group_top3': round(float(g_acc3), 2),
                'major_top1': round(float(m_acc1), 2), 'major_top3': round(float(m_acc3), 2),
                'major_top5': round(float(m_acc5), 2)}

    metrics = {
        'train': eval_split(train_mask, 'train'),
        'val': eval_split(val_mask, 'val'),
        'test': eval_split(test_mask, 'test'),
        'test_L12': eval_split(test_mask & g12_all, 'test_L12'),
    }

    # ---------------------------------------------------------------- Mô hình 2 (tùy chọn): GBDT
    if args.gbdt:
        import joblib
        from sklearn.ensemble import HistGradientBoostingClassifier
        print('\nHuấn luyện Mô hình 2: HistGradientBoostingClassifier...')
        raw_feature_cols = (
            ['lop', 'diem_uu_tien_khu_vuc', 'ngan_sach_hoc_phi_trieu_nam', 'the_luc', 'gpa_hoc_ba', 'ielts', 'dgnl_hsa_150'] +
            [f'holland_{t}' for t in HT] + qt_cols + hb_cols + thi_cols
        )
        X_tab = df[raw_feature_cols].copy()
        clf = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, max_depth=6, random_state=42)
        clf.fit(X_tab[train_mask], y_group[train_mask])
        proba = clf.predict_proba(X_tab[test_mask])
        print(f'  [GBDT - TEST] Top-1 {np.mean(np.argmax(proba, 1) == y_group[test_mask]) * 100:.2f}%')
        joblib.dump({'clf_gbdt': clf, 'feature_cols': raw_feature_cols},
                    os.path.join(os.path.dirname(args.out), 'sklearn_models.pkl'))

    # ---------------------------------------------------------------- Phân vị tổ hợp + xuất JSON
    combo_keys = [''.join(sorted(s, key=lambda x: SUBJ.index(x))) for s in ALLC]
    g12_idx = np.where(g12_all)[0]
    combo_percentiles = {}
    for i, c in enumerate(ALLC):
        ckey = combo_keys[i]
        scores_c = TOT[g12_idx, i]
        valid_c = scores_c[scores_c > 0]
        if len(valid_c) >= 20:
            qs = np.percentile(valid_c, np.linspace(0, 100, 21))
            combo_percentiles[ckey] = [round(float(x), 2) for x in qs]
        else:
            idx_s = [SI[x] for x in c]
            nd = NormalDist(float(ex_mean[idx_s].sum()), float(np.sqrt((ex_std[idx_s] ** 2).sum())))
            combo_percentiles[ckey] = [round(max(6.0, min(30.0, nd.inv_cdf(p))), 2) for p in np.linspace(0.01, 0.99, 21)]

    artifact = {
        'weights': {
            'w_feat': [round(float(x), 5) for x in w_feat],
            'b_major': [round(float(x), 5) for x in b_major],
            'ex_mean': {s: round(float(ex_mean[SI[s]]), 4) for s in SUBJ},
            'ex_std': {s: round(float(ex_std[SI[s]]), 4) for s in SUBJ},
        },
        'metrics': metrics,
        'groups': [
            {'code': G[0], 'name': G[1], 'holland': G[2], 'key_weights': {c[0]: float(c[1:]) for c in G[3].split(',')},
             'default_combos': G[4].split(','), 'min_tuition': G[5], 'prestige': G[6], 'value_tags': G[7]}
            for G in GROUPS
        ],
        'majors': [
            {'id': k, 'group_code': n['group'], 'group_idx': n['gi'], 'group_name': GROUPS[n['gi']][1], 'name': n['name'],
             'dc_top': round(float(DCk[k]), 2), 'dc_avg': round(float(DCm[k]), 2), 'dc_basic': round(float(DCb[k]), 2),
             'holland': {t: round(float(n['hol'][t]), 2) for t in HT},
             'key_weights': {s: round(float(w), 2) for s, w in n['key'].items()},
             'combos': [''.join(sorted(c, key=lambda x: SUBJ.index(x))) for c in n['combos']],
             'min_tuition': GROUPS[n['gi']][5], 'nang_khieu': bool(n['nang_khieu'])}
            for k, n in enumerate(NG)
        ],
        'combos_catalog': {
            ''.join(sorted(s, key=lambda x: SUBJ.index(x))): {
                'code': CODE.get(s, 'MOI'),
                'name': '-'.join(SSHORT[c] for c in sorted(s, key=lambda x: SUBJ.index(x))),
                'subjects': [c for c in sorted(s, key=lambda x: SUBJ.index(x))],
                'percentiles': combo_percentiles[''.join(sorted(s, key=lambda x: SUBJ.index(x)))],
            }
            for s in ALLC
        },
        'packages': [{'code': p, 'name': ' - '.join(SSHORT[c] for c in p), 'subjects': list(p)} for p in PACKAGES],
        'values': VALUES,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(artifact, f, ensure_ascii=False, indent=2)
    print(f'\nĐã lưu mô hình: {args.out}')


if __name__ == '__main__':
    main()
