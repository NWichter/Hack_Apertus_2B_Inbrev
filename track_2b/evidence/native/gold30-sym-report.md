# Inbrev evaluation

Gold: `gold-subset30.jsonl`, n = 30

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gold30-q4-vulkan-sym | 0.833 | 0.846 | 1.000 | 0.800 | 1.000 | 0.810 | 0.833 | 0.333 | 0.900 | 0.671 | 1584/267 | 64.023 |
| gold30-q4-vulkan | 0.833 | 0.846 | 0.688 | 0.786 | 0.765 | 0.812 | 0.733 | 0.533 | 0.938 | 0.671 | 1584/267 | 62.576 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| gold30-q4-vulkan-sym | 25/30 [0.66, 0.93] | 16/16 [0.81, 1.00] | 16/20 [0.58, 0.92] | 17/17 [0.82, 1.00] | 25/30 [0.66, 0.93] | 10/30 [0.19, 0.51] |
| gold30-q4-vulkan | 25/30 [0.66, 0.93] | 11/16 [0.44, 0.86] | 11/14 [0.52, 0.92] | 13/17 [0.53, 0.90] | 22/30 [0.56, 0.86] | 16/30 [0.36, 0.70] |

## gold30-q4-vulkan-sym

Safety missed: none · abstain on gold-ambiguous: 0/3 · all-correct on covered: 0.800

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 30, "sample_error_kinds": [], "prompt_tokens_mean": 1584.2, "completion_tokens_mean": 266.56666666666666, "latency_mean_s": 64.02333333333333, "latency_p95_s": 87.431, "quote_status": {"route:exact": 29, "exact": 98, "dropped": 20, "fuzzy": 3, "route:fuzzy": 1}, "lexical_only_safety": 5}`

Route F1: report_received 0.40, appointment 0.92, prescription_request 0.89, insurer 0.80, referral_in 1.00, certificate_request 1.00, billing 1.00, spam_marketing 1.00, other 0.60

Confusions (gold->pred): other->report_received ×3, appointment->prescription_request ×1, other->insurer ×1

Coverage curve: ≥1.00: cov 1.00 acc 0.833

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 15 | 11/15 [0.48, 0.89] | 0.867 | 7/7 [0.65, 1.00] | 0.467 |
| it | 9 | 8/9 [0.57, 0.98] | 0.889 | 5/5 [0.57, 1.00] | 0.333 |
| fr | 5 | 5/5 [0.57, 1.00] | 0.600 | 3/3 [0.44, 1.00] | 0.000 |
| en | 1 | 1/1 [0.21, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 0.000 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 16 | 12/16 [0.51, 0.90] | 0.812 | 6/6 [0.61, 1.00] | 0.500 |
| non_native | 6 | 5/6 [0.44, 0.97] | 1.000 | 5/5 [0.57, 1.00] | 0.167 |
| typos | 6 | 6/6 [0.61, 1.00] | 0.833 | 4/4 [0.51, 1.00] | 0.167 |
| dialect | 2 | 2/2 [0.34, 1.00] | 0.500 | 1/1 [0.21, 1.00] | 0.000 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 14 | 10/14 [0.45, 0.88] | 0.857 | 7/7 [0.65, 1.00] | 0.357 |
| web_form | 10 | 9/10 [0.60, 0.98] | 0.800 | 8/8 [0.68, 1.00] | 0.100 |
| hin_mail | 4 | 4/4 [0.51, 1.00] | 0.750 | – | 0.750 |
| fax | 2 | 2/2 [0.34, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 0.500 |

**By generator**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| claude | 17 | 15/17 [0.66, 0.97] | 0.882 | 9/9 [0.70, 1.00] | 0.412 |
| codex | 13 | 10/13 [0.50, 0.92] | 0.769 | 7/7 [0.65, 1.00] | 0.231 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 12 | 11/12 [0.65, 0.99] | 0.667 | – | 0.750 |
| acute_incidental | 9 | 9/9 [0.70, 1.00] | 1.000 | 9/9 [0.70, 1.00] | 0.000 |
| acute_explicit | 7 | 4/7 [0.25, 0.84] | 1.000 | 7/7 [0.65, 1.00] | 0.000 |
| medical_trap | 2 | 1/2 [0.09, 0.91] | 0.500 | – | 0.500 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 107 | 66 | 58 | 0.879 | 0.542 | 0.671 |
| fields.amount | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.appointment_action | 6 | 1 | 1 | 1.000 | 0.167 | 0.286 |
| fields.certificate_type | 4 | 0 | 0 | – | 0.000 | 0.000 |
| fields.creditor | 2 | 2 | 2 | 1.000 | 1.000 | 1.000 |
| fields.existing_appointment | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| fields.insurer_reference | 2 | 0 | 0 | – | 0.000 | 0.000 |
| fields.invoice_number | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.medication | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| fields.period | 4 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| fields.pharmacy | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.referral_reason | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.referring_physician | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.report_type | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.requested_dates | 6 | 2 | 2 | 1.000 | 0.333 | 0.500 |
| fields.requested_document | 2 | 3 | 1 | 0.333 | 0.500 | 0.400 |
| fields.sender_institution | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.topic | 7 | 0 | 0 | – | 0.000 | 0.000 |
| patient.ahv_number | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 21 | 13 | 13 | 1.000 | 0.619 | 0.765 |
| patient.insurer | 2 | 2 | 1 | 0.500 | 0.500 | 0.500 |
| patient.name | 27 | 24 | 20 | 0.833 | 0.741 | 0.784 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| syn-001 | de | non_native | other / today / True | report_received / today / True | {'report_received': 1} |  |
| syn-044 | it | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 1} |  |
| syn-054 | de | clean | other / today / True | report_received / today / True | {'report_received': 1} |  |
| syn-063 | it | clean | other / today / True | report_received / today / True | {'report_received': 1} |  |
| syn-065 | fr | typos | referral_in / none / False | referral_in / today / True | {'referral_in': 1} |  |
| syn-072 | fr | dialect | certificate_request / this_week / False | certificate_request / today / True | {'certificate_request': 1} |  |
| syn-085 | de | clean | appointment / this_week / False | prescription_request / this_week / False | {'prescription_request': 1} |  |
| syn-098 | de | clean | other / this_week / False | other / none / False | {'other': 1} |  |
| syn-120 | de | clean | other / this_week / False | insurer / today / True | {'insurer': 1} |  |

## gold30-q4-vulkan

Safety missed: syn-047, syn-079, syn-118, syn-154, syn-180 · abstain on gold-ambiguous: 0/3 · all-correct on covered: 0.562

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 30, "sample_error_kinds": [], "prompt_tokens_mean": 1584.2, "completion_tokens_mean": 266.56666666666666, "latency_mean_s": 62.57606666666667, "latency_p95_s": 84.903, "quote_status": {"route:exact": 29, "exact": 98, "dropped": 20, "fuzzy": 3, "route:fuzzy": 1}, "lexical_only_safety": 5}`

