# bmb/adapters/bio_faithful.py
"""Bio-faithful adapter(天花板):按艾宾浩斯保留率 × 角色偏置 概率性保留每条事实。
recall 在 current_ts 下,对每条已 ingest 事实,以 _target_retention(role, dt) 的概率输出。
行为对齐所有五透镜基准 → 真正的自检上界。
注:用确定性 PRNG(按 fact+ts)避免真随机不可复现。

确定性偏差说明:用 hashlib.sha256 派生 8 字节种子,跨进程稳定(Python 内建 hash() 自 3.3
起受 PYTHONHASHSEED 随机盐化)。"""
from __future__ import annotations
import hashlib
import random
from bmb.adapters.base import BaseAdapter
from bmb.contract import StructuredEvent, CapabilityFlag
from bmb.bio_baselines import (
    ebbinghaus_retention,
    EMOTIONAL_ENHANCEMENT,
    SELF_REFERENCE_EFFECT,
    BELIEF_RESIDUAL,
    SCHEMA_SALIENT,
    SCHEMA_DETAIL,
)

# 角色标签常量(与 generator.schemas 保持一致,避免 adapter → generator 的反向依赖)
_ROLE_SALIENT           = "salient"
_ROLE_DETAIL            = "detail"
_ROLE_BELIEF_OLD        = "beliefOld"
_ROLE_EMOTIONAL         = "emotional"
_ROLE_EMOTIONAL_NEUTRAL = "emotionalNeutral"
_ROLE_SELF              = "self"
_ROLE_SELF_OTHER        = "selfOther"


def _det_seed(text: str, current_ts: float) -> int:
    """按 (text, current_ts) 派生确定性 PRNG 种子(跨进程、跨机器稳定)。"""
    h = hashlib.sha256(f"{text}|{current_ts}".encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big")


def _target_retention(role: str, dt: float, S: float, c: float) -> float:
    """按角色返回目标保留概率。
    - 压缩/图式角色:固定在 SCHEMA_SALIENT / SCHEMA_DETAIL(与时间无关,模拟 schema 机制)。
    - 旧信念:固定在 BELIEF_RESIDUAL(大部分已被新信念覆盖)。
    - 情绪/自我角色:在艾宾浩斯 base 上加 BOOST(对齐健康情绪增强 / 自我参照效应)。
    - 其余(中性配对或无角色):纯艾宾浩斯 base。
    """
    base = ebbinghaus_retention(dt, S, c)
    if role == _ROLE_SALIENT:
        return SCHEMA_SALIENT
    if role == _ROLE_DETAIL:
        return SCHEMA_DETAIL
    if role == _ROLE_BELIEF_OLD:
        return BELIEF_RESIDUAL
    if role == _ROLE_EMOTIONAL:
        return min(1.0, base + EMOTIONAL_ENHANCEMENT)
    if role == _ROLE_EMOTIONAL_NEUTRAL:
        return base
    if role == _ROLE_SELF:
        return min(1.0, base + SELF_REFERENCE_EFFECT)
    if role == _ROLE_SELF_OTHER:
        return base
    return base   # 无角色 → 纯时间衰减(遗忘透镜)


class BioFaithfulAdapter(BaseAdapter):
    def __init__(self, S: float = 1.0, c: float = 0.2):
        super().__init__(structured=True, extra_flags={CapabilityFlag.TIME_AWARE})
        self._store: dict[str, list[tuple[float, str, str]]] = {}  # user -> [(ts, text, role)]
        self._S = S
        self._c = c

    def ingest(self, user_id: str, ts: float, event: StructuredEvent) -> None:
        self._store.setdefault(user_id, []).append((ts, event.text, event.role))

    def recall(self, user_id: str, cue: str, current_ts: float, session_id: str | None = None) -> str:
        out: list[str] = []
        for ts, text, role in self._store.get(user_id, []):
            dt = max(0.0, current_ts - ts)
            p = _target_retention(role, dt, self._S, self._c)
            rng = random.Random(_det_seed(text, current_ts))  # 确定性:同输入同输出
            if rng.random() < p:
                out.append(text)
        return "".join(out)
