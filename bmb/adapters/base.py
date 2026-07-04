# bmb/adapters/base.py
"""adapter 基类:管理 Capabilities + 按 structured 标志收事件。"""
from __future__ import annotations
from bmb.contract import BMBAdapter, Capabilities, CapabilityFlag, StructuredEvent


class BaseAdapter:
    """子类继承并实现 ingest/recall。本类只持有 Capabilities。"""
    def __init__(self, structured: bool, extra_flags: set[CapabilityFlag] | None = None):
        flags: set[CapabilityFlag] = set(extra_flags or set())
        if structured:
            flags.add(CapabilityFlag.STRUCTURED_EVENT)
        self.capabilities = Capabilities(flags=flags)
        self._structured = structured
