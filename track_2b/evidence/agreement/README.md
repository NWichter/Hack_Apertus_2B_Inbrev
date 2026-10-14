# Label agreement with two open-weights model annotators

Date: 2026-10-13. **The annotators are language models, not people.** [[NIKLAS-PRÜFUNG: agreement-readme – Satz zur menschlichen Prüfung im Agreement-README]]

- Annotator A: `nvidia/nemotron-3-super-120b-a12b:free` (open weights, 0 USD).
- Annotator B: `openai/gpt-oss-120b` (open weights, Apache-2.0), reasoning effort medium, 0.058 USD for 367 messages.
- Both saw only received time, channel, sender, subject and body, plus the written label rules taken
  from the generator prompt and `data/taxonomy.yaml` (`scripts/annotate_open_models.py`, guideline a1).
  They never saw the grid labels, the generator or any Inbrev output. Apertus is not used: it is the system under test.
- Caveat: annotator A is from the same model family as the generator of the Nemotron and challenge
  sets (Nemotron 3 Ultra); annotator B is not.

`scripts/agreement.py` computes Cohen's κ (grid vs A, grid vs B, A vs B), Fleiss κ and bootstrap
intervals, lists disputed messages, and scores every system against each label source.

## Main results (`agreement.md`)

| Label | n | κ grid–A | κ grid–B | κ A–B |
| --- | --- | --- | --- | --- |
| Route | 367 | 0.93 [0.90, 0.96] | 0.93 [0.90, 0.96] | 0.93 [0.91, 0.96] |
| Clinical content | 367 | 0.98 [0.96, 1.00] | 0.97 [0.93, 0.99] | 0.98 [0.96, 1.00] |
| Deadline | 367 | 0.90 | 0.60 | 0.62 |
| Ambiguous / abstain | 367 | 0.40 | 0.42 | 0.77 |

Sets: gold v0 (180), Swiss practice set (30), Nemotron set (42), challenge set (115). On gold v0 and the
challenge set both models agree with the grid on clinical content for every message. Deadline agreement is
lower mainly for annotator B; "ambiguous" is the least reliable label (as expected for a rare, fuzzy category).

36 of 367 messages are disputed (route or clinical content); in 13 both models agree against the grid.
These are the review queue for a person. Nothing was relabelled.

**Do the conclusions change with the label source?** No ranking changes: on every set Inbrev stays ahead of the
keyword rules on route and clinical exclusion whether scored against the grid, either model or the majority;
e.g. gold 8B route 170/180 vs grid, 167–169/180 vs the other sources; clinical exclusion 13/16 under all four.
Agreement shows that the written label rules can be applied consistently to the texts; it does not show
that a label is clinically correct.
