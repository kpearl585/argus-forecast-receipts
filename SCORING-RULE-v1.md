# Weekly Ukraine front forecast: pre-registered scoring rule v1

Status: PRE-REGISTRATION DRAFT, written 2026-10-12, before the first confirmed forecast (mdo-front-2026-10-11) resolves on 2026-10-18. It takes effect when the owner approves it in writing. Its sha256 is recorded in the forecast log and published with the forecast hashes. Author: Claude (program owner by delegation). Linear: ARG-1389.

This rule fixes **what counts, how it is scored, and what would count as success, before the outcomes are known.** It changes no code. Everything below is what `etl/ace/mdo_front_forecast.py` already computes.

## 1. What is forecast
- **Unit.** Each 20 km front cell on the issue-date DeepStateMap (DSM) map; 176 cells in the current cycle.
- **Event.** Any Russian gain of at least 0.05 km² in the cell between the issue map and the map 7 days later (`GAIN_FLOOR = 0.05`, `HORIZON = 7`).
- **Models.**
  - **G** (ground state only) is the **pre-specified primary model**.
  - **M** (ground plus event reports) is a logged alternative.
  - **GE** is governed by its own pre-registration (`docs/models/MDO-GE-PROSPECTIVE-PREREG-v1.md`).
  - The primary was fixed before any confirmed week was scored. M's better single-week result on 2026-10-02 does not change it.

## 2. What counts as a scored week
- **A week counts only if `real_forecast: true`:**
  - the forecast file is committed before its resolution map exists;
  - a confirmer who is not the operator writes a write-once confirmation;
  - the hash matches;
  - the first commit is before 03:00 UTC on the resolution date (existing protocol, `MDO-FRONT-WEEKLY-RUNBOOK.md`).
- **Every issued week stays in the log, including misses.** A missed cycle is logged as missed and never backfilled or backdated. A forecast that fails confirmation stays in the log as `real_forecast: false`, and is excluded from the success test, with the reason stated.
- **No model changes between weeks** beyond the pre-specified weekly refit on completed windows. Any change to features, model form, cells or event definition creates a new version (v2), which **restarts the week count**.

## 3. Scores (fixed in code since 2026-10-02)
For each scored week, per model:
- Brier;
- log loss (probabilities clipped to [1e-6, 1 − 1e-6]);
- AUC (when there is at least one positive and one negative cell);
- top-10 hits.

**Baseline:** climatology. Each forecast's training base rate is applied to every cell, and its Brier is recorded.

## 4. Success rule (decided now, applied later)
- **When it is applied.** After the first **8 confirmed scored weeks** of G under this version.
- **Skill is claimed for G only if:**
  - the mean over weeks of (climatology Brier − G Brier) is greater than 0, **and**
  - a **week-blocked bootstrap** 95% interval of that mean difference (2,000 replicates, seed 20261012, resampling whole weeks) lies **entirely above 0**.
- **Otherwise** the result is reported as "no demonstrated skill over climatology", in the same place and format as a success would have been.
- **M** is reported with the same statistic as a secondary result. It cannot replace G as primary without a new pre-registration.
- **Before 8 weeks,** single-week scores are reported as "N weeks; not evidence of skill".

## 5. What is published, and what is not
This section takes effect only with owner approval of publication.
- **Published:**
  - per forecast: `forecast_id`, sha256, issue and resolution map dates;
  - per resolution: the scores in §3 and `real_forecast`;
  - this rule's sha256.
- **Not published:** DSM or VIINA bytes, polygons, or per-cell inputs. Per-cell probabilities only if the owner's licence ruling allows it.
- **Labels.** Every published number carries "research model; uncalibrated against a public benchmark; N weeks scored".

## 6. Limits
- DSM is a single open source, and its map dates and publication timing drive both issue and resolution.
- Gains below 0.05 km² are treated as no gain.
- One week is a small, autocorrelated sample. Eight weeks is a minimum to test against, not a guarantee of power.
EOF
cd ~/dev/abdb-scoring-rule && f=docs/models/forecasts/MDO-FRONT-PUBLIC-SCORING-RULE-v1.md && shasum -a 256 $f