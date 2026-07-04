"""确定性信号提取。本 plan 用子串匹配(所有 key_tokens 都出现=保留),全程不依赖 LLM judge。
这是 v2「确定性优先」的命门:评分公信力取决于信号提取的可复现性。"""
from __future__ import annotations
from generator.schemas import Fact


def fact_retained(recall_text: str, fact: Fact) -> bool:
    """确定性判断:fact 的所有 key_tokens 是否都出现在召回文本里。"""
    return all(tok in recall_text for tok in fact.key_tokens)
