from generator.schemas import Fact, FactGraph


def test_fact_has_key_tokens():
    f = Fact(fact_id="f1", ts=0.0, text="周三下了暴雨",
             key_tokens=["周三", "暴雨"])
    assert f.key_tokens == ["周三", "暴雨"]
    assert f.supersedes is None


def test_factgraph_sorted_by_ts():
    f_late = Fact(fact_id="b", ts=10.0, text="晚", key_tokens=["晚"])
    f_early = Fact(fact_id="a", ts=1.0, text="早", key_tokens=["早"])
    g = FactGraph(user_id="u1", facts=[f_late, f_early])
    assert [f.fact_id for f in g.facts] == ["a", "b"]
