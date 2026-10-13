# Route study: plan fixed before the hold-out-2 runs (14 October 2026)

**Goal:** fewer wrong routes that run automatically (the remaining gap to Qwen3.5-9B / Ministral 8B), without losing
any clinical message and without much more work for people.

**Dev split (all earlier sets, used for selection only):** dev 60 + challenge 115 + gold v0 180 + Nemotron 42 + Swiss 30
= 427 messages, 81 clinical. Variants were built after reading the most frequent confusions on this split
(insurer vs billing, insurer vs other for authorities, report_received vs other); see `dev-study.md`.

**Variants** (all 8B runs with the default symptom pass):
- `base`: prompt p3 (today's default).
- `p4`: sharper route descriptions and three extra boundary rules.
- `p4fs`: p4 plus four short few-shot examples written for this purpose (not taken from any set).
- `+ 70B SO`: 70B as second opinion only for low-confidence messages. Because every unnoticed route error on dev had
  3 of 3 identical samples, "low confidence" is defined as: the keyword rules choose another route than 8B. 70B
  (p3, three samples) is asked; same route → automatic, otherwise a person decides.
- `+ rules gate`: every low-confidence message goes to a person (reference from the gap study).

**Selection rule** (written after the dev results above, before any hold-out run): among variants with 0 unnoticed
clinical messages on dev, the fewest unnoticed wrong routes, provided that no more than 5 percentage points more messages
go to a person than with `base` (dev: 141/427, cap 162). Dev outcome: `base` 24 / 141, `base + 70B SO` 19 / 147,
`p4fs` 20 / 148, **`p4fs + 70B SO` 16 / 152 → chosen**. `p4` is out (2 unnoticed clinical), the rules gates exceed the cap.

**Measured once on hold-out 2** (146 messages, frozen in `../holdout2/FREEZE.md`), all reported, whatever the result:
every variant above, 70B p3 alone, and Qwen3.5-9B as comparison in the same pipeline (prompt p3, three samples, without
the symptom pass, as in the earlier comparison in `../peers/`, to stay inside the budget for paid calls).
Reported on all 146 and on the 127 messages where both open-model annotators agree with the grid.
No change to prompts, examples or rules after the hold-out runs.
