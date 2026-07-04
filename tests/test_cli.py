# tests/test_cli.py
import subprocess
import sys


def test_cli_runs_cold_storage():
    result = subprocess.run(
        [sys.executable, "run_benchmark.py", "--seed", "1", "--adapter", "cold"],
        capture_output=True, text=True, cwd=".",
    )
    assert result.returncode == 0, result.stderr
    assert "forgetting" in result.stdout.lower()


def test_cli_runs_bio_faithful():
    result = subprocess.run(
        [sys.executable, "run_benchmark.py", "--seed", "1", "--adapter", "bio_faithful"],
        capture_output=True, text=True, cwd=".",
    )
    assert result.returncode == 0, result.stderr


def test_cli_outputs_five_dimensions():
    import json
    result = subprocess.run(
        [sys.executable, "run_benchmark.py", "--seed", "1", "--adapter", "cold"],
        capture_output=True, text=True, cwd=".",
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    keys = set(data["perDimension"].keys())
    assert {"forgetting", "emotional", "selfReference", "compression", "beliefUpdate"} <= keys
