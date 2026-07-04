"""BMB 一条命令复现。--model fake 用 FakeModel(无需 LLM);real 用 configs/judge.yaml。"""
from __future__ import annotations
import sys
from pathlib import Path

# 确保项目根在 sys.path(从任意目录调用都能 import bmb)
sys.path.insert(0, str(Path(__file__).resolve().parent))

import argparse
import json

import yaml

from bmb.dataset import load_dataset
from bmb.harness import BUDGETS, run_benchmark
from bmb.models import FakeModel, OpenAICompatibleModel
from bmb.adapters.naive_dump import NaiveDumpAdapter
from bmb.adapters.oracle import OracleAdapter

_ADAPTERS = {"naive_dump": NaiveDumpAdapter, "oracle": OracleAdapter}


def build_model(name: str, cfg: dict | None = None):
    if name == "fake":
        # smoke 用:载荷/真相含 accept 关键词即返回该关键词
        def responder(prompt: str) -> str:
            for kw in ("青霉素", "素食", "重新素食", "数码", "显卡", "键盘"):
                if kw in prompt:
                    return kw
            return "不知道"
        return FakeModel(responder)
    c = cfg or {}
    return OpenAICompatibleModel(c["base_url"], c["api_key"], c["model"])


def main():
    ap = argparse.ArgumentParser(description="BMB 记忆架构评测")
    ap.add_argument("--dataset", required=True, help="冻结数据集目录,如 datasets/smoke")
    ap.add_argument("--adapter", required=True, choices=list(_ADAPTERS),
                    help="v1 内置:naive_dump / oracle(真实系统以后插)")
    ap.add_argument("--model", default="fake", help="fake(测试)或 real(读 configs/judge.yaml)")
    ap.add_argument("--judge-config", default="configs/judge.yaml")
    ap.add_argument("--budgets", default=None, help="逗号分隔 token 数,缺省=8k/32k/64k/128k")
    ap.add_argument("--out", default=None, help="结果 JSON 路径")
    args = ap.parse_args()

    model_cfg = None
    if args.model == "real":
        model_cfg = yaml.safe_load(Path(args.judge_config).read_text(encoding="utf-8"))
    model = build_model(args.model, model_cfg)
    budgets = [int(x) for x in args.budgets.split(",")] if args.budgets else BUDGETS

    ds = load_dataset(args.dataset)
    # OracleAdapter 是天花板:作被测 adapter 时需注入 ground_truth 状态(否则 assemble 恒空)。
    if args.adapter == "oracle":
        adapter = OracleAdapter({uid: s.text for uid, s in ds.states_by_user.items()})
    else:
        adapter = _ADAPTERS[args.adapter]()
    result = run_benchmark(adapter, ds, model, budgets)

    out = args.out or f"results/{args.adapter}@{ds.manifest.get('version')}-{args.model}.json"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"完成:overall_auf={result['overall_auf']:.3f} → {out}")


if __name__ == "__main__":
    main()
