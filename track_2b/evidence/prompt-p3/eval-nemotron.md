# Inbrev evaluation

Gold: `nemotron.jsonl`, n = 42

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| majority | 0.167 | 0.032 | 0.000 | – | 1.000 | 0.429 | 0.429 | 1.000 | 0.167 | 0.000 | – | – |
| keywords | 0.762 | 0.725 | 0.750 | 0.857 | 0.833 | 0.750 | 0.810 | 1.000 | 0.762 | 0.000 | – | – |
| tfidf_logreg | 0.571 | 0.546 | 0.250 | 0.500 | 0.667 | 0.667 | 0.524 | 1.000 | 0.571 | 0.000 | – | – |
| nemotron-p2-8b | 0.905 | 0.838 | 1.000 | 0.889 | 0.944 | 1.000 | 0.905 | 0.976 | 0.902 | 0.729 | 1433/691 | 1.664 |
| nemotron-p3-8b | 0.929 | 0.860 | 1.000 | 0.800 | 0.944 | 1.000 | 0.881 | 1.000 | 0.929 | 0.725 | 1635/665 | 1.659 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| majority | 7/42 [0.08, 0.31] | 0/8 [0.00, 0.32] | – | 18/18 [0.82, 1.00] | 18/42 [0.29, 0.58] | 42/42 [0.92, 1.00] |
| keywords | 32/42 [0.61, 0.87] | 6/8 [0.41, 0.93] | 6/7 [0.49, 0.97] | 15/18 [0.61, 0.94] | 34/42 [0.67, 0.90] | 42/42 [0.92, 1.00] |
| tfidf_logreg | 24/42 [0.42, 0.71] | 2/8 [0.07, 0.59] | 2/4 [0.15, 0.85] | 12/18 [0.44, 0.84] | 22/42 [0.38, 0.67] | 42/42 [0.92, 1.00] |
| nemotron-p2-8b | 38/42 [0.78, 0.96] | 8/8 [0.68, 1.00] | 8/9 [0.57, 0.98] | 17/18 [0.74, 0.99] | 38/42 [0.78, 0.96] | 41/42 [0.88, 1.00] |
| nemotron-p3-8b | 39/42 [0.81, 0.98] | 8/8 [0.68, 1.00] | 8/10 [0.49, 0.94] | 17/18 [0.74, 0.99] | 37/42 [0.75, 0.95] | 42/42 [0.92, 1.00] |

## nemotron-p2-8b

