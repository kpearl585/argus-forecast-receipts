# Weekly Ukraine front ADVANCE-MAGNITUDE forecast: pre-registered scoring rule (advance v1)

Status: **APPROVED 2026-10-12 by the owner** (16:42 EDT; approval record at the end of this file). The first counted advance issue is Sun 2026-10-25.
- Written 2026-10-12 and finalized the same day, after the single pre-declared improvement pass (ledger at the end).
- The owner approved building this forecast in-session at 15:56 EDT that day, as the time-sealed blind test for advance. At about 16:31 EDT the owner chose one improvement pass, with the rule to be locked before the Sun 2026-10-25 issue.
- This file is the approved artifact. Its sha256 cannot appear inside the file itself, because adding it would change the hash; it is recorded in `MDO-FRONT-WEEKLY-RUNBOOK.md` and the forecast log.
- The earlier draft, sha256 `4fca21e2…a706`, was never approved and is superseded.
- No advance week before 2026-10-25 counts.
- Author: Claude (program owner by delegation). Linear: ARG-1402.

This rule sits beside public scoring rule v1 (`MDO-FRONT-PUBLIC-SCORING-RULE-v1.md` with Addendum 1) and changes nothing in it. The v1 G forecast, its payload, its hash and its verdict stay exactly as they are.

## 1. What is forecast
- **Unit.** Each 20 km front cell of that week's issued v1 forecast (`mdo-front-<map date>`): same cells, same issue map, and the resolution map exactly 7 days later.
- **Quantity.** The Russian territorial gain in km² in the cell between the issue map and the resolution map.
  - It is measured with the v1 resolution geometry (`etl.ace.mdo_front_forecast.cell_gains`, DeepStateMap polygons).
  - A gain below 0.05 km² is set to 0, because v1 treats it as no gain. A cell with no measured gain counts as 0.
- **Output.** Each model gives a predictive distribution as 19 quantiles, τ = 0.05, 0.10, …, 0.95, which include 0.1, 0.5 and 0.9. The point forecast is the predictive median (q0.5).

## 2. Models (code `etl/ace/mdo_front_adv.py`)
- **AB (primary).** AB is the hurdle model A blended with the climatology CLIM by quantile averaging: q_AB(τ) = w·q_A(τ) + (1 − w)·q_CLIM(τ).
  - **How w is chosen at each issue.** w comes from the grid {0, 0.1, …, 1.0}. It is the value that minimizes mean weekly grid-CRPS (km², §3) of the blend over the most recent 26 past origins whose outcome map is on or before the issue map.
  - **How the past origins are built.** Each past origin is rebuilt with no lookahead: G and the magnitude ridge are refit on windows ending at that origin, using maps up to that origin only.
  - **Edge cases.** Ties go to the larger w. With fewer than 8 past origins, w = 0.5.
  - **What is sealed.** w and the number of past origins are recorded in the forecast's `models.AB`, and the blended quantiles are sealed in `cells`.
  - **Where this came from.** AB was chosen by the declared improvement pass (ledger).
- **A (component, logged).** A hurdle model.
  - P(gain) is the v1 G probability, read from the sealed v1 forecast file. A refuses if that file's hash does not verify. G is never refit for the issued A.
  - The magnitude, given a gain, is lognormal. The mean of ln(km²) comes from a ridge on G's 9 features (`RidgeCV`, alphas 0.1/1/10/100, `GroupKFold(5)` by cell, standardized), fit on the gaining rows of exactly G's training windows. The spread is the pooled residual standard deviation.
  - The quantile at τ is 0 if τ ≤ 1 − p. Otherwise it is max(0.05, exp(μ + σ·Φ⁻¹((τ − (1 − p))/p))).
- **CLIM (baseline).** Per-cell climatology: the empirical quantiles (numpy, linear) of the cell's floored gain over the 12 weekly windows ending at the issue map. Window anchors are the nearest map on or before issue − 7k, as v1 uses.
- **PERS (baseline).** Persistence: the cell's floored gain over the 7-day window ending at the issue map, as a point mass.
- **ZERO (baseline).** Every quantile is 0.
- **Sealing.** AB, A, CLIM and PERS are sealed in one `cells` payload under one four-key hash. ZERO is implied.
- **No changes between weeks** beyond the weekly refit on completed windows and the weekly recomputation of w by the fixed procedure above. Any other change to features, model form, grid, blend procedure, baselines, cells or target creates advance v2, which **restarts the week count**.

