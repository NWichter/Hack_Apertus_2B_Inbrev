# Paired comparison: A vs. B

95 % Wilson intervals, k/n [low, high].

| Set | Metric | A | B |
| --- | --- | --- | --- |
| challenge: BF16 8B 3 samples vs local Q4 1 sample | Route accuracy | 103/115 [0.83, 0.94] | 99/115 [0.79, 0.91] |
| challenge: BF16 8B 3 samples vs local Q4 1 sample | Recall of route other | 9/20 [0.26, 0.66] | 5/20 [0.11, 0.47] |
| challenge: BF16 8B 3 samples vs local Q4 1 sample | Precision of route other | 9/9 [0.70, 1.00] | 5/5 [0.57, 1.00] |
| challenge: BF16 8B 3 samples vs local Q4 1 sample | Clinical exclusion recall | 41/44 [0.82, 0.98] | 38/44 [0.73, 0.94] |
| challenge: BF16 8B 3 samples vs local Q4 1 sample | Clinical exclusion precision | 41/45 [0.79, 0.96] | 38/42 [0.78, 0.96] |
| challenge: BF16 8B 3 samples vs local Q4 1 sample | Today recall | 56/59 [0.86, 0.98] | 53/59 [0.80, 0.95] |
| challenge: BF16 8B 3 samples vs local Q4 1 sample | Deadline accuracy | 107/115 [0.87, 0.96] | 102/115 [0.82, 0.93] |
| challenge: BF16 8B 3 samples vs local Q4 1 sample | Coverage | 70/115 [0.52, 0.69] | 73/115 [0.54, 0.72] |
| challenge: BF16 8B 1 sample (replay) vs local Q4 1 sample | Route accuracy | 104/115 [0.84, 0.95] | 99/115 [0.79, 0.91] |
| challenge: BF16 8B 1 sample (replay) vs local Q4 1 sample | Recall of route other | 10/20 [0.30, 0.70] | 5/20 [0.11, 0.47] |
| challenge: BF16 8B 1 sample (replay) vs local Q4 1 sample | Precision of route other | 10/10 [0.72, 1.00] | 5/5 [0.57, 1.00] |
| challenge: BF16 8B 1 sample (replay) vs local Q4 1 sample | Clinical exclusion recall | 40/44 [0.79, 0.96] | 38/44 [0.73, 0.94] |
| challenge: BF16 8B 1 sample (replay) vs local Q4 1 sample | Clinical exclusion precision | 40/44 [0.79, 0.96] | 38/42 [0.78, 0.96] |
| challenge: BF16 8B 1 sample (replay) vs local Q4 1 sample | Today recall | 55/59 [0.84, 0.97] | 53/59 [0.80, 0.95] |
| challenge: BF16 8B 1 sample (replay) vs local Q4 1 sample | Deadline accuracy | 106/115 [0.86, 0.96] | 102/115 [0.82, 0.93] |
| challenge: BF16 8B 1 sample (replay) vs local Q4 1 sample | Coverage | 71/115 [0.53, 0.70] | 73/115 [0.54, 0.72] |

Paired per message (exact two-sided McNemar test on the discordant pairs):

| Set | n | route changed | route right only with B | route right only with A | p | clinical caught only with B | clinical caught only with A | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| challenge: BF16 8B 3 samples vs local Q4 1 sample | 115 | 5 | 0 | 4 | 0.125 | 0 | 3 | 0.25 |
| challenge: BF16 8B 1 sample (replay) vs local Q4 1 sample | 115 | 5 | 0 | 5 | 0.0625 | 1 | 3 | 0.625 |
