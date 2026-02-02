from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.main import main  # noqa: E402


def test_smoke() -> None:
    exit_code = main(["--name", "Test", "--count", "2", "--quiet"])
    assert exit_code == 0
