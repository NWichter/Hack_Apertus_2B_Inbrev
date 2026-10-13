# Gap study: selection rule (written before any hold-out run)

Date: 2026-10-13, before the hold-out runs of this study.

- **Dev split:** dev set (60, Nemotron, seed 4049) + challenge set (115, Nemotron, seed 5151) = 175 messages,
  53 with clinical content. All variants were developed and compared on these only. The symptom-pass
  prompt and the few-shot examples were written after reading dev errors, never gold errors.
- **Hold-out:** gold v0 (180), Nemotron test set (42), Swiss practice set (30); GraSCCo (40) and PARHAF (38)
  only to count false flags on clinical reports. Each chosen variant is run once on the hold-out; no change
  after that.
- **Primary criterion:** unnoticed clinical messages (clinical content that runs automatically) = 0 on dev.
- **Secondary:** fewest unnoticed wrong routes, then fewest messages sent to a person, then fewest extra calls.
- **Deployability:** the local configuration (8B only) must be possible; a variant that needs 70B is reported
  as an optional cloud/endpoint configuration.
- Everything tried is reported in `dev-study.md`, including variants that did not help.

## Choice after the dev study (still before any hold-out run)

Dev results: `dev-study.md`. Variants with 0 unnoticed clinical messages on dev: symptom pass >= 1 (unnoticed wrong
routes 12, to a person 76/175), + 70B gate (9, 87/175), + rules gate (6, 102/175).
By the rule above the **primary configuration is "8B + symptom pass (>= 1 of 3) + rules gate"** (fewest unnoticed wrong
routes, 8B only, deployable locally). Because it sends 58 % of dev messages to a person, two alternatives are computed from
the same hold-out runs and reported next to it, not chosen afterwards: "8B + symptom pass" alone and "8B + symptom pass +
70B gate". Not carried forward (no gain or worse on dev): safety-first schema order, few-shot, five samples.
