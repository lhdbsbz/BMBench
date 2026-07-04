# 仿生记忆评测框架 BMB v2

> 测的不是「信息恢复多少」,而是**一个记忆系统的外部行为有多接近健康成人记忆的实证分布**。
> 详见 [设计文档](docs/design/bmb-v2-design.md)。

## 当前状态(Plan 1:核心引擎 + 遗忘曲线透镜)

可评测「遗忘曲线」一个维度,跑通自检硬门(冷库地板 < bio-faithful 天花板)。
其余五个透镜(情绪增强 / 再构·再巩固 / 压缩·图式 / 信念更新 / 自我关联)在后续 plan 扩展。

## 快速开始
```bash
pip install pytest          # 唯一依赖
python -m pytest -q         # 跑全部测试
python run_benchmark.py --seed 3 --adapter cold          # 冷库(地板)
python run_benchmark.py --seed 3 --adapter bio_faithful  # 天花板
```
> Windows 若 `python`/`pip` 不可用(Windows Store 占位符),改用 `py` 与 `py -m pip`。

## 核心概念
- **评测目标**:系统行为对齐健康成人记忆的实证分布(钟形评分,过度和不足都扣分)。
- **六个维度**:遗忘曲线、情绪增强、再构/再巩固、压缩/图式、信念更新、自我关联。
- **确定性优先**:信号提取用确定性事实探针,不依赖 LLM judge(可复现)。
- **自检电路**:每次出分先跑冷库(地板)+ bio-faithful(天花板),两端不正常则结果作废。

## 接入你的记忆系统
实现 `ingest(ts, event)` + `recall(cue, current_ts, session_id)` 两个方法。详见
[设计文档 §8](docs/design/bmb-v2-design.md#8-adapter-接入onboarding)。
