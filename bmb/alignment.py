# bmb/alignment.py
"""钟形对齐度:adapter 行为曲线与健康基准曲线的距离 → [0,1]。
距离越小对齐越高。冷库(恒 1)与全忘(恒 0)都远离衰减型基准 → 都低分,
贴近基准 → 高分。天然钟形(以基准为峰),无需显式构造钟形函数。"""
from __future__ import annotations


def curve_alignment(adapter_curve: list[tuple[float, float]],
                    baseline_curve: list[tuple[float, float]]) -> float:
    """两条曲线须在同一组 t 上采样。返回 1 - 归一化平均绝对差。"""
    if not baseline_curve:
        return 0.0
    # 用基准的 t 对齐(假设 adapter 在同 t 采样;透镜负责保证)
    base_by_t = {t: r for t, r in baseline_curve}
    diffs = []
    for t, r in adapter_curve:
        if t in base_by_t:
            diffs.append(abs(r - base_by_t[t]))
    if not diffs:
        return 0.0
    mad = sum(diffs) / len(diffs)           # 平均绝对差 ∈ [0,1]
    return max(0.0, min(1.0, 1.0 - mad))
