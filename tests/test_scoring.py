# tests/test_scoring.py
from bmb.contract import Dimension as D
from bmb.scoring import ScoreReport, aggregate


def test_report_holds_per_dimension():
    r = ScoreReport(per_dimension={D.FORGETTING: 0.8})
    assert r.per_dimension[D.FORGETTING] == 0.8
    assert r.overall is None  # 默认不聚合


def test_equal_weight_aggregate():
    per = {D.FORGETTING: 0.6, D.EMOTIONAL: 0.8}
    overall = aggregate(per)
    assert abs(overall - 0.7) < 1e-9


def test_custom_weights():
    per = {D.FORGETTING: 0.6, D.EMOTIONAL: 0.8}
    overall = aggregate(per, weights={D.FORGETTING: 3.0, D.EMOTIONAL: 1.0})
    # (0.6*3 + 0.8*1)/(3+1) = 2.6/4 = 0.65
    assert abs(overall - 0.65) < 1e-9


def test_empty_aggregate_is_zero():
    assert aggregate({}) == 0.0
