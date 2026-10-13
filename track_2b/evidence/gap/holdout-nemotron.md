# Gap study on nemotron (n = 42)

| Variant | Route (model) | Automatic and right | Clinical flagged | Clinical out of automation | Unnoticed wrong route | Unnoticed clinical | To a person | False flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8B p3 (stored) | 39/42 | 30 | 8/8 | 8/8 | 2 | 0 | 10/42 | 2 |
| 8B p3 (fresh run, no symptom pass) | 39/42 | 30 | 8/8 | 8/8 | 2 | 0 | 10/42 | 2 |
| 8B + symptom pass, flag if >= 1 of 3 | 39/42 | 24 | 8/8 | 8/8 | 2 | 0 | 16/42 | 8 |
| 8B + symptom pass, flag if >= 2 of 3 | 39/42 | 24 | 8/8 | 8/8 | 2 | 0 | 16/42 | 8 |
| 8B + symptom pass, flag if >= 3 of 3 | 39/42 | 26 | 8/8 | 8/8 | 2 | 0 | 14/42 | 6 |
| 70B p3 | 37/42 | 27 | 8/8 | 8/8 | 2 | 0 | 13/42 | 1 |
| 8B + 70B gate | 39/42 | 26 | 8/8 | 8/8 | 1 | 0 | 15/42 | 2 |
| 8B + symptom >= 1 + 70B gate | 39/42 | 20 | 8/8 | 8/8 | 1 | 0 | 21/42 | 8 |
| 8B + rules gate | 39/42 | 22 | 8/8 | 8/8 | 1 | 0 | 19/42 | 2 |
| 8B + symptom >= 1 + rules gate | 39/42 | 17 | 8/8 | 8/8 | 1 | 0 | 24/42 | 8 |

8B + 70B gate: 70B called for 32/42 messages
8B + symptom + 70B gate: 70B called for 26/42 messages

