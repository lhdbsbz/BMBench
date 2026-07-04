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
