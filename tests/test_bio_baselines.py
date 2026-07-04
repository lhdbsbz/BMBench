# tests/test_bio_baselines.py
import math
import pytest
from bmb.bio_baselines import (
    ebbinghaus_retention, forgetting_baseline_curve,
    EMOTIONAL_ENHANCEMENT, SELF_REFERENCE_EFFECT,
    BELIEF_RESIDUAL, SCHEMA_SALIENT, SCHEMA_DETAIL,
)


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


def test_ebbinghaus_rejects_nonpositive_S():
    with pytest.raises(ValueError):
        ebbinghaus_retention(1.0, S=0.0)
    with pytest.raises(ValueError):
        ebbinghaus_retention(1.0, S=-1.0)


def test_constants_in_unit_interval():
    for v in (EMOTIONAL_ENHANCEMENT, SELF_REFERENCE_EFFECT,
              BELIEF_RESIDUAL, SCHEMA_SALIENT, SCHEMA_DETAIL):
        assert 0.0 <= v <= 1.0


def test_schema_salient_above_detail():
    assert SCHEMA_SALIENT > SCHEMA_DETAIL  # 要义保留 > 细节保留


def test_reconstruction_baselines_in_unit_interval():
    from bmb.bio_baselines import RECONSTRUCTION_DRIFT, RECONSOLIDATION_EFFECT
    assert 0.0 <= RECONSTRUCTION_DRIFT <= 1.0
    assert 0.0 <= RECONSOLIDATION_EFFECT <= 1.0


def test_reconstruction_drift_is_moderate():
    from bmb.bio_baselines import RECONSTRUCTION_DRIFT
    # 健康漂移是中度:既非 0(冷库)也非 1(幻觉)
    assert 0.1 < RECONSTRUCTION_DRIFT < 0.6
