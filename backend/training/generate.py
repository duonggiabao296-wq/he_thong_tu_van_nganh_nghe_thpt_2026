# -*- coding: utf-8 -*-
import sys, numpy as np, pandas as pd
from statistics import NormalDist
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from catalog import *

nd = NormalDist()
rng = np.random.default_rng(20261111)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60000
OUT = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/out'
sig = lambda x: 1 / (1 + np.exp(-x))
gum = lambda *s: rng.gumbel(size=s)


def zstd(x):
    return (x - x.mean(0)) / x.std(0)


# ------------------------------------------------------------------ tham số quốc gia (hiệu chỉnh từ bài báo)
def solve(p_lt5, p_ge, thr):
    z1 = nd.inv_cdf(p_lt5); z2 = nd.inv_cdf(1 - p_ge)
    sd = (thr - 5) / (z2 - z1)
    return 5 - z1 * sd, sd


def one(p_lt5, sd):
    return 5 - nd.inv_cdf(p_lt5) * sd, sd


NAT = {'T': solve(.4234, .1178, 8), 'V': solve(.152, .3539, 7), 'L': solve(.4269, .0786, 8), 'B': solve(.347, .10, 8),
       'D': solve(.55, .028, 8), 'K': solve(.52, .0072, 8), 'A': solve(.556, .089, 8), 'I': solve(.2783, .1035, 8),
       'H': one(.2444, 1.6), 'S': one(.3284, 1.7), 'C': (6.5, 1.3)}
MU = np.array([NAT[s][0] for s in SUBJ]); SD = np.array([NAT[s][1] for s in SUBJ])
SD = SD * np.array([1, 1] + [1.18] * 9)  # phân tán rộng hơn do chọn lọc thí sinh
SI = {s: i for i, s in enumerate(SUBJ)}
TARGET_COMBO = {'TLH': 19.41, 'TVA': 19.01, 'TLA': 18.41, 'VSD': 17.23, 'THB': 16.69}

# ------------------------------------------------------------------ nhân khẩu học
R1, R2, R3, R4, R5, R6 = ('Đồng bằng sông Hồng', 'Trung du & miền núi phía Bắc', 'Bắc Trung Bộ & Duyên hải miền Trung',
                          'Tây Nguyên', 'Đông Nam Bộ', 'Đồng bằng sông Cửu Long')
PROV = [('Hà Nội', R1, 8.7, .55, 0, 1), ('Hải Phòng', R1, 4.7, .5, 0, 1), ('Bắc Ninh', R1, 3.6, .35, 0, 0),
        ('Hưng Yên', R1, 3.2, .2, 0, 0), ('Ninh Bình', R1, 4.4, .25, .03, 0), ('Quảng Ninh', R1, 1.4, .5, .15, 0),
        ('Tuyên Quang', R2, 1.9, .2, .6, 0), ('Lào Cai', R2, 1.8, .25, .6, 0), ('Thái Nguyên', R2, 1.8, .35, .2, 0),
        ('Phú Thọ', R2, 4.0, .25, .25, 0), ('Cao Bằng', R2, .54, .2, .8, 0), ('Lạng Sơn', R2, .8, .25, .6, 0),
        ('Lai Châu', R2, .46, .15, .9, 0), ('Điện Biên', R2, .6, .2, .85, 0), ('Sơn La', R2, 1.3, .15, .85, 0),
        ('Thanh Hóa', R3, 3.7, .2, .2, 0), ('Nghệ An', R3, 3.4, .2, .25, 0), ('Hà Tĩnh', R3, 1.3, .2, .1, 0),
        ('Quảng Trị', R3, 1.9, .25, .2, 0), ('Huế', R3, 1.2, .5, .1, 1), ('Đà Nẵng', R3, 3.1, .75, .02, 1),
        ('Quảng Ngãi', R3, 2.1, .25, .2, 0), ('Khánh Hòa', R3, 2.3, .4, .1, 0),
        ('Gia Lai', R4, 3.5, .3, .35, 0), ('Đắk Lắk', R4, 3.3, .25, .3, 0), ('Lâm Đồng', R4, 3.3, .3, .3, 0),
        ('TP. Hồ Chí Minh', R5, 14, .75, 0, 1), ('Đồng Nai', R5, 4.4, .4, .02, 0), ('Tây Ninh', R5, 3.2, .25, 0, 0),
        ('Cần Thơ', R6, 4.2, .6, 0, 1), ('Vĩnh Long', R6, 3.9, .2, 0, 0), ('Đồng Tháp', R6, 4.3, .2, 0, 0),
        ('Cà Mau', R6, 2.7, .2, 0, 0), ('An Giang', R6, 4.9, .25, .02, 0)]
