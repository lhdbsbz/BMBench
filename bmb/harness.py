# bmb/harness.py
"""评测单元编排 + 自检硬门:冷库(地板)必须显著低于 bio-faithful(天花板),否则测量不可信、结果作废。
继承 v1 的自检精神(地板/天花板硬门),但两端按 v2 对齐度重定义。"""
from __future__ import annotations

from bmb.contract import BMBAdapter, Dimension
from bmb.director import Director
from bmb.scoring import ScoreReport, aggregate
from bmb.adapters.cold_storage import ColdStorageAdapter
from bmb.adapters.bio_faithful import BioFaithfulAdapter
from generator.schemas import FactGraph
from lenses.base import Lens


class SelfCheckError(RuntimeError):
    """冷库未在地板 / bio-faithful 未在天花板,测量不可信。"""


def _evaluate(adapter: BMBAdapter, world: dict[str, FactGraph], lenses: list[Lens],
              structured: bool) -> ScoreReport:
    merged = ScoreReport()
    per_dim_acc: dict[Dimension, list[float]] = {}
    for graph in world.values():
        report = Director(adapter=adapter, structured=structured).evaluate(graph, lenses)
        for dim, score in report.per_dimension.items():
            per_dim_acc.setdefault(dim, []).append(score)
    for dim, scores in per_dim_acc.items():
        merged.per_dimension[dim] = sum(scores) / len(scores)
    merged.overall = aggregate(merged.per_dimension)
    return merged


def run_benchmark(adapter: BMBAdapter, world: dict[str, FactGraph], lenses: list[Lens],
                  structured: bool = True, margin: float = 0.05) -> ScoreReport:
    """自检硬门:冷库地板必须比 bio-faithful 天花板低至少 margin,否则抛 SelfCheckError。"""
    floor = _evaluate(ColdStorageAdapter(structured=structured), world, lenses, structured)
    ceil = _evaluate(BioFaithfulAdapter(), world, lenses, structured)
    if not (ceil.overall - floor.overall > margin):
        raise SelfCheckError(
            f"自检失败:bio-faithful AUF={ceil.overall:.3f} 未显著高于冷库 AUF={floor.overall:.3f}"
            f"(margin={margin});测量不可信,结果作废。"
        )
    return _evaluate(adapter, world, lenses, structured)
