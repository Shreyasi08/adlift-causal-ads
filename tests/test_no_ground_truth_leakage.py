"""Estimation code must not reference ground-truth data (PRD §9)."""

from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "adlift"
ALLOWED = {"simulate", "validation"}  # simulators write truth; validation scores against it


def test_no_ground_truth_leakage() -> None:
    offenders = []
    for py in SRC.rglob("*.py"):
        if py.relative_to(SRC).parts[0] in ALLOWED:
            continue
        if "ground_truth" in py.read_text():
            offenders.append(str(py.relative_to(SRC)))
    assert not offenders, f"ground_truth referenced in estimation code: {offenders}"
