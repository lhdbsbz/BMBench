"""地板标尺:append 全部,assemble 返回最近事件拼接到 ≤budget。零记忆智能。"""
from __future__ import annotations
from collections import defaultdict
from bmb.models import count_tokens


class NaiveDumpAdapter:
    def __init__(self, config: dict | None = None) -> None:
        self._store: dict[str, list[str]] = defaultdict(list)

    def ingest(self, user_id: str, ts: str, text: str) -> None:
        self._store[user_id].append(text)

    def assemble(self, user_id: str, query: str, budget_tokens: int) -> str:
        events = self._store.get(user_id, [])
        picked: list[str] = []
        used = 0
        # 从最近向最旧取,直到装满预算
        for text in reversed(events):
            t = count_tokens(text)
            if used + t > budget_tokens:
                break
            picked.append(text)
            used += t
        return "\n".join(reversed(picked))
