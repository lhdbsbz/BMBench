# tests/test_belief_update.py
from generator.schemas import Fact, FactGraph
from generator.render import fact_to_event
from bmb.contract import Capabilities, CapabilityFlag
from lenses.belief_update import BeliefUpdateLens


class _AllRecallAdapter:
    capabilities = Capabilities(flags={CapabilityFlag.STRUCTURED_EVENT})
    def __init__(self): self._s = []
    def ingest(self, user_id, ts, event): self._s.append(event.text)
    def recall(self, user_id, cue, current_ts, session_id=None): return "".join(self._s)


def _graph():
    # old 先, new 后(new.supersedes=old)
    old = Fact(fact_id="old", ts=1.0, text="会议周三", key_tokens=["会议", "周三"])
    new = Fact(fact_id="new", ts=2.0, text="会议周四", key_tokens=["会议", "周四"], supersedes="old")
    return FactGraph(user_id="u1", facts=[old, new])


def test_belief_update_returns_unit_interval():
    lens = BeliefUpdateLens(current_ts=3.0)
    a = _AllRecallAdapter()
    g = _graph()
    for f in g.facts: a.ingest(g.user_id, f.ts, fact_to_event(f, True))
    assert 0.0 <= lens.run(a, g) <= 1.0


def test_cold_storage_keeps_old_is_low():
    """冷库:旧 fact 全保留(残留=1.0)→ 偏离 BELIEF_RESIDUAL(0.30)→ 低分(不更新)。"""
    lens = BeliefUpdateLens(current_ts=3.0)
    a = _AllRecallAdapter()
    g = _graph()
    for f in g.facts: a.ingest(g.user_id, f.ts, fact_to_event(f, True))
    assert lens.run(a, g) < 0.4
