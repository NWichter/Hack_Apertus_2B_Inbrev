# Apertus vs. keyword rules vs. rules-first hybrid

Gold `swiss_practice_inbox.jsonl`, predictions `swiss-p3-8b.jsonl`, n = 30

| Setup | Model calls | Route acc | Macro-F1 | Clinical exclusion recall | Today recall | Deadline acc |
| --- | --- | --- | --- | --- | --- | --- |
| Keyword rules | 0 | 25/30 [0.66, 0.93] | 0.786 | 4/4 [0.51, 1.00] | 5/5 [0.57, 1.00] | 16/30 [0.36, 0.70] |
| Inbrev (Apertus) | 30 | 24/30 [0.63, 0.90] | 0.787 | 4/4 [0.51, 1.00] | 5/5 [0.57, 1.00] | 14/30 [0.30, 0.64] |
| Hybrid: rules if clear, else Apertus | 12 | 22/30 [0.56, 0.86] | 0.713 | 4/4 [0.51, 1.00] | 5/5 [0.57, 1.00] | 16/30 [0.36, 0.70] |

Route, paired: Apertus right and rules wrong 3, rules right and Apertus wrong 4, exact McNemar p = 1.

Rules are clear on 18 of 30 messages: route correct rules 16/18 [0.67, 0.97], Apertus 18/18 [0.82, 1.00]. Safety cases among them (missed by the hybrid unless Apertus is asked): none.

**By gold route**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| other | 6 | 3/6 [0.19, 0.81] | 1/6 [0.03, 0.56] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] |
| appointment | 5 | 5/5 [0.57, 1.00] | 5/5 [0.57, 1.00] | – | – |
| prescription_request | 5 | 5/5 [0.57, 1.00] | 5/5 [0.57, 1.00] | – | – |
| insurer | 4 | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | – | – |
| certificate_request | 3 | 2/3 [0.21, 0.94] | 3/3 [0.44, 1.00] | – | – |
| referral_in | 3 | 3/3 [0.44, 1.00] | 3/3 [0.44, 1.00] | – | – |
| billing | 2 | 2/2 [0.34, 1.00] | 1/2 [0.09, 0.91] | – | – |
| report_received | 1 | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] | – | – |
| spam_marketing | 1 | 0/1 [0.00, 0.79] | 1/1 [0.21, 1.00] | – | – |

**By writing level**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| None | 30 | 25/30 [0.66, 0.93] | 24/30 [0.63, 0.90] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] |

**Mixed topics**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| None | 30 | 25/30 [0.66, 0.93] | 24/30 [0.63, 0.90] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] |

**By safety case type**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| None | 30 | 25/30 [0.66, 0.93] | 24/30 [0.63, 0.90] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] |

**By language**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| de | 13 | 10/13 [0.50, 0.92] | 9/13 [0.42, 0.87] | 2/2 [0.34, 1.00] | 2/2 [0.34, 1.00] |
| fr | 8 | 7/8 [0.53, 0.98] | 7/8 [0.53, 0.98] | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] |
| it | 7 | 7/7 [0.65, 1.00] | 6/7 [0.49, 0.97] | 1/1 [0.21, 1.00] | 1/1 [0.21, 1.00] |
| en | 2 | 1/2 [0.09, 0.91] | 2/2 [0.34, 1.00] | – | – |

**By generator**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| synthetic_swiss_practice | 30 | 25/30 [0.66, 0.93] | 24/30 [0.63, 0.90] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] |

