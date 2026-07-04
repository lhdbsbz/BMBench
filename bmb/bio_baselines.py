# bmb/bio_baselines.py
"""生物基准:健康成人记忆的实证保留率曲线。
来源:艾宾浩斯(1885);power-law / 指数拟合见 Wixted & Ebbesen(1991)、Rubin & Wenzel(1996)。
此处用带渐近项的指数形式 R(t)=(1-c)·e^(-t/S)+c 作为可参数化的工程近似,默认值取文献典型量级。"""
from __future__ import annotations
import math


def ebbinghaus_retention(t: float, S: float = 1.0, c: float = 0.2) -> float:
    """t=逻辑时间单位,S=相对记忆强度,c=渐近保留率(长期记忆残余)。"""
    return (1.0 - c) * math.exp(-t / S) + c


def forgetting_baseline_curve(ts: list[float], S: float = 1.0, c: float = 0.2) -> list[tuple[float, float]]:
    """在给定时间点采样艾宾浩斯曲线,返回 [(t, retention)]。"""
    return [(t, ebbinghaus_retention(t, S, c)) for t in ts]
