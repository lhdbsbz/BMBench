import pytest
from bmb.harness import measure_adapter, self_check, run_benchmark, SelfCheckError
from bmb.dataset import load_dataset
from bmb.models import FakeModel
from bmb.adapters.naive_dump import NaiveDumpAdapter
from bmb.adapters.oracle import OracleAdapter

def _ds():
    return load_dataset("datasets/smoke")

def _kw_responder(prompt):
    # 载荷/真相里含关键词就返回该关键词,使确定性判分命中;否则"不知道"
    for kw in ("青霉素", "重新素食", "素食", "数码"):
        if kw in prompt:
            return kw
    return "不知道"

def test_measure_adapter_returns_frontiers_per_family():
    ds = _ds()
    oracle = OracleAdapter({uid: s.text for uid, s in ds.states_by_user.items()})
    frontiers = measure_adapter(oracle, ds, FakeModel(_kw_responder), budgets=[1024, 4096])
    assert len(frontiers) >= 1  # A 难题有信号(C/B 在 FakeModel 下被零信号过滤)
    for f in frontiers.values():
        assert len(f.points) == 2  # 两个预算档各一个点

def test_oracle_beats_naive_in_self_check():
    # kw 响应:oracle 载荷(真相态)含关键词→命中;naive 载荷(渲染废话)不含→不命中 → oracle AUF > naive
    self_check(_ds(), FakeModel(_kw_responder), budgets=[4096])  # 不抛即通过

def test_self_check_fails_when_naive_equals_oracle():
    # 恒答"命中":确定性判分匹配不到关键词→全零信号→两端 AUF 相等→抛 SelfCheckError
    with pytest.raises(SelfCheckError):
        self_check(_ds(), FakeModel(lambda p: "命中"), budgets=[4096])
