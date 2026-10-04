# Apertus vs. keyword rules vs. rules-first hybrid

Gold `dev.jsonl`, predictions `dev-p3a-8b.jsonl`, n = 60

| Setup | Model calls | Route acc | Macro-F1 | Clinical exclusion recall | Today recall | Deadline acc |
| --- | --- | --- | --- | --- | --- | --- |
| Keyword rules | 0 | 41/60 [0.56, 0.79] | 0.726 | 6/9 [0.35, 0.88] | 11/19 [0.36, 0.77] | 40/60 [0.54, 0.77] |
| Inbrev (Apertus) | 60 | 51/60 [0.74, 0.92] | 0.890 | 7/9 [0.45, 0.94] | 17/19 [0.69, 0.97] | 49/60 [0.70, 0.89] |
| Hybrid: rules if clear, else Apertus | 37 | 48/60 [0.68, 0.88] | 0.858 | 7/9 [0.45, 0.94] | 16/19 [0.62, 0.94] | 46/60 [0.65, 0.86] |

Route, paired: Apertus right and rules wrong 12, rules right and Apertus wrong 2, exact McNemar p = 0.0129.

Rules are clear on 23 of 60 messages: route correct rules 18/23 [0.58, 0.90], Apertus 21/23 [0.73, 0.98]. Safety cases among them (missed by the hybrid unless Apertus is asked): dev-021.

**By gold route**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| other | 20 | 7/20 [0.18, 0.57] | 11/20 [0.34, 0.74] | 3/4 [0.30, 0.95] | 4/4 [0.51, 1.00] |
| appointment | 6 | 6/6 [0.61, 1.00] | 6/6 [0.61, 1.00] | 3/3 [0.44, 1.00] | 3/3 [0.44, 1.00] |
| certificate_request | 6 | 5/6 [0.44, 0.97] | 6/6 [0.61, 1.00] | 0/1 [0.00, 0.79] | 0/1 [0.00, 0.79] |
| insurer | 6 | 5/6 [0.44, 0.97] | 6/6 [0.61, 1.00] | – | – |
| report_received | 6 | 3/6 [0.19, 0.81] | 6/6 [0.61, 1.00] | – | – |
| prescription_request | 5 | 5/5 [0.57, 1.00] | 5/5 [0.57, 1.00] | 0/1 [0.00, 0.79] | 0/1 [0.00, 0.79] |
| billing | 4 | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | – | – |
| referral_in | 4 | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | – | – |
| spam_marketing | 3 | 2/3 [0.21, 0.94] | 3/3 [0.44, 1.00] | – | – |

**By writing level**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| clean | 33 | 19/33 [0.41, 0.73] | 27/33 [0.66, 0.91] | 3/3 [0.44, 1.00] | 3/3 [0.44, 1.00] |
| typos | 16 | 13/16 [0.57, 0.93] | 14/16 [0.64, 0.97] | 3/5 [0.23, 0.88] | 4/5 [0.38, 0.96] |
| non_native | 6 | 5/6 [0.44, 0.97] | 6/6 [0.61, 1.00] | 0/1 [0.00, 0.79] | 0/1 [0.00, 0.79] |
| dialect | 5 | 4/5 [0.38, 0.96] | 4/5 [0.38, 0.96] | – | – |

**Mixed topics**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| False | 54 | 39/54 [0.59, 0.82] | 47/54 [0.76, 0.94] | 4/7 [0.25, 0.84] | 5/7 [0.36, 0.92] |
| True | 6 | 2/6 [0.10, 0.70] | 4/6 [0.30, 0.90] | 2/2 [0.34, 1.00] | 2/2 [0.34, 1.00] |

**By safety case type**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| none | 46 | 33/46 [0.57, 0.83] | 39/46 [0.72, 0.92] | – | – |
| acute_explicit | 5 | 2/5 [0.12, 0.77] | 4/5 [0.38, 0.96] | 5/5 [0.57, 1.00] | 5/5 [0.57, 1.00] |
| medical_trap | 5 | 2/5 [0.12, 0.77] | 4/5 [0.38, 0.96] | – | – |
| acute_incidental | 4 | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | 1/4 [0.05, 0.70] | 2/4 [0.15, 0.85] |

**By language**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| de | 33 | 25/33 [0.59, 0.87] | 28/33 [0.69, 0.93] | 2/4 [0.15, 0.85] | 3/4 [0.30, 0.95] |
| fr | 15 | 8/15 [0.30, 0.75] | 13/15 [0.62, 0.96] | 3/3 [0.44, 1.00] | 3/3 [0.44, 1.00] |
| it | 9 | 6/9 [0.35, 0.88] | 7/9 [0.45, 0.94] | 1/2 [0.09, 0.91] | 1/2 [0.09, 0.91] |
| en | 3 | 2/3 [0.21, 0.94] | 3/3 [0.44, 1.00] | – | – |

**By generator**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| nemotron | 60 | 41/60 [0.56, 0.79] | 51/60 [0.74, 0.92] | 6/9 [0.35, 0.88] | 7/9 [0.45, 0.94] |

