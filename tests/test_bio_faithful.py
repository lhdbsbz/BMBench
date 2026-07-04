# tests/test_bio_faithful.py
from bmb.contract import StructuredEvent, CapabilityFlag
from bmb.adapters.bio_faithful import BioFaithfulAdapter
from bmb.bio_baselines import (
    EMOTIONAL_ENHANCEMENT, SELF_REFERENCE_EFFECT, BELIEF_RESIDUAL,
    SCHEMA_SALIENT, SCHEMA_DETAIL,
)


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


def _ingest_role_facts(adapter, user_id, role, n, prefix, ts=3.0):
    """注入 n 条带指定 role 的独立事实(文本各异)。
    使用零填充索引(05d)避免子串误命中,如 'det_1' 不会误匹配 'det_10'。
    """
    for i in range(n):
        adapter.ingest(
            user_id, ts,
            StructuredEvent(
                fact_id=f"{prefix}_{i:05d}",
                ts=ts,
                text=f"{prefix}_{i:05d}",
                role=role,
            ),
        )


def _recall_role_rate(adapter, user_id, prefix, n, current_ts):
    """对 prefix 的 n 条事实统计保留率(子串匹配)。
    零填充索引保证每个 key 唯一、不互为子串。
    """
    out = adapter.recall(user_id, "x", current_ts=current_ts)
    return sum(1 for i in range(n) if f"{prefix}_{i:05d}" in out) / n


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


# ── 角色驱动保留率测试(RW7) ──────────────────────────────────────────────────

N_ROLE = 200   # 每个角色的独立事实数(足够统计稳定)
INGEST_TS = 3.0
RECALL_TS = 4.0   # dt=1.0 → ebbinghaus ≈ 0.54;角色偏差叠加在此 base 上


def test_salient_retained_more_than_detail():
    """要义事实保留率 > 细节事实保留率。"""
    a = BioFaithfulAdapter()
    _ingest_role_facts(a, "u_comp", "salient", N_ROLE, "sal", ts=INGEST_TS)
    _ingest_role_facts(a, "u_comp", "detail",   N_ROLE, "det", ts=INGEST_TS)
    rate_salient = _recall_role_rate(a, "u_comp", "sal", N_ROLE, RECALL_TS)
    rate_detail  = _recall_role_rate(a, "u_comp", "det", N_ROLE, RECALL_TS)
    assert rate_salient > rate_detail, (
        f"salient 保留率 {rate_salient:.2f} 应 > detail 保留率 {rate_detail:.2f}"
    )


def test_salient_retention_near_schema_salient():
    """要义保留率应接近 SCHEMA_SALIENT(0.80),容差 ±0.15。"""
    a = BioFaithfulAdapter()
    _ingest_role_facts(a, "u_sal", "salient", N_ROLE, "sal2", ts=INGEST_TS)
    rate = _recall_role_rate(a, "u_sal", "sal2", N_ROLE, RECALL_TS)
    assert abs(rate - SCHEMA_SALIENT) < 0.15, f"salient 保留率 {rate:.2f} 偏离 {SCHEMA_SALIENT}"


def test_detail_retention_near_schema_detail():
    """细节保留率应接近 SCHEMA_DETAIL(0.30),容差 ±0.15。"""
    a = BioFaithfulAdapter()
    _ingest_role_facts(a, "u_det", "detail", N_ROLE, "det2", ts=INGEST_TS)
    rate = _recall_role_rate(a, "u_det", "det2", N_ROLE, RECALL_TS)
    assert abs(rate - SCHEMA_DETAIL) < 0.15, f"detail 保留率 {rate:.2f} 偏离 {SCHEMA_DETAIL}"


def test_belief_old_low_retention():
    """旧信念保留率应接近 BELIEF_RESIDUAL(0.30),容差 ±0.15。"""
    a = BioFaithfulAdapter()
    _ingest_role_facts(a, "u_bel", "beliefOld", N_ROLE, "bold", ts=INGEST_TS)
    rate = _recall_role_rate(a, "u_bel", "bold", N_ROLE, RECALL_TS)
    assert abs(rate - BELIEF_RESIDUAL) < 0.15, f"beliefOld 保留率 {rate:.2f} 偏离 {BELIEF_RESIDUAL}"


def test_emotional_retained_more_than_neutral():
    """情绪事实保留率 > 情绪中性事实保留率(情绪增强效应)。"""
    a = BioFaithfulAdapter()
    _ingest_role_facts(a, "u_emo", "emotional",        N_ROLE, "emo",  ts=INGEST_TS)
    _ingest_role_facts(a, "u_emo", "emotionalNeutral", N_ROLE, "neu",  ts=INGEST_TS)
    rate_emo = _recall_role_rate(a, "u_emo", "emo",  N_ROLE, RECALL_TS)
    rate_neu = _recall_role_rate(a, "u_emo", "neu",  N_ROLE, RECALL_TS)
    assert rate_emo > rate_neu, (
        f"emotional 保留率 {rate_emo:.2f} 应 > emotionalNeutral 保留率 {rate_neu:.2f}"
    )


def test_self_retained_more_than_other():
    """自我关联事实保留率 > 他人事实保留率(自我参照效应)。"""
    a = BioFaithfulAdapter()
    _ingest_role_facts(a, "u_self", "self",      N_ROLE, "slf", ts=INGEST_TS)
    _ingest_role_facts(a, "u_self", "selfOther", N_ROLE, "oth", ts=INGEST_TS)
    rate_self  = _recall_role_rate(a, "u_self", "slf", N_ROLE, RECALL_TS)
    rate_other = _recall_role_rate(a, "u_self", "oth", N_ROLE, RECALL_TS)
    assert rate_self > rate_other, (
        f"self 保留率 {rate_self:.2f} 应 > selfOther 保留率 {rate_other:.2f}"
    )
