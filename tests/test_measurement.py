from bmb.measurement import (
    has_signal, recovery_ratio, aggregate_family, area_under_frontier,
)

def test_has_signal():
    assert has_signal(1.0, 0.2) is True
    assert has_signal(0.21, 0.2) is False

def test_recovery_ratio_basic():
    # 地板 0.2、架构 0.6 → (0.6-0.2)/(1-0.2)=0.5
    assert abs(recovery_ratio(0.6, 0.2) - 0.5) < 1e-9

def test_recovery_ratio_clamps_and_guards():
    assert recovery_ratio(1.5, 0.2) == 1.0      # 超 1 截断
    assert recovery_ratio(0.1, 0.2) == 0.0      # 负截断
    assert recovery_ratio(0.9, 0.9999) == 0.0   # 分母≈0 守护

def test_aggregate_mean():
    assert abs(aggregate_family([0.0, 0.5, 1.0]) - 0.5) < 1e-9
    assert aggregate_family([]) == 0.0

def test_auf_monotone_in_unit_square():
    # 预算 8k→r0.2、32k→0.5、64k→0.8、128k→1.0;AUF 应在 (0,1)
    pts = [(8192, 0.2), (32768, 0.5), (65536, 0.8), (131072, 1.0)]
    auf = area_under_frontier(pts)
    assert 0.0 < auf < 1.0
    # 全 0 → 0;全 1 → 1
    assert area_under_frontier([(8192, 0.0), (131072, 0.0)]) == 0.0
    assert area_under_frontier([(8192, 1.0), (131072, 1.0)]) == 1.0
