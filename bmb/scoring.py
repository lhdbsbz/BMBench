# bmb/scoring.py
"""评分容器:分项对齐度(核心真相)+ 可选等权总分(便利)。
维度异质,分项是核心;overall 仅在显式请求时算,默认 None。"""
from __future__ import annotations
from dataclasses import dataclass, field

from bmb.contract import Dimension


@dataclass
class ScoreReport:
    per_dimension: dict[Dimension, float] = field(default_factory=dict)
    overall: float | None = None   # 仅显式 aggregate 后填入


def aggregate(per_dimension: dict[Dimension, float],
              weights: dict[Dimension, float] | None = None) -> float:
    """等权聚合;weights 给出则按权重加权(归一化)。空集 → 0。"""
    if not per_dimension:
        return 0.0
    if weights is None:
        return sum(per_dimension.values()) / len(per_dimension)
    total_w = sum(weights.get(d, 0.0) for d in per_dimension)
    if total_w <= 0:
        return 0.0
    return sum(per_dimension[d] * weights.get(d, 0.0) for d in per_dimension) / total_w
