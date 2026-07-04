# tests/test_emotional.py
from generator.schemas import Fact, FactGraph
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
        Fact(fact_id="e", ts=1.0, text="告警恢复", key_tokens=["告警", "恢复"], arousal=0.8, valence=0.7),
        Fact(fact_id="n", ts=2.0, text="午餐拉面", key_tokens=["午餐", "拉面"]),
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
