# bmb/alignment.py
"""对齐度:以 baseline 为峰的钟形。distance 越远分越低,冷库/全忘都落尾部。"""
from __future__ import annotations
import math


def curve_alignment(adapter_curve: list[tuple[float, float]],
                    baseline_curve: list[tuple[float, float]],
                    scale: float = 0.3) -> float:
    """Gaussian 钟形:exp(-(mad/scale)²)。mad=0→1;mad 大→趋 0。"""
    if scale <= 0:
        raise ValueError(f"scale 必须为正,收到 {scale}")
    if not baseline_curve:
        return 0.0
    base_by_t = {t: r for t, r in baseline_curve}
    diffs = [abs(r - base_by_t[t]) for t, r in adapter_curve if t in base_by_t]
    if not diffs:
        return 0.0
    mad = sum(diffs) / len(diffs)
    return max(0.0, min(1.0, math.exp(-(mad / scale) ** 2)))


def scalar_alignment(value: float, baseline: float, scale: float = 0.2) -> float:
    """标量钟形:exp(-((value-baseline)/scale)²)。value=baseline→1;偏离→趋 0。"""
    if scale <= 0:
        raise ValueError(f"scale 必须为正,收到 {scale}")
    return max(0.0, min(1.0, math.exp(-((value - baseline) / scale) ** 2)))
