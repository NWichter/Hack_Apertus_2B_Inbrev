# Route study: hold-out 2, 127 undisputed (n = 127)

| Variant | Route (model) | Automatic and right | Clinical flagged | Clinical out of automation | Unnoticed wrong route | Unnoticed clinical | To a person | False flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8B base | 123/127 | 97 | 10/10 | 10/10 | 3 | 0 | 27/127 | 12 |
| 8B base + 70B SO | 123/127 | 95 | 10/10 | 10/10 | 1 | 0 | 31/127 | 12 |
| 8B base + rules gate | 123/127 | 78 | 10/10 | 10/10 | 0 | 0 | 49/127 | 12 |
| 8B p4 | 122/127 | 94 | 10/10 | 10/10 | 3 | 0 | 30/127 | 11 |
| 8B p4 + 70B SO | 122/127 | 92 | 10/10 | 10/10 | 0 | 0 | 35/127 | 11 |
| 8B p4 + rules gate | 122/127 | 76 | 10/10 | 10/10 | 0 | 0 | 51/127 | 11 |
| 8B p4fs | 122/127 | 98 | 10/10 | 10/10 | 3 | 0 | 26/127 | 11 |
| 8B p4fs + 70B SO | 122/127 | 98 | 10/10 | 10/10 | 0 | 0 | 29/127 | 11 |
| 8B p4fs + rules gate | 122/127 | 79 | 10/10 | 10/10 | 0 | 0 | 48/127 | 11 |
| 70B p3 alone | 126/127 | 106 | 10/10 | 10/10 | 1 | 0 | 20/127 | 4 |
| Qwen3.5-9B (comparison) | 125/127 | 111 | 10/10 | 10/10 | 0 | 0 | 16/127 | 4 |

8B base + 70B SO: 70B asked for 22 of 127 messages
8B p4 + 70B SO: 70B asked for 21 of 127 messages
8B p4fs + 70B SO: 70B asked for 22 of 127 messages

