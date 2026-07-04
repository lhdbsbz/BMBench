# tests/test_oracle.py
from bmb.contract import StructuredEvent, Dimension
from bmb.adapters.oracle import OracleAdapter


def test_oracle_returns_injected_truth():
    a = OracleAdapter({"u1": "项目周会推迟"})
    a.ingest("u1", 1.0, StructuredEvent(fact_id="x", ts=1.0, text="噪声"))  # 被忽略
    out = a.recall("u1", "anything", current_ts=999.0)
    assert "项目周会推迟" in out


def test_oracle_truth_overrides_time():
    a = OracleAdapter({"u1": "真相"})
    assert a.recall("u1", "x", current_ts=0.0) == a.recall("u1", "x", current_ts=100.0)
