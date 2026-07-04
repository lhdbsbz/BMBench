# lenses/forgetting.py
"""遗忘曲线透镜(样板)。探测协议:对每条事实,在多个 current_ts recall,
用确定性事实探针测保留率,得保留率曲线;与艾宾浩斯基准算钟形对齐度。"""
from __future__ import annotations

from bmb.contract import Dimension, BMBAdapter
from bmb.signals import fact_retained
from bmb.alignment import curve_alignment
from bmb.bio_baselines import forgetting_baseline_curve
from generator.schemas import FactGraph, Fact


class ForgettingLens:
    def __init__(self, sample_ts: list[float] | None = None, recall_cue: str = "请回忆所有事件"):
        self.sample_ts = sample_ts or [0.0, 1.0, 2.0, 5.0]
        self.recall_cue = recall_cue

    def dimension(self) -> Dimension:
        return Dimension.FORGETTING

    def _fact_retention_curve(self, adapter: BMBAdapter, user_id: str, fact: Fact) -> list[tuple[float, float]]:
        """对单条事实,在各采样时间点测保留率(多条采样取均值由 run 聚合)。"""
        pts: list[tuple[float, float]] = []
        for t in self.sample_ts:
            text = adapter.recall(user_id, self.recall_cue, current_ts=t)
            pts.append((t, 1.0 if fact_retained(text, fact) else 0.0))
        return pts

    def run(self, adapter: BMBAdapter, graph: FactGraph, **kwargs) -> float:
        if not graph.facts:
            return 0.0
        baseline = forgetting_baseline_curve(self.sample_ts)
        # 对每条事实算对齐度,取均值(跨事实聚合)
        per_fact: list[float] = []
        for fact in graph.facts:
            curve = self._fact_retention_curve(adapter, graph.user_id, fact)
            per_fact.append(curve_alignment(curve, baseline))
        return sum(per_fact) / len(per_fact)
