# tests/test_self_reference.py
from generator.schemas import Fact, FactGraph, ROLE_SELF, ROLE_SELF_OTHER
from generator.render import fact_to_event
from bmb.contract import Capabilities, CapabilityFlag
from lenses.self_reference import SelfReferenceLens


class _AllRecallAdapter:
    capabilities = Capabilities(flags={CapabilityFlag.STRUCTURED_EVENT})
    def __init__(self): self._s = []
    def ingest(self, user_id, ts, event): self._s.append(event.text)
    def recall(self, user_id, cue, current_ts, session_id=None): return "".join(self._s)


def _graph():
    return FactGraph(user_id="u1", facts=[
        Fact(fact_id="s", ts=1.0, text="我的周会", key_tokens=["我的", "周会"],
             self_relevance=0.8, role=ROLE_SELF),
        Fact(fact_id="o", ts=2.0, text="同事午餐", key_tokens=["同事", "午餐"],
             role=ROLE_SELF_OTHER),
    ])


def test_self_reference_returns_unit_interval():
    lens = SelfReferenceLens(current_ts=2.0)
    a = _AllRecallAdapter()
    g = _graph()
    for f in g.facts: a.ingest(g.user_id, f.ts, fact_to_event(f, True))
    assert 0.0 <= lens.run(a, g) <= 1.0


def test_cold_storage_no_bias_is_low():
    lens = SelfReferenceLens(current_ts=2.0)
    a = _AllRecallAdapter()
    g = _graph()
    for f in g.facts: a.ingest(g.user_id, f.ts, fact_to_event(f, True))
    assert lens.run(a, g) < 0.4
