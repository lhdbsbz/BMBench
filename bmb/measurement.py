"""恢复率 / 零信号过滤 / 聚合 / 前沿 / AUF。"""
from __future__ import annotations
import math
from dataclasses import dataclass, field

from bmb.contract import ProblemFamily

EPSILON = 0.05  # 天花板−地板 低于此 = 零信号探针


def has_signal(s_ceiling: float, s_floor: float, epsilon: float = EPSILON) -> bool:
    return (s_ceiling - s_floor) >= epsilon


def recovery_ratio(s_arch: float, s_floor: float) -> float:
    denom = 1.0 - s_floor
    if denom < EPSILON:
        return 0.0  # 零信号探针应由 has_signal 提前滤掉;此为守护
    r = (s_arch - s_floor) / denom
    return max(0.0, min(1.0, r))


def aggregate_family(recoveries: list[float]) -> float:
    if not recoveries:
        return 0.0
    return sum(recoveries) / len(recoveries)


@dataclass
class Frontier:
    family: ProblemFamily
    points: list[tuple[int, float]] = field(default_factory=list)  # [(budget, recovery)]


def area_under_frontier(points: list[tuple[int, float]]) -> float:
    """对 log(预算) 归一化梯形积分,返回 ∈[0,1]。"""
    pts = sorted(points)
    if len(pts) < 2:
        return float(pts[0][1]) if pts else 0.0
    xs = [math.log(b) for b, _ in pts]
    ys = [r for _, r in pts]
    x0, x1 = xs[0], xs[-1]
    span = (x1 - x0) or 1.0
    area = 0.0
    for i in range(len(xs) - 1):
        area += (ys[i] + ys[i + 1]) / 2.0 * (xs[i + 1] - xs[i])
    return max(0.0, min(1.0, area / span))
