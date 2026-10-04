# Prompt p3: route "other", developed on a separate dev set

Date: 2026-10-04. Model: `apertus-v1.5-8b` at the Hack Apertus endpoint, 3 samples, temperature 0.7,
JSON schema, safety mode `or`, abstain below 0.99 (the default operating point). Only the route
hints change; checks, vote and safety net are unchanged.

## Why

With prompt p2, Apertus was weakest on the route `other` (gold v0: 2/16 to 3/16 correct; the keyword
rules got 9/16). Most `other` messages went to `certificate_request` or `report_received`.

## How (no decisions on the test sets)

1. **Dev set** (`dev-set/`): 60 new messages from the open-weights model
   `nvidia/nemotron-3-ultra-550b-a55b` via OpenRouter (grid seed 4049, prefix `dev`, 20 of 60 are
   `other`; `scripts/generate_openrouter.py grid --preset dev`, same generator prompt as the Nemotron
   test set). Labels are fixed by the grid before generation. 60/60 valid, USD 0.13
   (`dev-set/generation-log.json`). Apertus wrote no text and no label.
2. **p2 on dev**: route 39/60, `other` 0/20. Errors read on dev only: copy/transfer requests of
   medical records went to `certificate_request`/`report_received`/`referral_in`; a patient asking
   for a referral elsewhere went to `referral_in`; symptom-only messages went to other routes.
3. **p3** (`src/inbrev/prompt.py`, `ROUTE_HINTS_P3`, `RULES_P3`): sharper boundaries for
   `certificate_request` (the doctor has to write something), `referral_in` (a physician sends a
   patient TO this practice) and `other` (records copy/transfer, authority letter, general question,
   referral elsewhere, symptoms only). One iteration: dev route 51/60, `other` 11/20, clinical
   exclusion unchanged 7/9. p3 was frozen after this single dev run.
4. **Test sets, once**: gold v0 (180), Swiss practice set (30), Nemotron set (42), GraSCCo (40),
   p3 and a fresh p2 run in the same session (`scripts/run_prompt_comparison.sh`, `run.log`).

Prompt fingerprints (SHA-256 of the system prompt, first 16 hex): p2 `7eef0498c88ae6ee`,
p3 `b4b4071128da69fc`. `INBREV_PROMPT=p2` restores the old prompt.

## Results (`compare-p2-p3.md`, Wilson 95 % intervals, exact McNemar on discordant pairs)

| Set | Route p2 | Route p3 | right only p3 / only p2 | McNemar p | `other` p2 → p3 | Clinical exclusion p2 → p3 |
| --- | --- | --- | --- | --- | --- | --- |
| Gold v0 | 158/180 [0.82, 0.92] | 170/180 [0.90, 0.97] | 13 / 1 | 0.0018 | 2/16 → 13/16 | 13/16 → 13/16 |
| Swiss | 23/30 [0.59, 0.88] | 24/30 [0.63, 0.90] | 1 / 0 | 1 | 1/6 → 1/6 | 4/4 → 4/4 |
| Nemotron | 38/42 [0.78, 0.96] | 39/42 [0.81, 0.98] | 1 / 0 | 1 | 0/3 → 0/3 | 8/8 → 8/8 |
| GraSCCo | 40/40 | 40/40 | 0 / 0 | 1 | – | – (no positives) |
| Dev (not a test) | 39/60 | 51/60 | 12 / 0 | 0.0005 | 0/20 → 11/20 | 7/9 → 7/9 |

Pooled over the four test sets: route 259/292 → 273/292. No message lost its clinical exclusion
(0 discordant pairs on every set). Gold macro-F1 0.839 → 0.943 (both runs from this session); coverage 173/180 → 177/180.

**Noise floor** (`noise-p2-rerun.md`): the stored p2 run from 2026-10-03 against the fresh p2 run
changes the route of 3 of 180 gold messages (Nemotron 0/42, GraSCCo 0/40); p3 changes 14 of 180.

**70B** (`compare-70b.md`, `run-70b.log`; p3 run once, compared with the stored p2 70B runs from
2026-10-03/04, no fresh p2 70B run): gold route 163/180 → 172/180 (9 / 0, p = 0.0039), `other`
5/16 → 14/16, clinical exclusion 15/16 → 15/16, coverage 169/180 → 176/180; Nemotron route
38/42 → 37/42 (0 / 1, p = 1), clinical 8/8 → 8/8.

**Apertus vs. keyword rules with p3** (`rules-vs-apertus-*.md`): gold 32 wins / 5 losses
(p = 7.4e-6, before 27/11), `other` 13/16 vs. rules 9/16; Nemotron 8/1 (p = 0.039); Swiss 3/4 (p = 1); 70B on gold 34/5 (p = 2.4e-6, before 31/11).

## What p3 does not fix

- Swiss set: 4 of 6 `other` messages are acute emergencies ("NOTFALL", "URGENCE", "EMERGENZA",
  allergic reaction) and still get the route `report_received`. All four carry the safety flag and go
  to "A person decides" with deadline today, so the route has no effect on handling. Observed on the
  test set only, not tuned.
- About 6 of the 9 remaining dev errors are texts that fit the predicted route better than the grid
  label (e.g. "Richiesta certificato" labelled `other`): the generator does not always follow the
  spec. Labels are still not checked by a human (κ open).
- Nemotron set: the 3 `other` messages are still missed (0/3).

## Files

| File | Content |
| --- | --- |
| `dev-set/` | dev grid (labels), generator prompt, generation log with cost. The 60 texts stay with the gold set in `$DATA_DIR/dev-set/` until a person has checked them for real names (same rule as the gold and Nemotron sets) |
| `predictions/` | all predictions with raw model output (`{set}-{p2,p3}-8b.jsonl`) |
| `compare-p2-p3.md` | paired comparison per set |
| `noise-p2-rerun.md` | stored p2 run vs. fresh p2 run |
| `eval-*.md` | full `inbrev eval` reports with baselines, per-language and per-field tables |
| `rules-vs-apertus-*.md` | Apertus p3 vs. keyword rules vs. rules-first hybrid |
| `run.log`, `run-70b.log` | timing of the test runs |
| `compare-70b.md`, `eval-gold-70b.md`, `rules-vs-apertus-gold-70b.md` | 70B with p3 |

Reproduce: `DATA_DIR=... bash scripts/run_prompt_comparison.sh`, then
`PYTHONPATH=scripts python scripts/compare_prompts.py --labels p2 p3 --set gold GOLD p2.jsonl p3.jsonl ... --report out.md`.
