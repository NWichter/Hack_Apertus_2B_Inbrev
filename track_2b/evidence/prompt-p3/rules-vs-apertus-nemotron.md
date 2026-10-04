# Apertus vs. keyword rules vs. rules-first hybrid

Gold `nemotron.jsonl`, predictions `nemotron-p3-8b.jsonl`, n = 42

| Setup | Model calls | Route acc | Macro-F1 | Clinical exclusion recall | Today recall | Deadline acc |
| --- | --- | --- | --- | --- | --- | --- |
| Keyword rules | 0 | 32/42 [0.61, 0.87] | 0.725 | 6/8 [0.41, 0.93] | 15/18 [0.61, 0.94] | 34/42 [0.67, 0.90] |
| Inbrev (Apertus) | 42 | 39/42 [0.81, 0.98] | 0.860 | 8/8 [0.68, 1.00] | 17/18 [0.74, 0.99] | 37/42 [0.75, 0.95] |
| Hybrid: rules if clear, else Apertus | 25 | 38/42 [0.78, 0.96] | 0.826 | 6/8 [0.41, 0.93] | 15/18 [0.61, 0.94] | 36/42 [0.72, 0.93] |

Route, paired: Apertus right and rules wrong 8, rules right and Apertus wrong 1, exact McNemar p = 0.0391.

Rules are clear on 17 of 42 messages: route correct rules 15/17 [0.66, 0.97], Apertus 16/17 [0.73, 0.99]. Safety cases among them (missed by the hybrid unless Apertus is asked): nem-023, nem-039.

**By gold route**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| appointment | 7 | 6/7 [0.49, 0.97] | 7/7 [0.65, 1.00] | 3/3 [0.44, 1.00] | 3/3 [0.44, 1.00] |
| prescription_request | 6 | 6/6 [0.61, 1.00] | 6/6 [0.61, 1.00] | 1/2 [0.09, 0.91] | 2/2 [0.34, 1.00] |
| report_received | 6 | 4/6 [0.30, 0.90] | 6/6 [0.61, 1.00] | – | – |
| certificate_request | 5 | 5/5 [0.57, 1.00] | 5/5 [0.57, 1.00] | 0/1 [0.00, 0.79] | 1/1 [0.21, 1.00] |
| insurer | 5 | 2/5 [0.12, 0.77] | 5/5 [0.57, 1.00] | – | – |
| referral_in | 4 | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | – | – |
| billing | 3 | 3/3 [0.44, 1.00] | 3/3 [0.44, 1.00] | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] |
| other | 3 | 1/3 [0.06, 0.79] | 0/3 [0.00, 0.56] | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] |
| spam_marketing | 3 | 1/3 [0.06, 0.79] | 3/3 [0.44, 1.00] | – | – |

**By writing level**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| clean | 27 | 17/27 [0.44, 0.78] | 25/27 [0.77, 0.98] | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] |
| typos | 8 | 8/8 [0.68, 1.00] | 8/8 [0.68, 1.00] | 2/3 [0.21, 0.94] | 3/3 [0.44, 1.00] |
| non_native | 4 | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | 2/3 [0.21, 0.94] | 3/3 [0.44, 1.00] |
| dialect | 3 | 3/3 [0.44, 1.00] | 2/3 [0.21, 0.94] | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] |

**Mixed topics**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| False | 38 | 29/38 [0.61, 0.87] | 36/38 [0.83, 0.99] | 6/8 [0.41, 0.93] | 8/8 [0.68, 1.00] |
| True | 4 | 3/4 [0.30, 0.95] | 3/4 [0.30, 0.95] | – | – |

**By safety case type**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| none | 27 | 19/27 [0.52, 0.84] | 26/27 [0.82, 0.99] | – | – |
| medical_trap | 7 | 5/7 [0.36, 0.92] | 6/7 [0.49, 0.97] | – | – |
| acute_incidental | 5 | 5/5 [0.57, 1.00] | 5/5 [0.57, 1.00] | 3/5 [0.23, 0.88] | 5/5 [0.57, 1.00] |
| acute_explicit | 3 | 3/3 [0.44, 1.00] | 2/3 [0.21, 0.94] | 3/3 [0.44, 1.00] | 3/3 [0.44, 1.00] |

**By language**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| de | 23 | 18/23 [0.58, 0.90] | 21/23 [0.73, 0.98] | 4/6 [0.30, 0.90] | 6/6 [0.61, 1.00] |
| fr | 10 | 8/10 [0.49, 0.94] | 9/10 [0.60, 0.98] | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] |
| it | 7 | 4/7 [0.25, 0.84] | 7/7 [0.65, 1.00] | – | – |
| en | 2 | 2/2 [0.34, 1.00] | 2/2 [0.34, 1.00] | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] |

**By generator**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| nemotron | 42 | 32/42 [0.61, 0.87] | 39/42 [0.81, 0.98] | 6/8 [0.41, 0.93] | 8/8 [0.68, 1.00] |

