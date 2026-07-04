# tests/test_compression.py
from generator.schemas import Fact, FactGraph
from generator.render import fact_to_event
from bmb.contract import Capabilities, CapabilityFlag
from lenses.compression import CompressionLens


class _AllRecallAdapter:
    capabilities = Capabilities(flags={CapabilityFlag.STRUCTURED_EVENT})
    def __init__(self): self._s = []
    def ingest(self, user_id, ts, event): self._s.append(event.text)
    def recall(self, user_id, cue, current_ts, session_id=None): return "".join(self._s)


def _graph():
    return FactGraph(user_id="u1", facts=[
        Fact(fact_id="sal", ts=1.0, text="核心结论", key_tokens=["核心", "结论"], is_salient=True),
        Fact(fact_id="det", ts=2.0, text="次要细节", key_tokens=["次要", "细节"], is_salient=False),
    ])


def test_compression_returns_unit_interval():
    lens = CompressionLens(current_ts=2.0)
    a = _AllRecallAdapter()
    g = _graph()
    for f in g.facts: a.ingest(g.user_id, f.ts, fact_to_event(f, True))
    s = lens.run(a, g)
    assert 0.0 <= s <= 1.0


def test_cold_storage_keeps_everything_is_low():
    """冷库:要义 1.0(基准 0.80)+ 细节 1.0(基准 0.30)→ 都偏离 → 低分(不压缩)。"""
    lens = CompressionLens(current_ts=2.0)
    a = _AllRecallAdapter()
    g = _graph()
    for f in g.facts: a.ingest(g.user_id, f.ts, fact_to_event(f, True))
    assert lens.run(a, g) < 0.4
