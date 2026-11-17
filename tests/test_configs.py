from pathlib import Path

import yaml

CFG = Path(__file__).resolve().parents[1] / "config"


def test_configs_load() -> None:
    sim = yaml.safe_load((CFG / "sim_config.yaml").read_text())
    ana = yaml.safe_load((CFG / "analysis_config.yaml").read_text())
    assert sim["viewers"]["n_viewers"] == 500_000
    assert sim["viewers"]["inject_srm"] is False
    assert ana["alpha"] == 0.05
    assert ana["min_practical_lift_conversion"] == 0.02
