"""state-first 确定性生成:产出带生物权重标注的配对 fact,供各透镜探测。
每个角色生成 N_PAIR 条事实(统计稳定性:单条 0/1 二值太噪、需样本均值收敛)。
配对内两条事实共享同一 ts(确保 Ebbinghaus base 相同,使偏置恰好等于效应量)。
key_tokens 使用「全文+唯一 idx 后缀」以防止跨事实 token 污染(false positive)。"""
from __future__ import annotations
import random

from generator.schemas import (Fact, FactGraph,
    ROLE_EMOTIONAL, ROLE_EMOTIONAL_NEUTRAL,
    ROLE_SELF, ROLE_SELF_OTHER,
    ROLE_BELIEF_OLD, ROLE_BELIEF_NEW,
    ROLE_SALIENT, ROLE_DETAIL,
    ROLE_RECONSTRUCTION)

_SUBJECTS = ["项目周会", "客户来电", "快递送达", "系统告警", "午餐", "晨跑"]
_PREDICATES = ["推迟到下午", "确认了需求", "放在前台", "已自动恢复", "吃的拉面", "绕了公园"]

# 再构角色 fact 数据:core 要义 + detail 可漂移细节
# text 布局 = core_str + "--------"(8 ASCII 短横) + det_str + "_{k:03d}"
# 总长 20-21 字节,cut = int(len*0.6) = 12;core 在前 4 字节内,detail 从第 12 字节起
# 验证:core_str(4) + sep(8) = 12 == cut;det_str 起始 >= cut ✓
_CORE_R = [("周会", "推迟"), ("客户", "签约"), ("系统", "宕机"), ("报告", "提交")]
_DETAILS_R = [["下午", "三点"], ["周一", "上午"], ["机房", "十分钟"], ["邮件", "抄送"]]

# 每个角色的事实数:≥50 使保留率均值在 2σ 内收敛到目标概率,并确保偏置维度(情绪/自我/压缩)
# 在所有 seed 上均成为 bioFaithful 相对冷库的逐维天花板(N=5 方差过大、低至 0.0002 失效)
N_PAIR = 50


def _fact(uid: str, idx: int, ts: float, subj: str, pred: str, **kw) -> Fact:
    """构造一条 Fact。text 含唯一 idx 后缀,key_tokens 取全文——防止跨事实 token 串扰。"""
    text = f"{subj}{pred}_{idx:03d}"  # 含 3 位 idx 后缀确保全局唯一
    return Fact(
        fact_id=f"{uid}_f{idx}", ts=ts, text=text,
        key_tokens=[text],          # 完整文本作为唯一探针,无歧义
        **kw,
    )


def generate_world(seed: int = 0, n_users: int = 1) -> dict[str, FactGraph]:
    """每用户生成 N_PAIR 组配对 fact(情绪/中性、自我/无关、矛盾对、要义/细节)。
    同组配对共享 ts(base 相同 → 偏置恰等于效应量);四组分配不同 ts 时间槽。
    按 ts 升序(FactGraph.__post_init__ 负责排序)。"""
    rng = random.Random(seed)
    world: dict[str, FactGraph] = {}
    for ui in range(n_users):
        uid = f"u{ui + 1}"
        facts: list[Fact] = []
        idx = 0
        ts = 1.0  # 各组的基准时间槽

        # ── 情绪 / 中性配对(同 ts → base 相同 → 偏置 ≈ EMOTIONAL_ENHANCEMENT) ──
        for _ in range(N_PAIR):
            subj = rng.choice(_SUBJECTS)
            emo_pred = rng.choice(_PREDICATES)
            neut_pred = rng.choice(_PREDICATES)
            facts.append(_fact(uid, idx, ts, subj, emo_pred,
                               arousal=0.8, valence=0.7, role=ROLE_EMOTIONAL)); idx += 1
            facts.append(_fact(uid, idx, ts, subj, neut_pred,
                               role=ROLE_EMOTIONAL_NEUTRAL)); idx += 1
        ts += 1.0  # 下一组起始 ts

        # ── 自我 / 无关配对 ──
        for _ in range(N_PAIR):
            subj2 = rng.choice(_SUBJECTS)
            self_pred = rng.choice(_PREDICATES)
            other_pred = rng.choice(_PREDICATES)
            facts.append(_fact(uid, idx, ts, subj2, self_pred,
                               self_relevance=0.8, role=ROLE_SELF)); idx += 1
            facts.append(_fact(uid, idx, ts, subj2, other_pred,
                               role=ROLE_SELF_OTHER)); idx += 1
        ts += 1.0

        # ── 矛盾配对:旧 fact 先 supersede,再生成新 fact ──
        for _ in range(N_PAIR):
            subj3 = rng.choice(_SUBJECTS)
            old_pred = rng.choice(_PREDICATES)
            new_pred = rng.choice(_PREDICATES)
            old = _fact(uid, idx, ts, subj3, old_pred, role=ROLE_BELIEF_OLD)
            facts.append(old); idx += 1
            new_f = _fact(uid, idx, ts, subj3, new_pred,
                          supersedes=old.fact_id, role=ROLE_BELIEF_NEW)
            facts.append(new_f); idx += 1
        ts += 1.0

        # ── 要义 / 细节配对 ──
        for _ in range(N_PAIR):
            subj4 = rng.choice(_SUBJECTS)
            sal_pred = rng.choice(_PREDICATES)
            det_pred = rng.choice(_PREDICATES)
            facts.append(_fact(uid, idx, ts, subj4, sal_pred,
                               is_salient=True, role=ROLE_SALIENT)); idx += 1
            facts.append(_fact(uid, idx, ts, subj4, det_pred,
                               is_salient=False, role=ROLE_DETAIL)); idx += 1

        # ── 再构/再巩固角色:每个 fact 带要义(core)+ 可漂移细节(detail) ──
        # text = "{core_str}--------{det_str}_{k:03d}"
        # sep "--------"(8 个 ASCII -)保证 det 从第 12 字节起,cut=int(total*0.6)=12
        # → core tokens 恒在前 60%,detail tokens 恒在后 40%,满足 T5/T6 对齐约束
        ts += 1.0
        for k in range(N_PAIR):
            core = _CORE_R[k % len(_CORE_R)]
            det = _DETAILS_R[k % len(_DETAILS_R)]
            text = f"{core[0]}{core[1]}--------{''.join(det)}_{k:03d}"
            facts.append(Fact(
                fact_id=f"{uid}_recon{k}", ts=ts, text=text,
                key_tokens=[text],
                core_tokens=list(core),
                detail_tokens=det[:],
                role=ROLE_RECONSTRUCTION,
            ))
            ts += 1

        world[uid] = FactGraph(user_id=uid, facts=facts)
    return world
