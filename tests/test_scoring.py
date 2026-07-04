import pytest
from bmb.contract import AnswerSpec, ProblemFamily
from bmb.models import FakeModel
from bmb.scoring import answer, score_deterministic, score_llm_judge, score

def test_deterministic_accept_hit():
    spec = AnswerSpec(accept_patterns=["vegan", "素食"], reject_patterns=["牛排"])
    assert score_deterministic("他现在是严格的素食者", spec) == 1.0

def test_deterministic_reject_blocks():
    spec = AnswerSpec(accept_patterns=["vegan"], reject_patterns=["牛排"])
    assert score_deterministic("他既吃 vegan 又吃牛排", spec) == 0.0

def test_deterministic_miss_is_zero():
    spec = AnswerSpec(accept_patterns=["青霉素"])
    assert score_deterministic("我不清楚", spec) == 0.0

def test_answer_uses_model():
    m = FakeModel(lambda p: " canned ")
    assert answer(m, "Q", "PAY") == " canned "

def test_llm_judge_parses_and_averages():
    # 模型无论 prompt 都回 "0.8"
    m = FakeModel(lambda p: "0.8")
    spec = AnswerSpec(judge_rubric="推荐应与数码相关")
    assert score_llm_judge(m, "送他一把机械键盘", spec, k=3) == pytest.approx(0.8)

def test_score_dispatches_by_family():
    spec_ac = AnswerSpec(accept_patterns=["vegan"])
    assert score(FakeModel(), ProblemFamily.TEMPORAL, "现在 vegan", spec_ac) == 1.0
    spec_b = AnswerSpec(judge_rubric="数码相关")
    # B 走 judge:模型回 "1"
    assert score(FakeModel(lambda p: "1"), ProblemFamily.ABSTRACTION, "显卡", spec_b) == 1.0
