# bmb/adapters/oracle.py
"""Oracle adapter:绕过 ingest,recall 直接返回导演注入的真相文本。
仅作参考(标定「给完整答案」的语义),不参与榜单。"""
from __future__ import annotations
from bmb.adapters.base import BaseAdapter
from bmb.contract import StructuredEvent, CapabilityFlag


class OracleAdapter(BaseAdapter):
    def __init__(self, truth_by_user: dict[str, str]):
        super().__init__(structured=True, extra_flags={
            CapabilityFlag.TIME_AWARE, CapabilityFlag.STATEFUL_RECALL,
        })
        self._truth = truth_by_user

    def ingest(self, user_id: str, ts: float, event: StructuredEvent) -> None:
        pass  # 忽略:oracle 已知真相

    def recall(self, user_id: str, cue: str, current_ts: float, session_id: str | None = None) -> str:
        return self._truth.get(user_id, "")
