# lenses/emotional.py
"""情绪增强透镜:对称事实对(情绪/中性),同时间 recall,测保留偏置,对齐 EMOTIONAL_ENHANCEMENT。"""
from __future__ import annotations

from bmb.contract import Dimension, BMBAdapter
from bmb.signals import fact_retained
from bmb.alignment import scalar_alignment
from bmb.bio_baselines import EMOTIONAL_ENHANCEMENT
from generator.schemas import FactGraph, Fact


class EmotionalLens:
    def __init__(self, current_ts: float = 2.0, recall_cue: str = "请回忆所有事件"):
        self.current_ts = current_ts
        self.recall_cue = recall_cue

    def dimension(self) -> Dimension:
        return Dimension.EMOTIONAL

    def run(self, adapter: BMBAdapter, graph: FactGraph, **kwargs) -> float:
        emo = [f for f in graph.facts if f.arousal > 0.5 or abs(f.valence) > 0.5]
        neut = [f for f in graph.facts
                if f.arousal == 0 and f.valence == 0 and f.self_relevance == 0]
        if not emo or not neut:
            return 0.0
        text = adapter.recall(graph.user_id, self.recall_cue, current_ts=self.current_ts)
        emo_rate = sum(1.0 if fact_retained(text, f) else 0.0 for f in emo) / len(emo)
        neut_rate = sum(1.0 if fact_retained(text, f) else 0.0 for f in neut) / len(neut)
        bias = emo_rate - neut_rate
        return scalar_alignment(bias, EMOTIONAL_ENHANCEMENT)
