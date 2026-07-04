# tests/test_forgetting.py(最终版,自包含,不依赖 Task 12)
from generator.schemas import Fact, FactGraph
from generator.render import fact_to_event
from bmb.contract import Capabilities, CapabilityFlag
from lenses.forgetting import ForgettingLens


class _FullRecallAdapter:
    """测试桩:永远返回全部已 ingest 事实的文本(模拟冷库)。"""
    capabilities = Capabilities(flags={CapabilityFlag.STRUCTURED_EVENT})
    def __init__(self):
        self._store = []
    def ingest(self, user_id, ts, event):
        self._store.append(event.text)
    def recall(self, user_id, cue, current_ts, session_id=None):
        return "".join(self._store)


def _graph():
    return FactGraph(user_id="u1", facts=[
        Fact(fact_id="f1", ts=1.0, text="项目周会推迟", key_tokens=["项目周会", "推迟"]),
    ])


def test_forgetting_returns_score_in_unit_interval():
    lens = ForgettingLens(sample_ts=[0.0, 1.0, 2.0, 5.0, 10.0])
    adapter = _FullRecallAdapter()
    g = _graph()
    for f in g.facts:
        adapter.ingest(g.user_id, f.ts, fact_to_event(f, structured=True))
    score = lens.run(adapter, g)
    assert 0.0 <= score <= 1.0


def test_cold_storage_scores_low_on_forgetting():
    lens = ForgettingLens(sample_ts=[0.0, 1.0, 2.0, 5.0, 10.0])
    adapter = _FullRecallAdapter()
    g = _graph()
    for f in g.facts:
        adapter.ingest(g.user_id, f.ts, fact_to_event(f, structured=True))
    assert lens.run(adapter, g) < 0.5