Route F1: report_received 0.40, appointment 0.92, prescription_request 0.89, insurer 0.80, referral_in 1.00, certificate_request 1.00, billing 1.00, spam_marketing 1.00, other 0.60

Confusions (gold->pred): other->report_received ×3, appointment->prescription_request ×1, other->insurer ×1

Coverage curve: ≥1.00: cov 1.00 acc 0.833

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 15 | 11/15 [0.48, 0.89] | 0.733 | 5/7 [0.36, 0.92] | 0.600 |
| it | 9 | 8/9 [0.57, 0.98] | 0.778 | 3/5 [0.23, 0.88] | 0.556 |
| fr | 5 | 5/5 [0.57, 1.00] | 0.600 | 2/3 [0.21, 0.94] | 0.400 |
| en | 1 | 1/1 [0.21, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 0.000 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 16 | 12/16 [0.51, 0.90] | 0.750 | 5/6 [0.44, 0.97] | 0.562 |
| non_native | 6 | 5/6 [0.44, 0.97] | 0.833 | 4/5 [0.38, 0.96] | 0.333 |
| typos | 6 | 6/6 [0.61, 1.00] | 0.500 | 1/4 [0.05, 0.70] | 0.667 |
| dialect | 2 | 2/2 [0.34, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 0.500 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 14 | 10/14 [0.45, 0.88] | 0.571 | 3/7 [0.16, 0.75] | 0.643 |
| web_form | 10 | 9/10 [0.60, 0.98] | 0.900 | 8/8 [0.68, 1.00] | 0.200 |
| hin_mail | 4 | 4/4 [0.51, 1.00] | 0.750 | – | 0.750 |
| fax | 2 | 2/2 [0.34, 1.00] | 1.000 | 0/1 [0.00, 0.79] | 1.000 |

**By generator**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| claude | 17 | 15/17 [0.66, 0.97] | 0.706 | 4/9 [0.19, 0.73] | 0.765 |
| codex | 13 | 10/13 [0.50, 0.92] | 0.769 | 7/7 [0.65, 1.00] | 0.231 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 12 | 11/12 [0.65, 0.99] | 0.750 | – | 0.833 |
| acute_incidental | 9 | 9/9 [0.70, 1.00] | 0.556 | 5/9 [0.27, 0.81] | 0.444 |
| acute_explicit | 7 | 4/7 [0.25, 0.84] | 1.000 | 6/7 [0.49, 0.97] | 0.143 |
| medical_trap | 2 | 1/2 [0.09, 0.91] | 0.500 | – | 0.500 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 107 | 66 | 58 | 0.879 | 0.542 | 0.671 |
| fields.amount | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.appointment_action | 6 | 1 | 1 | 1.000 | 0.167 | 0.286 |
| fields.certificate_type | 4 | 0 | 0 | – | 0.000 | 0.000 |
| fields.creditor | 2 | 2 | 2 | 1.000 | 1.000 | 1.000 |
| fields.existing_appointment | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| fields.insurer_reference | 2 | 0 | 0 | – | 0.000 | 0.000 |
| fields.invoice_number | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.medication | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| fields.period | 4 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| fields.pharmacy | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.referral_reason | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.referring_physician | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.report_type | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.requested_dates | 6 | 2 | 2 | 1.000 | 0.333 | 0.500 |
| fields.requested_document | 2 | 3 | 1 | 0.333 | 0.500 | 0.400 |
| fields.sender_institution | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.topic | 7 | 0 | 0 | – | 0.000 | 0.000 |
| patient.ahv_number | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 21 | 13 | 13 | 1.000 | 0.619 | 0.765 |
| patient.insurer | 2 | 2 | 1 | 0.500 | 0.500 | 0.500 |
| patient.name | 27 | 24 | 20 | 0.833 | 0.741 | 0.784 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| syn-001 | de | non_native | other / today / True | report_received / today / True | {'report_received': 1} |  |
| syn-044 | it | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 1} |  |
| syn-047 | de | typos | prescription_request / today / True | prescription_request / none / False | {'prescription_request': 1} |  |
| syn-054 | de | clean | other / today / True | report_received / today / True | {'report_received': 1} |  |
| syn-063 | it | clean | other / today / True | report_received / today / True | {'report_received': 1} |  |
| syn-065 | fr | typos | referral_in / none / False | referral_in / today / True | {'referral_in': 1} |  |
| syn-079 | de | typos | other / today / True | other / none / False | {'other': 1} |  |
| syn-085 | de | clean | appointment / this_week / False | prescription_request / this_week / False | {'prescription_request': 1} |  |
| syn-098 | de | clean | other / this_week / False | other / none / False | {'other': 1} |  |
| syn-118 | it | non_native | certificate_request / today / True | certificate_request / none / False | {'certificate_request': 1} |  |
| syn-120 | de | clean | other / this_week / False | insurer / today / True | {'insurer': 1} |  |
| syn-154 | fr | clean | appointment / today / True | appointment / none / False | {'appointment': 1} |  |
| syn-180 | it | typos | appointment / today / True | appointment / today / False | {'appointment': 1} |  |
