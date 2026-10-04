# Paired comparison: p2 vs. p3

95 % Wilson intervals, k/n [low, high].

| Set | Metric | p2 | p3 |
| --- | --- | --- | --- |
| gold | Route accuracy | 158/180 [0.82, 0.92] | 170/180 [0.90, 0.97] |
| gold | Recall of route other | 2/16 [0.03, 0.36] | 13/16 [0.57, 0.93] |
| gold | Precision of route other | 2/5 [0.12, 0.77] | 13/14 [0.69, 0.99] |
| gold | Clinical exclusion recall | 13/16 [0.57, 0.93] | 13/16 [0.57, 0.93] |
| gold | Clinical exclusion precision | 13/28 [0.30, 0.64] | 13/28 [0.30, 0.64] |
| gold | Today recall | 44/50 [0.76, 0.94] | 44/50 [0.76, 0.94] |
| gold | Deadline accuracy | 148/180 [0.76, 0.87] | 151/180 [0.78, 0.89] |
| gold | Coverage | 146/180 [0.75, 0.86] | 151/180 [0.78, 0.89] |
| swiss | Route accuracy | 23/30 [0.59, 0.88] | 24/30 [0.63, 0.90] |
| swiss | Recall of route other | 1/6 [0.03, 0.56] | 1/6 [0.03, 0.56] |
| swiss | Precision of route other | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] |
| swiss | Clinical exclusion recall | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] |
| swiss | Clinical exclusion precision | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] |
| swiss | Today recall | 5/5 [0.57, 1.00] | 5/5 [0.57, 1.00] |
| swiss | Deadline accuracy | 14/30 [0.30, 0.64] | 14/30 [0.30, 0.64] |
| swiss | Coverage | 25/30 [0.66, 0.93] | 25/30 [0.66, 0.93] |
| nemotron | Route accuracy | 38/42 [0.78, 0.96] | 39/42 [0.81, 0.98] |
| nemotron | Recall of route other | 0/3 [0.00, 0.56] | 0/3 [0.00, 0.56] |
| nemotron | Precision of route other | 0/1 [0.00, 0.79] | – |
| nemotron | Clinical exclusion recall | 8/8 [0.68, 1.00] | 8/8 [0.68, 1.00] |
| nemotron | Clinical exclusion precision | 8/9 [0.57, 0.98] | 8/10 [0.49, 0.94] |
| nemotron | Today recall | 17/18 [0.74, 0.99] | 17/18 [0.74, 0.99] |
| nemotron | Deadline accuracy | 38/42 [0.78, 0.96] | 37/42 [0.75, 0.95] |
| nemotron | Coverage | 32/42 [0.61, 0.87] | 32/42 [0.61, 0.87] |
| grascco | Route accuracy | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |
| grascco | Recall of route other | – | – |
| grascco | Precision of route other | – | – |
| grascco | Clinical exclusion recall | – | – |
| grascco | Clinical exclusion precision | 0/7 [0.00, 0.35] | 0/7 [0.00, 0.35] |
| grascco | Today recall | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |
| grascco | Deadline accuracy | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |
| grascco | Coverage | 33/40 [0.68, 0.91] | 33/40 [0.68, 0.91] |
| dev | Route accuracy | 39/60 [0.52, 0.76] | 51/60 [0.74, 0.92] |
| dev | Recall of route other | 0/20 [0.00, 0.16] | 11/20 [0.34, 0.74] |
| dev | Precision of route other | 0/1 [0.00, 0.79] | 11/11 [0.74, 1.00] |
| dev | Clinical exclusion recall | 7/9 [0.45, 0.94] | 7/9 [0.45, 0.94] |
| dev | Clinical exclusion precision | 7/9 [0.45, 0.94] | 7/9 [0.45, 0.94] |
| dev | Today recall | 17/19 [0.69, 0.97] | 17/19 [0.69, 0.97] |
| dev | Deadline accuracy | 50/60 [0.72, 0.91] | 49/60 [0.70, 0.89] |
| dev | Coverage | 51/60 [0.74, 0.92] | 51/60 [0.74, 0.92] |

Paired per message (exact two-sided McNemar test on the discordant pairs):

| Set | n | route changed | route right only with p3 | route right only with p2 | p | clinical caught only with p3 | clinical caught only with p2 | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gold | 180 | 14 | 13 | 1 | 0.00183 | 0 | 0 | 1 |
| swiss | 30 | 1 | 1 | 0 | 1 | 0 | 0 | 1 |
| nemotron | 42 | 1 | 1 | 0 | 1 | 0 | 0 | 1 |
| grascco | 40 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| dev | 60 | 13 | 12 | 0 | 0.000488 | 0 | 0 | 1 |
