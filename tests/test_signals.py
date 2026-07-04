from generator.schemas import Fact
from bmb.signals import fact_retained


def _f():
    return Fact(fact_id="f1", ts=1.0, text="项目周会推迟", key_tokens=["项目周会", "推迟"])


def test_retained_when_all_key_tokens_present():
    assert fact_retained("上周的项目周会推迟到了下午", _f()) is True


def test_not_retained_when_token_missing():
    assert fact_retained("项目周会很顺利", _f()) is False  # 缺「推迟」


def test_case_insensitive_irrelevant_for_chinese():
    # 中文无大小写,但接口要稳:缺一个锚点即未保留
    assert fact_retained("推迟了", _f()) is False
