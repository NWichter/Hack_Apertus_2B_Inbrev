# Label agreement: grid labels vs. two open-weights model annotators

Annotators are language models, not people: **Nemotron-Super** = nvidia/nemotron-3-super-120b-a12b:free (cost 0.0 USD); **gpt-oss-120b** = openai/gpt-oss-120b (cost 0.0579 USD). They saw only received time, channel, sender, subject and body plus the written label rules (`scripts/annotate_open_models.py`, guideline a1), never the grid labels or Inbrev output. The grid label is the label the generator was asked to write the text for. κ = Cohen's kappa; Fleiss κ over all three; 95 % bootstrap intervals (2,000 resamples, seed 2026).

## Agreement per label

| Set | n | Label | grid–Nemotron-Super | grid–gpt-oss-120b | Nemotron-Super–gpt-oss-120b | Fleiss κ | raw agreement all three |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all | 367 | route | 0.93 [0.90, 0.96] | 0.93 [0.90, 0.96] | 0.93 [0.91, 0.96] | 0.93 [0.91, 0.95] | 335/367 |
| all | 367 | deadline | 0.90 [0.86, 0.94] | 0.60 [0.54, 0.66] | 0.62 [0.55, 0.68] | 0.70 [0.66, 0.75] | 262/367 |
| all | 367 | clinical | 0.98 [0.96, 1.00] | 0.97 [0.93, 0.99] | 0.98 [0.96, 1.00] | 0.98 [0.95, 0.99] | 363/367 |
| all | 367 | ambiguous | 0.40 [0.11, 0.63] | 0.42 [0.13, 0.66] | 0.77 [0.39, 1.00] | 0.49 [0.20, 0.69] | 352/367 |
| gold | 180 | route | 0.95 [0.91, 0.98] | 0.94 [0.91, 0.97] | 0.93 [0.89, 0.97] | 0.94 [0.91, 0.97] | 166/180 |
| gold | 180 | deadline | 0.97 [0.93, 0.99] | 0.62 [0.52, 0.71] | 0.63 [0.53, 0.72] | 0.74 [0.67, 0.80] | 133/180 |
| gold | 180 | clinical | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 180/180 |
| gold | 180 | ambiguous | 0.35 [0.00, 0.69] | 0.19 [0.00, 0.52] | 0.66 [0.00, 1.00] | 0.32 [-0.02, 0.64] | 172/180 |
| swiss | 30 | route | 0.96 [0.88, 1.00] | 0.96 [0.88, 1.00] | 0.96 [0.88, 1.00] | 0.96 [0.88, 1.00] | 29/30 |
| swiss | 30 | deadline | 0.34 [0.04, 0.60] | 0.20 [-0.06, 0.45] | 0.26 [0.05, 0.47] | 0.24 [0.02, 0.43] | 9/30 |
| swiss | 30 | clinical | 1.00 [1.00, 1.00] | 0.87 [0.47, 1.00] | 0.87 [0.47, 1.00] | 0.91 [0.58, 1.00] | 29/30 |
| swiss | 30 | ambiguous | 0.65 [0.00, 1.00] | 0.65 [0.00, 1.00] | 1.00 [1.00, 1.00] | 0.74 [-0.03, 1.00] | 29/30 |
| nemotron | 42 | route | 0.89 [0.78, 0.97] | 0.86 [0.73, 0.97] | 0.92 [0.81, 1.00] | 0.89 [0.80, 0.96] | 36/42 |
| nemotron | 42 | deadline | 0.89 [0.74, 1.00] | 0.46 [0.25, 0.66] | 0.58 [0.37, 0.77] | 0.64 [0.49, 0.78] | 28/42 |
| nemotron | 42 | clinical | 0.86 [0.64, 1.00] | 0.80 [0.55, 1.00] | 0.94 [0.77, 1.00] | 0.87 [0.70, 1.00] | 39/42 |
| nemotron | 42 | ambiguous | 0.00 [0.00, 0.00] | 0.66 [0.00, 1.00] | 0.00 [0.00, 0.00] | 0.32 [-0.02, 0.49] | 40/42 |
| challenge | 115 | route | 0.91 [0.85, 0.96] | 0.93 [0.87, 0.97] | 0.94 [0.89, 0.98] | 0.93 [0.88, 0.96] | 104/115 |
| challenge | 115 | deadline | 0.94 [0.88, 0.99] | 0.69 [0.58, 0.81] | 0.70 [0.58, 0.80] | 0.78 [0.70, 0.86] | 92/115 |
| challenge | 115 | clinical | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 115/115 |
| challenge | 115 | ambiguous | 0.48 [-0.02, 0.88] | 0.56 [-0.01, 1.00] | 0.85 [0.00, 1.00] | 0.62 [-0.01, 0.92] | 111/115 |

Messages without an annotation from both models (left out): 0. Bootstrap resamples with an undefined κ (only one class drawn) are skipped: 3195 of 2000 × cells; intervals on sparse labels are therefore conditional. A κ of 1.00 [1.00, 1.00] means no disagreement was observed, not zero uncertainty. Fleiss κ treats the three sources as interchangeable raters (they are fixed); it is given as a summary only.

## Disputed messages

36 of 367 messages have at least one annotator disagreeing with the grid on route or clinical content; in 13 of them both annotators agree with each other against the grid (candidates for a wrong grid label or a text that does not fit its spec; two models agreeing is a hint, not proof). These are the review queue for a person; nothing was relabelled.

