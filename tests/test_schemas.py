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


def test_fact_role_field():
    """role 字段标记该 fact 在配对中的角色;默认空字符串。"""
    f = Fact(fact_id="f2", ts=1.0, text="开心的事", role="emotional")
    assert f.role == "emotional"


def test_fact_role_default_empty():
    f = Fact(fact_id="f3", ts=2.0, text="普通的事")
    assert f.role == ""


def test_fact_core_detail_tokens_default_empty():
    from generator.schemas import Fact
    f = Fact(fact_id="f", ts=1.0, text="周三暴雨", key_tokens=["周三"])
    assert f.core_tokens == []
    assert f.detail_tokens == []


def test_fact_core_detail_tokens_set():
    from generator.schemas import Fact
    f = Fact(fact_id="f", ts=1.0, text="周会推迟到下午三点",
             key_tokens=["周会"], core_tokens=["周会", "推迟"],
             detail_tokens=["下午", "三点"])
    assert f.core_tokens == ["周会", "推迟"]
    assert f.detail_tokens == ["下午", "三点"]


def test_role_reconstruction_constant():
    from generator.schemas import ROLE_RECONSTRUCTION
    assert ROLE_RECONSTRUCTION == "reconstruction"
