# Gap study on dev + challenge (n = 175)

| Variant | Route | Clinical flagged | Clinical out of automation | Unnoticed wrong route | Unnoticed clinical | To a person | False flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8B p3 (stored) | 154/175 | 48/53 | 48/53 | 14 | 5 | 54/175 | 6 |
| 8B p3 (fresh run, no symptom pass) | 155/175 | 48/53 | 48/53 | 14 | 5 | 56/175 | 7 |
| 8B + symptom pass, flag if >= 1 of 3 | 155/175 | 53/53 | 53/53 | 12 | 0 | 76/175 | 22 |
| 8B + symptom pass, flag if >= 2 of 3 | 155/175 | 52/53 | 52/53 | 12 | 1 | 75/175 | 22 |
| 8B + symptom pass, flag if >= 3 of 3 | 155/175 | 52/53 | 52/53 | 13 | 1 | 72/175 | 19 |
| 8B safety_first | 153/175 | 47/53 | 47/53 | 15 | 6 | 55/175 | 6 |
| 8B fewshot | 153/175 | 50/53 | 50/53 | 13 | 3 | 65/175 | 6 |
| 8B n5 | 155/175 | 48/53 | 48/53 | 14 | 5 | 56/175 | 6 |
| 70B p3 | 157/175 | 52/53 | 52/53 | 13 | 1 | 66/175 | 7 |
| 8B + 70B gate | 154/175 | 52/53 | 52/53 | 10 | 1 | 71/175 | 7 |
| 8B + symptom >= 1 + 70B gate | 155/175 | 53/53 | 53/53 | 9 | 0 | 87/175 | 22 |
| 8B + rules gate | 154/175 | 48/53 | 49/53 | 8 | 4 | 83/175 | 6 |
| 8B + symptom >= 1 + rules gate | 155/175 | 53/53 | 53/53 | 6 | 0 | 102/175 | 22 |

8B + 70B gate: 70B called for 121/175 messages
8B + symptom + 70B gate: 70B called for 99/175 messages

