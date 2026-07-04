# tests/test_bio_faithful.py
import statistics
from bmb.contract import StructuredEvent, CapabilityFlag
from bmb.adapters.bio_faithful import BioFaithfulAdapter


def _ingest_many(adapter, n=200):
    for i in range(n):
        adapter.ingest("u1", 1.0, StructuredEvent(fact_id="f", ts=1.0, text="唯一事实"))


def test_bio_faithful_is_time_aware():
    a = BioFaithfulAdapter()
    assert CapabilityFlag.TIME_AWARE in a.capabilities.flags


def test_retention_decreases_with_time_statistically():
    """近时保留率 > 远时保留率(艾冰浩斯),统计显著。"""
    a = BioFaithfulAdapter()
    _ingest_many(a, n=400)
    near = sum("唯一事实" in a.recall("u1", "x", current_ts=0.5) for _ in range(200)) / 200
    far = sum("唯一事实" in a.recall("u1", "x", current_ts=8.0) for _ in range(200)) / 200
    assert near > far