assert len(PROV) == 34
pw = np.array([p[2] for p in PROV]); pw /= pw.sum()
pi = rng.choice(len(PROV), N, p=pw)
province = np.array([PROV[i][0] for i in pi]); region = np.array([PROV[i][1] for i in pi])
urb_p = np.array([PROV[i][3] for i in pi]); mtn_p = np.array([PROV[i][4] for i in pi]); big = np.array([PROV[i][5] for i in pi])
AREA_MTN = 'Miền núi - vùng khó khăn'
area = np.where(rng.random(N) < mtn_p, AREA_MTN, np.where(rng.random(N) < urb_p, 'Thành thị', 'Nông thôn'))
urban = (area == 'Thành thị').astype(float); mtn = (area == AREA_MTN).astype(float)
nam = rng.random(N) < .49
gender = np.where(nam, 'Nam', 'Nữ')
minority = ((mtn == 1) & (rng.random(N) < .55)) | (rng.random(N) < .02)
r = rng.random(N)
school = np.where(minority & (mtn == 1) & (r < .12), 'THPT DTNT',
         np.where(r < .025, 'GDTX',
         np.where((rng.random(N) < np.where(big == 1, .06, .035)) & (mtn == 0), 'THPT chuyên',
         np.where(rng.random(N) < np.where(urban == 1, .15, .04), 'THPT tư thục', 'THPT công lập'))))
kv = np.where(mtn == 1, np.where(rng.random(N) < .8, 'KV1', 'KV2-NT'),
     np.where(area == 'Nông thôn', np.where(rng.random(N) < .8, 'KV2-NT', 'KV2'),
              np.where((big == 1) & (rng.random(N) < .85), 'KV3', 'KV2')))
PRI = {'KV1': .75, 'KV2-NT': .5, 'KV2': .25, 'KV3': 0.0}
pri = np.array([PRI[k] for k in kv])
grade = rng.choice([10, 11, 12], N, p=[.30, .30, .40]); g12 = grade == 12


def rank_cut(x, cum):
    rk = x.argsort().argsort() / N
    return 1 + np.searchsorted(np.array(cum), rk, side='right')


ed_lat = rng.normal(0, 1, N) + .55 * urban - .45 * mtn + .3 * big
edu = rank_cut(ed_lat, [.10, .40, .62, .92])  # 1..5
in_lat = .45 * zstd(edu.astype(float)) + .4 * urban + .25 * big - .4 * mtn + rng.normal(0, .85, N)
income = rank_cut(in_lat, [.12, .40, .72, .90])  # 1..5

JW = {'Thành thị': [.02, .15, .22, .14, .04, .04, .10, .04, .16, .09], 'Nông thôn': [.22, .20, .15, .08, .04, .02, .03, .03, .17, .06],
      AREA_MTN: [.45, .10, .08, .12, .05, .02, .01, .04, .10, .03]}
EM_HI = np.array([.3, .3, .9, 2.2, 3, 3, 3.5, 1.5, .5, .8]); EM_LO = np.array([1.5, 1.3, .9, .4, .2, .1, .1, .6, 1.2, 1.2])


def sample_jobs(mother):
    w = np.array([JW[a] for a in area], float)
    mult = np.where((edu >= 4)[:, None], EM_HI, np.where((edu <= 2)[:, None], EM_LO, 1.0))
    w = w * mult
    if mother:
        w[:, 9] *= 2.2; w[:, 7] *= .2; w[:, 1] *= .8
    w /= w.sum(1, keepdims=True)
    c = w.cumsum(1); u = rng.random(N)[:, None]
    return (u > c).sum(1)


fj, mj = sample_jobs(False), sample_jobs(True)
fjob = np.array(JOBS)[fj]; mjob = np.array(JOBS)[mj]

# ------------------------------------------------------------------ Holland RIASEC
HT = ['R', 'I', 'A', 'S', 'E', 'C']
main = rng.choice(6, N, p=[.15, .19, .15, .18, .19, .14])
second = (main + rng.integers(1, 6, N)) % 6
RI = 2.5 + rng.normal(0, .55, (N, 6))
RI[np.arange(N), main] += 1.2; RI[np.arange(N), second] += .6
g = (rng.normal(0, 1, N) + np.select([school == 'THPT chuyên', school == 'THPT tư thục', school == 'GDTX', school == 'THPT DTNT'],
                                      [1.3, .15, -.9, -.2], 0)
     + .15 * urban - .4 * mtn - .1 * minority
     + np.select([region == R1, region == R2, region == R3, region == R4, region == R5, region == R6],
                 [.12, -.2, .1, -.2, .05, -.15], 0)
     + .08 * (income - 3) + .1 * (edu - 3))
RI[:, 0] += .25 * nam; RI[:, 3] += .2 * (~nam); RI[:, 2] += .1 * (~nam); RI[:, 1] += .25 * g; RI[:, 5] += .1 * g
RI = np.clip(np.round(RI, 1), 1, 5)
ZH = zstd(RI)  # z Holland (R,I,A,S,E,C)

