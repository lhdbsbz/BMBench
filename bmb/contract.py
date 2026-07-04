# bmb/contract.py
"""BMB v2 数据类型 + adapter 契约。全框架的类型真相源。"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class Dimension(str, Enum):
    """六个仿生维度(框架身份边界)。值 = lowerCamelCase(wire 字段)。"""
    FORGETTING = "forgetting"            # 遗忘曲线
    EMOTIONAL = "emotional"              # 情绪增强
    RECONSTRUCTION = "reconstruction"    # 再构 / 再巩固
    COMPRESSION = "compression"          # 压缩 / 图式
    BELIEF_UPDATE = "beliefUpdate"      # 信念更新
    SELF_REFERENCE = "selfReference"    # 自我关联


class CapabilityFlag(str, Enum):
    """adapter 能力声明。框架据此标注每个维度是「真测」还是「因不支持而冷库化」。"""
    STRUCTURED_EVENT = "structuredEvent"  # 吃结构化 event(否则只收纯文本)
    TIME_AWARE = "timeAware"              # 用 current_ts 做衰减(否则永不衰减=冷库)
    STATEFUL_RECALL = "statefulRecall"    # recall 有副作用(再巩固);否则无状态


@dataclass
class Capabilities:
    flags: set[CapabilityFlag] = field(default_factory=set)


@dataclass
class StructuredEvent:
    """导演喂给 adapter 的结构化事件。携带生物权重(对 adapter 可见或渲染进文本)。"""
    fact_id: str
    ts: float                            # 逻辑时间戳(导演注入)
    text: str
    valence: float = 0.0                 # 情绪效价 [-1, 1]
    arousal: float = 0.0                 # 情绪唤醒 [0, 1]
    self_relevance: float = 0.0          # 自我关联度 [0, 1]
    supersedes: str | None = None        # 被哪条后续事实修正(该事实的 fact_id)
    is_salient: bool = False             # 是否要义(压缩维度用)
    role: str = ""                       # 配对角色标签(lowerCamelCase);空=未指定


class BMBAdapter(Protocol):
    """被测记忆架构契约。adapter 是被试,框架是导演。"""
    capabilities: Capabilities

    def ingest(self, user_id: str, ts: float, event: StructuredEvent) -> None: ...
    def recall(self, user_id: str, cue: str, current_ts: float,
               session_id: str | None = None) -> str: ...
