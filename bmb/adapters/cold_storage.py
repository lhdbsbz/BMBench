# bmb/adapters/cold_storage.py
"""冷库 adapter:全保真、不衰减、不漂移。是地板(最不仿生参照)与自检下界。"""
from __future__ import annotations
from bmb.adapters.base import BaseAdapter
from bmb.contract import StructuredEvent


class ColdStorageAdapter(BaseAdapter):
    def __init__(self, structured: bool = True):
        super().__init__(structured=structured)  # 冷库:不时间感知、无副作用召回
        self._store: dict[str, list[str]] = {}

    def ingest(self, user_id: str, ts: float, event: StructuredEvent) -> None:
        self._store.setdefault(user_id, []).append(event.text)

    def recall(self, user_id: str, cue: str, current_ts: float, session_id: str | None = None) -> str:
        return "".join(self._store.get(user_id, []))
