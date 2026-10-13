# Gap study on gold (n = 180)

| Variant | Route (model) | Automatic and right | Clinical flagged | Clinical out of automation | Unnoticed wrong route | Unnoticed clinical | To a person | False flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8B p3 (stored) | 170/180 | 142 | 13/16 | 13/16 | 9 | 3 | 29/180 | 15 |
| 8B p3 (fresh run, no symptom pass) | 170/180 | 142 | 14/16 | 14/16 | 8 | 2 | 30/180 | 15 |
| 8B + symptom pass, flag if >= 1 of 3 | 170/180 | 132 | 16/16 | 16/16 | 8 | 0 | 40/180 | 23 |
| 8B + symptom pass, flag if >= 2 of 3 | 170/180 | 132 | 16/16 | 16/16 | 8 | 0 | 40/180 | 23 |
| 8B + symptom pass, flag if >= 3 of 3 | 170/180 | 134 | 16/16 | 16/16 | 8 | 0 | 38/180 | 21 |
| 70B p3 | 172/180 | 139 | 15/16 | 15/16 | 8 | 1 | 33/180 | 15 |
| 8B + 70B gate | 170/180 | 136 | 16/16 | 16/16 | 6 | 0 | 38/180 | 15 |
| 8B + symptom >= 1 + 70B gate | 170/180 | 128 | 16/16 | 16/16 | 6 | 0 | 46/180 | 23 |
| 8B + rules gate | 170/180 | 115 | 14/16 | 14/16 | 4 | 2 | 61/180 | 15 |
| 8B + symptom >= 1 + rules gate | 170/180 | 107 | 16/16 | 16/16 | 4 | 0 | 69/180 | 23 |

8B + 70B gate: 70B called for 150/180 messages
8B + symptom + 70B gate: 70B called for 140/180 messages

