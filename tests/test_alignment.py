# tests/test_alignment.py
import pytest
from bmb.alignment import curve_alignment


# 基准:典型的艾宾浩斯衰减
BASELINE = [(0.0, 1.0), (1.0, 0.5), (2.0, 0.35), (5.0, 0.25)]


def test_perfect_match_is_high():
    same = list(BASELINE)
    assert curve_alignment(same, BASELINE) == 1.0  # mad=0 → exp(0)=1


def test_cold_storage_flat_one_is_low():
    cold = [(t, 1.0) for t, _ in BASELINE]
    assert curve_alignment(cold, BASELINE) < 0.2  # 强区分度:冷库落尾部


def test_total_loss_flat_zero_is_low():
    gone = [(t, 0.0) for t, _ in BASELINE]
    assert curve_alignment(gone, BASELINE) < 0.2  # 钟形两端都低


def test_in_unit_interval():
    cold = [(t, 1.0) for t, _ in BASELINE]
    assert 0.0 <= curve_alignment(cold, BASELINE) <= 1.0


from bmb.alignment import scalar_alignment


def test_scalar_perfect_match():
    assert scalar_alignment(0.25, 0.25) == 1.0


def test_scalar_off_baseline_is_low():
    assert scalar_alignment(0.0, 0.25) < 0.25   # 无偏置 vs 基准 0.25; exp(-1.5625)≈0.2096
    assert scalar_alignment(1.0, 0.25) < 0.25   # 过度偏置


def test_scalar_in_unit_interval():
    assert 0.0 <= scalar_alignment(0.5, 0.25) <= 1.0


def test_scalar_alignment_rejects_nonpositive_scale():
    with pytest.raises(ValueError):
        scalar_alignment(0.5, 0.25, scale=0.0)
    with pytest.raises(ValueError):
        scalar_alignment(0.5, 0.25, scale=-1.0)


def test_curve_alignment_rejects_nonpositive_scale():
    with pytest.raises(ValueError):
        curve_alignment([(0.0, 1.0)], [(0.0, 1.0)], scale=0.0)
