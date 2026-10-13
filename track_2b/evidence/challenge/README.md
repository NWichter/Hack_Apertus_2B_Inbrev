# Clinical-exclusion challenge set

Note (14 Oct): unseen for prompt p3 when these numbers were measured, but on 13 October it became part of the dev split for the second check (`../gap/`), so it is not a hold-out for that check.

Date: 2026-10-13. Purpose: the gold set has only 16 messages with clinical content, so the main safety
number had a wide interval (13/16, 95 % CI 0.57–0.93). This set adds 44 clinical messages and 39
medical traps, written after prompt p3, the checks and the lexical net were frozen. Nothing was tuned on it.

## Data

- Grid: `scripts/generate_openrouter.py grid --seed 5151 --prefix chl --preset challenge`
  (`grid-challenge.jsonl`, 120 specs: 18 acute explicit, 30 acute in passing, 40 medical traps,
  32 plain; DE 60, FR 32, IT 22, EN 6; more typos and dialect than the gold set). Labels are fixed
  by the grid before any text exists.
- Text: `nvidia/nemotron-3-ultra-550b-a55b:free` (open weights, NVIDIA Open Model License) via
  OpenRouter, same generator prompt as the Nemotron test set (`PROMPT-v0.2-nemotron.txt`), 0 USD.
  The free provider was often overloaded; 100 specs passed validation in the first run, 15 of the 20
  missing ones in a second run (`generation-log-part1.json`, `-part2.json`); 5 were dropped after
  three attempts. **115 messages: 44 with clinical content (17 explicit, 27 in passing), 39 traps,
  32 plain.** The texts are not in the repository yet (same rule as the gold set: after human review).
- Apertus wrote no text and no label. No person reviewed the labels; two open-weights models labelled
  the texts blind (`../agreement/`): clinical content agreed with the grid on 115/115 for both.

## Results (Hack Apertus endpoint, p3, 3 samples, T = 0.7, default operating point)

| Setup | Route | Clinical exclusion recall | Precision of the flag | Today recall |
| --- | --- | --- | --- | --- |
| Keyword rules + lexical net | 87/115 [0.67, 0.83] | 31/44 [0.56, 0.82] | 31/35 | 45/59 |
| TF-IDF + LogReg (5-fold CV on this set) | 84/115 [0.64, 0.80] | 39/44 [0.76, 0.95] | 39/43 | 52/59 |
| Inbrev, Apertus 8B | 103/115 [0.83, 0.94] | **41/44 [0.82, 0.98]** | 41/45 | 56/59 |
| Inbrev, Apertus 70B | 106/115 [0.86, 0.96] | **44/44 [0.92, 1.00]** | 44/48 | 58/59 |

Paired (exact McNemar): 8B vs keyword rules, route 20 vs 4 discordant (p = 0.0015), clinical 10 vs 0
(p = 0.002). 8B vs 70B: route 1 vs 4 (p = 0.375), clinical 0 vs 3 (p = 0.25). The TF-IDF row is
trained by cross-validation on this very set, so it is an in-domain upper reference, not a deployable baseline.
Files: `eval-challenge.md/.json`, `rules-vs-apertus-8b.md`, `compare-8b-70b.md`, `predictions/`.
The local Q4 run on the same set is in `../native/`.
