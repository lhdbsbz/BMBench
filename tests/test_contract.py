# tests/test_contract.py
from bmb.contract import Dimension, StructuredEvent, CapabilityFlag, Capabilities


def test_dimension_six_members():
    assert {d.value for d in Dimension} == {
        "forgetting", "emotional", "reconstruction",
        "compression", "beliefUpdate", "selfReference",
    }


def test_structured_event_defaults():
    e = StructuredEvent(fact_id="f1", ts=0.0, text="下雨了")
    assert e.valence == 0.0 and e.arousal == 0.0
    assert e.self_relevance == 0.0
    assert e.supersedes is None
    assert e.is_salient is False


def test_capabilities_default_empty():
    c = Capabilities()
    assert c.flags == set()


def test_capabilities_with_flags():
    c = Capabilities(flags={CapabilityFlag.TIME_AWARE})
    assert CapabilityFlag.TIME_AWARE in c.flags


def test_structured_event_role_field():
    """role 字段标记该事件在配对中的角色;默认空字符串。"""
    e = StructuredEvent(fact_id="f", ts=1.0, text="x", role="emotional")
    assert e.role == "emotional"


def test_structured_event_role_default_empty():
    e = StructuredEvent(fact_id="f2", ts=2.0, text="y")
    assert e.role == ""