## 3. Score
- **Primary: grid CRPS in km².** Per cell, CRPS = 2 × the mean over the 19 levels of the pinball loss ρ_τ(y, q_τ), where ρ_τ(y, q) = (y − q)(τ − 1{y < q}). The weekly score is the mean over cells.
- **Why not pinball over only q0.1/q0.5/q0.9.** About 94% of cell-weeks have no gain, so q0.1 and q0.5 are 0 for nearly every model in nearly every cell. A 3-quantile average would in effect score q0.9 alone.
- **Why the 19-level grid.**
  - It is a proper score for the quantiles it publishes.
  - It approximates CRPS with no interpolation or tail assumption.
  - Anyone can recompute it from the reveal.
  - For a point forecast it equals |y − x| exactly, so ZERO scores the mean gain.
- **Why km².** km² is the unit of the stated target. The log1p-scale grid CRPS is logged but decides nothing.
- **Secondary: MAE of log1p(q0.5) against log1p(y).** The median is the optimal point forecast for this loss.

## 4. What counts as a scored week
- **A week counts under the same protocol as v1.** The advance forecast file `mdo-front-adv-<map date>.json`:
  - is committed before its resolution map exists, with its first commit before 03:00 UTC on the resolution date;
  - has a four-key hash that verifies;
  - is confirmed by a confirmer who is not the operator, in a write-once confirmation from `etl.ace.mdo_front_forecast confirm`. The resolution then records `real_forecast: true`.
- **The v1 G forecast it builds on** must be the canonical issued v1 file for that map date.
- **Missed weeks** are logged as missed, never backfilled. A failed confirmation stays in the log, uncounted, with the reason given.

## 5. Decision rule (decided now, applied later)
- **When it is applied.** After the first **K = 26 counted weeks**, by `issued_for_map_date`.
- **Per week and baseline B ∈ {CLIM, PERS}:** d_w(B) = CRPS(B) − CRPS(AB). Values are used exactly as recorded in the resolution.
- **Bootstrap (Addendum 1 method).** Each comparison uses a fresh `numpy.random.default_rng(20261012)` with 2,000 replicates. Each replicate draws 26 week indices with `rng.integers(0, 26, size=26)` and takes the mean. The interval is `numpy.percentile(means, [2.5, 97.5])`.
- **Skill claim.** "advance skill over climatology and persistence demonstrated (advance rule v1)" only if, for **both** CLIM and PERS, the mean of d is greater than 0 **and** the lower bound is greater than 0.
- **Otherwise:** "**no demonstrated skill** (advance rule v1)", reported in the same place and format as a success would have been.
- **Reported beside the verdict, deciding nothing:** A, ZERO and the secondary MAE.
- **Before 26 weeks:** "N advance weeks counted; not evidence of skill".
- **Reference implementation:** `etl/ace/mdo_front_adv_verdict.py`. It writes nothing before 26 counted weeks. The verdict is computed only by that script.

## 6. Why K = 26 (power of AB on exposed history)
- **Method.** Slide every contiguous K-week window over the 87-week series (§7), apply §5 exactly, and count the share of windows that pass against both baselines. Contiguous windows are used because weeks are autocorrelated.

  | K | 8 | 12 | 16 | 20 | 26 | 30 | 40 |
  |---|---|---|---|---|---|---|---|
  | pooled power, 87 weeks | 0.49 | 0.59 | 0.65 | 0.69 | 0.76 | 0.79 | 0.96 |
  | power inside 2026 only | 0.03 | 0.03 | 0.00 | 0.00 | 0.00 | — | — |

- **What limits power.** Power is limited by CLIM. Against PERS, AB passes in every window.
- **K = 26, set by the owner on 2026-10-12** when approving this rule, before any outcome existed. The draft had proposed 16.
  - Full-backtest power at K = 26 is **0.76**.
  - Power inside the 2026 regime is **about 0**.
  - The first verdict comes after 26 counted weeks, about six months after the first counted issue on 2026-10-25, so around April 2027.
- **Honest expectation.** Inside the 2026 regime, power is close to 0 at every K. Over the 40 weeks of 2026, AB vs CLIM is +0.0044 km², with 95% CI [−0.0014, +0.0114].
- **If that regime persists,** the most likely outcome of this rule is "no demonstrated skill", even though AB beats persistence and zero by wide margins. That outcome would be published exactly as written.

## 7. Exposed-history results (EXPOSED HISTORY, NOT BLIND)
- **Inputs.**
  - DSM daily maps 2024-07-08 to 2026-10-11: the 2026-10-11 cycle inventory, `SHA256SUMS-daily` sha256 `362288eb…0d105`.
  - Sector-weeks `d3fde87c…023e2`.
  - KATOTTH tessellation and GeoNames places as pinned in the runbook.
