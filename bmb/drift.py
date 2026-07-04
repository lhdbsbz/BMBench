"""确定性漂移信号:再构/再巩固维度的信号提取,全程 token 集合运算,无 LLM judge。
core_tokens 应稳定(健康再构保要义),detail_tokens 应中度漂移(健康重组细节)。"""
from __future__ import annotations
from generator.schemas import Fact


def _retained_details(text: str, fact: Fact) -> set[str]:
    """text 中保留了 fact 的哪些 detail_tokens(集合)。"""
    return {t for t in fact.detail_tokens if t in text}


def core_stability(recalls: list[str], fact: Fact) -> float:
    """core_tokens 在多次 recall 中的平均保留率 ∈[0,1]。健康再构应接近 1(要义稳定)。"""
    if not recalls or not fact.core_tokens:
        return 0.0
    total = 0.0
    for text in recalls:
        kept = sum(1.0 for t in fact.core_tokens if t in text)
        total += kept / len(fact.core_tokens)
    return total / len(recalls)


def detail_drift_rate(recalls: list[str], fact: Fact) -> float:
    """相邻 recall 间 detail 保留集合变化的平均比例 ∈[0,1]。
    用对称差 / 并集(Jaccard 距离)度量相邻两次的 detail 集合差异。
    冷库(每次相同)→ 0;健康(中度重组)→ 中值;每次全变 → 趋 1。"""
    if len(recalls) < 2 or not fact.detail_tokens:
        return 0.0
    drifts = []
    prev = _retained_details(recalls[0], fact)
    for text in recalls[1:]:
        cur = _retained_details(text, fact)
        union = prev | cur
        if union:
            drifts.append(len(prev ^ cur) / len(union))  # Jaccard 距离
        else:
            drifts.append(0.0)  # 两次都空 → 无漂移信号
        prev = cur
    return sum(drifts) / len(drifts)


def token_set_divergence(text_a: str, text_b: str, fact: Fact) -> float:
    """两段文本对 fact.detail_tokens 保留集合的 Jaccard 距离 ∈[0,1](再巩固对照用)。"""
    a = _retained_details(text_a, fact)
    b = _retained_details(text_b, fact)
    union = a | b
    if not union:
        return 0.0
    return len(a ^ b) / len(union)
