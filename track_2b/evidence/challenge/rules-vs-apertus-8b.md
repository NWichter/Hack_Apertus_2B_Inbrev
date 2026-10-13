# Apertus vs. keyword rules vs. rules-first hybrid

Gold `challenge.v1.jsonl`, predictions `chl-p3-8b.jsonl`, n = 115

| Setup | Model calls | Route acc | Macro-F1 | Clinical exclusion recall | Today recall | Deadline acc |
| --- | --- | --- | --- | --- | --- | --- |
| Keyword rules | 0 | 87/115 [0.67, 0.83] | 0.759 | 31/44 [0.56, 0.82] | 45/59 [0.64, 0.85] | 86/115 [0.66, 0.82] |
| Inbrev (Apertus) | 115 | 103/115 [0.83, 0.94] | 0.902 | 41/44 [0.82, 0.98] | 56/59 [0.86, 0.98] | 107/115 [0.87, 0.96] |
| Hybrid: rules if clear, else Apertus | 84 | 99/115 [0.79, 0.91] | 0.867 | 36/44 [0.68, 0.90] | 52/59 [0.77, 0.94] | 102/115 [0.82, 0.93] |

Route, paired: Apertus right and rules wrong 20, rules right and Apertus wrong 4, exact McNemar p = 0.00154.

Rules are clear on 31 of 115 messages: route correct rules 22/31 [0.53, 0.84], Apertus 26/31 [0.67, 0.93]. Safety cases among them (missed by the hybrid unless Apertus is asked): chl-011, chl-058, chl-069, chl-105, chl-107, chl-113, chl-119.

**By gold route**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| appointment | 20 | 18/20 [0.70, 0.97] | 20/20 [0.84, 1.00] | 11/14 [0.52, 0.92] | 14/14 [0.78, 1.00] |
| other | 20 | 9/20 [0.26, 0.66] | 9/20 [0.26, 0.66] | 7/12 [0.32, 0.81] | 12/12 [0.76, 1.00] |
| prescription_request | 16 | 15/16 [0.72, 0.99] | 16/16 [0.81, 1.00] | 7/8 [0.53, 0.98] | 7/8 [0.53, 0.98] |
| certificate_request | 15 | 13/15 [0.62, 0.96] | 15/15 [0.80, 1.00] | 3/7 [0.16, 0.75] | 5/7 [0.36, 0.92] |
| insurer | 12 | 10/12 [0.55, 0.95] | 12/12 [0.76, 1.00] | – | – |
| billing | 10 | 9/10 [0.60, 0.98] | 9/10 [0.60, 0.98] | 3/3 [0.44, 1.00] | 3/3 [0.44, 1.00] |
| report_received | 10 | 5/10 [0.24, 0.76] | 10/10 [0.72, 1.00] | – | – |
| referral_in | 8 | 5/8 [0.31, 0.86] | 8/8 [0.68, 1.00] | – | – |
| spam_marketing | 4 | 3/4 [0.30, 0.95] | 4/4 [0.51, 1.00] | – | – |

**By writing level**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| clean | 46 | 37/46 [0.67, 0.89] | 42/46 [0.80, 0.97] | 6/9 [0.35, 0.88] | 9/9 [0.70, 1.00] |
| typos | 32 | 19/32 [0.42, 0.74] | 28/32 [0.72, 0.95] | 8/11 [0.43, 0.90] | 10/11 [0.62, 0.98] |
| dialect | 19 | 16/19 [0.62, 0.94] | 15/19 [0.57, 0.91] | 10/12 [0.55, 0.95] | 11/12 [0.65, 0.99] |
| non_native | 18 | 15/18 [0.61, 0.94] | 18/18 [0.82, 1.00] | 7/12 [0.32, 0.81] | 11/12 [0.65, 0.99] |

**Mixed topics**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| False | 107 | 82/107 [0.68, 0.84] | 97/107 [0.84, 0.95] | 29/42 [0.54, 0.81] | 39/42 [0.81, 0.98] |
| True | 8 | 5/8 [0.31, 0.86] | 6/8 [0.41, 0.93] | 2/2 [0.34, 1.00] | 2/2 [0.34, 1.00] |

**By safety case type**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| medical_trap | 39 | 27/39 [0.54, 0.81] | 35/39 [0.76, 0.96] | – | – |
| none | 32 | 24/32 [0.58, 0.87] | 29/32 [0.76, 0.97] | – | – |
| acute_incidental | 27 | 22/27 [0.63, 0.92] | 26/27 [0.82, 0.99] | 18/27 [0.48, 0.81] | 24/27 [0.72, 0.96] |
| acute_explicit | 17 | 14/17 [0.59, 0.94] | 13/17 [0.53, 0.90] | 13/17 [0.53, 0.90] | 17/17 [0.82, 1.00] |

**By language**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| de | 57 | 46/57 [0.69, 0.89] | 50/57 [0.77, 0.94] | 18/26 [0.50, 0.83] | 24/26 [0.76, 0.98] |
| fr | 31 | 22/31 [0.53, 0.84] | 27/31 [0.71, 0.95] | 7/10 [0.40, 0.89] | 10/10 [0.72, 1.00] |
| it | 21 | 14/21 [0.45, 0.83] | 20/21 [0.77, 0.99] | 4/6 [0.30, 0.90] | 5/6 [0.44, 0.97] |
| en | 6 | 5/6 [0.44, 0.97] | 6/6 [0.61, 1.00] | 2/2 [0.34, 1.00] | 2/2 [0.34, 1.00] |

**By generator**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| nemotron | 115 | 87/115 [0.67, 0.83] | 103/115 [0.83, 0.94] | 31/44 [0.56, 0.82] | 41/44 [0.82, 0.98] |

