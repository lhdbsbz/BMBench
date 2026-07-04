"""state-first 确定性生成:产出带生物权重标注的配对 fact,供各透镜探测。"""
from __future__ import annotations
import random

from generator.schemas import Fact, FactGraph

_SUBJECTS = ["项目周会", "客户来电", "快递送达", "系统告警", "午餐", "晨跑"]
_PREDICATES = ["推迟到下午", "确认了需求", "放在前台", "已自动恢复", "吃的拉面", "绕了公园"]


def _fact(uid: str, idx: int, ts: float, subj: str, pred: str, **kw) -> Fact:
    return Fact(
        fact_id=f"{uid}_f{idx}", ts=ts, text=f"{subj}{pred}",
        key_tokens=[subj, pred], **kw,
    )


def generate_world(seed: int = 0, n_users: int = 1) -> dict[str, FactGraph]:
    """每用户生成配对 fact:情绪/中性、自我/无关、矛盾(新 supersedes 旧)、要义/细节。
    按 ts 升序,矛盾对的旧 fact 先于新 fact。"""
    rng = random.Random(seed)
    world: dict[str, FactGraph] = {}
    for ui in range(n_users):
        uid = f"u{ui + 1}"
        facts: list[Fact] = []
        ts = 1.0
        idx = 0

        subj = rng.choice(_SUBJECTS)
        # 情绪 / 中性对(同主题不同谓词,内容相当)
        emo_pred = rng.choice(_PREDICATES)
        neut_pred = rng.choice(_PREDICATES)
        facts.append(_fact(uid, idx, ts, subj, emo_pred, arousal=0.8, valence=0.7)); idx += 1; ts += 1
        facts.append(_fact(uid, idx, ts, subj, neut_pred)); idx += 1; ts += 1

        # 自我 / 无关对
        subj2 = rng.choice(_SUBJECTS)
        self_pred = rng.choice(_PREDICATES)
        other_pred = rng.choice(_PREDICATES)
        facts.append(_fact(uid, idx, ts, subj2, self_pred, self_relevance=0.8)); idx += 1; ts += 1
        facts.append(_fact(uid, idx, ts, subj2, other_pred)); idx += 1; ts += 1

        # 矛盾对:旧 fact,然后新 fact supersedes 旧
        subj3 = rng.choice(_SUBJECTS)
        old_pred = rng.choice(_PREDICATES)
        new_pred = rng.choice(_PREDICATES)
        old = _fact(uid, idx, ts, subj3, old_pred); facts.append(old); idx += 1; ts += 1
        new = _fact(uid, idx, ts, subj3, new_pred, supersedes=old.fact_id); facts.append(new); idx += 1; ts += 1

        # 要义 / 细节
        subj4 = rng.choice(_SUBJECTS)
        sal_pred = rng.choice(_PREDICATES)
        det_pred = rng.choice(_PREDICATES)
        facts.append(_fact(uid, idx, ts, subj4, sal_pred, is_salient=True)); idx += 1; ts += 1
        facts.append(_fact(uid, idx, ts, subj4, det_pred, is_salient=False)); idx += 1; ts += 1

        world[uid] = FactGraph(user_id=uid, facts=facts)
    return world
