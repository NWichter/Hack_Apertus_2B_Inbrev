# Route study (14 October 2026)

Question: with the clinical gap closed, can Inbrev let fewer wrong routes run automatically, using Apertus only?
Plan and selection rule were committed before any hold-out run (`PREREGISTRATION.md`, commit `7a7e3fd`); the hold-out
was frozen with hashes before that (`../holdout2/FREEZE.md`, commit `d9867d8`).

**Dev split** (427 messages, all earlier sets; `dev-study.md`). The most frequent confusions were boundary questions,
not uncertainty: an insurer asking about an invoice (grid `billing`, model `insurer`), requests from authorities (grid
`other`, model `insurer`), patients asking about results or describing emergencies (grid `other`, model
`report_received`). All 24 wrong routes that ran automatically had 3 of 3 identical samples, so sample agreement cannot
find them; the second opinion therefore uses disagreement with the keyword rules as its trigger.

**Hold-out 2** (146 messages written by Gemma 4 31B, measured once; `holdout2-all.md`, `holdout2-undisputed.md`):

| Configuration | Unnoticed wrong route | Unnoticed clinical | To a person | Automatic and right |
| --- | --- | --- | --- | --- |
| Apertus 8B, today's default (p3 + symptom pass) | 5 | 0 | 40 | 101 |
| p4 (sharper route descriptions) | 5 | 0 | 42 | 99 |
| p4 + few-shot | 5 | 0 | 39 | 102 |
| **p4 + few-shot + 70B second opinion (chosen on dev)** | **2** | **0** | **43** | 101 |
| default + 70B second opinion | 3 | 0 | 45 | 98 |
| default + rules gate (reference) | 0 | 0 | 66 | 80 |
| Apertus 70B alone (p3, no symptom pass) | 3 | 0 | 30 | 113 |
| Qwen3.5-9B, same pipeline (p3, no symptom pass; comparison) | 0 | 0 | 24 | 122 |

On the 127 messages where both open-model annotators agree with the grid: default 3 / 27 to a person, chosen 0 / 29,
Qwen 0 / 16. The 70B second opinion was asked for 26 of 146 messages.

**Reading.** The new prompt and examples alone do not reduce automatic route errors on the hold-out (5 → 5); the gain comes
from asking 70B when the keyword rules disagree (5 → 2, three more messages for a person). This needs the 70B endpoint and
is therefore an option for endpoint or cloud deployments, not for an 8B-only box; the shipped default is unchanged. The gap
to the comparison model stays large: Qwen3.5-9B lets no wrong route through while sending 24 instead of 43 messages to a
person, and Apertus 70B alone (30 to a person) is closer to Qwen than any 8B configuration. Hold-out 2 has 14 clinical
messages, too few for a new safety claim; all configurations take all 14 out of automation.

Costs (paid open models via OpenRouter, from token prices): generation USD 0.049, second labels USD 0.010, Qwen comparison
USD 0.083. Apertus calls on the Hack Apertus endpoint: 4 × 146 runs plus the dev runs (2 × 427 with 8B).

**Built into the code (14 October):** `INBREV_SECOND_OPINION_MODEL` (off by default; e.g. `apertus-v1.5-70b`), available as
an option for practices with 70B access (e.g. a Swiss cloud). `scripts/replay_second_opinion.py` feeds the stored 70B
samples through the built-in path and reproduces the table above exactly (default 3 / 45, p4 2 / 48, p4 + few-shot 2 / 43;
26, 25 and 26 messages asked). Live smoke test against the Hack Apertus endpoint on 4 triggering messages:
`second-opinion-live-smoke.jsonl` (three 70B samples each, all four agreed). Unit tests: `tests/test_second_opinion.py`.
