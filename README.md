# adlift — Measuring the Impact of AI-Generated Video Ad Creatives

> **Transparency:** StreamAds and AutoCreative are fictional. All platform data is simulated with known ground truth so estimators can be validated. The uplift section also uses the public Criteo Uplift dataset, whose "treatment" is ad exposure (not AI creatives). No Google or YouTube data is used.

Status: **Phase 1, M0 (project setup) complete.** See `PRD.md` for the full plan.

## Setup
```
make setup   # uv sync --all-extras (Python 3.11)
make test
```

## Roadmap
| Phase | Scope | Status |
|---|---|---|
| 1 — Apply-ready | M0–M7 | M0 done |
| 2 — Causal depth | M8–M10 | not started |
| 3 — Polish | M11–M12 | not started |
