# tests/test_cli.py
import subprocess
import sys


def test_cli_runs_cold_storage():
    result = subprocess.run(
        [sys.executable, "run_benchmark.py", "--seed", "3", "--adapter", "cold"],
        capture_output=True, text=True, cwd=".",
    )
    assert result.returncode == 0, result.stderr
    assert "forgetting" in result.stdout.lower()


def test_cli_runs_bio_faithful():
    result = subprocess.run(
        [sys.executable, "run_benchmark.py", "--seed", "3", "--adapter", "bio_faithful"],
        capture_output=True, text=True, cwd=".",
    )
    assert result.returncode == 0, result.stderr
