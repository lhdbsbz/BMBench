# tests/test_drift.py
from generator.schemas import Fact
from bmb.drift import core_stability, detail_drift_rate, token_set_divergence


def _f():
    return Fact(fact_id="f", ts=1.0, text="周会推迟下午三点",
                key_tokens=["周会"], core_tokens=["周会", "推迟"],
                detail_tokens=["下午", "三点", "会议室"])


def test_core_stability_all_present_is_one():
    # 每次 recall 都含全部 core → 稳定率 1.0
    recalls = ["周会推迟了", "周会推迟到明天", "周会推迟"]
    assert core_stability(recalls, _f()) == 1.0


def test_core_stability_missing_lowers():
    recalls = ["周会推迟", "周会取消"]  # 第二次缺"推迟"
    assert core_stability(recalls, _f()) < 1.0


def test_detail_drift_zero_when_identical():
    # 每次 recall 的 detail 保留集合都相同 → 漂移率 0(冷库式逐字不变)
    recalls = ["周会推迟下午三点", "周会推迟下午三点"]
    assert detail_drift_rate(recalls, _f()) == 0.0


def test_detail_drift_positive_when_details_change():
    # detail 集合在变 → 漂移率 > 0
    recalls = ["周会推迟下午三点", "周会推迟会议室", "周会推迟"]
    assert detail_drift_rate(recalls, _f()) > 0.0


def test_detail_drift_in_unit_interval():
    recalls = ["周会推迟下午", "周会推迟三点会议室"]
    assert 0.0 <= detail_drift_rate(recalls, _f()) <= 1.0


def test_token_set_divergence_identical_is_zero():
    assert token_set_divergence("周会推迟下午三点", "周会推迟下午三点", _f()) == 0.0


def test_token_set_divergence_positive_when_differ():
    assert token_set_divergence("周会下午三点", "周会会议室", _f()) > 0.0
