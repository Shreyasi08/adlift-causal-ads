# CLAUDE.md — adlift conventions

`PRD.md` is the source of truth. Build one phase at a time, one milestone at a time; after each milestone run tests + the relevant pipeline step, summarize, and STOP for review.

## Conventions
- All analysis logic lives in `src/adlift/` as typed, tested, importable functions. Notebooks are thin narrative layers.
- Python 3.11, managed with `uv` (`make setup`). Type hints and docstrings on public functions. `ruff` clean.
- Every random process takes a seed from `config/sim_config.yaml` (use `numpy.random.default_rng`). Same seed => identical numbers.
- Estimation code must NEVER read `data/ground_truth/` (enforced by `tests/test_no_ground_truth_leakage.py`). Ground truth is used only in `validation/` and the simulators.
- No hand-typed results: reports/dashboard read numbers from `outputs/*.json`.
- Figures: use `viz/style.py`; title states the takeaway, labeled axes with units, CIs where applicable, PNG 300 dpi into `reports/figures/`.
- Unit tests for all `stats/` functions and `uplift/evaluation.py`.
- If EconML/CausalML version conflicts appear, pin working versions in `pyproject.toml` and note it in README.
- StreamAds/AutoCreative are fictional; keep the transparency statement in README and reports.