# ------------------------------------------------------------------ năng lực tiềm ẩn theo môn
e = rng.normal(0, 1, (N, 11))
ZI, ZA_, ZS, ZE, ZC, ZR = ZH[:, 1], ZH[:, 2], ZH[:, 3], ZH[:, 4], ZH[:, 5], ZH[:, 0]
raw = np.zeros((N, 11))
raw[:, 0] = .7 * g + .15 * ZI + .1 * ZC + .6 * e[:, 0]
raw[:, 1] = .55 * g + .2 * ZA_ + .15 * ZS + .15 * (~nam) + .7 * e[:, 1]
raw[:, 2] = .5 * g + .15 * ZA_ + .1 * ZE + .25 * (income - 3) / 1.4 + .3 * urban + .6 * e[:, 2]
raw[:, 3] = .6 * g + .2 * ZI + .15 * ZR + .15 * nam + .6 * e[:, 3]
raw[:, 4] = .6 * g + .2 * ZI + .1 * ZR + .65 * e[:, 4]
raw[:, 5] = .5 * g + .15 * ZI + .1 * ZS + .08 * (~nam) + .7 * e[:, 5]
raw[:, 6] = .45 * g + .15 * ZS + .1 * ZA_ + .75 * e[:, 6]
raw[:, 7] = .45 * g + .12 * ZS + .7 * e[:, 7]
raw[:, 8] = .45 * g + .15 * ZE + .1 * ZS + .75 * e[:, 8]
raw[:, 9] = .5 * g + .2 * ZI + .15 * ZC + .1 * ZR + .06 * (income - 3) + .65 * e[:, 9]
raw[:, 10] = .45 * g + .2 * ZR + .1 * ZI + .75 * e[:, 10]
Z = zstd(raw)

# sở thích môn học -> chọn tổ hợp 4 môn
pref = np.zeros((N, 11))
pref[:, 2] = .3 * Z[:, 2]
pref[:, 3] = .4 * ZI + .3 * ZR; pref[:, 4] = .4 * ZI + .1 * ZR; pref[:, 5] = .3 * ZI + .4 * ZS
pref[:, 6] = .4 * ZS + .3 * ZA_; pref[:, 7] = .3 * ZS + .2 * ZR; pref[:, 8] = .4 * ZE + .3 * ZS + .2 * ZC
pref[:, 9] = .4 * ZI + .2 * ZC + .2 * ZR + .15; pref[:, 10] = .4 * ZR + .2 * ZI
LET = {'L': 3, 'H': 4, 'B': 5, 'S': 6, 'D': 7, 'K': 8, 'I': 9, 'C': 10}
PM = np.zeros((11, len(PACKAGES)))
for j, p in enumerate(PACKAGES):
    for ch in p:
        PM[LET[ch], j] = 1
putil = (.8 * Z + .8 * pref) @ PM + rng.gumbel(size=(N, len(PACKAGES))) * .6 + .3 * PM[9]
pk = putil.argmax(1)
studied = np.zeros((N, 11), bool); studied[:, :3] = True
studied |= PM[:, pk].T.astype(bool)
pack_name = np.array([' - '.join(SSHORT[c] for c in PACKAGES[i]) for i in range(len(PACKAGES))])[pk]

# học bạ
infl = np.select([school == 'THPT chuyên', school == 'THPT tư thục', school == 'GDTX'], [.2, .25, .3], 0)
HB = np.clip(np.round(7.7 + .95 * Z + infl[:, None] + .35 * rng.normal(0, 1, (N, 11)), 1), 4, 10)
HB[~studied] = np.nan
ZHB = (HB - 7.7) / .95

# ------------------------------------------------------------------ điểm thi tốt nghiệp THPT 2026 (lớp 12)
cand = studied.copy()  # môn thi tự chọn: 1 trong 4 môn học sâu hoặc Tiếng Anh
cand[:, 0] = False; cand[:, 1] = False
# chọn môn thi: A00/D01 chọn lọc theo năng lực chung (Toán/Văn), B00/C00 gần như không chọn lọc
gz = (.5 * Z[:, 0] + .5 * Z[:, 1])
eu = .5 * pref + rng.gumbel(size=(N, 11)) * .7
eu[:, 3] += 1.3 * Z[:, 0]; eu[:, 4] += .8 * Z[:, 0]; eu[:, 9] += .3 + .4 * Z[:, 0]; eu[:, 5] += .2 * Z[:, 0]
eu[:, 6] += .9 * Z[:, 1]; eu[:, 7] += .9 * Z[:, 1]
eu[:, 2] += 1.5 * gz + .3 * urban - .55      # Tiếng Anh: chọn theo năng lực Toán/Văn + điều kiện học

eu[~cand] = -1e9
order = np.argsort(-eu, 1)
taken = np.zeros((N, 11), bool); taken[:, 0] = taken[:, 1] = True
taken[np.arange(N), order[:, 0]] = True; taken[np.arange(N), order[:, 1]] = True
taken &= g12[:, None]
exam_noise = rng.normal(0, 1, (N, 11))
boost = np.zeros(11)


