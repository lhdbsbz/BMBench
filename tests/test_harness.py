# tests/test_harness.py
import pytest
from generator.generate import generate_world
from bmb.harness import run_benchmark, SelfCheckError
from bmb.adapters.cold_storage import ColdStorageAdapter
from bmb.adapters.bio_faithful import BioFaithfulAdapter
from lenses.forgetting import ForgettingLens
from lenses.emotional import EmotionalLens
from lenses.self_reference import SelfReferenceLens
from lenses.compression import CompressionLens
from lenses.belief_update import BeliefUpdateLens
from bmb.contract import Dimension


def _world():
    # generate_world 每角色 N_PAIR 条事实,forgetting diff 远大于 margin=0.05
    return generate_world(seed=1)


def _lenses():
    return [ForgettingLens(sample_ts=[0.0, 1.0, 2.0, 5.0])]


def _five_lenses():
    return [
        ForgettingLens(sample_ts=[0.0, 1.0, 2.0, 5.0]),
        EmotionalLens(current_ts=3.0),
        SelfReferenceLens(current_ts=3.0),
        CompressionLens(current_ts=3.0),
        BeliefUpdateLens(current_ts=3.0),
    ]


def test_self_check_passes_and_scores_adapter():
    report = run_benchmark(ColdStorageAdapter(structured=True), _world(), _lenses())
    assert Dimension.FORGETTING in report.per_dimension


def test_cold_scores_lower_than_bio_faithful():
    cold = run_benchmark(ColdStorageAdapter(structured=True), _world(), _lenses())
    bio = run_benchmark(BioFaithfulAdapter(), _world(), _lenses())
    # 冷库(永不衰减)在遗忘维度应低于 bio-faithful(对齐艾宾浩斯)
    assert cold.per_dimension[Dimension.FORGETTING] < bio.per_dimension[Dimension.FORGETTING]


# ── 多 seed 自检稳健性验证(RW8) ──────────────────────────────────────────────
# run_benchmark 内部执行冷库地板 vs bio-faithful 天花板自检;
# 若任意 seed 的 gap <= margin(0.05),则抛 SelfCheckError → 测试失败。
# 全部 pass 即证明 bioFaithful 在 6 个独立 seed 上均是可信天花板。

@pytest.mark.parametrize("seed", [1, 2, 3, 7, 11, 42])
def test_self_check_robust_across_seeds(seed):
    """多 seed 稳健自检:run_benchmark 不抛 SelfCheckError,天花板始终有效。"""
    world = generate_world(seed=seed)
    # run_benchmark 内含自检门;若 gap <= margin 则抛异常,此测试失败
    report = run_benchmark(ColdStorageAdapter(), world, _five_lenses())
    assert report.overall is not None


@pytest.mark.parametrize("seed", [1, 2, 3, 7, 11, 42])
def test_cold_below_bio_faithful_across_seeds(seed):
    """多 seed 地板/天花板间距验证:cold.overall < bioFaithful.overall,且差距 > 0.05。"""
    world = generate_world(seed=seed)
    cold = run_benchmark(ColdStorageAdapter(), world, _five_lenses())
    bio  = run_benchmark(BioFaithfulAdapter(), world, _five_lenses())
    assert cold.overall < bio.overall, (
        f"seed={seed}: cold={cold.overall:.4f} 应 < bio={bio.overall:.4f}"
    )
    assert bio.overall - cold.overall > 0.05, (
        f"seed={seed}: gap={bio.overall - cold.overall:.4f} 未超过 margin=0.05"
    )


@pytest.mark.parametrize("seed", [1, 2, 3, 7, 11, 42])
def test_bio_faithful_beats_cold_per_dimension(seed):
    """逐维天花板验证:bioFaithful 在全部 5 透镜各维度上均高于冷库,N_PAIR=50 确保统计稳定。"""
    world = generate_world(seed=seed)
    lenses = _five_lenses()
    cold = run_benchmark(ColdStorageAdapter(), world, lenses)
    bio  = run_benchmark(BioFaithfulAdapter(), world, lenses)
    for dim in cold.per_dimension:
        assert bio.per_dimension[dim] > cold.per_dimension[dim], (
            f"seed={seed} dim={dim}: bio={bio.per_dimension[dim]:.4f} "
            f"!> cold={cold.per_dimension[dim]:.4f}"
        )
