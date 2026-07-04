"""结构化真相 schema:导演已知的事实图。每个事实带生物权重 + 确定性信号探针用的 key_tokens。"""
from __future__ import annotations
from dataclasses import dataclass, field

# 配对角色常量(lowerCamelCase wire 值),供透镜精确筛选
ROLE_EMOTIONAL        = "emotional"
ROLE_EMOTIONAL_NEUTRAL = "emotionalNeutral"
ROLE_SELF             = "self"
ROLE_SELF_OTHER       = "selfOther"
ROLE_BELIEF_OLD       = "beliefOld"
ROLE_BELIEF_NEW       = "beliefNew"
ROLE_SALIENT          = "salient"
ROLE_DETAIL           = "detail"


@dataclass
class Fact:
    """一条结构化事实。key_tokens 用于确定性信号提取(子串匹配判断是否保留)。
    role: 该 fact 在配对中的角色(如 emotional/emotionalNeutral),用于透镜精确筛选。
    """
    fact_id: str
    ts: float
    text: str
    key_tokens: list[str] = field(default_factory=list)  # 确定性探针锚点
    valence: float = 0.0
    arousal: float = 0.0
    self_relevance: float = 0.0
    supersedes: str | None = None     # 该事实修正了哪条旧事实
    is_salient: bool = False
    role: str = ""                    # 配对角色标签(lowerCamelCase);空=未指定


@dataclass
class FactGraph:
    """一个用户的全部事实,按 ts 升序。"""
    user_id: str
    facts: list[Fact] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.facts.sort(key=lambda f: f.ts)
