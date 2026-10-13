# Route study: extended dev split (n = 427)

| Variant | Route (model) | Automatic and right | Clinical flagged | Clinical out of automation | Unnoticed wrong route | Unnoticed clinical | To a person | False flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8B base | 388/427 | 262 | 81/81 | 81/81 | 24 | 0 | 141/427 | 57 |
| 8B base + 70B SO | 388/427 | 261 | 81/81 | 81/81 | 19 | 0 | 147/427 | 57 |
| 8B base + rules gate | 388/427 | 209 | 81/81 | 81/81 | 11 | 0 | 207/427 | 57 |
| 8B p4 | 394/427 | 263 | 79/81 | 79/81 | 21 | 2 | 143/427 | 58 |
| 8B p4 + 70B SO | 394/427 | 263 | 79/81 | 79/81 | 15 | 2 | 149/427 | 58 |
| 8B p4 + rules gate | 394/427 | 213 | 79/81 | 79/81 | 11 | 2 | 203/427 | 58 |
| 8B p4fs | 395/427 | 259 | 81/81 | 81/81 | 20 | 0 | 148/427 | 58 |
| 8B p4fs + 70B SO | 395/427 | 259 | 81/81 | 81/81 | 16 | 0 | 152/427 | 58 |
| 8B p4fs + rules gate | 395/427 | 205 | 81/81 | 81/81 | 9 | 0 | 213/427 | 58 |
| 70B p3 alone | 394/427 | 286 | 79/81 | 79/81 | 25 | 2 | 116/427 | 23 |

8B base + 70B SO: 70B asked for 66 of 427 messages
8B p4 + 70B SO: 70B asked for 60 of 427 messages
8B p4fs + 70B SO: 70B asked for 65 of 427 messages

