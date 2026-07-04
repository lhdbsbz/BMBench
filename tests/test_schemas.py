from generator.schemas import (
    UserTruth, SalientFact, StateVariable, LatentProfile,
    derive_probes, build_ground_truth_state,
)
from bmb.contract import ProblemFamily

def _truth():
    return UserTruth(
        user_id="u1", span_days=100,
        salient=[SalientFact("f1", "对青霉素严重过敏", ["青霉素"], "有什么用药禁忌?")],
        states=[StateVariable("饮食", [(0, "素食"), (30, "破戒吃牛排"), (60, "重新素食")], "现在饮食?")],
        profiles=[LatentProfile("p1", "数码爱好者", ["买了机械键盘", "买了GPU"],
                                judge_rubric="推荐应与数码相关", probe_query="送什么生日礼物?")],
    )

def test_derive_probes_covers_three_families():
    probes = derive_probes(_truth())
    families = {p.family for p in probes}
    assert families == {ProblemFamily.SALIENCE, ProblemFamily.TEMPORAL, ProblemFamily.ABSTRACTION}
    # A 探针带 accept 关键词
    a = next(p for p in probes if p.family is ProblemFamily.SALIENCE)
    assert "青霉素" in a.answer_spec.accept_patterns

def test_state_current_value_is_last():
    t = _truth()
    assert t.states[0].timeline[-1][1] == "重新素食"

def test_ground_truth_state_compact_and_current():
    st = build_ground_truth_state(_truth())
    assert "青霉素" in st.text and "重新素食" in st.text and "数码爱好者" in st.text
    assert st.user_id == "u1"
