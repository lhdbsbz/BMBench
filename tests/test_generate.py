from generator.generate import generate_world


def test_generate_is_deterministic():
    a = generate_world(seed=42)
    b = generate_world(seed=42)
    assert [f.fact_id for f in a["u1"].facts] == [f.fact_id for f in b["u1"].facts]


def test_generate_yields_facts_with_key_tokens():
    g = generate_world(seed=1)["u1"]
    assert len(g.facts) > 0
    assert all(f.key_tokens for f in g.facts)  # 每条事实都有确定性探针锚点


def test_different_seeds_differ():
    a = generate_world(seed=1)
    c = generate_world(seed=999)
    # 至少文本集合不同(不同种子产出不同世界)
    assert {f.text for f in a["u1"].facts} != {f.text for f in c["u1"].facts} or \
           [f.fact_id for f in a["u1"].facts] != [f.fact_id for f in c["u1"].facts]


def test_world_has_emotional_and_neutral_facts():
    g = generate_world(seed=1)["u1"]
    emo = [f for f in g.facts if f.arousal > 0.5 or abs(f.valence) > 0.5]
    neut = [f for f in g.facts if f.arousal == 0 and f.valence == 0 and f.self_relevance == 0]
    assert emo and neut


def test_world_has_self_and_other_facts():
    g = generate_world(seed=1)["u1"]
    self_f = [f for f in g.facts if f.self_relevance > 0.5]
    other = [f for f in g.facts if f.self_relevance == 0]
    assert self_f and other


def test_world_has_supersede_pair():
    g = generate_world(seed=1)["u1"]
    sup = [f for f in g.facts if f.supersedes is not None]
    assert sup  # 至少一对:新 fact supersedes 旧 fact
    ids = {f.fact_id for f in g.facts}
    assert all(f.supersedes in ids for f in sup)  # 指向存在的旧 fact


def test_world_has_salient_and_detail_facts():
    g = generate_world(seed=1)["u1"]
    salient = [f for f in g.facts if f.is_salient]
    detail = [f for f in g.facts if not f.is_salient]
    assert salient and detail


def test_world_facts_have_all_roles():
    from generator.generate import N_PAIR
    from generator.schemas import (ROLE_EMOTIONAL, ROLE_EMOTIONAL_NEUTRAL, ROLE_SELF,
        ROLE_SELF_OTHER, ROLE_BELIEF_OLD, ROLE_BELIEF_NEW, ROLE_SALIENT, ROLE_DETAIL)
    g = generate_world(seed=1)["u1"]
    roles = [f.role for f in g.facts]
    for r in (ROLE_EMOTIONAL, ROLE_EMOTIONAL_NEUTRAL, ROLE_SELF, ROLE_SELF_OTHER,
              ROLE_BELIEF_OLD, ROLE_BELIEF_NEW, ROLE_SALIENT, ROLE_DETAIL):
        assert roles.count(r) == N_PAIR, f"角色 {r!r} 期望 {N_PAIR} 条,实际 {roles.count(r)}"


def test_world_has_reconstruction_facts_with_tokens():
    from generator.schemas import ROLE_RECONSTRUCTION
    g = generate_world(seed=1)["u1"]
    recon = [f for f in g.facts if f.role == ROLE_RECONSTRUCTION]
    assert recon, "应有 reconstruction 角色 fact"
    for f in recon:
        assert f.core_tokens and f.detail_tokens  # 要义+细节都有


def test_reconstruction_facts_core_detail_alignment():
    """core_tokens 在文本前 60%，detail_tokens 在文本后 40%（T5/T6 对齐）。"""
    from generator.generate import N_PAIR
    from generator.schemas import ROLE_RECONSTRUCTION
    g = generate_world(seed=1)["u1"]
    recon = [f for f in g.facts if f.role == ROLE_RECONSTRUCTION]
    assert len(recon) == N_PAIR, f"应有 {N_PAIR} 条 reconstruction fact,实际 {len(recon)}"
    for f in recon:
        cut = int(len(f.text) * 0.6)
        front = f.text[:cut]
        back = f.text[cut:]
        for tok in f.core_tokens:
            assert tok in front, (
                f"core_token {tok!r} 不在前 60%: text={f.text!r}, cut={cut}"
            )
        for tok in f.detail_tokens:
            assert tok in back, (
                f"detail_token {tok!r} 不在后 40%: text={f.text!r}, cut={cut}"
            )
