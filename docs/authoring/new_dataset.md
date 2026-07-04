# 如何生成新数据集

配置字段(见 `generator/schemas.py`):`version`、`span_days`、`noise_per_user`、`salient_pool`、`state_pool`、`profile_pool`。
真相先于渲染(state-first),探针与答案确定性派生。

字段顺序约定(池里每条按 dataclass 字段序排):
- `salient_pool`:`[fact_id, text, keywords, probe_query]`
- `state_pool`:`[name, timeline, probe_query]`
- `profile_pool`:`[profile_id, profile_text, evidence, judge_rubric, probe_query]`

```bash
# 用 FakeModel 生成 smoke(无需 LLM)
python scripts/make_smoke.py
```

真实 v1:写 `configs/v1.yaml`(放大规模:`~30 用户、每人 5万–15万 token、噪音≈99%`)+ 配 `configs/judge.yaml`(真模型),跑 `python -m generator.generate`(或扩展 make_smoke 调用)一次后冻结到 `datasets/v1/`,随仓库分发。
