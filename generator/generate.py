"""state-first 生成管线:作者相(seeded)→ 渲染(LLM temp=0)→ 派生探针 → 冻结。"""
from __future__ import annotations
import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from bmb.contract import ExperienceEvent, Probe, GroundTruthState
from bmb.models import FixedModel
from generator.schemas import (
    UserTruth, SalientFact, StateVariable, LatentProfile,
    derive_probes, build_ground_truth_state,
)
from generator.noise import make_noise


@dataclass
class FrozenDataset:
    events: list[ExperienceEvent] = field(default_factory=list)
    probes: list[Probe] = field(default_factory=list)
    states: list[GroundTruthState] = field(default_factory=list)
    manifest: dict = field(default_factory=dict)


def author_truth(user_id: str, seed: int, config: dict) -> UserTruth:
    rng = random.Random(seed)
    salient_pool = config.get("salient_pool", [])
    state_pool = config.get("state_pool", [])
    profile_pool = config.get("profile_pool", [])
    salient = [SalientFact(*s) for s in rng.sample(salient_pool, k=min(1, len(salient_pool)))] if salient_pool else []
    states = [StateVariable(*s) for s in state_pool] if state_pool else []
    profiles = [LatentProfile(*p) for p in profile_pool] if profile_pool else []
    return UserTruth(user_id, config["span_days"], salient, states, profiles)


def render_events(truth: UserTruth, noise_events: list[str], model: FixedModel,
                  seed: int) -> list[ExperienceEvent]:
    """逐事件用固定模型渲染成自然文本(temp=0)。真相项 + 噪音混合后按天铺开。"""
    rng = random.Random(seed + 1)
    base = datetime(2026, 1, 1)
    items: list[tuple[int, str]] = []
    for f in truth.salient:
        day = rng.randint(0, max(1, truth.span_days - 1))
        items.append((day, f.text))
    for s in truth.states:
        for day, val in s.timeline:
            items.append((min(day, truth.span_days - 1), f"{s.name}变为:{val}"))
    for p in truth.profiles:
        for ev in p.evidence:
            day = rng.randint(0, max(1, truth.span_days - 1))
            items.append((day, ev))
    by_day: dict[int, list[str]] = {}
    for day, raw in items:
        by_day.setdefault(day, []).append(raw)
    events: list[ExperienceEvent] = []
    noise_iter = iter(noise_events)
    for day in range(truth.span_days):
        ts = (base + timedelta(days=day)).isoformat()
        for raw in by_day.get(day, []):
            rendered = model.generate(f"把这句经历改写成自然口语独白,只输出改写结果:\n{raw}", temperature=0.0, seed=seed)
            events.append(ExperienceEvent(truth.user_id, ts, rendered.strip()))
        try:
            nw = next(noise_iter)
            events.append(ExperienceEvent(truth.user_id, ts, nw))
        except StopIteration:
            pass
    return events


def generate_dataset(config: dict, model: FixedModel, seed: int, n_users: int) -> FrozenDataset:
    events: list[ExperienceEvent] = []
    probes: list[Probe] = []
    states: list[GroundTruthState] = []
    for i in range(n_users):
        uid = f"u{i+1}"
        truth = author_truth(uid, seed * 1000 + i, config)
        noise = make_noise(random.Random(seed * 100 + i), config.get("noise_per_user", 10))
        events += render_events(truth, noise, model, seed * 100 + i)
        probes += derive_probes(truth)
        states.append(build_ground_truth_state(truth))
    manifest = {"version": config.get("version", "dev"), "seed": seed,
                "n_users": n_users, "span_days": config["span_days"]}
    return FrozenDataset(events, probes, states, manifest)


def save_dataset(ds: FrozenDataset, path: str) -> None:
    root = Path(path)
    (root / "users").mkdir(parents=True, exist_ok=True)
    by_user: dict[str, list[ExperienceEvent]] = {}
    for e in ds.events:
        by_user.setdefault(e.user_id, []).append(e)
    for uid, evs in by_user.items():
        with (root / "users" / f"{uid}.jsonl").open("w", encoding="utf-8") as f:
            for e in evs:
                f.write(json.dumps({"user_id": e.user_id, "timestamp": e.timestamp, "text": e.text}, ensure_ascii=False) + "\n")
    gt = {
        "probes": [
            {"probe_id": p.probe_id, "user_id": p.user_id, "family": p.family.value,
             "query": p.query,
             "answer_spec": {"accept_patterns": p.answer_spec.accept_patterns,
                             "reject_patterns": p.answer_spec.reject_patterns,
                             "judge_rubric": p.answer_spec.judge_rubric}}
            for p in ds.probes
        ],
        "states": [{"user_id": s.user_id, "text": s.text} for s in ds.states],
    }
    (root / "ground_truth.json").write_text(json.dumps(gt, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps(ds.manifest, ensure_ascii=False, indent=2), encoding="utf-8")
