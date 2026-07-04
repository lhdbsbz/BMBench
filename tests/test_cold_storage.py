# tests/test_cold_storage.py
from bmb.contract import StructuredEvent, CapabilityFlag
from bmb.adapters.cold_storage import ColdStorageAdapter


def test_cold_storage_remembers_everything():
    a = ColdStorageAdapter(structured=True)
    a.ingest("u1", 1.0, StructuredEvent(fact_id="f1", ts=1.0, text="甲"))
    a.ingest("u1", 2.0, StructuredEvent(fact_id="f2", ts=2.0, text="乙"))
    out = a.recall("u1", "随便", current_ts=100.0)  # 很久以后
    assert "甲" in out and "乙" in out  # 永不衰减


def test_cold_storage_not_time_aware():
    a = ColdStorageAdapter(structured=True)
    assert CapabilityFlag.TIME_AWARE not in a.capabilities.flags


def test_cold_storage_plain_text_mode():
    a = ColdStorageAdapter(structured=False)  # 只收纯文本
    assert CapabilityFlag.STRUCTURED_EVENT not in a.capabilities.flags
