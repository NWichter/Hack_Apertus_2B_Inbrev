# Inbrev evaluation

Gold: `gold-subset30.jsonl`, n = 30

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gold30-q4-vulkan | 0.833 | 0.846 | 0.688 | 0.786 | 0.765 | 0.812 | 0.733 | 0.533 | 0.938 | 0.671 | 1584/267 | 62.576 |
| gold-p3-8b-k1 | 0.933 | 0.948 | 0.750 | 0.800 | 0.765 | 0.812 | 0.600 | 0.500 | 0.933 | 0.732 | 1584/634 | 1.538 |
| gold-p3-8b | 0.933 | 0.948 | 0.812 | 0.812 | 0.824 | 0.824 | 0.667 | 0.467 | 0.929 | 0.707 | 1584/634 | 1.538 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| gold30-q4-vulkan | 25/30 [0.66, 0.93] | 11/16 [0.44, 0.86] | 11/14 [0.52, 0.92] | 13/17 [0.53, 0.90] | 22/30 [0.56, 0.86] | 16/30 [0.36, 0.70] |
| gold-p3-8b-k1 | 28/30 [0.79, 0.98] | 12/16 [0.51, 0.90] | 12/15 [0.55, 0.93] | 13/17 [0.53, 0.90] | 18/30 [0.42, 0.75] | 15/30 [0.33, 0.67] |
| gold-p3-8b | 28/30 [0.79, 0.98] | 13/16 [0.57, 0.93] | 13/16 [0.57, 0.93] | 14/17 [0.59, 0.94] | 20/30 [0.49, 0.81] | 14/30 [0.30, 0.64] |

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

## gold-p3-8b-k1

