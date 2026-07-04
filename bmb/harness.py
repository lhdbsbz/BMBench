"""编排 + 自检硬门:naive 与 oracle 必须把恢复率标尺两端钉死,否则结果作废。"""
from __future__ import annotations
from collections import defaultdict

from bmb.contract import ProblemFamily
from bmb.dataset import LoadedDataset
from bmb.measurement import Frontier, aggregate_family, area_under_frontier, has_signal, recovery_ratio
from bmb.models import FixedModel, count_tokens
from bmb.scoring import answer, score

BUDGETS = [8192, 32768, 65536, 131072]


class SelfCheckError(RuntimeError):
    """naive 未在低端 / oracle 未在天花板,结果不可信。"""


def _enforce_budget(payload: str, budget_tokens: int) -> str:
    """硬截断载荷到 ≤budget(默认策略:截断+记录)。"""
    while payload and count_tokens(payload) > budget_tokens:
        payload = payload[:-1]
    return payload


def _ingest_all(adapter, ds: LoadedDataset) -> None:
    for uid, events in ds.events_by_user.items():
        for e in events:
            adapter.ingest(e.user_id, e.timestamp, e.text)


def measure_adapter(adapter, ds: LoadedDataset, model: FixedModel,
                    budgets: list | None = None, judge_k: int = 5) -> dict[ProblemFamily, Frontier]:
    budgets = budgets or BUDGETS
    _ingest_all(adapter, ds)
    # 地板(空载荷)与天花板(真相态)与 B 无关——每探针在预算循环外算一次;
    # 零信号探针整探针跳过(所有预算都不计)。预算循环内只重算依赖 B 的 s_arch。
    grouped: dict[tuple[ProblemFamily, int], list[float]] = defaultdict(list)
    for p in ds.probes:
        state = ds.states_by_user[p.user_id]
        s_floor = score(model, p.family, answer(model, p.query, ""), p.answer_spec, judge_k)
        s_ceil  = score(model, p.family, answer(model, p.query, state.text), p.answer_spec, judge_k)
        if not has_signal(s_ceil, s_floor):
            continue
        for B in budgets:
            payload = _enforce_budget(adapter.assemble(p.user_id, p.query, B), B)
            s_arch = score(model, p.family, answer(model, p.query, payload), p.answer_spec, judge_k)
            grouped[(p.family, B)].append(recovery_ratio(s_arch, s_floor))
    frontiers: dict[ProblemFamily, Frontier] = {}
    for (family, B), recs in grouped.items():
        fr = frontiers.setdefault(family, Frontier(family))
        fr.points.append((B, aggregate_family(recs)))
    for fr in frontiers.values():
        fr.points.sort()
    return frontiers


def _overall_auf(frontiers: dict[ProblemFamily, Frontier], all_families: set[ProblemFamily]) -> float:
    # 诚实化:按数据集中出现的全部 family 取均值;无存活点的 family 记 0.0(不静默丢难题族)。
    if not all_families:
        return 0.0
    aufs = []
    for f in all_families:
        fr = frontiers.get(f)
        if fr and fr.points:
            aufs.append(area_under_frontier(fr.points))
        else:
            aufs.append(0.0)
    return sum(aufs) / len(aufs)


def self_check(ds: LoadedDataset, model: FixedModel, budgets: list | None = None, judge_k: int = 5) -> None:
    budgets = budgets or BUDGETS
    from bmb.adapters.naive_dump import NaiveDumpAdapter
    from bmb.adapters.oracle import OracleAdapter
    oracle = OracleAdapter({uid: s.text for uid, s in ds.states_by_user.items()})
    naive = NaiveDumpAdapter()
    all_families = {p.family for p in ds.probes}
    o_fr = measure_adapter(oracle, ds, model, budgets, judge_k)
    n_fr = measure_adapter(naive, ds, model, budgets, judge_k)
    o_auf = _overall_auf(o_fr, all_families)
    n_auf = _overall_auf(n_fr, all_families)
    if not (o_auf > n_auf):
        raise SelfCheckError(
            f"自检失败:oracle AUF={o_auf:.3f} 未高于 naive AUF={n_auf:.3f};测量不可信,结果作废。"
        )


def run_benchmark(adapter, ds: LoadedDataset, model: FixedModel,
                  budgets: list | None = None, judge_k: int = 5) -> dict:
    budgets = budgets or BUDGETS
    self_check(ds, model, budgets, judge_k)  # 硬门
    frontiers = measure_adapter(adapter, ds, model, budgets, judge_k)
    all_families = {p.family for p in ds.probes}
    no_signal_families = [f.value for f in all_families if f not in frontiers or not frontiers[f].points]
    return {
        "frontiers": {f.value: {"points": fr.points} for f, fr in frontiers.items()},
        "overall_auf": _overall_auf(frontiers, all_families),
        "no_signal_families": no_signal_families,
        "budgets": list(budgets),
        "dataset_version": ds.manifest.get("version"),
    }