def make_exam(boost):
    s = MU + SD * (.85 * Z + .527 * exam_noise) + boost
    return np.where(taken, np.clip(np.round(s * 4) / 4, 0, 10), np.nan)


def combo_total(EX, cs):
    idx = [SI[c] for c in cs]
    ok = taken[:, idx].all(1)
    return ok, EX[:, idx].sum(1)


for it in range(60):
    EX = make_exam(boost)
    for sname in 'LHBSDKAIC':
        i = SI[sname]; m = np.nanmean(EX[:, i])
        boost[i] = np.clip(boost[i] + .6 * (NAT[sname][0] - m), -1.5, 1.5)
EX = make_exam(boost)
EXAM_ALL = EX
mon1 = np.where(g12, np.array(SUBJ)[order[:, 0]], '')
mon2 = np.where(g12, np.array(SUBJ)[order[:, 1]], '')

# ------------------------------------------------------------------ chuẩn hóa điểm cho tư vấn
zexam = (EX - MU - boost) / SD
zperf = np.full((N, 11), np.nan)
has_hb = ~np.isnan(ZHB); has_ex = ~np.isnan(zexam)
zperf = np.where(has_ex & has_hb, .6 * zexam + .4 * ZHB, np.where(has_hb, .75 * ZHB, np.nan))
proj = MU + boost + SD * .8 * ZHB  # điểm thi dự kiến từ học bạ (lớp 10/11)
SCORE = np.where(g12[:, None], EX, np.where(studied, proj, np.nan))
AVc = np.where(g12[:, None], taken, studied)

# ------------------------------------------------------------------ danh mục ngành/tổ hợp
gid, NG = build()
K = len(NG); NGp = len(GROUPS)
ALLC = sorted({frozenset(c) for G in GROUPS for c in G[4].split(',')} | {frozenset(c) for n in NG for c in n['combos']},
              key=lambda s: ''.join(sorted(s)))
CI = {c: i for i, c in enumerate(ALLC)}
NEG = -1e9
TOT = np.full((N, len(ALLC)), NEG)
for i, c in enumerate(ALLC):
    idx = [SI[x] for x in c]
    ok = AVc[:, idx].all(1)
    TOT[:, i] = np.where(ok, np.nansum(SCORE[:, idx], 1), NEG)


def adj(t):  # điểm ưu tiên khu vực quy đổi theo quy chế (giảm dần khi tổng >= 22.5)
    p = pri[:, None] if t.ndim == 2 else pri
    return t + np.where(t >= 22.5, (30 - t) / 7.5 * p, p)


# ------------------------------------------------------------------ nhóm ngành: độ phù hợp Holland, quan tâm
HV = np.array([[G[2][t] for t in HT] for G in GROUPS])  # 15x6
rc = RI - RI.mean(1, keepdims=True)
fit_g = rc @ (HV / HV.sum(1, keepdims=True)).T


def keymat(keys):
    M = np.zeros((len(keys), 11))
    for i, d in enumerate(keys):
        for s, w in d.items(): M[i, SI[s]] = w
    return M


def apt_of(M):
    Zf = np.nan_to_num(zperf); A = (~np.isnan(zperf)).astype(float)
    num = Zf @ M.T; den = A @ M.T
    return np.where(den > 0, num / np.maximum(den, 1e-9), 0)


KG = keymat([{c[0]: float(c[1:]) for c in G[3].split(',')} for G in GROUPS])
apt_g = np.clip(apt_of(KG), -2.5, 2.5)
q_lat = 3 + .9 * zstd(fit_g) + .3 * apt_g + rng.normal(0, .7, (N, NGp))
quan_tam = np.clip(np.round(q_lat), 1, 5).astype(int)

# giá trị ưu tiên, ngân sách, gia đình gợi ý
vprob = np.array([[.28, .22, .22, .08, .20]] * N)
vprob[:, 0] += .08 * (income >= 4); vprob[:, 4] += .15 * (income <= 2) + .1 * mtn; vprob[:, 2] += .06 * (g > .5)
vprob /= vprob.sum(1, keepdims=True)
value = (rng.random(N)[:, None] > vprob.cumsum(1)).sum(1)
budget = np.clip(np.round(np.array([12, 20, 30, 50, 90])[income - 1] * np.exp(rng.normal(0, .35, N))), 5, 300).astype(int)
du_hoc = (rng.random(N) < sig(-2.4 + .6 * (income - 3) + .5 * urban + .3 * Z[:, 2])).astype(int)
hoc_xa = (rng.random(N) < sig(.3 + .4 * (income - 3) - .4 * (value == 4) * 2 + .3 * minority * 0)).astype(int)

