"""state-first 的结构化真相 schema + 探针/真相态派生(全确定性,不经 LLM)。"""
from __future__ import annotations
from dataclasses import dataclass, field

from bmb.contract import AnswerSpec, GroundTruthState, ProblemFamily, Probe


@dataclass
class SalientFact:
    fact_id: str
    text: str
    keywords: list[str]            # accept 关键词
    probe_query: str


@dataclass
class StateVariable:
    name: str
    timeline: list[tuple[int, str]]   # [(day, value)] 升序
    probe_query: str

    @property
    def current_value(self) -> str:
        return self.timeline[-1][1]


@dataclass
class LatentProfile:
    profile_id: str
    profile_text: str
    evidence: list[str]
    judge_rubric: str
    probe_query: str


@dataclass
class UserTruth:
    user_id: str
    span_days: int
    salient: list[SalientFact] = field(default_factory=list)
    states: list[StateVariable] = field(default_factory=list)
    profiles: list[LatentProfile] = field(default_factory=list)


def derive_probes(truth: UserTruth) -> list[Probe]:
    probes: list[Probe] = []
    for f in truth.salient:
        probes.append(Probe(f"f-{f.fact_id}", truth.user_id, ProblemFamily.SALIENCE,
                            f.probe_query, AnswerSpec(accept_patterns=list(f.keywords))))
    for s in truth.states:
        probes.append(Probe(f"s-{s.name}", truth.user_id, ProblemFamily.TEMPORAL,
                            s.probe_query, AnswerSpec(accept_patterns=[s.current_value])))
    for p in truth.profiles:
        probes.append(Probe(f"p-{p.profile_id}", truth.user_id, ProblemFamily.ABSTRACTION,
                            p.probe_query, AnswerSpec(judge_rubric=p.judge_rubric)))
    return probes


def build_ground_truth_state(truth: UserTruth) -> GroundTruthState:
    parts: list[str] = []
    for f in truth.salient:
        parts.append(f"关键事实:{f.text}")
    for s in truth.states:
        parts.append(f"{s.name}(当前):{s.current_value}")
    for p in truth.profiles:
        parts.append(f"画像:{p.profile_text}")
    return GroundTruthState(truth.user_id, ";".join(parts))
