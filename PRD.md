# PRD — Measuring the Impact of AI-Generated Video Ad Creatives

**Project codename:** `adlift`
**Owner:** _[your name]_
**Status:** Draft v1.0
**Build tool:** Claude Code (VS Code)
**Target audience for the finished project:** Hiring managers and interviewers for Business Data Scientist roles (Google Ads / YouTube Ads)

---

## 0. How to use this document (for Claude Code)

- This PRD is the source of truth. Put it in the repo root as `PRD.md`.
- Build **one phase at a time**, and within a phase **one milestone at a time**. After each milestone: run tests, run the relevant pipeline step, summarize what was built, and **stop for review** before moving on.
- All analysis logic lives in `src/adlift/` as tested, importable functions. Notebooks are **thin narrative layers** that call `src/` functions and display results.
- Every random process uses a seed from `config/sim_config.yaml`. Re-running the pipeline must reproduce identical numbers.
- Never read ground-truth files inside estimation code. Ground truth is only used in `validation` steps to score estimators.
- If a library version conflict appears (EconML / CausalML are sensitive), pin working versions in `pyproject.toml` and note it in `README.md`.

---

## 1. Summary

A fictional video ad platform, **StreamAds**, launches **"AutoCreative"**, a generative-AI tool that automatically produces video ad variants for advertisers. Leadership must decide whether to launch it globally.

This project simulates and analyzes the full measurement program behind that decision:

1. **Experiment design** — hypotheses, metrics, power analysis.
2. **Viewer-level A/B test** — do AI creatives outperform human creatives?
3. **Novelty & fatigue analysis** — is the lift durable or does it decay?
4. **Advertiser-level A/B test** — does access to the tool increase advertiser spend and retention?
5. **Uplift / heterogeneous treatment effects** — which viewers and advertisers benefit (simulated data + real Criteo data).
6. **Geo rollout analysis** — DiD, Synthetic Control, and CausalImpact for countries that launched without randomization.
7. **Revenue forecast** — 12-month incremental revenue of a global launch, with uncertainty.
8. **Automated dashboard** — Streamlit app regenerated from the pipeline.
9. **Auction interference** — why naive creative-split tests overstate lift, and better designs.
10. **Decision memo** — a clear, defended launch recommendation.

> **Transparency statement (must appear in README and reports):** StreamAds and AutoCreative are fictional. All platform data is simulated with known ground truth so that estimators can be validated. The uplift section additionally uses the real, public Criteo Uplift dataset, whose "treatment" is ad exposure (not AI creatives); it is analyzed as a separate ad-incrementality case study. No Google or YouTube data is used.

---

## 2. Goals & non-goals

### Goals
- Demonstrate rigorous **experimental design, A/B testing, causal inference, uplift modeling, regression/forecasting, and dashboarding** in one coherent business story.
- **Validate every estimator against ground truth** (simulated data) before applying methods to real data (Criteo).
- Produce artifacts a hiring manager can consume in < 5 minutes (README + decision memo + dashboard screenshots) and an interviewer can dig into for 45 minutes (technical report + code).

### Non-goals
- Not building a real ad server, real generative model, or production experimentation platform.
- Not modeling a fully realistic auction (Phase 3 uses a simplified auction purely to illustrate interference).
- Out of scope for v1: peeking / sequential testing, multi-armed bandits, brand-lift surveys (listed as future work).

---

## 3. Phased delivery plan

| Phase | Goal | Target | Scope |
|---|---|---|---|
| **Phase 1 — Apply-ready** | Complete, polished story: design → test → who benefits → decide | ~7–10 days | M0 setup, M1 simulator (viewer side), M2 experiment design doc, M3 viewer A/B test, M4 novelty/fatigue, M5 uplift (sim + Criteo), M6 decision memo v1, M7 README |
| **Phase 2 — Causal depth** | Non-randomized causal inference + forecasting | +1–2 weeks | M8 advertiser simulator + A/B (ITT & CACE), M9 geo rollout (DiD, SC, CausalImpact), M10 revenue forecast, memo v2 |
| **Phase 3 — Polish** | Dashboard + senior-level insight | +1–2 weeks | M11 Streamlit dashboard, M12 auction interference simulation & write-up, technical report final |

