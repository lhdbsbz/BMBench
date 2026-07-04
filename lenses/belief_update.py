# lenses/belief_update.py
"""信念更新透镜:被矛盾新信息修正的旧 fact,测其残留度,对齐 BELIEF_RESIDUAL。
冷库全保留旧 fact(残留 1.0,不更新)→ 低分;全忘(残留 0)→ 也低;健康残留≈0.30。"""
from __future__ import annotations

from bmb.contract import Dimension, BMBAdapter
from bmb.signals import fact_retained
from bmb.alignment import scalar_alignment
from bmb.bio_baselines import BELIEF_RESIDUAL
from generator.schemas import FactGraph, Fact


class BeliefUpdateLens:
    def __init__(self, current_ts: float = 3.0, recall_cue: str = "请回忆所有事件"):
        self.current_ts = current_ts
        self.recall_cue = recall_cue

    def dimension(self) -> Dimension:
        return Dimension.BELIEF_UPDATE

    def run(self, adapter: BMBAdapter, graph: FactGraph, **kwargs) -> float:
        # 找被修正的旧 fact(superseded):有新 fact 的 supersedes 指向它
        superseded_ids = {f.supersedes for f in graph.facts if f.supersedes}
        old_facts: list[Fact] = [f for f in graph.facts if f.fact_id in superseded_ids]
        if not old_facts:
            return 0.0
        text = adapter.recall(graph.user_id, self.recall_cue, current_ts=self.current_ts)
        residual = sum(1.0 if fact_retained(text, f) else 0.0 for f in old_facts) / len(old_facts)
        return scalar_alignment(residual, BELIEF_RESIDUAL)
