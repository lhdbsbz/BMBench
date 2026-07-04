# 仿生记忆评测框架 BMB

> 测的不是"答案准不准",而是**记忆架构在固定模型 + 预算下,用多小的载荷恢复多少决策相关信息**——逼近"最小充分统计量"的程度。详见 [设计文档](docs/design/bmb-v1-design.md)。

## 快速开始
```bash
pip install -r requirements.txt
python scripts/make_smoke.py                       # 生成迷你数据集(FakeModel,无需 LLM)
python run_benchmark.py --dataset datasets/smoke --adapter naive_dump --model fake
python run_benchmark.py --dataset datasets/smoke --adapter oracle   --model fake
```
> Windows 若 `python`/`pip` 不可用(Windows Store 占位符),改用 `py` 与 `py -m pip`。

oracle 应明显高于 naive(自检电路)。真实评测:配 `configs/judge.yaml` 接开源模型,生成 `datasets/v1`(见下)。

## 三件事
- **核心指标**:信息恢复率 ∈[0,1],沿预算画「保真–预算前沿」,标量=前沿下面积 AUF。
- **三个压缩难题**:A 噪音→显著性、C 历史→当前态、B 流水账→隐结构。
- **自检电路**:每次出分先跑 naive(地板)+ oracle(天花板),两端不正常则结果作废。

## 接入你的记忆系统
见 [adapter 作者指南](docs/authoring/adapter_authoring.md)。