Safety missed: syn-047, syn-079, syn-154, syn-180 · abstain on gold-ambiguous: 0/3 · all-correct on covered: 0.400

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 30, "sample_error_kinds": [], "prompt_tokens_mean": 1584.2, "completion_tokens_mean": 634.0333333333333, "latency_mean_s": 1.5375, "latency_p95_s": 2.333, "quote_status": {"route:exact": 29, "exact": 96, "dropped": 19, "route:fuzzy": 1, "fuzzy": 1}, "lexical_only_safety": 5}`

Route F1: report_received 1.00, appointment 0.92, prescription_request 0.89, insurer 0.80, referral_in 1.00, certificate_request 1.00, billing 1.00, spam_marketing 1.00, other 0.92

Confusions (gold->pred): appointment->prescription_request ×1, other->insurer ×1

Coverage curve: ≥1.00: cov 1.00 acc 0.933

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 15 | 13/15 [0.62, 0.96] | 0.600 | 5/7 [0.36, 0.92] | 0.600 |
| it | 9 | 9/9 [0.70, 1.00] | 0.667 | 4/5 [0.38, 0.96] | 0.444 |
| fr | 5 | 5/5 [0.57, 1.00] | 0.400 | 2/3 [0.21, 0.94] | 0.400 |
| en | 1 | 1/1 [0.21, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 0.000 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 16 | 14/16 [0.64, 0.97] | 0.562 | 5/6 [0.44, 0.97] | 0.562 |
| non_native | 6 | 6/6 [0.61, 1.00] | 1.000 | 5/5 [0.57, 1.00] | 0.167 |
| typos | 6 | 6/6 [0.61, 1.00] | 0.333 | 1/4 [0.05, 0.70] | 0.667 |
| dialect | 2 | 2/2 [0.34, 1.00] | 0.500 | 1/1 [0.21, 1.00] | 0.500 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 14 | 12/14 [0.60, 0.96] | 0.500 | 4/7 [0.25, 0.84] | 0.571 |
| web_form | 10 | 10/10 [0.72, 1.00] | 0.800 | 8/8 [0.68, 1.00] | 0.200 |
| hin_mail | 4 | 4/4 [0.51, 1.00] | 0.750 | – | 0.750 |
| fax | 2 | 2/2 [0.34, 1.00] | 0.000 | 0/1 [0.00, 0.79] | 1.000 |

**By generator**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| claude | 17 | 16/17 [0.73, 0.99] | 0.471 | 5/9 [0.27, 0.81] | 0.706 |
| codex | 13 | 12/13 [0.67, 0.99] | 0.769 | 7/7 [0.65, 1.00] | 0.231 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 12 | 11/12 [0.65, 0.99] | 0.500 | – | 0.833 |
| acute_incidental | 9 | 9/9 [0.70, 1.00] | 0.667 | 6/9 [0.35, 0.88] | 0.333 |
| acute_explicit | 7 | 7/7 [0.65, 1.00] | 0.857 | 6/7 [0.49, 0.97] | 0.143 |
| medical_trap | 2 | 1/2 [0.09, 0.91] | 0.000 | – | 0.500 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 107 | 76 | 67 | 0.882 | 0.626 | 0.732 |
| fields.amount | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| fields.appointment_action | 6 | 1 | 1 | 1.000 | 0.167 | 0.286 |
| fields.certificate_type | 4 | 0 | 0 | – | 0.000 | 0.000 |
| fields.creditor | 2 | 2 | 2 | 1.000 | 1.000 | 1.000 |
| fields.examination_date | 0 | 1 | 0 | 0.000 | – | 0.000 |
| fields.existing_appointment | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| fields.insurer_reference | 2 | 2 | 2 | 1.000 | 1.000 | 1.000 |
| fields.invoice_number | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.medication | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| fields.period | 4 | 1 | 1 | 1.000 | 0.250 | 0.400 |
| fields.pharmacy | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.referral_reason | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.referring_physician | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.report_type | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.requested_dates | 6 | 2 | 2 | 1.000 | 0.333 | 0.500 |
| fields.requested_document | 2 | 3 | 1 | 0.333 | 0.500 | 0.400 |
| fields.sender_institution | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.topic | 7 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| patient.ahv_number | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 21 | 17 | 17 | 1.000 | 0.810 | 0.895 |
| patient.insurer | 2 | 3 | 1 | 0.333 | 0.500 | 0.400 |
| patient.name | 27 | 23 | 21 | 0.913 | 0.778 | 0.840 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| syn-044 | it | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 1} |  |
| syn-047 | de | typos | prescription_request / today / True | prescription_request / none / False | {'prescription_request': 1} |  |
| syn-062 | de | clean | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 1} |  |
| syn-065 | fr | typos | referral_in / none / False | referral_in / today / True | {'referral_in': 1} |  |
| syn-072 | fr | dialect | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 1} |  |
| syn-079 | de | typos | other / today / True | other / none / False | {'other': 1} |  |
| syn-085 | de | clean | appointment / this_week / False | prescription_request / none / False | {'prescription_request': 1} |  |
| syn-098 | de | clean | other / this_week / False | other / none / False | {'other': 1} |  |
| syn-120 | de | clean | other / this_week / False | insurer / today / True | {'insurer': 1} |  |
| syn-154 | fr | clean | appointment / today / True | appointment / none / False | {'appointment': 1} |  |
| syn-168 | it | clean | billing / this_week / False | billing / none / False | {'billing': 1} |  |
| syn-180 | it | typos | appointment / today / True | appointment / none / False | {'appointment': 1} |  |

## gold-p3-8b

Safety missed: syn-079, syn-154, syn-180 · abstain on gold-ambiguous: 0/3 · all-correct on covered: 0.500

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 90, "sample_error_kinds": [], "prompt_tokens_mean": 1584.2, "completion_tokens_mean": 634.0333333333333, "latency_mean_s": 1.5375, "latency_p95_s": 2.333, "quote_status": {"route:exact": 87, "exact": 278, "dropped": 56, "fuzzy": 4, "route:fuzzy": 3, "normalized": 2}, "lexical_only_safety": 5}`

Route F1: report_received 1.00, appointment 0.92, prescription_request 0.89, insurer 0.80, referral_in 1.00, certificate_request 1.00, billing 1.00, spam_marketing 1.00, other 0.92

Confusions (gold->pred): appointment->prescription_request ×1, other->insurer ×1

