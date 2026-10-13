# Paired comparison: A vs. B

95 % Wilson intervals, k/n [low, high].

| Set | Metric | A | B |
| --- | --- | --- | --- |
| gold: Apertus 8B vs Qwen3.5-9B | Route accuracy | 170/180 [0.90, 0.97] | 177/180 [0.95, 0.99] |
| gold: Apertus 8B vs Qwen3.5-9B | Recall of route other | 13/16 [0.57, 0.93] | 16/16 [0.81, 1.00] |
| gold: Apertus 8B vs Qwen3.5-9B | Precision of route other | 13/14 [0.69, 0.99] | 16/16 [0.81, 1.00] |
| gold: Apertus 8B vs Qwen3.5-9B | Clinical exclusion recall | 13/16 [0.57, 0.93] | 16/16 [0.81, 1.00] |
| gold: Apertus 8B vs Qwen3.5-9B | Clinical exclusion precision | 13/28 [0.30, 0.64] | 16/32 [0.34, 0.66] |
| gold: Apertus 8B vs Qwen3.5-9B | Today recall | 44/50 [0.76, 0.94] | 50/50 [0.93, 1.00] |
| gold: Apertus 8B vs Qwen3.5-9B | Deadline accuracy | 151/180 [0.78, 0.89] | 153/180 [0.79, 0.89] |
| gold: Apertus 8B vs Qwen3.5-9B | Coverage | 151/180 [0.78, 0.89] | 142/180 [0.72, 0.84] |
| gold: Apertus 8B vs Ministral 8B | Route accuracy | 170/180 [0.90, 0.97] | 177/180 [0.95, 0.99] |
| gold: Apertus 8B vs Ministral 8B | Recall of route other | 13/16 [0.57, 0.93] | 15/16 [0.72, 0.99] |
| gold: Apertus 8B vs Ministral 8B | Precision of route other | 13/14 [0.69, 0.99] | 15/16 [0.72, 0.99] |
| gold: Apertus 8B vs Ministral 8B | Clinical exclusion recall | 13/16 [0.57, 0.93] | 16/16 [0.81, 1.00] |
| gold: Apertus 8B vs Ministral 8B | Clinical exclusion precision | 13/28 [0.30, 0.64] | 16/32 [0.34, 0.66] |
| gold: Apertus 8B vs Ministral 8B | Today recall | 44/50 [0.76, 0.94] | 48/50 [0.87, 0.99] |
| gold: Apertus 8B vs Ministral 8B | Deadline accuracy | 151/180 [0.78, 0.89] | 152/180 [0.78, 0.89] |
| gold: Apertus 8B vs Ministral 8B | Coverage | 151/180 [0.78, 0.89] | 139/180 [0.71, 0.83] |
| gold: Apertus 70B vs Qwen3.5-9B | Route accuracy | 172/180 [0.91, 0.98] | 177/180 [0.95, 0.99] |
| gold: Apertus 70B vs Qwen3.5-9B | Recall of route other | 14/16 [0.64, 0.97] | 16/16 [0.81, 1.00] |
| gold: Apertus 70B vs Qwen3.5-9B | Precision of route other | 14/14 [0.78, 1.00] | 16/16 [0.81, 1.00] |
| gold: Apertus 70B vs Qwen3.5-9B | Clinical exclusion recall | 15/16 [0.72, 0.99] | 16/16 [0.81, 1.00] |
| gold: Apertus 70B vs Qwen3.5-9B | Clinical exclusion precision | 15/30 [0.33, 0.67] | 16/32 [0.34, 0.66] |
| gold: Apertus 70B vs Qwen3.5-9B | Today recall | 47/50 [0.84, 0.98] | 50/50 [0.93, 1.00] |
| gold: Apertus 70B vs Qwen3.5-9B | Deadline accuracy | 156/180 [0.81, 0.91] | 153/180 [0.79, 0.89] |
| gold: Apertus 70B vs Qwen3.5-9B | Coverage | 147/180 [0.75, 0.87] | 142/180 [0.72, 0.84] |

Paired per message (exact two-sided McNemar test on the discordant pairs):

| Set | n | route changed | route right only with B | route right only with A | p | clinical caught only with B | clinical caught only with A | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gold: Apertus 8B vs Qwen3.5-9B | 180 | 9 | 8 | 1 | 0.0391 | 3 | 0 | 0.25 |
| gold: Apertus 8B vs Ministral 8B | 180 | 10 | 8 | 1 | 0.0391 | 3 | 0 | 0.25 |
| gold: Apertus 70B vs Qwen3.5-9B | 180 | 7 | 6 | 1 | 0.125 | 1 | 0 | 1 |
