import json
import subprocess
import sys

def test_cli_smoke_run(tmp_path):
    out = tmp_path / "r.json"
    r = subprocess.run(
        [sys.executable, "run_benchmark.py",
         "--dataset", "datasets/smoke",
         "--adapter", "naive_dump",
         "--model", "fake",
         "--out", str(out)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "overall_auf" in data and "frontiers" in data
    assert data["dataset_version"] == "smoke"
