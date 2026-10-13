# Paired comparison: A vs. B

95 % Wilson intervals, k/n [low, high].

| Set | Metric | A | B |
| --- | --- | --- | --- |
| challenge | Route accuracy | 103/115 [0.83, 0.94] | 106/115 [0.86, 0.96] |
| challenge | Recall of route other | 9/20 [0.26, 0.66] | 13/20 [0.43, 0.82] |
| challenge | Precision of route other | 9/9 [0.70, 1.00] | 13/13 [0.77, 1.00] |
| challenge | Clinical exclusion recall | 41/44 [0.82, 0.98] | 44/44 [0.92, 1.00] |
| challenge | Clinical exclusion precision | 41/45 [0.79, 0.96] | 44/48 [0.80, 0.97] |
| challenge | Today recall | 56/59 [0.86, 0.98] | 58/59 [0.91, 1.00] |
| challenge | Deadline accuracy | 107/115 [0.87, 0.96] | 108/115 [0.88, 0.97] |
| challenge | Coverage | 70/115 [0.52, 0.69] | 62/115 [0.45, 0.63] |

Paired per message (exact two-sided McNemar test on the discordant pairs):

| Set | n | route changed | route right only with B | route right only with A | p | clinical caught only with B | clinical caught only with A | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| challenge | 115 | 7 | 4 | 1 | 0.375 | 3 | 0 | 0.25 |
