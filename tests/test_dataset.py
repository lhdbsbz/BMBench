from pathlib import Path
from bmb.dataset import load_dataset

SMOKE = Path("datasets/smoke")

def test_load_smoke_roundtrip():
    ds = load_dataset(str(SMOKE))
    assert ds.manifest["version"] == "smoke"
    assert len(ds.probes) >= 3 * 3
    # 某用户有事件
    any_uid = next(iter(ds.events_by_user))
    assert len(ds.events_by_user[any_uid]) > 0
    # states 可按 user 取
    assert any_uid in ds.states_by_user

def test_probes_typed():
    from bmb.contract import ProblemFamily
    ds = load_dataset(str(SMOKE))
    p = ds.probes[0]
    assert isinstance(p.family, ProblemFamily)