Safety missed: none · abstain on gold-ambiguous: 0/2 · all-correct on covered: 0.805

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 126, "sample_error_kinds": [], "prompt_tokens_mean": 1433.0714285714287, "completion_tokens_mean": 690.6904761904761, "latency_mean_s": 1.6638095238095238, "latency_p95_s": 2.44, "quote_status": {"route:exact": 123, "exact": 426, "dropped": 65, "normalized": 20, "route:missing": 3, "fuzzy": 16}, "lexical_only_safety": 1}`

Route F1: report_received 0.92, appointment 1.00, prescription_request 1.00, insurer 0.91, referral_in 1.00, certificate_request 0.91, billing 1.00, spam_marketing 0.80, other 0.00

Confusions (gold->pred): other->insurer ×1, spam_marketing->other ×1, other->certificate_request ×1, other->report_received ×1

Coverage curve: ≥1.00: cov 1.00 acc 0.905

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 23 | 20/23 [0.68, 0.95] | 0.913 | 6/6 [0.61, 1.00] | 0.957 |
| fr | 10 | 9/10 [0.60, 0.98] | 0.800 | 1/1 [0.21, 1.00] | 1.000 |
| it | 7 | 7/7 [0.65, 1.00] | 1.000 | – | 1.000 |
| en | 2 | 2/2 [0.34, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 1.000 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 27 | 24/27 [0.72, 0.96] | 0.889 | 1/1 [0.21, 1.00] | 1.000 |
| typos | 8 | 8/8 [0.68, 1.00] | 1.000 | 3/3 [0.44, 1.00] | 1.000 |
| non_native | 4 | 4/4 [0.51, 1.00] | 0.750 | 3/3 [0.44, 1.00] | 1.000 |
| dialect | 3 | 2/3 [0.21, 0.94] | 1.000 | 1/1 [0.21, 1.00] | 0.667 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 19 | 16/19 [0.62, 0.94] | 0.947 | 4/4 [0.51, 1.00] | 1.000 |
| web_form | 10 | 9/10 [0.60, 0.98] | 0.900 | 4/4 [0.51, 1.00] | 0.900 |
| hin_mail | 9 | 9/9 [0.70, 1.00] | 0.889 | – | 1.000 |
| fax | 4 | 4/4 [0.51, 1.00] | 0.750 | – | 1.000 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 27 | 25/27 [0.77, 0.98] | 0.889 | – | 0.963 |
| medical_trap | 7 | 6/7 [0.49, 0.97] | 0.857 | – | 1.000 |
| acute_incidental | 5 | 5/5 [0.57, 1.00] | 1.000 | 5/5 [0.57, 1.00] | 1.000 |
| acute_explicit | 3 | 2/3 [0.21, 0.94] | 1.000 | 3/3 [0.44, 1.00] | 1.000 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 159 | 110 | 98 | 0.891 | 0.616 | 0.729 |
| fields.amount | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| fields.appointment_action | 7 | 0 | 0 | – | 0.000 | 0.000 |
| fields.certificate_type | 5 | 4 | 3 | 0.750 | 0.600 | 0.667 |
| fields.creditor | 3 | 3 | 2 | 0.667 | 0.667 | 0.667 |
| fields.examination_date | 6 | 5 | 3 | 0.600 | 0.500 | 0.545 |
| fields.insurer_reference | 4 | 0 | 0 | – | 0.000 | 0.000 |
| fields.invoice_number | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| fields.medication | 6 | 5 | 4 | 0.800 | 0.667 | 0.727 |
| fields.period | 5 | 2 | 1 | 0.500 | 0.200 | 0.286 |
| fields.pharmacy | 5 | 2 | 2 | 1.000 | 0.400 | 0.571 |
| fields.referral_reason | 4 | 4 | 2 | 0.500 | 0.500 | 0.500 |
| fields.referring_physician | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| fields.report_type | 6 | 4 | 4 | 1.000 | 0.667 | 0.800 |
| fields.requested_dates | 7 | 2 | 2 | 1.000 | 0.286 | 0.444 |
| fields.requested_document | 5 | 5 | 3 | 0.600 | 0.600 | 0.600 |
| fields.sender_institution | 6 | 2 | 2 | 1.000 | 0.333 | 0.500 |
| fields.topic | 3 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| patient.ahv_number | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 31 | 28 | 28 | 1.000 | 0.903 | 0.949 |
| patient.insurance_number | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| patient.insurer | 6 | 3 | 3 | 1.000 | 0.500 | 0.667 |
| patient.name | 36 | 26 | 25 | 0.962 | 0.694 | 0.806 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| nem-006 | de | clean | other / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| nem-009 | de | clean | referral_in / today / False | referral_in / none / False | {'referral_in': 3} |  |
| nem-010 | de | clean | spam_marketing / none / False | other / none / False | {'other': 3} |  |
| nem-018 | fr | clean | other / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| nem-026 | de | non_native | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| nem-030 | fr | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| nem-035 | de | dialect | other / today / True | report_received / today / True | {'report_received': 3} |  |
| nem-044 | fr | clean | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |

## nemotron-p3-8b

Safety missed: none · abstain on gold-ambiguous: 0/2 · all-correct on covered: 0.786

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 126, "sample_error_kinds": [], "prompt_tokens_mean": 1635.0714285714287, "completion_tokens_mean": 665.2380952380952, "latency_mean_s": 1.6585714285714286, "latency_p95_s": 2.416, "quote_status": {"route:exact": 120, "exact": 394, "dropped": 62, "route:normalized": 1, "route:missing": 2, "fuzzy": 15, "normalized": 16, "route:fuzzy": 3}, "lexical_only_safety": 1}`

Route F1: report_received 0.92, appointment 1.00, prescription_request 1.00, insurer 0.91, referral_in 1.00, certificate_request 0.91, billing 1.00, spam_marketing 1.00, other 0.00

Confusions (gold->pred): other->insurer ×1, other->certificate_request ×1, other->report_received ×1

