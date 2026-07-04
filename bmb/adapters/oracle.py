"""天花板标尺(合法作弊):直接拿真相状态当载荷,验证测量正确。绕过 ingest。"""
from __future__ import annotations
from bmb.models import count_tokens


class OracleAdapter:
    def __init__(self, ground_truth_states: dict[str, str] | None = None) -> None:
        self._states = ground_truth_states or {}

    def ingest(self, user_id: str, ts: str, text: str) -> None:
        # 故意忽略:oracle 直接读真相,不经历流
        return None

    def assemble(self, user_id: str, query: str, budget_tokens: int) -> str:
        text = self._states.get(user_id, "")
        # 截到预算:逐字符缩到 token 数达标
        while text and count_tokens(text) > budget_tokens:
            text = text[:-1]
        return text
