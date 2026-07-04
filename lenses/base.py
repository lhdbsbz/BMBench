# lenses/base.py
"""Lens 协议:每个测量透镜的统一接口。
一个透镜 = (探测协议 + 信号提取 + 基准 + 对齐度),封装在 run() 里。
run() 负责:在 adapter 上执行探测 → 收集行为样本 → 提取信号 → 算对齐度 → 返回 [0,1]。"""
from __future__ import annotations
from typing import Protocol, runtime_checkable

from bmb.contract import Dimension, BMBAdapter
from generator.schemas import FactGraph


@runtime_checkable
class Lens(Protocol):
    def dimension(self) -> Dimension: ...
    def run(self, adapter: BMBAdapter, graph: FactGraph, **kwargs) -> float: ...