Coverage curve: ≥1.00: cov 1.00 acc 0.929

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 23 | 21/23 [0.73, 0.98] | 0.870 | 6/6 [0.61, 1.00] | 1.000 |
| fr | 10 | 9/10 [0.60, 0.98] | 0.800 | 1/1 [0.21, 1.00] | 1.000 |
| it | 7 | 7/7 [0.65, 1.00] | 1.000 | – | 1.000 |
| en | 2 | 2/2 [0.34, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 1.000 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 27 | 25/27 [0.77, 0.98] | 0.852 | 1/1 [0.21, 1.00] | 1.000 |
| typos | 8 | 8/8 [0.68, 1.00] | 1.000 | 3/3 [0.44, 1.00] | 1.000 |
| non_native | 4 | 4/4 [0.51, 1.00] | 0.750 | 3/3 [0.44, 1.00] | 1.000 |
| dialect | 3 | 2/3 [0.21, 0.94] | 1.000 | 1/1 [0.21, 1.00] | 1.000 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 19 | 17/19 [0.69, 0.97] | 0.947 | 4/4 [0.51, 1.00] | 1.000 |
| web_form | 10 | 9/10 [0.60, 0.98] | 0.900 | 4/4 [0.51, 1.00] | 1.000 |
| hin_mail | 9 | 9/9 [0.70, 1.00] | 0.889 | – | 1.000 |
| fax | 4 | 4/4 [0.51, 1.00] | 0.500 | – | 1.000 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 27 | 26/27 [0.82, 0.99] | 0.852 | – | 1.000 |
| medical_trap | 7 | 6/7 [0.49, 0.97] | 0.857 | – | 1.000 |
| acute_incidental | 5 | 5/5 [0.57, 1.00] | 1.000 | 5/5 [0.57, 1.00] | 1.000 |
| acute_explicit | 3 | 2/3 [0.21, 0.94] | 1.000 | 3/3 [0.44, 1.00] | 1.000 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 159 | 106 | 96 | 0.906 | 0.604 | 0.725 |
| fields.amount | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| fields.appointment_action | 7 | 0 | 0 | – | 0.000 | 0.000 |
| fields.certificate_type | 5 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| fields.creditor | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.examination_date | 6 | 5 | 4 | 0.800 | 0.667 | 0.727 |
| fields.insurer_reference | 4 | 1 | 1 | 1.000 | 0.250 | 0.400 |
| fields.invoice_number | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| fields.medication | 6 | 6 | 5 | 0.833 | 0.833 | 0.833 |
| fields.period | 5 | 2 | 1 | 0.500 | 0.200 | 0.286 |
| fields.pharmacy | 5 | 0 | 0 | – | 0.000 | 0.000 |
| fields.referral_reason | 4 | 4 | 2 | 0.500 | 0.500 | 0.500 |
| fields.referring_physician | 4 | 3 | 3 | 1.000 | 0.750 | 0.857 |
| fields.report_type | 6 | 6 | 6 | 1.000 | 1.000 | 1.000 |
| fields.requested_dates | 7 | 3 | 3 | 1.000 | 0.429 | 0.600 |
| fields.requested_document | 5 | 5 | 3 | 0.600 | 0.600 | 0.600 |
| fields.sender_institution | 6 | 2 | 2 | 1.000 | 0.333 | 0.500 |
| fields.topic | 3 | 0 | 0 | – | 0.000 | 0.000 |
| patient.ahv_number | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 31 | 27 | 27 | 1.000 | 0.871 | 0.931 |
| patient.insurance_number | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| patient.insurer | 6 | 2 | 2 | 1.000 | 0.333 | 0.500 |
| patient.name | 36 | 27 | 25 | 0.926 | 0.694 | 0.794 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| nem-006 | de | clean | other / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| nem-009 | de | clean | referral_in / today / False | referral_in / none / False | {'referral_in': 3} |  |
| nem-018 | fr | clean | other / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| nem-026 | de | non_native | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| nem-028 | fr | typos | certificate_request / today / False | certificate_request / today / True | {'certificate_request': 3} |  |
| nem-030 | fr | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| nem-032 | de | clean | referral_in / none / False | referral_in / this_week / False | {'referral_in': 3} |  |
| nem-035 | de | dialect | other / today / True | report_received / today / True | {'report_received': 3} |  |
| nem-044 | fr | clean | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
