"""加载冻结数据集:users/*.jsonl + ground_truth.json + manifest.json → 内存对象。"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path

from bmb.contract import AnswerSpec, ExperienceEvent, GroundTruthState, ProblemFamily, Probe


@dataclass
class LoadedDataset:
    events_by_user: dict[str, list[ExperienceEvent]] = field(default_factory=dict)
    probes: list[Probe] = field(default_factory=list)
    states_by_user: dict[str, GroundTruthState] = field(default_factory=dict)
    manifest: dict = field(default_factory=dict)


def load_dataset(path: str) -> LoadedDataset:
    root = Path(path)
    ds = LoadedDataset()
    for jp in sorted((root / "users").glob("*.jsonl")):
        with jp.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                o = json.loads(line)
                e = ExperienceEvent(o["user_id"], o["timestamp"], o["text"])
                ds.events_by_user.setdefault(e.user_id, []).append(e)
    gt = json.loads((root / "ground_truth.json").read_text(encoding="utf-8"))
    for p in gt["probes"]:
        a = p["answer_spec"]
        ds.probes.append(Probe(
            p["probe_id"], p["user_id"], ProblemFamily(p["family"]), p["query"],
            AnswerSpec(a.get("accept_patterns", []), a.get("reject_patterns", []), a.get("judge_rubric")),
        ))
    for s in gt["states"]:
        st = GroundTruthState(s["user_id"], s["text"])
        ds.states_by_user[st.user_id] = st
    ds.manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    return ds
