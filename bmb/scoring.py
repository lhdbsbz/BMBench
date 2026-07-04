"""打分:A/C 确定性(关键词),B 用固定模型当 judge 多采样。"""
from __future__ import annotations
import re
from bmb.contract import AnswerSpec, ProblemFamily
from bmb.models import FixedModel

_JUDGE_PROMPT = """你是阅卷员。按 rubric 给回答打分,只输出一个数字:0(完全不符)/ 0.5(部分)/ 1(完全符合)。
rubric:{rubric}
回答:{answer}
分数:"""


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def score_deterministic(answer_text: str, spec: AnswerSpec) -> float:
    a = _normalize(answer_text)
    if any(_normalize(p) and _normalize(p) in a for p in spec.reject_patterns):
        return 0.0
    if spec.accept_patterns and any(_normalize(p) in a for p in spec.accept_patterns if _normalize(p)):
        return 1.0
    return 0.0


def answer(model: FixedModel, query: str, payload: str, seed: int = 0) -> str:
    prompt = (
        "根据以下【记忆载荷】回答问题。只能依赖载荷内容。\n\n"
        f"载荷:\n{payload}\n\n问题:{query}\n\n回答:"
    )
    return model.generate(prompt, temperature=0.0, seed=seed)


def _parse_score(text: str) -> float:
    m = re.search(r"(0(\.\d+)?|1(\.0+)?)", text.strip())
    if not m:
        return 0.0
    v = float(m.group(0))
    return max(0.0, min(1.0, v))


def score_llm_judge(model: FixedModel, answer_text: str, spec: AnswerSpec,
                    k: int = 5, seed: int = 0) -> float:
    rubric = spec.judge_rubric or ""
    vals = []
    for i in range(k):
        out = model.generate(
            _JUDGE_PROMPT.format(rubric=rubric, answer=answer_text),
            temperature=0.3, seed=seed + i,
        )
        vals.append(_parse_score(out))
    return sum(vals) / len(vals) if vals else 0.0


def score(model: FixedModel, family: ProblemFamily, answer_text: str,
          spec: AnswerSpec, judge_k: int = 5) -> float:
    if family is ProblemFamily.ABSTRACTION:
        return score_llm_judge(model, answer_text, spec, k=judge_k)
    return score_deterministic(answer_text, spec)
