"""程序化废话生成(99% 噪音的来源)。完全 seeded。"""
from __future__ import annotations
import random

_TEMPLATES = [
    "今天{w},没什么特别。",
    "午饭吃了{food},味道一般。",
    "路上看到一只{animal},心情还行。",
    "晚上{activity},有点累。",
    "今天的天气让人{mood}。",
]
_W = ["晴", "阴", "小雨", "大风"]
_FOOD = ["黄焖鸡", "面条", "沙拉", "煎饼"]
_ANIMAL = ["野猫", "小狗", "鸽子", "松鼠"]
_ACT = ["刷剧", "加班", "散步", "打游戏"]
_MOOD = ["平静", "怀旧", "犯困", "莫名感伤"]


def make_noise(rng: random.Random, n: int) -> list[str]:
    out = []
    for _ in range(n):
        t = rng.choice(_TEMPLATES)
        out.append(t.format(
            w=rng.choice(_W), food=rng.choice(_FOOD), animal=rng.choice(_ANIMAL),
            activity=rng.choice(_ACT), mood=rng.choice(_MOOD),
        ))
    return out
