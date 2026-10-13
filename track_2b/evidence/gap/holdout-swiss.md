# Gap study on swiss (n = 30)

| Variant | Route (model) | Automatic and right | Clinical flagged | Clinical out of automation | Unnoticed wrong route | Unnoticed clinical | To a person | False flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8B p3 (stored) | 24/30 | 23 | 4/4 | 4/4 | 2 | 0 | 5/30 | 0 |
| 8B p3 (fresh run, no symptom pass) | 24/30 | 23 | 4/4 | 4/4 | 2 | 0 | 5/30 | 0 |
| 8B + symptom pass, flag if >= 1 of 3 | 24/30 | 19 | 4/4 | 4/4 | 2 | 0 | 9/30 | 4 |
| 8B + symptom pass, flag if >= 2 of 3 | 24/30 | 19 | 4/4 | 4/4 | 2 | 0 | 9/30 | 4 |
| 8B + symptom pass, flag if >= 3 of 3 | 24/30 | 19 | 4/4 | 4/4 | 2 | 0 | 9/30 | 4 |
| 70B p3 | 28/30 | 24 | 4/4 | 4/4 | 2 | 0 | 4/30 | 0 |
| 8B + 70B gate | 24/30 | 22 | 4/4 | 4/4 | 1 | 0 | 7/30 | 0 |
| 8B + symptom >= 1 + 70B gate | 24/30 | 18 | 4/4 | 4/4 | 1 | 0 | 11/30 | 4 |
| 8B + rules gate | 24/30 | 21 | 4/4 | 4/4 | 0 | 0 | 9/30 | 0 |
| 8B + symptom >= 1 + rules gate | 24/30 | 18 | 4/4 | 4/4 | 0 | 0 | 12/30 | 4 |

8B + 70B gate: 70B called for 25/30 messages
8B + symptom + 70B gate: 70B called for 21/30 messages