- **Origins.** Rolling, with no lookahead: weekly Sundays, 2025-02-09 to 2026-10-04, 87 scored weeks.
  - An origin was skipped only when it had fewer than 26 training windows.
  - G and the magnitude ridge are refit at each origin on windows ending on or before the origin.
  - Features and baselines use maps on or before the origin, and the outcome uses the exact map 7 days later.
- **Deviation from live.** Live G drops the last window or two past the VIINA events lag. The backtest does not, because G uses no event features.
- **Aggregate files.** `mdo-front-adv-backtest-v1.json` (first backtest: A, CLIM, PERS, ZERO, plus MAE) and `mdo-front-adv-improve-v1.json` (improvement pass, with the w chosen at each origin). They hold weekly aggregates only, with no per-cell data.
- **Mean grid CRPS (km²):**

  | | 87 weeks | 2026 (40 weeks) |
  |---|---|---|
  | **AB** (primary) | 0.2719 | 0.1509 |
  | A | 0.2739 | 0.1581 |
  | CLIM | 0.2984 | 0.1553 |
  | PERS | 0.4410 | 0.2628 |
  | ZERO | 0.3579 | — |

- **AB, baseline − AB, with week-blocked 95% CIs (Addendum-1 method):**
  - vs CLIM: full +0.0265 [+0.0176, +0.0362]; 2026 +0.0044 [−0.0014, +0.0114].
  - vs PERS: full +0.1691 [+0.1398, +0.1993]; 2026 +0.1119 [+0.0886, +0.1361].
- **Week counts.** AB beat CLIM in 59 of 87 weeks (20 of 40 in 2026) and PERS in 83 of 87.
- **The chosen w.** It was 0.8–1.0 through 2025 (the first 8 weeks used the 0.5 fallback) and fell to 0.3 by September 2026; the median over 2026 is 0.7. On the 2026-10-11 map, the live procedure gives w = 0.3.
- **What this is not.** These are exposed numbers. The 2026 weeks were also used to select AB (ledger). They are not evidence of skill.

## 8. What is published, and what is not
This section takes effect only with owner approval of publication under this rule. The only channel is the public receipts repo, under `advance/`.
- **At issue:** `forecast_id`, the four-key sha256 (the same formula as v1 and `verify.py`), and the issue and resolution map dates. **The hash only.**
- **After resolution:**
  - the reveal of exactly `{forecast_id, issued_for_map_date, resolves_on_map_date, cells}`, with the AB quantiles, A's p_gain, mean and quantiles, CLIM's quantiles and the PERS value, verified with `verify.py`;
  - per-model scores (§3);
  - `real_forecast`;
  - this rule's sha256.
- **Never published:** quantiles before resolution, DSM or VIINA bytes, polygons, or inputs.
- **Labels.** Every published number carries "research model; N advance weeks counted; not evidence of skill" until the §5 test runs.

## 9. Limits
- DSM is a single open source, and its map timing drives both issue and resolution.
- Gains below 0.05 km² are treated as 0.
- Weekly gains are heavy-tailed: the largest cell-week in the training data is about 69 km². A few large weeks can dominate the km² score.
- AB inherits G's probabilities through A, and leans on CLIM when w is low.
- The 26-week verdict has modest power (§6): 0.76 on the full backtest and about 0 inside the 2026 regime. In the current regime it is unlikely to show skill over climatology.

## Ledger: improvement pass declared 2026-10-12, before it was run
- **Owner instruction (2026-10-12, about 16:31 EDT).** One pre-declared improvement pass. The rule is then locked before the Sun 2026-10-25 issue. The draft hashed `4fca21e2…a706` is **not** approved and is superseded by whatever this pass produces.
- **Disclosure.** The 40 weeks of 2026 were already seen in the first backtest (§6–§7). Selecting on them is **exposed, not blind**. The blind test is the prospective counted weeks only.
- **Code.** `etl/ace/mdo_front_adv.py`, subcommand `improve`, committed with this ledger before the run. The run happens once, on the same inputs and the same 87 origins as §7.
- **Candidates. There are three, and no others will be tried.**
  - **A0.** A unchanged: the control.
  - **AB.** A blended with CLIM by quantile averaging: q = w·q_A + (1 − w)·q_CLIM.
  - **AR.** A blended with a recency-weighted climatology, RCLIM: q = w·q_A + (1 − w)·q_RCLIM.
    - RCLIM uses the same 12 weekly windows as CLIM. Window k (k = 0 is the most recent) gets weight 0.5^(k/4), a 4-week half-life.
    - The quantile at τ is the smallest value whose normalized cumulative weight, with values sorted ascending, is ≥ τ.
    - Why it is justified: in 2026, CLIM matched A (§6). That suggests recent local history carries most of the signal, and a 4-week half-life tests that while staying anchored to climatology.