Phase 1 must stand on its own. The README always shows a **Roadmap** table with phase status.

---

## 4. Tech stack

- **Python 3.11**, managed with `uv` (or `pip` + `venv`), dependencies in `pyproject.toml`.
- Data: `pandas`, `numpy`, `pyarrow` (parquet), `polars` optional for Criteo.
- Stats: `scipy`, `statsmodels`.
- Uplift / HTE: `econml` (causal forest / DML), `causalml` (meta-learners), `scikit-uplift` (Qini/uplift curves, Criteo loader), `scikit-learn`, `lightgbm`.
- Causal (Phase 2): `linearmodels` or `statsmodels` (DiD with clustered SEs), `pysyncon` (synthetic control), `tfcausalimpact` (Python port of Google's CausalImpact).
- Forecast (Phase 2): `statsmodels` SARIMAX (primary), `prophet` (optional comparison).
- Viz: `matplotlib` + `seaborn` for static report figures; `plotly` for dashboard.
- Dashboard (Phase 3): `streamlit`.
- Quality: `pytest`, `ruff`, `pre-commit` (optional).
- Config: `pyyaml`.

---

## 5. Repository structure

```
adlift/
├── PRD.md
├── README.md
├── CLAUDE.md                     # short coding conventions for Claude Code
├── pyproject.toml
├── Makefile                      # make sim / make analyze / make report / make dashboard / make all
├── config/
│   ├── sim_config.yaml           # all simulation parameters + seeds
│   └── analysis_config.yaml      # alpha, power, MDE thresholds, cost assumptions
├── src/adlift/
│   ├── __init__.py
│   ├── simulate/
│   │   ├── viewers.py            # viewer population + viewer-level experiment
│   │   ├── advertisers.py        # (Phase 2) advertiser population + tool-access experiment
│   │   ├── geo.py                # (Phase 2) country-level weekly revenue panel
│   │   ├── auction.py            # (Phase 3) simplified auction for interference
│   │   └── ground_truth.py       # true effect functions tau(x, t)
│   ├── data/
│   │   ├── io.py                 # read/write parquet, paths
│   │   └── criteo.py             # download, downcast, sample Criteo Uplift
│   ├── stats/
│   │   ├── power.py              # sample size / MDE (binary & continuous, with CUPED)
│   │   ├── srm.py                # sample ratio mismatch chi-square test
│   │   ├── ab_test.py            # diff in means, Welch t, z-test props, Mann-Whitney
│   │   ├── cuped.py              # CUPED adjustment
│   │   ├── delta_method.py       # variance of ratio metrics (CTR etc.)
│   │   ├── bootstrap.py          # bootstrap CIs
│   │   └── multiple_testing.py   # Holm, Benjamini-Hochberg
│   ├── uplift/
│   │   ├── learners.py           # S-, T-, X-learner, causal forest wrappers
│   │   ├── evaluation.py         # Qini, uplift@k, AUUC, true-tau correlation (sim only)
│   │   └── policy.py             # targeting policy + expected profit by threshold
│   ├── causal/                   # (Phase 2)
│   │   ├── did.py                # 2x2 DiD, event study, clustered SEs
│   │   ├── synth.py              # synthetic control + placebo tests
│   │   ├── causal_impact.py      # CausalImpact wrapper
│   │   └── iv.py                 # ITT, CACE/LATE via 2SLS
│   ├── forecast/                 # (Phase 2)
│   │   ├── adoption.py           # adoption curve model
│   │   └── revenue.py            # baseline forecast + incremental revenue simulation
│   ├── validation/
│   │   └── recovery.py           # compare estimates vs ground truth, coverage
│   └── viz/
│       ├── style.py              # one consistent plot style
│       └── plots.py
├── pipelines/
│   ├── run_simulation.py
│   ├── run_phase1.py
│   ├── run_phase2.py
│   └── run_phase3.py
├── notebooks/
│   ├── 01_experiment_design.ipynb
│   ├── 02_viewer_ab_test.ipynb
│   ├── 03_novelty_fatigue.ipynb
│   ├── 04_uplift_simulated.ipynb
│   ├── 05_uplift_criteo.ipynb
│   ├── 06_advertiser_ab_test.ipynb      # Phase 2
│   ├── 07_geo_rollout.ipynb             # Phase 2
│   ├── 08_revenue_forecast.ipynb        # Phase 2
│   └── 09_auction_interference.ipynb    # Phase 3
├── reports/
│   ├── experiment_design.md
│   ├── decision_memo.md
│   ├── technical_report.md
│   ├── assumptions.md            # every simulation assumption + rationale
│   └── figures/
├── dashboard/
│   └── app.py                    # Phase 3
├── data/                         # gitignored
│   ├── raw/                      # Criteo download
│   ├── simulated/
│   └── ground_truth/             # NEVER read by estimation code
├── outputs/                      # result tables/JSON consumed by reports & dashboard
└── tests/
```

---

## 6. Business context & metrics

### 6.1 The decision
> "Should StreamAds launch AutoCreative to all advertisers globally, launch to specific segments only, or iterate further?"

### 6.2 Metric framework

**Viewer-side experiment (unit = viewer)**

| Type | Metric | Definition | Notes |
|---|---|---|---|
| **Primary** | Conversion rate | % of viewers with ≥1 conversion during the test | Binary per viewer; unit of randomization = unit of analysis |
| Secondary | CTR | clicks / impressions | Ratio metric → **delta method** |
| Secondary | View-through rate (VTR) | completed views / impressions | Ratio metric → delta method |
| Guardrail | Skip rate | skips / impressions | Must not increase by > configured threshold |
| Guardrail | Organic watch time per viewer | minutes of non-ad content watched | Protects viewer experience |
| Guardrail | Ad negative feedback rate | "hide ad"/report events per 1k impressions | Brand-safety proxy for AI content |

**Advertiser-side experiment (unit = advertiser) — Phase 2**

| Type | Metric | Definition |
|---|---|---|
| **Primary** | Weekly ad spend | Platform revenue per advertiser |
| Secondary | ROAS | advertiser-reported conversion value / spend |
| Secondary | Tool adoption | % of treated advertisers who used AutoCreative ≥1 time |
| Guardrail | Advertiser churn | % with zero spend in final 2 weeks |
| Guardrail | Creative policy-violation rate | % AI creatives flagged by review |

### 6.3 Practical significance & cost
`analysis_config.yaml` defines:
- `min_practical_lift_conversion` (e.g., +2% relative) — the smallest lift worth launching.
- `ai_cost_per_creative` and `ai_serving_cost_per_1k_impressions` (illustrative values, documented in `assumptions.md`).
- Decision rule: launch only if the **lower bound of the 95% CI** for incremental profit (incremental revenue − AI cost) is > 0, and guardrails pass.

---

## 7. Simulation specification

All defaults below are **illustrative and configurable**. Every value must appear in `config/sim_config.yaml` and be explained in `reports/assumptions.md`.

### 7.1 Viewer-level experiment (Phase 1)

**Population:** `n_viewers = 500_000` (configurable; must run on a laptop).

**Viewer features:**
| Feature | Type | Distribution (default) |
|---|---|---|
| `device` | cat | mobile 60%, desktop 25%, CTV (connected TV) 15% |
| `age_bucket` | cat | 18–24, 25–34, 35–44, 45–54, 55+ |
| `is_new_viewer` | bool | 20% new (account < 30 days) |
| `country` | cat | 30 countries, Zipf-like sizes |
| `content_affinity` | cat | gaming, music, education, lifestyle, news, sports |
| `pre_watch_minutes` | float | lognormal, 4-week pre-period |
| `pre_ad_clicks` | int | Poisson tied to engagement — **CUPED covariate** |
| `pre_converted` | bool | pre-period conversion flag — **CUPED covariate** |
| `ad_frequency` | float | expected ad impressions/week, depends on watch minutes |

**Assignment:** 50/50 random by `viewer_id` hash. Include an **optional SRM bug flag** (`inject_srm: false`) that, when true, drops a fraction of treatment viewers on one device to demonstrate SRM detection.

**Experiment length:** 4 weeks. Output is a **viewer-week panel** (`viewer_id, week, impressions, skips, completed_views, clicks, conversions, organic_minutes, negative_feedback`) plus a viewer-level summary table.

**Outcome model (per viewer-week):**
- `impressions ~ Poisson(ad_frequency)`
- `click ~ Binomial(impressions, p_click)` with `logit(p_click) = baseline(x) + tau_click(x, t, cum_freq) * treatment`
- `conversion` logistic on clicks + viewer propensity, with treatment effect flowing through clicks plus a small direct effect.
- `skips`, `completed_views` similarly, with AI creatives **slightly lower skip rate on mobile, slightly higher on CTV**.

**Ground truth (`simulate/ground_truth.py`):**
- **Heterogeneity:** `tau(x)` larger for mobile, ages 18–34, new viewers, gaming/lifestyle affinity; **near zero for desktop 45+**; **negative for CTV 55+** (so a "launch to segment" recommendation is meaningful).
- **Novelty decay:** `tau(x, t) = tau_inf(x) + (tau_0(x) − tau_inf(x)) * exp(−λ * (t − 1))`, defaults so that overall relative lift ≈ +6% in week 1 decaying toward ≈ +2.5% steady state.
- **Fatigue:** additional decay as cumulative exposures to the same creative increase (heavy viewers fatigue faster).
- Save per-viewer `true_tau_week{1..4}`, `true_tau_inf`, and the true population ATE per week and per segment to `data/ground_truth/`.

### 7.2 Advertiser-level experiment (Phase 2)

- `n_advertisers = 3_000`; features: `vertical` (gaming, retail, CPG, finance, travel, education, apps), `size_tier` (SMB 70%, mid 22%, enterprise 8%), `has_creative_team` (prob increases with size), `tenure_months`, `country`, `pre_spend_weekly` (heavy-tailed lognormal, 8-week pre-period).
- Random 50/50 assignment to **tool access**; 8-week test.
- **Non-compliance:** only some treated advertisers adopt (default overall ~40%; SMB without creative team ~55%; enterprise ~20%). Control cannot adopt.
- True effect on spend **only for adopters**: larger for SMB without creative team, small for enterprise.
- Outputs: advertiser-week panel (`spend`, `conversions_value`, `adopted`, `n_ai_creatives`, `policy_flags`, `active`).
- Ground truth: true ITT, true CACE (effect on adopters), per-segment effects.

### 7.3 Geo rollout panel (Phase 2)

- 30 countries × 156 weeks of weekly ad revenue.
- Components: country level, trend, yearly seasonality, holiday spikes, shared global shocks, noise.
- **Non-random launch:** at week 130, AutoCreative launches in 4 countries **selected because they had above-average recent growth** (so naive pre/post is biased upward).
- True effect: ramps from 0 to +3% revenue over 6 weeks, then flat. 26 post-weeks.
- One donor country gets an unrelated shock in the post-period (to show why donor screening/placebo tests matter).
- Ground truth: true weekly effect per launched country.

### 7.4 Auction (Phase 3)

- Simplified repeated auction: N advertisers' creatives compete for impression slots; rank by `bid × predicted_CTR`.
- AI creatives have higher predicted CTR → win more auctions → **take impressions from control creatives in the same auction** (SUTVA violation).
- Compare three estimates against the **true global-launch effect**: (a) naive creative-level split, (b) budget-split design, (c) cluster/market-level randomization.

### 7.5 Criteo Uplift (real data, Phase 1)

- Source: Criteo Uplift Prediction Dataset (Diemert et al., "A Large Scale Benchmark for Uplift Modeling", AdKDD 2018). Load via `scikit-uplift` (`sklift.datasets.fetch_criteo`) or the official Criteo AI Lab download. **Check and cite the license** in README.
- ~13.9M rows; features `f0`–`f11` (anonymized), `treatment`, `exposure`, `visit`, `conversion`. Treatment share is heavily imbalanced (~85% treated).
- `data/criteo.py` must: download once, cache as parquet, downcast to float32, and provide a **stratified sample** function (e.g., 10% / ~1.4M rows for model development; full data for ATE estimates if memory allows).
- Framing: "ad incrementality & targeting" — treatment = being eligible for ad targeting, not AI creatives.

---

## 8. Functional requirements by milestone

### Phase 1

#### M0 — Project setup
- Repo structure from §5, `pyproject.toml`, `Makefile`, `CLAUDE.md`, `.gitignore` (data/, outputs/ large files), `ruff` config, `pytest` passing on an empty test.
- `config/sim_config.yaml` and `config/analysis_config.yaml` with all parameters from §6–7.
- **Acceptance:** `make test` passes; `python -c "import adlift"` works.

#### M1 — Viewer simulator
- Implement §7.1 in `simulate/viewers.py` + `simulate/ground_truth.py`.
- `pipelines/run_simulation.py` writes parquet to `data/simulated/` and ground truth to `data/ground_truth/`.
- **Acceptance:**
  - Same seed → identical output (test).
  - Sanity table printed: baseline CTR, conversion rate, skip rate by device; values within configured ranges.
  - Assignment balance: covariate standardized mean differences < 0.02 (test).
  - Runtime < 2 min for 500k viewers.

#### M2 — Experiment design doc (`reports/experiment_design.md` + notebook 01)
- Hypotheses (H0/H1) for primary metric; metric table from §6.2; randomization unit and why.
- **Power analysis** (`stats/power.py`):
  - Required sample size for the primary metric at α = 0.05, power = 0.8, two-sided, given baseline rate and `min_practical_lift`.
  - Same with **CUPED** variance reduction (using estimated pre-period correlation) → show sample size savings.
  - MDE curve: MDE vs. sample size / test duration plot.
- Pre-registered decision rule and guardrail thresholds.
- Planned run length justified by power **and** by novelty concerns (≥ 4 weeks to see decay).
- Multiple-testing plan: Holm for secondary metrics.
- **Acceptance:** power functions unit-tested against `statsmodels` results; design doc reads like a real pre-registration.

#### M3 — Viewer A/B test analysis (notebook 02)
1. **SRM check** (chi-square) — pass/fail reported first.
2. **Assumption checks**, with explicit commentary:
   - Normality: show distribution, explain that with large N the **CLT** justifies a z/Welch test, and that Shapiro-Wilk is uninformative at this sample size.
   - Variance homogeneity: Levene test → justify **Welch** over Student t.
   - Heavy-tailed metrics (organic minutes): compare Welch vs. **Mann-Whitney** vs. **bootstrap CI**.
3. **Primary metric:** absolute and relative lift, 95% CI, p-value.
4. **CUPED:** re-estimate with pre-period covariate; report variance reduction % and CI width shrinkage.
5. **Ratio metrics (CTR, VTR, skip rate):** delta-method SEs; show the naive (wrong) SE vs. delta-method SE.
6. **Guardrails** with Holm correction.
7. **Practical significance:** compare CI to `min_practical_lift`; translate into incremental conversions & revenue.
8. **Segment cut** (pre-registered segments only: device, new vs. returning) with a forest plot; warn about multiple comparisons and Simpson's paradox.
9. **Ground-truth validation:** does the 95% CI cover the true ATE? Repeat simulation 200× (smaller N) to report **empirical coverage** of naive vs. CUPED CIs (`validation/recovery.py`).
- **Acceptance:** all numbers written to `outputs/viewer_ab_results.json`; coverage in [0.93, 0.97] for correct methods.

#### M4 — Novelty & fatigue (notebook 03)
- Treatment effect **by week** with CIs; plot week-over-week lift with true effect overlaid.
- Effect by **cumulative exposure bucket** (fatigue) — note this cut is post-treatment and explain the caveat.
- Fit decay model `tau_t = tau_inf + (tau_0 − tau_inf)·exp(−λ(t−1))` (nonlinear least squares) → estimate **steady-state lift** with CI.
- Compare: "naive 4-week average lift" vs. "steady-state lift" vs. truth.
- Business implication: forecasting/decisions should use steady-state lift; recommend creative refresh cadence.
- **Acceptance:** steady-state estimate's CI covers `true_tau_inf` population average; findings written to `outputs/novelty_results.json`.

#### M5 — Uplift modeling
**5a. Simulated data (notebook 04) — validate methods**
- Train S-, T-, X-learner (LightGBM base learners) and Causal Forest (EconML) on viewer features → predict `tau_hat(x)` (use steady-state week or full-period outcome; state choice).
- Honest train/test split; cross-fitting where supported.
- Evaluate: Qini curve, AUUC, uplift@top-k%, **and** correlation / RMSE between `tau_hat` and `true_tau` (only possible because of simulation).
- Interpretability: SHAP or feature importance of the CATE model; segment-level CATE table matching business segments.
- **Targeting policy** (`uplift/policy.py`): rank viewers by `tau_hat`; plot expected incremental profit vs. % targeted (include AI serving cost); identify optimal targeting fraction; compare to "treat all" and "treat none".

**5b. Criteo (notebook 05) — apply to real data**
- ATE on visit & conversion (difference in means with CIs); note treatment imbalance.
- Discuss `exposure` (ITT vs. exposed) — parallels non-compliance in Phase 2.
- Train the best 2 learners from 5a on Criteo sample; Qini/AUUC on held-out data; compare to random targeting.
- Clear caveat: anonymized features → segments can't be given business names; treatment ≠ AI creative.

- **Acceptance:** On simulated data, best learner achieves Spearman(`tau_hat`, `true_tau`) reported and Qini > random; on Criteo, Qini curve above random baseline on held-out data. Results to `outputs/uplift_results.json`.

#### M6 — Decision memo v1 (`reports/decision_memo.md`)
One page, written for a VP. Structure:
1. **Recommendation (first line):** e.g., "Launch AutoCreative to mobile and new-viewer inventory; hold on CTV pending creative fixes."
2. **Evidence:** 3–4 bullets with numbers + CIs (primary lift, steady-state vs. week-1, segment results, guardrails).
3. **Business impact:** incremental conversions & profit after AI costs (with range).
4. **Risks & caveats:** novelty decay, simulated-data caveat, CTV negative effect.
5. **Answers explicitly:** Roll out to all? Only a segment? Run longer or stop?
6. **Next steps:** follow-up experiment(s).
- Numbers must be pulled from `outputs/*.json` (generated by a small script) — no hand-typed results.

#### M7 — README (Phase 1 release)
- Title, one-paragraph story, **key results with 2–3 hero figures**, decision summary, transparency statement, methods list, how to reproduce (`make all`), repo map, roadmap table (Phase 2/3 status), skills demonstrated mapped to the job description.
- **Acceptance:** a reader understands the project and its recommendation in under 2 minutes.

### Phase 2

#### M8 — Advertiser A/B test (notebook 06)
- Simulator §7.2.
- SRM, balance check; power analysis showing why advertiser-level tests are **underpowered** (few units, heavy-tailed spend) → mitigations: CUPED on pre-spend, log transform / winsorizing (and how they change the estimand), stratified randomization by size tier.
- **ITT** (effect of offering the tool) and **CACE/LATE** (effect on adopters) via 2SLS with assignment as instrument; explain which one leadership needs and why.
- Spend uses Welch + bootstrap; ROAS via delta method; churn guardrail.
- Segment effects by size tier & creative team.
- Ground-truth validation of ITT and CACE.
- **Acceptance:** CIs cover true ITT and CACE; results to `outputs/advertiser_ab_results.json`.

#### M9 — Geo rollout (notebook 07)
- Simulator §7.3.
- **Naive pre/post** estimate → show bias vs. truth.
- **DiD** (treated vs. all controls), with **event-study plot** of leads/lags to assess parallel trends; country-clustered SEs.
- **Synthetic control** (`pysyncon`): donor weights table, pre-period fit (RMSPE), post-period gap plot; **placebo-in-space** (each donor as fake treated, RMSPE ratio ranking) and **placebo-in-time** tests; demonstrate impact of excluding the shocked donor.
- **CausalImpact**: donor countries as covariates; posterior cumulative effect with credible interval.
- **Comparison table:** naive / DiD / SC / CausalImpact vs. true effect, with intervals.
- Short discussion of staggered adoption (why TWFE can be biased; Callaway–Sant'Anna as extension).
- **Acceptance:** DiD/SC/CausalImpact estimates closer to truth than naive pre/post; results to `outputs/geo_results.json`.

#### M10 — Revenue forecast (notebook 08)
- **Baseline forecast:** SARIMAX on aggregate weekly revenue (holdout backtest: last 26 weeks; report MAPE; compare with seasonal-naive and optionally Prophet).
- **Adoption curve:** fit logistic adoption over time by size tier using advertiser-test data (regression).
- **Incremental revenue (12 months)** = baseline × adoption(t) × steady-state effect (from M4/M8, **not** week-1 lift) − AI costs.
- Uncertainty via Monte Carlo: sample effect sizes from their CIs, adoption parameters, forecast errors → P10/P50/P90 fan chart.
- Scenario table: launch to all vs. segment-only vs. no launch.
- **Acceptance:** backtest metrics reported; forecast intervals displayed; results to `outputs/forecast_results.json`.
- Update decision memo to **v2** with advertiser, geo, and forecast evidence.

### Phase 3

#### M11 — Automated dashboard (`dashboard/app.py`)
- Streamlit app reading only from `outputs/` (regenerated by `make all`, so it is "automated").
- Pages:
  1. **Executive summary** — recommendation, KPI tiles (lift, CI, incremental profit), guardrail status (pass/fail).
  2. **Experiment scorecard** — all metrics with lift, CI, p-value (adjusted), SRM status.
  3. **Novelty & fatigue** — weekly lift chart, steady-state estimate.
  4. **Uplift explorer** — select segment filters → CATE, Qini curve, targeting-fraction slider with profit curve.
  5. **Advertiser impact** — ITT vs. CACE, by size tier.
  6. **Geo rollout** — method selector (DiD / SC / CausalImpact) with gap plot.
  7. **Forecast** — fan chart and scenario comparison.
- **Acceptance:** `make dashboard` launches locally; screenshots added to README; optional deploy to Streamlit Community Cloud.

#### M12 — Auction interference (notebook 09 + section in technical report)
- Simulator §7.4.
- Show naive creative-split test **overstates** the global-launch effect due to cannibalization; quantify bias.
- Compare budget-split and cluster-randomized designs; discuss power trade-offs (fewer units).
- Recommendation for how StreamAds should run the *next* AutoCreative experiment.
- **Acceptance:** bias plot (estimate vs. truth by design) and a clear 1-paragraph takeaway.

#### Technical report final (`reports/technical_report.md`)
- Full methodology, assumptions, validation results (coverage, recovery), limitations, future work (sequential testing, bandits, brand lift, staggered DiD).

---

## 9. Non-functional requirements

- **Reproducibility:** `make all` regenerates everything from scratch with fixed seeds.
- **Performance:** full Phase 1 pipeline < 15 min on a laptop with 16 GB RAM (Criteo sampled).
- **Code quality:** type hints, docstrings on public functions, `ruff` clean, unit tests for all `stats/` and `uplift/evaluation.py` functions.
- **Separation:** estimation code never imports from `data/ground_truth/`; a test enforces this (grep-based).
- **Figures:** consistent style from `viz/style.py`; every figure has a title stating the takeaway, axis labels with units, and CIs where applicable. Saved to `reports/figures/` as PNG (300 dpi).
- **No hand-typed results:** reports pull numbers from `outputs/*.json`.

---

## 10. Key tests (minimum)

| Test | What it checks |
|---|---|
| `test_seed_reproducibility` | identical simulation output for same seed |
| `test_randomization_balance` | SMD < 0.02 on covariates |
| `test_srm_detects_injected_bug` | SRM test flags `inject_srm: true` |
| `test_power_matches_statsmodels` | sample-size function vs. statsmodels |
| `test_delta_method_vs_bootstrap` | delta-method SE ≈ bootstrap SE within tolerance |
| `test_cuped_reduces_variance` | CUPED variance < unadjusted variance |
| `test_ci_coverage` | repeated sims → coverage within [0.93, 0.97] |
| `test_qini_random_baseline` | random scores give Qini ≈ 0 |
| `test_no_ground_truth_leakage` | estimation modules don't reference ground_truth paths |
| `test_did_recovers_effect` (Phase 2) | DiD on clean sim recovers true effect |

---

## 11. Deliverables checklist

**Phase 1**
- [ ] Reproducible simulator with ground truth
- [ ] `reports/experiment_design.md`
- [ ] Notebooks 01–05
- [ ] `reports/decision_memo.md` v1
- [ ] `reports/assumptions.md`
- [ ] README with hero figures, transparency statement, roadmap

**Phase 2**
- [ ] Notebooks 06–08
- [ ] Decision memo v2

**Phase 3**
- [ ] Streamlit dashboard + screenshots
- [ ] Notebook 09
- [ ] Final technical report

---

## 12. Skills mapping (for README & resume)

| Job requirement | Project evidence |
|---|---|
| Statistical modeling | CUPED, delta method, bootstrap, decay model, 2SLS |
| Causal inference | Uplift/HTE, ITT vs. CACE, DiD, synthetic control, CausalImpact |
| A/B testing / experimental design | Power analysis, SRM, guardrails, multiple testing, novelty analysis, interference-aware designs |
| Regression for prediction & forecasting | Adoption curve regression, SARIMAX forecast with backtest, Monte Carlo revenue intervals |
| AI products | Measuring a generative-AI ads feature, including AI cost and AI-content guardrails |
| Dashboards & visualization (preferred) | Automated Streamlit dashboard driven by pipeline outputs |

**Draft resume bullets (fill in real numbers after build):**
- Designed and analyzed a simulated 500K-viewer A/B test of AI-generated video ad creatives; applied CUPED to cut variance by __% and delta-method inference for ratio metrics, with CI coverage validated against known ground truth.
- Identified novelty decay (week-1 lift __% → steady-state __%), preventing a __% overestimate in projected annual revenue.
- Built uplift models (X-learner, causal forest) on simulated data and the 13.9M-row Criteo dataset; a targeting policy improved incremental profit by __% vs. treat-all.
- Estimated the impact of a non-randomized geo launch using DiD, synthetic control, and CausalImpact; naive pre/post overstated impact by __%.
- Delivered an automated Streamlit dashboard and a one-page launch recommendation for leadership.

---

## 13. Risks & mitigations

| Risk | Mitigation |
|---|---|
| "Simulated data is circular" critique | Hybrid design: validate on sim, apply to real Criteo; document assumptions; include deliberate messiness (heavy tails, SRM bug, shocked donor, non-compliance) |
| EconML/CausalML install issues | Pin versions; fall back to own T-/X-learner implementations in `uplift/learners.py` |
| Criteo memory pressure | float32 downcast, parquet, stratified 10% sample for modeling |
| Scope creep delays applying | Phase gates; Phase 1 must be complete and polished before Phase 2 starts |
| Over-complex notebooks | Logic in `src/`, notebooks only narrate |

---

## 14. First prompt for Claude Code (copy-paste)

```
Read PRD.md in full. We are building Phase 1 only.
Start with Milestone M0 (project setup) exactly as specified in §5 and §8 M0:
create the repo structure, pyproject.toml (Python 3.11), Makefile, CLAUDE.md with
coding conventions from §0 and §9, .gitignore, config/sim_config.yaml and
config/analysis_config.yaml populated with every parameter in §6–§7 (Phase 1 values
active, Phase 2/3 values present but commented as future), and a passing pytest.
When done, run the tests, show me the tree and the configs, and STOP for my review
before starting M1.
```

Subsequent prompts: `"Proceed to M1 per PRD §7.1 and §8 M1. Stop for review when acceptance criteria pass."` — repeat per milestone.
