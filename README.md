# ARGUS forecast receipts

A public, append-only record of ARGUS's weekly forecasts of the Ukraine front line. Each record is committed **before** the outcome is known and scored **after**, under a rule written in advance.

## What is forecast
- **Question.** For each 20 km cell along the front, the probability that Russian forces gain any ground (at least 0.05 km²) in the next 7 days, as shown on the DeepStateMap (DSM) front-line map.
- **Size.** About 176 cells per week.
- **Models.** G (ground state only) is the pre-registered primary model. M (ground state plus event reports) is a secondary model.

## How a week works
1. **Issue.** A forecast is issued from one DSM map date. Its sha256 hash is published in `receipts.csv` as soon as it is issued.
2. **Confirm.** A confirmer other than the operator confirms, before the outcome map exists, that the forecast was committed in time. Today the operator and the confirmer are separate automated agents run by ARGUS. This is separation of duties, not third-party audit.
3. **Reveal and score.** Seven days later, against the next DSM map:
   - the per-cell probabilities are revealed in `reveals/`, so anyone can recompute the hash with `verify.py`;
   - the scores are added to `scores.csv`.
4. **Nothing is edited or deleted.** Misses stay. Missed weeks are recorded as missed.

## The rule
- `SCORING-RULE-v1.md`, sha256 `49f3dffb2d502a04a6297bb5a1bfcf98cd29199d8f1f8790be6b7d775e119dbb`, approved 2026-10-12 before the first counted forecast resolved.
- **Skill claim.** After 8 independently confirmed weeks, ARGUS claims skill for G only if G beats climatology in Brier score with a week-blocked bootstrap 95% interval entirely above zero.
- **Otherwise** this page will say there is no demonstrated skill.

## What this is not
- **Not evidence of skill yet.** Today there are 0 counted weeks scored.
  - The first row (2026-10-02) was issued before an independent confirmer existed, so it never counts.
  - Single weeks are not evidence.
- **A research model.** It is not calibrated against any public benchmark and is not an operational product.
- **Inputs are not published.** No DSM or event-report data appear here, only hashes, per-cell probabilities and scores.
- **Disclosure.** The 2026-10-11 hash was first published here on 2026-10-12, one day after issue. Its earlier commitment is a private git commit (2026-10-11T16:21:14Z) and the separate confirmer's record. From now on, each hash is published here when it is issued.

Pearl Labs LLC · ARGUS.