FJ = {'Giáo viên': {'SUPHAM': 4, 'KHXH': 1.8, 'NGOAINGU': 1.5}, 'Y tế': {'YDUOC': 5, 'KHTN': 1.5},
      'Kỹ sư - IT - chuyên môn': {'CNTT': 3, 'KTCN': 3, 'KIENTRUC': 2, 'KTTCNH': 1.8},
      'Buôn bán - kinh doanh': {'KTTCNH': 3, 'QTKD': 3.5, 'DULICH': 1.8},
      'Công chức - viên chức': {'LUAT': 3, 'SUPHAM': 2.5, 'KTTCNH': 2, 'QPAN': 1.8, 'YDUOC': 1.8},
      'Lực lượng vũ trang': {'QPAN': 5}, 'Nông - lâm - ngư nghiệp': {'NONGLAM': 3, 'SUPHAM': 2, 'YDUOC': 2, 'QPAN': 1.5},
      'Công nhân - lao động phổ thông': {'KTCN': 2.5, 'CNTT': 1.5, 'SUPHAM': 1.5},
      'Lao động tự do': {'DULICH': 1.5, 'QTKD': 1.8, 'KTCN': 1.5}}
FJM = np.ones((len(JOBS), NGp)) * .5
for j, nm in enumerate(JOBS):
    for gname, w in FJ.get(nm, {}).items(): FJM[j, gid[gname]] += w
fam_w = FJM[fj] + FJM[mj]
fam_w = fam_w / fam_w.sum(1, keepdims=True)
fam_has = rng.random(N) < .5
fam_sug = (rng.random(N)[:, None] > fam_w.cumsum(1)).sum(1)
fam_sug = np.minimum(fam_sug, NGp - 1)

# ------------------------------------------------------------------ hiệu số ở mức ngành
HK = np.array([[n['hol'][t] for t in HT] for n in NG])
fit_k = rc @ (HK / HK.sum(1, keepdims=True)).T
apt_k = np.clip(apt_of(keymat([n['key'] for n in NG])), -2.5, 2.5)
gi = np.array([n['gi'] for n in NG])
DCk = np.array([n['dc_mid'] for n in NG])          # nhóm trường top (neo theo điểm chuẩn 2026 trên báo)
DCm = 15 + (DCk - 15) * .65                          # mức trung bình toàn hệ thống (ước tính)
DCb = np.maximum(15, DCm - 3.0)                      # nhóm trường cơ bản (sàn 15 điểm theo quy định 2026)
best_tot = np.full((N, K), NEG); best_c = np.zeros((N, K), np.int16)
for k, n in enumerate(NG):
    ci = [CI[frozenset(c)] for c in n['combos']]
    sub = TOT[:, ci]; best_tot[:, k] = sub.max(1); best_c[:, k] = np.array(ci)[sub.argmax(1)]
elig = best_tot > NEG / 2
tot_adj = np.where(elig, adj(np.where(elig, best_tot, 0)), 0)
reach_raw = tot_adj - DCm
reach_k = np.clip((reach_raw + 1.0) / 3.0, -2.5, .4)
MINC = np.array([G[5] for G in GROUPS], float); PREST = np.array([G[6] for G in GROUPS]); TAG = np.array([G[7] for G in GROUPS])
bud_pen = -np.minimum(1.5, np.maximum(0, MINC[gi][None, :] - budget[:, None]) / 12)
val_k = TAG[gi][:, value].T  # N x K
fam_k = (fam_has[:, None] & (fam_sug[:, None] == gi[None, :])).astype(float)
int_k = (quan_tam[:, gi] - 3).astype(float)
the_luc = np.clip(np.round(3.2 + .2 * nam + .9 * rng.normal(0, 1, N)), 1, 5).astype(int)
qp_pen = np.where((gi == gid['QPAN'])[None, :] & (the_luc[:, None] <= 2), -1.0, 0)
low_inc_bonus = ((gi == gid['SUPHAM']) | (gi == gid['QPAN']))[None, :] * (income <= 2)[:, None] * .4

noise_g = gum(N, NGp)[:, gi] * .3 + gum(N, K) * .3
DEM = np.array([.9, .6, .3, 1.0, .9, .9, .6, .5, .6, .6, .3, .1, .4, .5, .5])  # nhu cầu/độ phổ biến của nhóm ngành
prior_k = .6 * DEM[gi] + .06 * (DCk - 22)
U = (1.4 * fit_k + .7 * int_k + .9 * apt_k + 1.4 * reach_k + prior_k + bud_pen + .4 * fam_k + .5 * val_k
     + np.where(elig, 0, -3) + qp_pen + low_inc_bonus + noise_g)
top = np.argsort(-U, 1)[:, :3]
t1, t2, t3 = top[:, 0], top[:, 1], top[:, 2]
ar = np.arange(N)
G_max = np.full((N, NGp), -1e9)
for j in range(NGp):
    G_max[:, j] = U[:, gi == j].max(1)
gorder = np.argsort(-G_max, 1)[:, :3]
p_g = np.exp(G_max - G_max.max(1, keepdims=True)); p_g /= p_g.sum(1, keepdims=True)
conf = p_g[ar, gorder[:, 0]]
fit_score = np.round(100 * sig((U[ar, t1] - 1.6) / 1.4), 1)

