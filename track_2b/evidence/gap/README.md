# Closing the gap to other open models (13 October 2026)

Question: Apertus 8B let more errors through unnoticed than Qwen3.5-9B and Ministral 8B in the same
pipeline (gold v0: 9 wrong routes + 3 clinical messages handled automatically, against 1 + 0). Can the
pipeline, with Apertus only, close that gap?

**Method.** Dev split = dev set (60) + challenge set (115), 53 clinical messages. Every variant was built and
compared on dev only (`dev-study.md`); the selection rule and the choice were committed before any hold-out
run (`PREREGISTRATION.md`, commit `ee0daf7`). Hold-out = gold v0 (180), Nemotron (42), Swiss (30), plus
GraSCCo (40) and PARHAF (38) for false flags; run once (`holdout-*.md`). Two metric bugs found by review
(wrong routes of clinical messages were not counted; gates used a different 8B run) were fixed before
the hold-out was scored (commit `4e93787`). All runs: Hack Apertus endpoint, prompt p3, 3 samples.

**Variants tried on dev** (unnoticed wrong route + unnoticed clinical; messages to a person, of 175):

| Variant | Unnoticed | To a person | Verdict |
| --- | --- | --- | --- |
| 8B p3 (fresh run) | 14 + 5 | 56 | baseline |
| Schema order "safety first" | 15 + 6 | 55 | worse, dropped |
| Five samples instead of three | 14 + 5 | 56 | no effect, dropped |
| Four few-shot examples | 13 + 3 | 65 | partial, dropped |
| **Symptom pass** (second 8B call: "does someone describe a current complaint?", verified quote; flag if 1 of 3 says yes) | 12 + 0 | 76 | **meets the primary criterion** |
| 70B alone | 13 + 1 | 66 | – |
| 8B + 70B gate (automatic only if 70B agrees) | 10 + 1 | 73 | – |
| Symptom pass + 70B gate | 9 + 0 | 87 | reported |
| Rules gate (abstain if keyword rules choose another route) | 8 + 4 | 85 | – |
| **Symptom pass + rules gate** | 6 + 0 | 102 | **chosen by the rule** |

**Hold-out, gold v0 (180 messages), measured once:**

| Configuration | Unnoticed wrong route | Unnoticed clinical | To a person | Automatic and right |
| --- | --- | --- | --- | --- |
| Apertus 8B p3 (before) | 9 | 3 | 29 | 142 |
| Apertus 8B + symptom pass | 8 | **0** | 40 | 132 |
| Apertus 8B + symptom pass + rules gate (chosen) | **4** | **0** | 69 | 107 |
| Apertus 8B + symptom pass + 70B gate | 6 | 0 | 46 | 128 |
| Qwen3.5-9B (same pipeline, no symptom pass) | 1 | 0 | 38 | 141 |
| Ministral 8B (same) | 1 | 0 | 41 | 138 |

Nemotron (42) and Swiss (30): unnoticed clinical was already 0 and stays 0; unnoticed wrong routes 2 → 1
(Nemotron) and 2 → 0 (Swiss) with the chosen configuration. GraSCCo and PARHAF: false flags unchanged
(7 and 17), because the symptom pass is not applied to messages routed as reports.

**Reading.** The clinical part of the gap is closed on every hold-out set: no clinical message runs
automatically, as with the comparison models. The price is about 10 more messages per 180 for a person
(29 → 40); most of the extra flags on dev were real current complaints that the grid did not count as acute
(e.g. "fever for two days"). The route part of the gap is narrowed, not closed: at about the same human
workload as Qwen (40 vs 38), Apertus still lets 8 wrong routes through against 1; the rules gate halves that
to 4 but sends 69 of 180 messages to a person. The symptom prompt was written after reading dev errors, so the
dev numbers are optimistic; the hold-out numbers are the ones to cite. The symptom pass adds one short 8B
call per message; its cost on local hardware has not been measured.
