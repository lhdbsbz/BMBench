"""结构化真相 schema:导演已知的事实图。每个事实带生物权重 + 确定性信号探针用的 key_tokens。"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Fact:
    """一条结构化事实。key_tokens 用于确定性信号提取(子串匹配判断是否保留)。"""
    fact_id: str
    ts: float
    text: str
    key_tokens: list[str] = field(default_factory=list)  # 确定性探针锚点
    valence: float = 0.0
    arousal: float = 0.0
    self_relevance: float = 0.0
    supersedes: str | None = None     # 该事实修正了哪条旧事实
    is_salient: bool = False


@dataclass
class FactGraph:
    """一个用户的全部事实,按 ts 升序。"""
    user_id: str
    facts: list[Fact] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.facts.sort(key=lambda f: f.ts)
