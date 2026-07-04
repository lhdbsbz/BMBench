"""把 Fact 渲染成 StructuredEvent。按 adapter 能力决定标注作为字段还是渲染进文本。"""
from __future__ import annotations
from generator.schemas import Fact
from bmb.contract import StructuredEvent


def fact_to_event(fact: Fact, structured: bool) -> StructuredEvent:
    """structured=True:标注作为结构化字段传入。
    structured=False:标注渲染进 text,字段清零(测系统能否从文本隐式识别)。"""
    if structured:
        return StructuredEvent(
            fact_id=fact.fact_id, ts=fact.ts, text=fact.text,
            valence=fact.valence, arousal=fact.arousal,
            self_relevance=fact.self_relevance,
            supersedes=fact.supersedes, is_salient=fact.is_salient,
        )
    # 纯文本:把情绪/自我标注烘进文本
    text = fact.text
    if abs(fact.valence) > 0.5 or fact.arousal > 0.5:
        tag = "令人激动" if fact.arousal > 0.5 else ("令人愉悦" if fact.valence > 0 else "令人不快")
        text = f"{text}(这件事{tag})"
    if fact.self_relevance > 0.5:
        text = f"{text}(和我本人相关)"
    return StructuredEvent(fact_id=fact.fact_id, ts=fact.ts, text=text)
