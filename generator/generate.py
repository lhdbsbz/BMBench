"""state-first 确定性生成:先造结构化真相,再渲染。本 plan 只需遗忘曲线透镜能用的最小真相。"""
from __future__ import annotations
import random

from generator.schemas import Fact, FactGraph

# 词库(确定性生成的素材;后续透镜扩展更多字段)
_SUBJECTS = ["项目周会", "客户来电", "快递送达", "系统告警", "午餐", "晨跑"]
_PREDICATES = ["推迟到下午", "确认了需求", "放在前台", "已自动恢复", "吃的拉面", "绕了公园"]


def generate_world(seed: int = 0, n_users: int = 1, facts_per_user: int = 6) -> dict[str, FactGraph]:
    """按种子确定性生成合成世界。每个事实带 key_tokens(确定性探针锚点)。"""
    rng = random.Random(seed)
    world: dict[str, FactGraph] = {}
    for ui in range(n_users):
        uid = f"u{ui + 1}"
        facts: list[Fact] = []
        for fi in range(facts_per_user):
            subj = rng.choice(_SUBJECTS)
            pred = rng.choice(_PREDICATES)
            text = f"{subj}{pred}"
            ts = float(fi + 1)  # 逻辑时间按事实序递增
            facts.append(Fact(
                fact_id=f"{uid}_f{fi}",
                ts=ts,
                text=text,
                key_tokens=[subj, pred],  # 两个锚点都出现才算「保留」
            ))
        world[uid] = FactGraph(user_id=uid, facts=facts)
    return world
