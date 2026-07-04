from generator.schemas import Fact
from generator.render import fact_to_event


def _fact(**kw):
    base = dict(fact_id="f1", ts=1.0, text="项目周会推迟", key_tokens=["项目周会", "推迟"])
    base.update(kw)
    return Fact(**base)


def test_render_structured_keeps_fields():
    f = _fact(valence=0.8, arousal=0.6)
    e = fact_to_event(f, structured=True)
    assert e.valence == 0.8 and e.arousal == 0.6
    assert e.fact_id == "f1" and e.ts == 1.0


def test_render_plain_text_bakes_annotation_in():
    """纯文本模式:把情绪标注渲染进 text(测系统能否从文本隐式识别)。"""
    f = _fact(valence=0.8, arousal=0.6, text="客户来电")
    e = fact_to_event(f, structured=False)
    assert e.valence == 0.0  # 结构化字段清零(已在文本里)
    assert "情绪" in e.text or "激动" in e.text  # 标注进了文本


def test_render_structured_passes_role():
    """structured=True:role 字段透传进 StructuredEvent。"""
    f = _fact(role="emotional")
    e = fact_to_event(f, structured=True)
    assert e.role == "emotional"


def test_render_plain_text_passes_role():
    """structured=False:role 字段仍透传(配对元数据,与情绪标注无关)。"""
    f = _fact(role="emotional")
    e = fact_to_event(f, structured=False)
    assert e.role == "emotional"
