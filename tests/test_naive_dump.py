from bmb.adapters.naive_dump import NaiveDumpAdapter

def test_ingest_then_assemble_recent():
    a = NaiveDumpAdapter()
    for i in range(5):
        a.ingest("u1", f"2026-01-0{i+1}T09:00:00", f"事件{i}")
    out = a.assemble("u1", "Q", budget_tokens=3)  # 每条≈1 token;预算3→只装最近3条
    assert "事件4" in out       # 最近的在内
    assert "事件0" not in out   # 最旧的被挤掉

def test_user_isolation():
    a = NaiveDumpAdapter()
    a.ingest("u1", "t", "属于u1")
    a.ingest("u2", "t", "属于u2")
    assert "u2" not in a.assemble("u1", "Q", 100)

def test_empty_returns_empty():
    a = NaiveDumpAdapter()
    assert a.assemble("u1", "Q", 100) == ""
