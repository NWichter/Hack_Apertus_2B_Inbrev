# Route study: hold-out 2, all 146 (n = 146)

| Variant | Route (model) | Automatic and right | Clinical flagged | Clinical out of automation | Unnoticed wrong route | Unnoticed clinical | To a person | False flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8B base | 138/146 | 101 | 14/14 | 14/14 | 5 | 0 | 40/146 | 21 |
| 8B base + 70B SO | 138/146 | 98 | 14/14 | 14/14 | 3 | 0 | 45/146 | 21 |
| 8B base + rules gate | 138/146 | 80 | 14/14 | 14/14 | 0 | 0 | 66/146 | 21 |
| 8B p4 | 137/146 | 99 | 14/14 | 14/14 | 5 | 0 | 42/146 | 19 |
| 8B p4 + 70B SO | 137/146 | 96 | 14/14 | 14/14 | 2 | 0 | 48/146 | 19 |
| 8B p4 + rules gate | 137/146 | 79 | 14/14 | 14/14 | 0 | 0 | 67/146 | 19 |
| 8B p4fs | 137/146 | 102 | 14/14 | 14/14 | 5 | 0 | 39/146 | 19 |
| 8B p4fs + 70B SO | 137/146 | 101 | 14/14 | 14/14 | 2 | 0 | 43/146 | 19 |
| 8B p4fs + rules gate | 137/146 | 81 | 14/14 | 14/14 | 0 | 0 | 65/146 | 19 |
| 70B p3 alone | 143/146 | 113 | 14/14 | 14/14 | 3 | 0 | 30/146 | 8 |
| Qwen3.5-9B (comparison) | 143/146 | 122 | 14/14 | 14/14 | 0 | 0 | 24/146 | 7 |

8B base + 70B SO: 70B asked for 26 of 146 messages
8B p4 + 70B SO: 70B asked for 25 of 146 messages
8B p4fs + 70B SO: 70B asked for 26 of 146 messages

