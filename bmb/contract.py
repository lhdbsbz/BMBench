"""BMB 数据类型 + 适配器契约。全框架的类型真相源。"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class ProblemFamily(str, Enum):
    """三个压缩难题。注意:值是 A/C/B(对齐设计文档,非字典序)。"""
    SALIENCE = "A"       # 噪音→显著性
    TEMPORAL = "C"       # 历史→当前态
    ABSTRACTION = "B"    # 流水账→隐结构


@dataclass
class ExperienceEvent:
    user_id: str
    timestamp: str       # ISO 8601
    text: str


@dataclass
class AnswerSpec:
    """打分规格。A/C 用 accept/reject 关键词(确定性);B 用 judge_rubric(LLM-judge)。"""
    accept_patterns: list[str] = field(default_factory=list)
    reject_patterns: list[str] = field(default_factory=list)
    judge_rubric: str | None = None


@dataclass
class Probe:
    probe_id: str
    user_id: str
    family: ProblemFamily
    query: str
    answer_spec: AnswerSpec


@dataclass
class GroundTruthState:
    """导演机已知的最小充分统计量(天花板载荷)。对架构保密。"""
    user_id: str
    text: str


class BMBMemoryArchitecture(Protocol):
    """被测记忆架构契约。"""

    def ingest(self, user_id: str, ts: str, text: str) -> None: ...
    def assemble(self, user_id: str, query: str, budget_tokens: int) -> str: ...
