# Paired comparison: p2 70B (stored run) vs. p3 70B

95 % Wilson intervals, k/n [low, high].

| Set | Metric | p2 70B (stored run) | p3 70B |
| --- | --- | --- | --- |
| gold | Route accuracy | 163/180 [0.85, 0.94] | 172/180 [0.91, 0.98] |
| gold | Recall of route other | 5/16 [0.14, 0.56] | 14/16 [0.64, 0.97] |
| gold | Precision of route other | 5/5 [0.57, 1.00] | 14/14 [0.78, 1.00] |
| gold | Clinical exclusion recall | 15/16 [0.72, 0.99] | 15/16 [0.72, 0.99] |
| gold | Clinical exclusion precision | 15/30 [0.33, 0.67] | 15/30 [0.33, 0.67] |
| gold | Today recall | 47/50 [0.84, 0.98] | 47/50 [0.84, 0.98] |
| gold | Deadline accuracy | 153/180 [0.79, 0.89] | 156/180 [0.81, 0.91] |
| gold | Coverage | 169/180 [0.89, 0.97] | 176/180 [0.94, 0.99] |
| nemotron | Route accuracy | 38/42 [0.78, 0.96] | 37/42 [0.75, 0.95] |
| nemotron | Recall of route other | 0/3 [0.00, 0.56] | 0/3 [0.00, 0.56] |
| nemotron | Precision of route other | – | – |
| nemotron | Clinical exclusion recall | 8/8 [0.68, 1.00] | 8/8 [0.68, 1.00] |
| nemotron | Clinical exclusion precision | 8/9 [0.57, 0.98] | 8/9 [0.57, 0.98] |
| nemotron | Today recall | 17/18 [0.74, 0.99] | 17/18 [0.74, 0.99] |
| nemotron | Deadline accuracy | 37/42 [0.75, 0.95] | 37/42 [0.75, 0.95] |
| nemotron | Coverage | 39/42 [0.81, 0.98] | 38/42 [0.78, 0.96] |

Paired per message (exact two-sided McNemar test on the discordant pairs):

| Set | n | route changed | route right only with p3 70B | route right only with p2 70B (stored run) | p | clinical caught only with p3 70B | clinical caught only with p2 70B (stored run) | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gold | 180 | 9 | 9 | 0 | 0.00391 | 0 | 0 | 1 |
| nemotron | 42 | 1 | 0 | 1 | 1 | 0 | 0 | 1 |
