# lenses/self_reference.py
"""自我关联透镜:对称事实对(自我相关/无关),同时间 recall,测保留偏置,对齐 SELF_REFERENCE_EFFECT。"""
from __future__ import annotations

from bmb.contract import Dimension, BMBAdapter
from bmb.signals import fact_retained
from bmb.alignment import scalar_alignment
from bmb.bio_baselines import SELF_REFERENCE_EFFECT
from generator.schemas import FactGraph


class SelfReferenceLens:
    def __init__(self, current_ts: float = 2.0, recall_cue: str = "请回忆所有事件"):
        self.current_ts = current_ts
        self.recall_cue = recall_cue

    def dimension(self) -> Dimension:
        return Dimension.SELF_REFERENCE

    def run(self, adapter: BMBAdapter, graph: FactGraph, **kwargs) -> float:
        self_f = [f for f in graph.facts if f.self_relevance > 0.5]
        other = [f for f in graph.facts
                 if f.self_relevance == 0 and f.arousal == 0 and f.valence == 0]
        if not self_f or not other:
            return 0.0
        text = adapter.recall(graph.user_id, self.recall_cue, current_ts=self.current_ts)
        self_rate = sum(1.0 if fact_retained(text, f) else 0.0 for f in self_f) / len(self_f)
        other_rate = sum(1.0 if fact_retained(text, f) else 0.0 for f in other) / len(other)
        bias = self_rate - other_rate
        return scalar_alignment(bias, SELF_REFERENCE_EFFECT, scale=0.12)