| Set | disputed route | disputed clinical | both annotators against grid |
| --- | --- | --- | --- |
| gold | 14 | 0 | 3 |
| swiss | 1 | 1 | 0 |
| nemotron | 6 | 3 | 5 |
| challenge | 11 | 0 | 5 |

## Do the conclusions depend on the label source?

Route accuracy and clinical-exclusion recall of each system, scored against the grid labels, against each model annotator, against the majority of the three, and on the consensus subset (grid and both annotators agree on route and clinical content). The consensus subset leaves out all disputed messages, which can inflate scores; it is shown only to see whether the ranking of systems changes. Majority: two of three; when all three route labels differ, the grid label is kept (ties: see count below). Intervals are per system (Wilson), not paired tests.

| Set | System | Route vs grid | vs Nemotron-Super | vs gpt-oss-120b | vs majority | consensus subset | Clinical recall vs grid | consensus subset | vs Nemotron-Super | vs gpt-oss-120b | vs majority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gold | keyword rules | 143/180 [0.73, 0.85] | 138/180 [0.70, 0.82] | 140/180 [0.71, 0.83] | 142/180 [0.72, 0.84] | 134/166 [0.74, 0.86] | 7/16 [0.23, 0.67] | 5/13 [0.18, 0.64] | 7/16 [0.23, 0.67] | 7/16 [0.23, 0.67] | 7/16 [0.23, 0.67] |
| gold | Inbrev 8B p3 | 170/180 [0.90, 0.97] | 169/180 [0.89, 0.97] | 167/180 [0.88, 0.96] | 169/180 [0.89, 0.97] | 162/166 [0.94, 0.99] | 13/16 [0.57, 0.93] | 10/13 [0.50, 0.92] | 13/16 [0.57, 0.93] | 13/16 [0.57, 0.93] | 13/16 [0.57, 0.93] |
| gold | Inbrev 70B p3 | 172/180 [0.91, 0.98] | 173/180 [0.92, 0.98] | 171/180 [0.91, 0.97] | 173/180 [0.92, 0.98] | 165/166 [0.97, 1.00] | 15/16 [0.72, 0.99] | 12/13 [0.67, 0.99] | 15/16 [0.72, 0.99] | 15/16 [0.72, 0.99] | 15/16 [0.72, 0.99] |
| swiss | keyword rules | 25/30 [0.66, 0.93] | 25/30 [0.66, 0.93] | 25/30 [0.66, 0.93] | 25/30 [0.66, 0.93] | 24/28 [0.69, 0.94] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | 4/5 [0.38, 0.96] | 4/4 [0.51, 1.00] |
| swiss | Inbrev 8B p3 | 24/30 [0.63, 0.90] | 24/30 [0.63, 0.90] | 25/30 [0.66, 0.93] | 24/30 [0.63, 0.90] | 23/28 [0.64, 0.92] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | 4/5 [0.38, 0.96] | 4/4 [0.51, 1.00] |
| nemotron | keyword rules | 32/42 [0.61, 0.87] | 33/42 [0.64, 0.88] | 32/42 [0.61, 0.87] | 34/42 [0.67, 0.90] | 26/33 [0.62, 0.89] | 6/8 [0.41, 0.93] | 5/7 [0.36, 0.92] | 6/10 [0.31, 0.83] | 6/11 [0.28, 0.79] | 6/10 [0.31, 0.83] |
| nemotron | Inbrev 8B p3 | 39/42 [0.81, 0.98] | 39/42 [0.81, 0.98] | 37/42 [0.75, 0.95] | 39/42 [0.81, 0.98] | 33/33 [0.90, 1.00] | 8/8 [0.68, 1.00] | 7/7 [0.65, 1.00] | 9/10 [0.60, 0.98] | 9/11 [0.52, 0.95] | 9/10 [0.60, 0.98] |
| nemotron | Inbrev 70B p3 | 37/42 [0.75, 0.95] | 39/42 [0.81, 0.98] | 37/42 [0.75, 0.95] | 39/42 [0.81, 0.98] | 32/33 [0.85, 0.99] | 8/8 [0.68, 1.00] | 7/7 [0.65, 1.00] | 8/10 [0.49, 0.94] | 8/11 [0.43, 0.90] | 8/10 [0.49, 0.94] |
| challenge | keyword rules | 87/115 [0.67, 0.83] | 85/115 [0.65, 0.81] | 87/115 [0.67, 0.83] | 87/115 [0.67, 0.83] | 81/104 [0.69, 0.85] | 31/44 [0.56, 0.82] | 28/40 [0.55, 0.82] | 31/44 [0.56, 0.82] | 31/44 [0.56, 0.82] | 31/44 [0.56, 0.82] |
| challenge | Inbrev 8B p3 | 103/115 [0.83, 0.94] | 104/115 [0.84, 0.95] | 104/115 [0.84, 0.95] | 104/115 [0.84, 0.95] | 100/104 [0.91, 0.98] | 41/44 [0.82, 0.98] | 37/40 [0.80, 0.97] | 41/44 [0.82, 0.98] | 41/44 [0.82, 0.98] | 41/44 [0.82, 0.98] |
| challenge | Inbrev 70B p3 | 106/115 [0.86, 0.96] | 108/115 [0.88, 0.97] | 109/115 [0.89, 0.98] | 109/115 [0.89, 0.98] | 102/104 [0.93, 0.99] | 44/44 [0.92, 1.00] | 40/40 [0.91, 1.00] | 44/44 [0.92, 1.00] | 44/44 [0.92, 1.00] | 44/44 [0.92, 1.00] |

Three-way route ties (grid label kept): gold 0, swiss 1, nemotron 0, challenge 0.

