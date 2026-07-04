# tests/test_bio_baselines.py
import math
from bmb.bio_baselines import ebbinghaus_retention, forgetting_baseline_curve


def test_retention_decreases_with_time():
    assert ebbinghaus_retention(0.0) > ebbinghaus_retention(1.0) > ebbinghaus_retention(5.0)


def test_retention_at_zero_near_one():
    assert abs(ebbinghaus_retention(0.0) - 1.0) < 1e-9


def test_retention_asymptote_above_zero():
    # 渐近保留率 c=0.2 → 很长时间后趋于 0.2
    assert abs(ebbinghaus_retention(1000.0) - 0.2) < 1e-3


def test_baseline_curve_monotone_decreasing_sampled():
    pts = forgetting_baseline_curve([0.0, 1.0, 2.0, 5.0])
    vals = [r for _, r in pts]
    assert all(vals[i] >= vals[i + 1] for i in range(len(vals) - 1))
