# Paired comparison: p2 (stored run) vs. p2 (rerun)

95 % Wilson intervals, k/n [low, high].

| Set | Metric | p2 (stored run) | p2 (rerun) |
| --- | --- | --- | --- |
| gold | Route accuracy | 159/180 [0.83, 0.92] | 158/180 [0.82, 0.92] |
| gold | Recall of route other | 3/16 [0.07, 0.43] | 2/16 [0.03, 0.36] |
| gold | Precision of route other | 3/6 [0.19, 0.81] | 2/5 [0.12, 0.77] |
| gold | Clinical exclusion recall | 13/16 [0.57, 0.93] | 13/16 [0.57, 0.93] |
| gold | Clinical exclusion precision | 13/28 [0.30, 0.64] | 13/28 [0.30, 0.64] |
| gold | Today recall | 43/50 [0.74, 0.93] | 44/50 [0.76, 0.94] |
| gold | Deadline accuracy | 147/180 [0.75, 0.87] | 148/180 [0.76, 0.87] |
| gold | Coverage | 172/180 [0.91, 0.98] | 173/180 [0.92, 0.98] |
| nemotron | Route accuracy | 38/42 [0.78, 0.96] | 38/42 [0.78, 0.96] |
| nemotron | Recall of route other | 0/3 [0.00, 0.56] | 0/3 [0.00, 0.56] |
| nemotron | Precision of route other | 0/1 [0.00, 0.79] | 0/1 [0.00, 0.79] |
| nemotron | Clinical exclusion recall | 8/8 [0.68, 1.00] | 8/8 [0.68, 1.00] |
| nemotron | Clinical exclusion precision | 8/9 [0.57, 0.98] | 8/9 [0.57, 0.98] |
| nemotron | Today recall | 17/18 [0.74, 0.99] | 17/18 [0.74, 0.99] |
| nemotron | Deadline accuracy | 37/42 [0.75, 0.95] | 38/42 [0.78, 0.96] |
| nemotron | Coverage | 42/42 [0.92, 1.00] | 41/42 [0.88, 1.00] |
| grascco | Route accuracy | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |
| grascco | Recall of route other | – | – |
| grascco | Precision of route other | – | – |
| grascco | Clinical exclusion recall | – | – |
| grascco | Clinical exclusion precision | 0/7 [0.00, 0.35] | 0/7 [0.00, 0.35] |
| grascco | Today recall | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |
| grascco | Deadline accuracy | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |
| grascco | Coverage | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |

Paired per message (exact two-sided McNemar test on the discordant pairs):

| Set | n | route changed | route right only with p2 (rerun) | route right only with p2 (stored run) | p | clinical caught only with p2 (rerun) | clinical caught only with p2 (stored run) | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gold | 180 | 3 | 0 | 1 | 1 | 0 | 0 | 1 |
| nemotron | 42 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| grascco | 40 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
