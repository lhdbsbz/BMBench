from bmb.models import FixedModel, FakeModel, count_tokens

def test_fake_model_deterministic():
    m = FakeModel(lambda p: f"回声:{p[:2]}")
    assert m.generate("你好世界") == "回声:你好"
    assert m.generate("你好世界") == m.generate("你好世界")  # 确定性

def test_count_tokens_positive_and_stable():
    assert count_tokens("") >= 1
    assert count_tokens("a"*400) == 100
    assert count_tokens("a"*400) == count_tokens("a"*400)

def test_fixed_model_is_abstract():
    import pytest
    with pytest.raises(TypeError):
        FixedModel()  # type: ignore[abstract]