# dự định của chính học sinh (khác khuyến nghị chuyên gia)
Rg = np.full((N, NGp), -3.0)
for j in range(NGp):
    Rg[:, j] = np.where(elig[:, gi == j], reach_k[:, gi == j], -3).max(1)
U2 = (.9 * (quan_tam - 3) + 1.2 * (fam_has[:, None] & (fam_sug[:, None] == np.arange(NGp)[None, :])) + .5 * zstd(fit_g)
      + .6 * TAG[:, value].T + .35 * PREST[None, :] + .25 * Rg + gum(N, NGp) * .8)
du_dinh = U2.argmax(1)

# ------------------------------------------------------------------ nhãn phụ
combo_names = np.array(['-'.join(SSHORT[c] for c in sorted(s, key=lambda x: SUBJ.index(x))) for s in ALLC])
combo_codes = np.array([CODE.get(s, 'MOI') for s in ALLC])
bc = best_c[ar, t1]
tot_top = best_tot[ar, t1]
tot_top_adj = tot_adj[ar, t1]
reach_top = reach_raw[ar, t1]
elig_top = elig[ar, t1]
tot_raw_top = np.where(elig_top, tot_top, 0)
muc_kt = np.where(~elig_top, 'Chưa đủ tổ hợp',
         np.where(tot_raw_top < 15, 'Dưới ngưỡng sàn 15 điểm',
         np.where(tot_top_adj >= DCk[t1] - 1, 'Cao',
         np.where(tot_top_adj >= DCm[t1], 'Trung bình',
         np.where(tot_top_adj >= DCb[t1], 'Thấp - chỉ nhóm trường cơ bản', 'Rất thấp')))))
nk = np.array([n['nang_khieu'] for n in NG])

# --- học bạ / hạnh kiểm
MAIN7 = np.where(np.isnan(HB), np.nan, HB)
gpa = np.round(np.nanmean(HB, 1), 2)
minm = np.nanmin(HB, 1)
hl = np.where((gpa >= 8) & (minm >= 6.5), 'Tốt', np.where((gpa >= 6.5) & (minm >= 5), 'Khá', np.where((gpa >= 5) & (minm >= 3.5), 'Đạt', 'Chưa đạt')))
hk = np.where(rng.random(N) < sig(2.6 + .4 * g), 'Tốt', np.where(rng.random(N) < .8, 'Khá', 'Đạt'))

# --- IELTS, ĐGNL, HSG
p_ielts = sig(-5.2 + .45 * income + .7 * urban + .5 * Z[:, 2] + .35 * (grade - 10) + .9 * (school == 'THPT tư thục') + .6 * (school == 'THPT chuyên'))
ielts = np.where(rng.random(N) < p_ielts, np.clip(np.round((4.5 + .9 * Z[:, 2] + .6 * rng.normal(0, 1, N)) * 2) / 2, 4, 8.5), np.nan)
abil = .5 * Z[:, 0] + .3 * Z[:, 1] + .2 * Z[:, 2]
dgnl = np.where(g12 & (rng.random(N) < sig(-.9 + .5 * g)), np.clip(np.round(72 + 22 * abil + 8 * rng.normal(0, 1, N)), 30, 150), np.nan)
p_hsg = sig(-3.6 + .9 * g + 1.2 * (school == 'THPT chuyên') + .3 * (grade - 10))
hsg_any = rng.random(N) < p_hsg
hsg_nat = hsg_any & (rng.random(N) < .10 + .25 * (school == 'THPT chuyên'))
hsg = np.where(hsg_nat, 'Quốc gia/Quốc tế', np.where(hsg_any, 'Cấp tỉnh/thành', 'Không'))
hsg_sub = np.where(hsg_any, np.array(SUBJ)[np.argmax(np.where(studied, Z + rng.normal(0, .6, (N, 11)), -9), 1)], '')
hsg_sub = np.array([SN[s] if s else '' for s in hsg_sub])

# --- phương thức xét tuyển đề xuất (chỉ lớp 12)
grp1 = gi[t1]
GN = np.array([G[0] for G in GROUPS])
hb3 = gpa * 3
gname1 = GN[grp1]
kc_ok = np.isin(gname1, ['CNTT', 'KTTCNH', 'QTKD', 'NGOAINGU', 'TT_NT', 'LUAT', 'DULICH', 'KHXH'])
dg_ok = np.isin(gname1, ['CNTT', 'KTCN', 'KHTN', 'KTTCNH', 'QTKD', 'YDUOC', 'KIENTRUC'])
pt = np.full(N, 'Thi tốt nghiệp THPT', dtype=object)
pt[(hb3 >= DCm[t1] + 1) & (reach_top < 0)] = 'Xét học bạ (kết hợp thi THPT)'
pt[~np.isnan(dgnl) & (np.nan_to_num(dgnl) >= 90) & dg_ok] = 'Đánh giá năng lực (HSA/TSA)'
pt[~np.isnan(ielts) & (np.nan_to_num(ielts) >= 6.0) & (gpa >= 7.5) & kc_ok] = 'Xét tuyển kết hợp (IELTS + học bạ/thi THPT)'
pt[hsg_nat & (grade == 12)] = 'Tuyển thẳng/Ưu tiên xét tuyển (HSG quốc gia)'
pt = np.where(g12, pt, 'Chưa áp dụng (lớp 10/11)')

