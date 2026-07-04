# tests/test_bio_faithful.py
from bmb.contract import StructuredEvent, CapabilityFlag
from bmb.adapters.bio_faithful import BioFaithfulAdapter


def _ingest_many(adapter, n=400):
    # 每条事实文本各异 → _det_seed(text, ts) 各不相同 → 每条事实独立的伯努利抽取,
    # 避免同种子导致 N 条事实拿到完全相同的 keep/drop 决策。
    for i in range(n):
        adapter.ingest("u1", 1.0, StructuredEvent(fact_id=f"f{i}", ts=1.0, text=f"fact_{i}"))


def _retention_rate(adapter, n=400, **recall_kwargs):
    """单次 recall 即对 n 条独立事实各做一次伯努利抽取;统计存活比例。

    recall 输出是存活事实文本的拼接,每条 `fact_{i}` 恰好贡献一个 `"fact_"` 前缀,
    故 `out.count("fact_")` = 存活事实数。
    """
    out = adapter.recall("u1", "x", **recall_kwargs)
    return out.count("fact_") / n


def test_bio_faithful_is_time_aware():
    a = BioFaithfulAdapter()
    assert CapabilityFlag.TIME_AWARE in a.capabilities.flags


def test_retention_decreases_with_time_statistically():
    """近时保留率 > 远时保留率(艾宾浩斯),基于 400 条独立事实的统计比较。"""
    a = BioFaithfulAdapter()
    _ingest_many(a, n=400)
    near = _retention_rate(a, n=400, current_ts=0.5)  # dt=0 → p≈1.0
    far = _retention_rate(a, n=400, current_ts=8.0)   # dt=7 → p≈0.2
    assert near > far
