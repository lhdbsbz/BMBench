from bmb.adapters.oracle import OracleAdapter

def test_oracle_returns_state_ignoring_ingest():
    a = OracleAdapter({"u1": "用户当前严格素食;青霉素过敏。"})
    a.ingest("u1", "t", "假经历,应被忽略")
    out = a.assemble("u1", "Q", 1000)
    assert "素食" in out and "假经历" not in out

def test_oracle_truncates_to_budget():
    from bmb.models import count_tokens
    a = OracleAdapter({"u1": "x" * 1000})  # 1000 字符 ≈250 token
    out = a.assemble("u1", "Q", 10)
    assert count_tokens(out) <= 10   # 截断保证:token 数 ≤ 预算

def test_oracle_unknown_user_empty():
    a = OracleAdapter({"u1": "状态"})
    assert a.assemble("uX", "Q", 100) == ""