# --- cảnh báo
warn = []
for i in range(N):
    w = []
    if not elig_top[i]: w.append('Thiếu tổ hợp xét tuyển phù hợp')
    if budget[i] < MINC[grp1[i]]: w.append('Ngân sách thấp hơn học phí dự kiến')
    if elig_top[i] and tot_top[i] < 15: w.append('Tổng điểm tổ hợp dưới ngưỡng sàn 15 điểm')
    elif elig_top[i] and tot_top_adj[i] < DCb[t1[i]]: w.append('Điểm dự kiến thấp hơn cả nhóm trường cơ bản')
    elif elig_top[i] and tot_top_adj[i] < DCm[t1[i]]: w.append('Điểm dự kiến thấp hơn điểm chuẩn trung bình ngành')
    if fit_g[i, grp1[i]] > fit_g[:, grp1[i]].mean() + fit_g[:, grp1[i]].std() and apt_k[i, t1[i]] < -.5: w.append('Lệch giữa sở thích và năng lực')
    if nk[t1[i]]: w.append('Cần thi năng khiếu/đánh giá riêng')
    if GN[grp1[i]] == 'QPAN': w.append('Cần sơ tuyển (sức khỏe, lý lịch)' + (' - thể lực chưa đáp ứng' if the_luc[i] <= 2 else ''))
    warn.append(' | '.join(w) if w else 'Không')

# ------------------------------------------------------------------ kỹ năng mềm
def lik(x): return np.clip(np.round(x), 1, 5).astype(int)
sk_gt = lik(2.9 + .5 * ZE + .4 * ZS + rng.normal(0, .7, N))
sk_logic = lik(2.9 + .5 * ZI + .4 * Z[:, 0] + rng.normal(0, .7, N))
sk_st = lik(2.9 + .6 * ZA_ + .2 * ZE + rng.normal(0, .8, N))
sk_nhom = lik(3.0 + .4 * ZS + .3 * ZE + rng.normal(0, .8, N))

# ------------------------------------------------------------------ phân vị tổ hợp (theo tinh thần hướng dẫn quy đổi 2026)
tt = np.where(g12, tot_top, np.nan)
cb = np.where(g12 & elig_top, combo_names[bc], '')
dfp = pd.DataFrame({'c': cb, 't': tt})
pct = dfp.groupby('c')['t'].rank(pct=True) * 100
pct = np.where((cb != '') & g12, pct.values, np.nan)

