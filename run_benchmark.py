"""BMB v2 CLI(基础版,Plan 1):生成合成世界 → 跑遗忘曲线透镜 → 自检 → 打印分项。
用法:python run_benchmark.py --seed 3 --adapter {cold|bio_faithful}"""
from __future__ import annotations
import argparse
import json

from generator.generate import generate_world
from bmb.harness import run_benchmark
from bmb.adapters.cold_storage import ColdStorageAdapter
from bmb.adapters.bio_faithful import BioFaithfulAdapter
from lenses.forgetting import ForgettingLens


def build_adapter(name: str, structured: bool):
    if name == "cold":
        return ColdStorageAdapter(structured=structured)
    if name == "bio_faithful":
        return BioFaithfulAdapter()
    raise ValueError(f"未知 adapter: {name}(Plan 1 仅支持 cold / bio_faithful)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--adapter", default="cold", choices=["cold", "bio_faithful"])
    ap.add_argument("--plain-text", action="store_true", help="纯文本模式(不传结构化标注)")
    args = ap.parse_args()

    world = generate_world(seed=args.seed)
    lenses = [ForgettingLens(sample_ts=[0.0, 1.0, 2.0, 5.0])]
    adapter = build_adapter(args.adapter, structured=not args.plain_text)

    report = run_benchmark(adapter, world, lenses, structured=not args.plain_text)

    out = {
        "adapter": args.adapter,
        "perDimension": {d.value: round(s, 4) for d, s in report.per_dimension.items()},
        "overall": round(report.overall, 4) if report.overall is not None else None,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
