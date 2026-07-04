# tests/test_smoke.py
"""端到端冒烟:冷库 < bio-faithful,且全链路无异常。"""
from generator.generate import generate_world
from bmb.harness import run_benchmark
from bmb.adapters.cold_storage import ColdStorageAdapter
from bmb.adapters.bio_faithful import BioFaithfulAdapter
from lenses.forgetting import ForgettingLens


def test_end_to_end_cold_below_bio():
    world = generate_world(seed=11)
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
