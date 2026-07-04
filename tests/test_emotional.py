# tests/test_emotional.py
from generator.schemas import Fact, FactGraph, ROLE_EMOTIONAL, ROLE_EMOTIONAL_NEUTRAL, ROLE_SALIENT
from generator.render import fact_to_event
from bmb.contract import Capabilities, CapabilityFlag
from lenses.emotional import EmotionalLens


class _AllRecallAdapter:
    """测试桩:永远返回全部已 ingest 事实的文本(冷库:无偏置)。"""
    capabilities = Capabilities(flags={CapabilityFlag.STRUCTURED_EVENT})
    def __init__(self): self._s = []
    def ingest(self, user_id, ts, event): self._s.append(event.text)
    def recall(self, user_id, cue, current_ts, session_id=None): return "".join(self._s)


def _graph():
    return FactGraph(user_id="u1", facts=[
        Fact(fact_id="e", ts=1.0, text="告警恢复", key_tokens=["告警", "恢复"],
             arousal=0.8, valence=0.7, role=ROLE_EMOTIONAL),
        Fact(fact_id="n", ts=2.0, text="午餐拉面", key_tokens=["午餐", "拉面"],
             role=ROLE_EMOTIONAL_NEUTRAL),
    ])


def test_emotional_returns_unit_interval():
    lens = EmotionalLens(current_ts=2.0)
    a = _AllRecallAdapter()
    g = _graph()
    for f in g.facts: a.ingest(g.user_id, f.ts, fact_to_event(f, True))
    assert 0.0 <= lens.run(a, g) <= 1.0


def test_cold_storage_no_bias_is_low():
    """冷库平等保留 → 偏置≈0 → 偏离 EMOTIONAL_ENHANCEMENT(0.25)→ 低分。"""
    lens = EmotionalLens(current_ts=2.0)
    a = _AllRecallAdapter()
    g = _graph()
    for f in g.facts: a.ingest(g.user_id, f.ts, fact_to_event(f, True))
    assert lens.run(a, g) < 0.4


def test_precise_pairing_ignores_foreign_roles():
    """精确配对回归:图中含外来 ROLE_SALIENT fact,不应污染情绪透镜的中性集合。

    构造:
      baseline 图 = [ROLE_EMOTIONAL, ROLE_EMOTIONAL_NEUTRAL]
      污染图   = baseline + 2 个 ROLE_SALIENT fact(未 ingest → 不在召回文本)

    旧透镜(宽泛属性谓词)会把 2 个 ROLE_SALIENT fact 纳入中性集合
    → neut_rate 由 1.0 降为 1/3 → bias 改变 → 得分变化 → assert 失败。
    新透镜(role 精确匹配)只取 ROLE_EMOTIONAL_NEUTRAL → 结果不变 → assert 通过。
    """
    lens = EmotionalLens(current_ts=2.0)
    g_base = _graph()
    a = _AllRecallAdapter()
    for f in g_base.facts:
        a.ingest(g_base.user_id, f.ts, fact_to_event(f, True))
    score_base = lens.run(a, g_base)

    # 加入 2 个外来 ROLE_SALIENT fact(未 ingest,不在召回文本)
    f1 = Fact(fact_id="x1", ts=1.3, text="外来要义甲", key_tokens=["外来", "要义甲"],
              role=ROLE_SALIENT)
    f2 = Fact(fact_id="x2", ts=1.6, text="外来要义乙", key_tokens=["外来", "要义乙"],
              role=ROLE_SALIENT)
    g_plus = FactGraph(user_id="u1", facts=[*g_base.facts, f1, f2])
    score_plus = lens.run(a, g_plus)   # 同一 adapter,召回文本不变

    assert score_base == score_plus, (
        f"外来 ROLE_SALIENT fact 污染了情绪透镜: base={score_base:.4f}, plus={score_plus:.4f}"
    )
