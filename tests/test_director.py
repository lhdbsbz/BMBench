# tests/test_director.py
from generator.generate import generate_world
from generator.render import fact_to_event
from bmb.director import Director
from bmb.adapters.cold_storage import ColdStorageAdapter
from lenses.forgetting import ForgettingLens


def test_director_ingests_in_time_order_then_runs_lens():
    world = generate_world(seed=3)
    graph = world["u1"]
    adapter = ColdStorageAdapter(structured=True)
    director = Director(adapter=adapter, structured=True)
    report = director.evaluate(graph, lenses=[ForgettingLens(sample_ts=[0.0, 1.0, 5.0])])
    assert report.per_dimension  # 有分项
    from bmb.contract import Dimension
    assert Dimension.FORGETTING in report.per_dimension


def test_director_ingest_uses_structured_flag():
    """structured=False 时,导演应把标注渲染进文本(基类收到的事件文本含标注)。"""
    seen = {}

    class Spy:
        capabilities = ColdStorageAdapter(structured=False).capabilities
        def ingest(self, user_id, ts, event):
            seen["text"] = event.text
        def recall(self, *a, **k):
            return ""

    from generator.schemas import Fact, FactGraph
    g = FactGraph(user_id="u1", facts=[
        Fact(fact_id="f1", ts=1.0, text="客户来电", key_tokens=["客户来电"],
             arousal=0.9, valence=0.8)])
    d = Director(adapter=Spy(), structured=False)
    d.evaluate(g, lenses=[])
    assert "激动" in seen["text"]  # 标注烘进了文本
