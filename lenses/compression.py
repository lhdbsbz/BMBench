# lenses/compression.py
"""压缩/图式透镜:测要义保留率 + 细节保留率,复合对齐 SCHEMA_SALIENT / SCHEMA_DETAIL。
冷库全保留(要义≈1、细节≈1)→ 细节端偏离基准(0.30)→ 低分;健康系统保要义丢细节。"""
from __future__ import annotations

from bmb.contract import Dimension, BMBAdapter
from bmb.signals import fact_retained
from bmb.alignment import scalar_alignment
from bmb.bio_baselines import SCHEMA_SALIENT, SCHEMA_DETAIL
from generator.schemas import FactGraph, ROLE_SALIENT, ROLE_DETAIL


class CompressionLens:
    def __init__(self, current_ts: float = 2.0, recall_cue: str = "请回忆所有事件"):
        self.current_ts = current_ts
        self.recall_cue = recall_cue

    def dimension(self) -> Dimension:
        return Dimension.COMPRESSION

    def run(self, adapter: BMBAdapter, graph: FactGraph, **kwargs) -> float:
        salient = [f for f in graph.facts if f.role == ROLE_SALIENT]
        detail = [f for f in graph.facts if f.role == ROLE_DETAIL]
        if not salient or not detail:
            return 0.0
        text = adapter.recall(graph.user_id, self.recall_cue, current_ts=self.current_ts)
        sal_rate = sum(1.0 if fact_retained(text, f) else 0.0 for f in salient) / len(salient)
        det_rate = sum(1.0 if fact_retained(text, f) else 0.0 for f in detail) / len(detail)
        # 复合:要义保留对齐 SCHEMA_SALIENT,细节保留对齐 SCHEMA_DETAIL,取均值
        return (scalar_alignment(sal_rate, SCHEMA_SALIENT)
                + scalar_alignment(det_rate, SCHEMA_DETAIL)) / 2.0
