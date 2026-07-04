# tests/test_smoke.py
"""端到端冒烟:冷库 < bio-faithful,且全链路无异常。"""
from generator.generate import generate_world
from bmb.harness import run_benchmark
from bmb.adapters.cold_storage import ColdStorageAdapter
from bmb.adapters.bio_faithful import BioFaithfulAdapter
from lenses.forgetting import ForgettingLens


def test_end_to_end_cold_below_bio():
    # generate_world 现在每角色 N_PAIR 条事实,forgetting 维度稳健拉开差距
    world = generate_world(seed=3)
    lenses = [ForgettingLens(sample_ts=[0.0, 1.0, 2.0, 5.0])]
    cold = run_benchmark(ColdStorageAdapter(), world, lenses)
    bio = run_benchmark(BioFaithfulAdapter(), world, lenses)
    from bmb.contract import Dimension
    assert cold.per_dimension[Dimension.FORGETTING] < bio.per_dimension[Dimension.FORGETTING]


def test_self_check_guarded():
    """自检硬门存在:正常路径不抛(已由上覆盖)。这里断言 run_benchmark 返回类型正确。"""
    world = generate_world(seed=1)
    r = run_benchmark(ColdStorageAdapter(), world, [ForgettingLens(sample_ts=[0.0, 5.0])])
    assert r.overall is not None and 0.0 <= r.overall <= 1.0


def test_end_to_end_cold_below_bio_overall():
    """5 维聚合后冷库地板 < bio-faithful 天花板。seed=11 经 RW8 验证稳定。"""
    from lenses.emotional import EmotionalLens
    from lenses.self_reference import SelfReferenceLens
    from lenses.compression import CompressionLens
    from lenses.belief_update import BeliefUpdateLens

    lenses = [
        ForgettingLens(sample_ts=[0.0, 1.0, 2.0, 5.0]),
        EmotionalLens(current_ts=3.0),
        SelfReferenceLens(current_ts=3.0),
        CompressionLens(current_ts=3.0),
        BeliefUpdateLens(current_ts=3.0),
    ]
    world = generate_world(seed=11)
    cold = run_benchmark(ColdStorageAdapter(), world, lenses)
    bio = run_benchmark(BioFaithfulAdapter(), world, lenses)
    assert cold.overall < bio.overall  # 5 维聚合后冷库仍低于天花板
