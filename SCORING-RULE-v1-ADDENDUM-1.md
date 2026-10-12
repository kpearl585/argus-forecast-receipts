# Scoring rule v1, addendum 1: the bootstrap is fully specified

Status: written 2026-10-12, before the first counted forecast (mdo-front-2026-10-11) resolves on 2026-10-18 and before any outcome under rule v1 is known. It specifies implementation details that rule v1 §4 left open. It changes no decision threshold. Linear: ARG-1389.

## 1. The verdict computation (rule v1 §4)
- **Weeks used:** the first 8 forecasts, by `issued_for_map_date`, whose resolution has `real_forecast: true` and that count under rule v1.
- **Per-week statistic:** d_w = climatology Brier − G Brier, both taken from the forecast's resolution record. Values are used exactly as recorded, with no rounding before the computation.
- **Bootstrap:**
  - Generator: `numpy.random.default_rng(20261012)`.
  - For each of 2,000 replicates, draw 8 week indices with replacement using `rng.integers(0, 8, size=8)`, and take the mean of d over the drawn weeks.
- **Interval:** `numpy.percentile(replicate_means, [2.5, 97.5])`, using numpy's default linear interpolation.
- **Verdict:**
  - "skill over climatology demonstrated (rule v1)" if mean(d) > 0 **and** the lower bound is > 0;
  - otherwise "no demonstrated skill over climatology (rule v1)".
- **Reference implementation:** `etl/ace/mdo_front_verdict.py`. With 8 or more counted weeks, it writes `verdict.csv` (columns `rule_version, counted_weeks, mean_diff, ci_low, ci_high, verdict, method_ref, published_utc`). With fewer, it writes nothing.
- **Single source:** the verdict is computed only by this script and published once to the public receipts repo. Displays such as the ARGUS platform strip show the published verdict and never recompute it.
- **M and challengers:** reported with the same statistic as secondary results, as rule v1 says.

## 2. Errata
The published file `MDO-FRONT-PUBLIC-SCORING-RULE-v1.md` (sha256 `49f3dffb…9dbb`) ends with two lines that are an editing artifact: `EOF` and a `cd … shasum` shell command. They are not part of the rule. The file is kept byte-for-byte as approved so its hash stays verifiable.
