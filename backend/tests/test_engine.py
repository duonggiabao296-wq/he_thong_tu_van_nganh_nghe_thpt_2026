# -*- coding: utf-8 -*-
"""Chạy:  python -m pytest tests -q   hoặc   python tests/test_engine.py   (từ thư mục backend/)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.engine import CareerExpertSystem2026  # noqa: E402

SAMPLE = {
    'lop': 12, 'diem_uu_tien_khu_vuc': 0.25, 'ngan_sach_hoc_phi_trieu_nam': 35,
    'uu_tien_dinh_huong': 'Thu nhập cao', 'gia_dinh_goi_y_nhom_nganh': 'CNTT',
    'du_dinh_nhom_nganh_cua_hoc_sinh': 'Công nghệ thông tin, AI & Dữ liệu',
    'the_luc': 4, 'ielts': 6.5, 'dgnl_hsa_150': 98, 'giai_hsg': 'Không',
    'holland': {'R': 3.5, 'I': 4.8, 'A': 2.4, 'S': 2.6, 'E': 3.2, 'C': 3.9},
    'quan_tam': {'CNTT': 5, 'KTCN': 4, 'KHTN': 4, 'KTTCNH': 3},
    'hb': {'T': 9.0, 'V': 7.5, 'A': 8.4, 'L': 8.6, 'H': 8.1, 'I': 9.2, 'C': 8.5},
    'thi': {'T': 8.75, 'V': 7.25, 'L': 8.5, 'I': 9.0},
}


def test_advise_structure():
    res = CareerExpertSystem2026().advise(SAMPLE)
    assert len(res['top_majors']) == 5
    assert len(res['top_groups']) == 3
    assert res['top_majors'][0]['group_code'] == 'CNTT'


def test_grade10_has_no_exam_scores():
    p = dict(SAMPLE, lop=10, thi={})
    res = CareerExpertSystem2026().advise(p)
    assert res['student_grade'] == 10 and res['top_majors']


if __name__ == '__main__':
    test_advise_structure(); test_grade10_has_no_exam_scores(); print('OK')