Coverage curve: ≥1.00: cov 1.00 acc 0.933

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 15 | 13/15 [0.62, 0.96] | 0.733 | 6/7 [0.49, 0.97] | 0.533 |
| it | 9 | 9/9 [0.70, 1.00] | 0.667 | 4/5 [0.38, 0.96] | 0.444 |
| fr | 5 | 5/5 [0.57, 1.00] | 0.400 | 2/3 [0.21, 0.94] | 0.400 |
| en | 1 | 1/1 [0.21, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 0.000 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 16 | 14/16 [0.64, 0.97] | 0.625 | 5/6 [0.44, 0.97] | 0.562 |
| non_native | 6 | 6/6 [0.61, 1.00] | 1.000 | 5/5 [0.57, 1.00] | 0.167 |
| typos | 6 | 6/6 [0.61, 1.00] | 0.500 | 2/4 [0.15, 0.85] | 0.500 |
| dialect | 2 | 2/2 [0.34, 1.00] | 0.500 | 1/1 [0.21, 1.00] | 0.500 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 14 | 12/14 [0.60, 0.96] | 0.571 | 5/7 [0.36, 0.92] | 0.500 |
| web_form | 10 | 10/10 [0.72, 1.00] | 0.800 | 8/8 [0.68, 1.00] | 0.200 |
| hin_mail | 4 | 4/4 [0.51, 1.00] | 0.750 | – | 0.750 |
| fax | 2 | 2/2 [0.34, 1.00] | 0.500 | 0/1 [0.00, 0.79] | 1.000 |

**By generator**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| claude | 17 | 16/17 [0.73, 0.99] | 0.588 | 6/9 [0.35, 0.88] | 0.647 |
| codex | 13 | 12/13 [0.67, 0.99] | 0.769 | 7/7 [0.65, 1.00] | 0.231 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 12 | 11/12 [0.65, 0.99] | 0.500 | – | 0.833 |
| acute_incidental | 9 | 9/9 [0.70, 1.00] | 0.778 | 7/9 [0.45, 0.94] | 0.222 |
| acute_explicit | 7 | 7/7 [0.65, 1.00] | 0.857 | 6/7 [0.49, 0.97] | 0.143 |
| medical_trap | 2 | 1/2 [0.09, 0.91] | 0.500 | – | 0.500 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 107 | 77 | 65 | 0.844 | 0.607 | 0.707 |
| fields.amount | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| fields.appointment_action | 6 | 1 | 1 | 1.000 | 0.167 | 0.286 |
| fields.certificate_type | 4 | 0 | 0 | – | 0.000 | 0.000 |
| fields.creditor | 2 | 2 | 2 | 1.000 | 1.000 | 1.000 |
| fields.examination_date | 0 | 1 | 0 | 0.000 | – | 0.000 |
| fields.existing_appointment | 2 | 0 | 0 | – | 0.000 | 0.000 |
| fields.insurer_reference | 2 | 2 | 2 | 1.000 | 1.000 | 1.000 |
| fields.invoice_number | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.medication | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| fields.period | 4 | 2 | 1 | 0.500 | 0.250 | 0.333 |
| fields.pharmacy | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| fields.referral_reason | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.referring_physician | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.report_type | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.requested_dates | 6 | 2 | 1 | 0.500 | 0.167 | 0.250 |
| fields.requested_document | 2 | 3 | 1 | 0.333 | 0.500 | 0.400 |
| fields.sender_institution | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.topic | 7 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| patient.ahv_number | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 21 | 18 | 18 | 1.000 | 0.857 | 0.923 |
| patient.insurer | 2 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| patient.name | 27 | 23 | 20 | 0.870 | 0.741 | 0.800 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| syn-044 | it | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-065 | fr | typos | referral_in / none / False | referral_in / today / True | {'referral_in': 3} |  |
| syn-072 | fr | dialect | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| syn-079 | de | typos | other / today / True | other / none / False | {'other': 3} |  |
| syn-085 | de | clean | appointment / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-098 | de | clean | other / this_week / False | other / none / False | {'other': 3} |  |
| syn-120 | de | clean | other / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-154 | fr | clean | appointment / today / True | appointment / none / False | {'appointment': 3} |  |
| syn-168 | it | clean | billing / this_week / False | billing / none / False | {'billing': 3} |  |
| syn-180 | it | typos | appointment / today / True | appointment / none / False | {'appointment': 3} |  |
