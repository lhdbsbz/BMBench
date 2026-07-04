# tests/test_harness.py
from generator.generate import generate_world
from bmb.harness import run_benchmark, SelfCheckError
from bmb.adapters.cold_storage import ColdStorageAdapter
from bmb.adapters.bio_faithful import BioFaithfulAdapter
from lenses.forgetting import ForgettingLens
from bmb.contract import Dimension


def _world():
    # generate_world 每角色 N_PAIR 条事实,forgetting diff 远大于 margin=0.05
    return generate_world(seed=1)


def _lenses():
    return [ForgettingLens(sample_ts=[0.0, 1.0, 2.0, 5.0])]


def test_self_check_passes_and_scores_adapter():
    report = run_benchmark(ColdStorageAdapter(structured=True), _world(), _lenses())
    assert Dimension.FORGETTING in report.per_dimension


def test_cold_scores_lower_than_bio_faithful():
    cold = run_benchmark(ColdStorageAdapter(structured=True), _world(), _lenses())
    bio = run_benchmark(BioFaithfulAdapter(), _world(), _lenses())
    # 冷库(永不衰减)在遗忘维度应低于 bio-faithful(对齐艾宾浩斯)
    assert cold.per_dimension[Dimension.FORGETTING] < bio.per_dimension[Dimension.FORGETTING]
