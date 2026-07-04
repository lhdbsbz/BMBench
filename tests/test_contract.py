from bmb.contract import (
    ProblemFamily, AnswerSpec, Probe, GroundTruthState,
)

def test_family_values():
    assert ProblemFamily.SALIENCE.value == "A"
    assert ProblemFamily.TEMPORAL.value == "C"
    assert ProblemFamily.ABSTRACTION.value == "B"

def test_answer_spec_defaults():
    s = AnswerSpec()
    assert s.accept_patterns == [] and s.reject_patterns == [] and s.judge_rubric is None

def test_probe_construction():
    p = Probe("p1", "u1", ProblemFamily.TEMPORAL, "现在饮食?",
              AnswerSpec(accept_patterns=["vegan", "素食"]))
    assert p.family is ProblemFamily.TEMPORAL
    assert p.answer_spec.accept_patterns == ["vegan", "素食"]

def test_state_carries_text():
    st = GroundTruthState("u1", "用户当前严格素食;无药物过敏记录。")
    assert st.user_id == "u1" and "素食" in st.text
