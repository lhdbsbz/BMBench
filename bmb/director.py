# bmb/director.py
"""导演:持有真相(经 adapter 视角是不可见的),按逻辑时间在线 ingest,再逐透镜探测。
导演 = 受控实验环境的编排者:它负责「ingest 全部 + 调度透镜」,不碰评分细节(透镜自含)。"""
from __future__ import annotations

from bmb.contract import BMBAdapter, Dimension
from bmb.scoring import ScoreReport
from generator.schemas import FactGraph
from generator.render import fact_to_event
from lenses.base import Lens


class Director:
    def __init__(self, adapter: BMBAdapter, structured: bool = True):
        self._adapter = adapter
        self._structured = structured

    def evaluate(self, graph: FactGraph, lenses: list[Lens]) -> ScoreReport:
        # 1) 在线时序 ingest(按 ts 升序,FactGraph 已排序)
        for fact in graph.facts:
            event = fact_to_event(fact, structured=self._structured)
            self._adapter.ingest(graph.user_id, fact.ts, event)
        # 2) 逐透镜探测
        report = ScoreReport()
        for lens in lenses:
            report.per_dimension[lens.dimension()] = lens.run(self._adapter, graph)
        return report
