# Apertus vs. keyword rules vs. rules-first hybrid

Gold `merged.v0.jsonl`, predictions `gold-p3-8b.jsonl`, n = 180

| Setup | Model calls | Route acc | Macro-F1 | Clinical exclusion recall | Today recall | Deadline acc |
| --- | --- | --- | --- | --- | --- | --- |
| Keyword rules | 0 | 143/180 [0.73, 0.85] | 0.763 | 7/16 [0.23, 0.67] | 38/50 [0.63, 0.86] | 122/180 [0.61, 0.74] |
| Inbrev (Apertus) | 180 | 170/180 [0.90, 0.97] | 0.943 | 13/16 [0.57, 0.93] | 44/50 [0.76, 0.94] | 151/180 [0.78, 0.89] |
| Hybrid: rules if clear, else Apertus | 94 | 161/180 [0.84, 0.93] | 0.876 | 10/16 [0.39, 0.82] | 41/50 [0.69, 0.90] | 137/180 [0.69, 0.82] |

Route, paired: Apertus right and rules wrong 32, rules right and Apertus wrong 5, exact McNemar p = 7.43e-06.

Rules are clear on 86 of 180 messages: route correct rules 74/86 [0.77, 0.92], Apertus 83/86 [0.90, 0.99]. Safety cases among them (missed by the hybrid unless Apertus is asked): syn-005, syn-026, syn-118, syn-154, syn-180.

**By gold route**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| appointment | 26 | 22/26 [0.66, 0.94] | 24/26 [0.76, 0.98] | 2/5 [0.12, 0.77] | 3/5 [0.23, 0.88] |
| report_received | 26 | 24/26 [0.76, 0.98] | 26/26 [0.87, 1.00] | – | – |
| insurer | 24 | 16/24 [0.47, 0.82] | 24/24 [0.86, 1.00] | – | – |
| prescription_request | 22 | 21/22 [0.78, 0.99] | 22/22 [0.85, 1.00] | 1/3 [0.06, 0.79] | 3/3 [0.44, 1.00] |
| certificate_request | 18 | 17/18 [0.74, 0.99] | 18/18 [0.82, 1.00] | 0/2 [0.00, 0.66] | 2/2 [0.34, 1.00] |
| referral_in | 18 | 15/18 [0.61, 0.94] | 17/18 [0.74, 0.99] | – | – |
| billing | 16 | 15/16 [0.72, 0.99] | 13/16 [0.57, 0.93] | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] |
| other | 16 | 9/16 [0.33, 0.77] | 13/16 [0.57, 0.93] | 3/5 [0.23, 0.88] | 4/5 [0.38, 0.96] |
| spam_marketing | 14 | 4/14 [0.12, 0.55] | 13/14 [0.69, 0.99] | – | – |

**By writing level**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| clean | 112 | 86/112 [0.68, 0.84] | 106/112 [0.89, 0.98] | 5/6 [0.44, 0.97] | 5/6 [0.44, 0.97] |
| typos | 37 | 29/37 [0.63, 0.89] | 33/37 [0.75, 0.96] | 1/4 [0.05, 0.70] | 2/4 [0.15, 0.85] |
| non_native | 17 | 16/17 [0.73, 0.99] | 17/17 [0.82, 1.00] | 1/5 [0.04, 0.62] | 5/5 [0.57, 1.00] |
| dialect | 14 | 12/14 [0.60, 0.96] | 14/14 [0.78, 1.00] | 0/1 [0.00, 0.79] | 1/1 [0.21, 1.00] |

**Mixed topics**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| False | 162 | 129/162 [0.73, 0.85] | 155/162 [0.91, 0.98] | 6/13 [0.23, 0.71] | 10/13 [0.50, 0.92] |
| True | 18 | 14/18 [0.55, 0.91] | 15/18 [0.61, 0.94] | 1/3 [0.06, 0.79] | 3/3 [0.44, 1.00] |

**By safety case type**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| none | 150 | 119/150 [0.72, 0.85] | 141/150 [0.89, 0.97] | – | – |
| medical_trap | 14 | 11/14 [0.52, 0.92] | 13/14 [0.69, 0.99] | – | – |
| acute_incidental | 9 | 8/9 [0.57, 0.98] | 9/9 [0.70, 1.00] | 3/9 [0.12, 0.65] | 7/9 [0.45, 0.94] |
| acute_explicit | 7 | 5/7 [0.36, 0.92] | 7/7 [0.65, 1.00] | 4/7 [0.25, 0.84] | 6/7 [0.49, 0.97] |

**By language**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| de | 99 | 80/99 [0.72, 0.87] | 94/99 [0.89, 0.98] | 4/7 [0.25, 0.84] | 6/7 [0.49, 0.97] |
| fr | 45 | 36/45 [0.66, 0.89] | 44/45 [0.88, 1.00] | 0/3 [0.00, 0.56] | 2/3 [0.21, 0.94] |
| it | 27 | 19/27 [0.52, 0.84] | 24/27 [0.72, 0.96] | 2/5 [0.12, 0.77] | 4/5 [0.38, 0.96] |
| en | 9 | 8/9 [0.57, 0.98] | 8/9 [0.57, 0.98] | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] |

**By generator**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| claude | 90 | 74/90 [0.73, 0.89] | 85/90 [0.88, 0.98] | 3/9 [0.12, 0.65] | 6/9 [0.35, 0.88] |
| codex | 90 | 69/90 [0.67, 0.84] | 85/90 [0.88, 0.98] | 4/7 [0.25, 0.84] | 7/7 [0.65, 1.00] |

