# bmb/adapters/bio_faithful.py
"""Bio-faithful adapter(天花板):按艾宾浩斯保留率概率性保留每条事实。
recall 在 current_ts 下,对每条已 ingest 事实,以 R=ebbinghaus(t_now - t_fact) 的概率输出。
行为天然对齐遗忘基准 → 自检上界。注:用确定性 PRNG(按 fact+ts)避免真随机不可复现。

确定性偏差说明:brief 原用 `hash((text, current_ts))` 作种子,但 Python 内建 `hash()` 自 3.3 起
被 PYTHONHASHSEED 按进程随机化盐化 —— 跨进程跑会得到不同的衰减结果,违反框架的确定性命门、
使自检不可复现。改用 hashlib.sha256 派生 8 字节种子,跨进程稳定。"""
from __future__ import annotations
import hashlib
import random
from bmb.adapters.base import BaseAdapter
from bmb.contract import StructuredEvent, CapabilityFlag
from bmb.bio_baselines import ebbinghaus_retention


def _det_seed(text: str, current_ts: float) -> int:
    """按 (text, current_ts) 派生确定性 PRNG 种子(跨进程、跨机器稳定)。"""
    h = hashlib.sha256(f"{text}|{current_ts}".encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big")


class BioFaithfulAdapter(BaseAdapter):
    def __init__(self, S: float = 1.0, c: float = 0.2):
        super().__init__(structured=True, extra_flags={CapabilityFlag.TIME_AWARE})
        self._store: dict[str, list[tuple[float, str]]] = {}  # user -> [(ts, text)]
        self._S = S
        self._c = c

    def ingest(self, user_id: str, ts: float, event: StructuredEvent) -> None:
        self._store.setdefault(user_id, []).append((ts, event.text))

    def recall(self, user_id: str, cue: str, current_ts: float, session_id: str | None = None) -> str:
        out: list[str] = []
        for ts, text in self._store.get(user_id, []):
            dt = max(0.0, current_ts - ts)
            p = ebbinghaus_retention(dt, self._S, self._c)
            rng = random.Random(_det_seed(text, current_ts))  # 确定性:同输入同输出
            if rng.random() < p:
                out.append(text)
        return "".join(out)