- **How w is chosen (AB and AR, separately, at every origin).**
  - The grid is w ∈ {0, 0.1, …, 1.0}.
  - The chosen w minimizes mean weekly grid-CRPS (km²) over the most recent 26 earlier origins whose outcome map is on or before the current issue map. This is rolling-origin CV inside the training window. Evaluation weeks never inform their own w.
  - Ties go to the larger w.
  - With fewer than 8 such earlier origins, w = 0.5.
  - Live, the same procedure is rerun at each issue on the past origins.
- **Evaluation.**
  - The score is primary grid-CRPS in km².
  - Each candidate is compared with CLIM and PERS, over the 40 weeks of 2026 and over the full 87 weeks.
  - CIs use the Addendum-1 week-blocked bootstrap.
- **Selection rule, fixed now (`select` in code).**
  - Among candidates whose full-backtest comparison with CLIM has mean > 0 and lower bound > 0, pick the one with the **lowest mean 2026 CRPS**.
  - If none qualifies, keep A0 and state that the expected outcome is "no demonstrated skill".
- **After selection.** K and power are recomputed for the chosen model, and §1–§9 are finalized for it. The status stays DRAFT, PENDING OWNER APPROVAL.

## Ledger: improvement pass outcome (run once, 2026-10-12, after declaration commit c8b7a7f30)
- **Run.** `python -m etl.ace.mdo_front_adv improve`, on the same inputs and the same 87 origins as §7. Output: `mdo-front-adv-improve-v1.json`.

  | candidate | 2026 mean CRPS | 2026 vs CLIM | 2026 vs PERS | full mean CRPS | full vs CLIM | full vs PERS |
  |---|---|---|---|---|---|---|
  | A0 (control) | 0.1581 | −0.0028 [−0.0103, +0.0062] | +0.1047 [+0.0816, +0.1291] | 0.2739 | +0.0245 [+0.0140, +0.0360] | +0.1671 [+0.1377, +0.1972] |
  | **AB** | **0.1509** | +0.0044 [−0.0014, +0.0114] | +0.1119 [+0.0886, +0.1361] | 0.2719 | +0.0265 [+0.0176, +0.0362] | +0.1691 [+0.1398, +0.1993] |
  | AR | 0.1525 | +0.0028 [−0.0027, +0.0096] | +0.1103 [+0.0876, +0.1340] | 0.2702 | +0.0283 [+0.0193, +0.0378] | +0.1709 [+0.1415, +0.2016] |

  Each comparison is baseline − candidate in km², with week-blocked 95% CIs. CLIM's mean CRPS is 0.1553 over 2026 and 0.2984 over the full period.
- **Selection.** All three candidates have a full-backtest CI vs CLIM above 0. The lowest 2026 CRPS belongs to **AB**, so **AB is the primary**.
  - AR has the better full-period mean, but the declared rule selects on 2026.
  - No candidate's 2026 CI vs CLIM excludes 0.
- **Disclosure, repeated.** This selection used 2026 weeks that had already been seen. It is exposed, not blind. The only blind evidence will be the prospective counted weeks.

## Approval record (2026-10-12)
- **Owner approval, 16:42 EDT, in-session.** The exact quoted text: "approve: 1. Approve the advance rule (sha 94982268…c810), with AB as primary. 2. Set K = 26 … 3. Approve publishing it in the public receipts repo, under advance/, with the honest expectation stated up front. The first forecast issues October 25."
- **What is approved.**
  - AB is the primary model.
  - K = 26.
  - Publication goes to the public receipts repo under `advance/`, with the honest expectation (§6) stated up front.
  - The first counted advance issue is Sun 2026-10-25.
- **How this file differs from the reviewed draft.** The draft is sha256 `94982268279d8335726bae7374a0034d8cb3c5b377ad466393ee7fa43826c810` (commit 5a44e514e). This file differs from it only by:
  - K: 16 becomes 26, in §5, §6 and §9;
  - the status and approval lines: the header, this record, and the note that the sha is recorded in the runbook.
- **The approved artifact** is this file, byte for byte. Its sha256 is recorded in `MDO-FRONT-WEEKLY-RUNBOOK.md`, because a file cannot contain its own hash.