# ------------------------------------------------------------------ lắp DataFrame
D = {}
D['ma_hoc_sinh'] = [f'HS{i + 1:06d}' for i in range(N)]
D['tap'] = rng.choice(['train', 'val', 'test'], N, p=[.7, .15, .15])
D['lop'] = grade; D['gioi_tinh'] = gender; D['tinh_thanh'] = province; D['vung_mien'] = region
D['khu_vuc_cu_tru'] = area; D['loai_truong'] = school; D['dan_toc_thieu_so'] = minority.astype(int)
D['khu_vuc_uu_tien'] = kv; D['diem_uu_tien_khu_vuc'] = pri
D['nghe_cha'] = fjob; D['nghe_me'] = mjob; D['hoc_van_cha_me_cao_nhat'] = edu
D['muc_thu_nhap_gia_dinh'] = income; D['ngan_sach_hoc_phi_trieu_nam'] = budget
D['san_sang_hoc_xa_nha'] = hoc_xa; D['muon_du_hoc'] = du_hoc; D['uu_tien_dinh_huong'] = np.array(VALUES)[value]
D['gia_dinh_goi_y_nhom_nganh'] = np.where(fam_has, GN[fam_sug], 'Không')
D['to_hop_mon_chon'] = pack_name
for s in ELECTIVES: D[f'chon_{SCOL[s]}'] = studied[:, SI[s]].astype(int)
for s in SUBJ: D[f'hb_{SCOL[s]}'] = HB[:, SI[s]]
D['gpa_hoc_ba'] = gpa; D['hoc_luc'] = hl; D['hanh_kiem'] = hk
for t, i in zip(HT, range(6)): D[f'holland_{t}'] = RI[:, i]
D['ma_holland_3'] = np.array([''.join(np.array(HT)[np.argsort(-(RI[i] + rng.random(6) * .01))[:3]]) for i in range(N)])
D['ky_nang_giao_tiep'] = sk_gt; D['ky_nang_tu_duy_logic'] = sk_logic; D['ky_nang_sang_tao'] = sk_st; D['ky_nang_lam_viec_nhom'] = sk_nhom
D['the_luc'] = the_luc
for j, G in enumerate(GROUPS): D[f'quan_tam_{G[0].lower()}'] = quan_tam[:, j]
D['ielts'] = ielts; D['dgnl_hsa_150'] = dgnl; D['giai_hsg'] = hsg; D['mon_hsg'] = hsg_sub
D['mon_thi_tu_chon_1'] = np.array([SN[s] if s else '' for s in mon1]); D['mon_thi_tu_chon_2'] = np.array([SN[s] if s else '' for s in mon2])
for s in SUBJ: D[f'thi_{SCOL[s]}'] = EXAM_ALL[:, SI[s]]
D['tong_4_mon_thi'] = np.where(g12, np.round(np.nansum(EXAM_ALL, 1), 2), np.nan)
# nhãn
D['nhom_nganh_top1'] = np.array([GROUPS[j][1] for j in gorder[:, 0]])
D['nhom_nganh_top2'] = np.array([GROUPS[j][1] for j in gorder[:, 1]])
D['nhom_nganh_top3'] = np.array([GROUPS[j][1] for j in gorder[:, 2]])
D['ma_nhom_nganh_top1'] = GN[gorder[:, 0]]
D['nganh_goi_y_1'] = np.array([NG[k]['name'] for k in t1]); D['nganh_goi_y_2'] = np.array([NG[k]['name'] for k in t2]); D['nganh_goi_y_3'] = np.array([NG[k]['name'] for k in t3])
D['diem_phu_hop_top1'] = fit_score; D['do_tin_cay_nhom_top1'] = np.round(conf, 3)
D['to_hop_xet_tuyen_de_xuat'] = np.where(elig_top, combo_names[bc], 'Chưa có')
D['ma_to_hop_de_xuat'] = np.where(elig_top, combo_codes[bc], '')
D['tong_diem_to_hop_de_xuat'] = np.where(elig_top, np.round(tot_top, 2), np.nan)
D['tong_diem_sau_uu_tien'] = np.where(elig_top, np.round(tot_top_adj, 2), np.nan)
D['diem_chuan_nhom_truong_top_top1'] = DCk[t1]; D['diem_chuan_trung_binh_top1'] = np.round(DCm[t1], 2); D['diem_chuan_nhom_co_ban_top1'] = np.round(DCb[t1], 2)
D['chenh_lech_diem_so_voi_trung_binh_nganh'] = np.where(elig_top, np.round(reach_top, 2), np.nan)
D['muc_do_kha_thi_top1'] = muc_kt
D['phan_vi_to_hop_de_xuat'] = np.round(pct, 1)
D['phuong_thuc_xet_tuyen_de_xuat'] = pt
D['canh_bao'] = warn
D['du_dinh_nhom_nganh_cua_hoc_sinh'] = np.array([GROUPS[j][1] for j in du_dinh])
D['khop_du_dinh_voi_tu_van'] = (du_dinh == gorder[:, 0]).astype(int)
DF = pd.DataFrame(D)
# nhóm cột: điểm thi là NaN với lớp 10/11 (giữ trống)
import os
os.makedirs(OUT, exist_ok=True)
DF.to_csv(f'{OUT}/dataset_tu_van_nganh_nghe_thpt_2026.csv', index=False, encoding='utf-8-sig')

CAT = pd.DataFrame([{'ma_nhom': n['group'], 'nhom_nganh': GROUPS[n['gi']][1], 'nganh': n['name'],
                     'diem_chuan_nhom_truong_top_thang30': n['dc_mid'],
                     'diem_chuan_trung_binh_he_thong': round(15 + (n['dc_mid'] - 15) * .65, 2),
                     'diem_chuan_nhom_co_ban': round(max(15, 15 + (n['dc_mid'] - 15) * .65 - 3), 2),
                     **{f'holland_{t}': round(n['hol'][t], 2) for t in HT},
                     'mon_then_chot': ', '.join(f"{SN[s]} ({w})" for s, w in n['key'].items()),
                     'to_hop_xet_tuyen': '; '.join(f"{CODE.get(frozenset(c), 'MOI')}:" + '-'.join(SSHORT[x] for x in sorted(c, key=SUBJ.index)) for c in n['combos']),
                     'hoc_phi_toi_thieu_trieu_nam': GROUPS[n['gi']][5], 'can_nang_khieu_hoac_so_tuyen': int(n['nang_khieu'] or n['group'] == 'QPAN')}
                    for n in NG])
CAT.to_csv(f'{OUT}/danh_muc_nganh_2026.csv', index=False, encoding='utf-8-sig')
np.save('/tmp/boost.npy', boost)
print(DF.shape, 'boost', dict(zip(SUBJ, boost.round(2))))
