# Inbrev evaluation

Gold: `gold-subset60.jsonl`, n = 60

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fax60-p3-8b | 0.833 | 0.860 | 0.750 | 0.923 | 0.905 | 0.950 | 0.783 | 0.700 | 0.929 | 0.624 | 1645/588 | 1.466 |
| gold-p3-8b | 0.933 | 0.948 | 0.812 | 0.812 | 0.857 | 0.857 | 0.833 | 0.733 | 0.932 | 0.703 | 1591/623 | 1.496 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| fax60-p3-8b | 50/60 [0.72, 0.91] | 12/16 [0.51, 0.90] | 12/13 [0.67, 0.99] | 19/21 [0.71, 0.97] | 47/60 [0.66, 0.87] | 42/60 [0.57, 0.80] |
| gold-p3-8b | 56/60 [0.84, 0.97] | 13/16 [0.57, 0.93] | 13/16 [0.57, 0.93] | 18/21 [0.65, 0.95] | 50/60 [0.72, 0.91] | 44/60 [0.61, 0.83] |

## fax60-p3-8b

Safety missed: syn-005, syn-047, syn-154, syn-180 · abstain on gold-ambiguous: 0/6 · all-correct on covered: 0.690

Ops: `{"errors": 0, "invalid_samples": 2, "samples": 180, "sample_error_kinds": [["truncated", 1], ["json: Unterminated string starting at", 1]], "prompt_tokens_mean": 1644.75, "completion_tokens_mean": 588.4666666666667, "latency_mean_s": 1.4662833333333334, "latency_p95_s": 2.184, "quote_status": {"route:exact": 156, "exact": 442, "normalized": 28, "dropped": 82, "route:fuzzy": 5, "fuzzy": 19, "route:missing": 10, "route:normalized": 7}, "lexical_only_safety": 2}`

Route F1: report_received 0.77, appointment 0.80, prescription_request 0.88, insurer 0.91, referral_in 1.00, certificate_request 0.83, billing 1.00, spam_marketing 1.00, other 0.56

Confusions (gold->pred): other->report_received ×2, certificate_request->other ×2, other->appointment ×2, prescription_request->report_received ×1, appointment->prescription_request ×1, other->insurer ×1, appointment->other ×1

Coverage curve: ≥0.67: cov 1.00 acc 0.833, ≥1.00: cov 0.97 acc 0.845

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 38 | 32/38 [0.70, 0.93] | 0.763 | 6/7 [0.49, 0.97] | 0.737 |
| it | 12 | 9/12 [0.47, 0.91] | 0.833 | 3/5 [0.23, 0.88] | 0.667 |
| fr | 8 | 7/8 [0.53, 0.98] | 0.750 | 2/3 [0.21, 0.94] | 0.625 |
| en | 2 | 2/2 [0.34, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 0.500 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 33 | 29/33 [0.73, 0.95] | 0.727 | 5/6 [0.44, 0.97] | 0.758 |
| typos | 13 | 9/13 [0.42, 0.87] | 0.923 | 2/4 [0.15, 0.85] | 0.769 |
| non_native | 8 | 7/8 [0.53, 0.98] | 0.875 | 4/5 [0.38, 0.96] | 0.375 |
| dialect | 6 | 5/6 [0.44, 0.97] | 0.667 | 1/1 [0.21, 1.00] | 0.667 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 30 | 22/30 [0.56, 0.86] | 0.800 | 5/7 [0.36, 0.92] | 0.700 |
| web_form | 15 | 13/15 [0.62, 0.96] | 0.667 | 7/8 [0.53, 0.98] | 0.400 |
| hin_mail | 8 | 8/8 [0.68, 1.00] | 0.875 | – | 1.000 |
| fax | 7 | 7/7 [0.65, 1.00] | 0.857 | 0/1 [0.00, 0.79] | 1.000 |

**By generator**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| claude | 32 | 27/32 [0.68, 0.93] | 0.688 | 6/9 [0.35, 0.88] | 0.719 |
| codex | 28 | 23/28 [0.64, 0.92] | 0.893 | 6/7 [0.49, 0.97] | 0.679 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 42 | 37/42 [0.75, 0.95] | 0.786 | – | 0.905 |
| acute_incidental | 9 | 8/9 [0.57, 0.98] | 0.778 | 6/9 [0.35, 0.88] | 0.222 |
| acute_explicit | 7 | 4/7 [0.25, 0.84] | 1.000 | 6/7 [0.49, 0.97] | 0.143 |
| medical_trap | 2 | 1/2 [0.09, 0.91] | 0.000 | – | 0.500 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 208 | 135 | 107 | 0.793 | 0.514 | 0.624 |
| fields.amount | 6 | 5 | 5 | 1.000 | 0.833 | 0.909 |
| fields.appointment_action | 9 | 2 | 1 | 0.500 | 0.111 | 0.182 |
| fields.certificate_type | 7 | 1 | 1 | 1.000 | 0.143 | 0.250 |
| fields.creditor | 3 | 4 | 3 | 0.750 | 1.000 | 0.857 |
| fields.examination_date | 3 | 5 | 3 | 0.600 | 1.000 | 0.750 |
| fields.existing_appointment | 3 | 1 | 1 | 1.000 | 0.333 | 0.500 |
| fields.insurer_reference | 4 | 2 | 1 | 0.500 | 0.250 | 0.333 |
| fields.invoice_number | 6 | 4 | 4 | 1.000 | 0.667 | 0.800 |
| fields.medication | 9 | 7 | 6 | 0.857 | 0.667 | 0.750 |
| fields.period | 6 | 2 | 2 | 1.000 | 0.333 | 0.500 |
| fields.pharmacy | 6 | 4 | 4 | 1.000 | 0.667 | 0.800 |
| fields.referral_reason | 5 | 3 | 1 | 0.333 | 0.200 | 0.250 |
| fields.referring_institution | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.referring_physician | 4 | 5 | 2 | 0.400 | 0.500 | 0.444 |
| fields.report_type | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| fields.requested_dates | 9 | 7 | 3 | 0.429 | 0.333 | 0.375 |
| fields.requested_document | 5 | 3 | 2 | 0.667 | 0.400 | 0.500 |
| fields.sender_institution | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| fields.topic | 10 | 4 | 0 | 0.000 | 0.000 | 0.000 |
| patient.ahv_number | 6 | 3 | 3 | 1.000 | 0.500 | 0.667 |
| patient.birth_date | 39 | 25 | 25 | 1.000 | 0.641 | 0.781 |
| patient.insurer | 4 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| patient.name | 53 | 39 | 33 | 0.846 | 0.623 | 0.717 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| syn-001 | de | non_native | other / today / True | report_received / today / True | {'report_received': 3} |  |
| syn-005 | it | non_native | certificate_request / today / True | certificate_request / none / False | {'certificate_request': 3} |  |
| syn-020 | de | typos | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-044 | it | clean | certificate_request / none / False | other / none / False (abstain) | {'other': 3} | model marks message as ambiguous; no verifiable evidence for route |
| syn-047 | de | typos | prescription_request / today / True | report_received / today / False (abstain) | {'report_received': 3} | no verifiable evidence for route |
| syn-053 | de | dialect | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-062 | de | clean | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-063 | it | clean | other / today / True | report_received / today / True | {'report_received': 2} |  |
| syn-072 | fr | dialect | certificate_request / this_week / False | other / none / False (abstain) | {'other': 2} | model marks message as ambiguous; no verifiable evidence for route |
| syn-073 | de | clean | billing / this_week / False | billing / none / False | {'billing': 3} |  |
| syn-083 | de | clean | referral_in / this_week / False | referral_in / none / False | {'referral_in': 3} |  |
| syn-085 | de | clean | appointment / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-098 | de | clean | other / this_week / False | other / none / False | {'other': 3} |  |
| syn-103 | de | typos | other / this_week / False | appointment / this_week / False | {'appointment': 3} |  |
| syn-120 | de | clean | other / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-137 | de | typos | appointment / today / True | other / today / True (abstain) | {'other': 2, 'report_received': 1} | samples disagree on route (0.67) |
| syn-154 | fr | clean | appointment / today / True | appointment / none / False | {'appointment': 3} |  |
| syn-163 | it | typos | other / none / False | appointment / none / False | {'appointment': 3} |  |
| syn-164 | de | clean | insurer / this_week / False | insurer / none / False (abstain) | {'insurer': 3} | model marks message as ambiguous |
| syn-168 | it | clean | billing / this_week / False | billing / none / False | {'billing': 3} |  |
| syn-180 | it | typos | appointment / today / True | appointment / today / False | {'appointment': 3} |  |

## gold-p3-8b

Safety missed: syn-079, syn-154, syn-180 · abstain on gold-ambiguous: 0/6 · all-correct on covered: 0.795

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 180, "sample_error_kinds": [], "prompt_tokens_mean": 1590.6166666666666, "completion_tokens_mean": 623.3, "latency_mean_s": 1.4955833333333333, "latency_p95_s": 2.333, "quote_status": {"route:exact": 174, "exact": 521, "dropped": 111, "fuzzy": 19, "normalized": 9, "route:missing": 2, "route:fuzzy": 4}, "lexical_only_safety": 5}`

Route F1: report_received 1.00, appointment 0.86, prescription_request 0.94, insurer 0.91, referral_in 1.00, certificate_request 1.00, billing 1.00, spam_marketing 1.00, other 0.82

Confusions (gold->pred): other->appointment ×2, appointment->prescription_request ×1, other->insurer ×1

Coverage curve: ≥1.00: cov 1.00 acc 0.933

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 38 | 35/38 [0.79, 0.97] | 0.895 | 6/7 [0.49, 0.97] | 0.816 |
| it | 12 | 11/12 [0.65, 0.99] | 0.750 | 4/5 [0.38, 0.96] | 0.583 |
| fr | 8 | 8/8 [0.68, 1.00] | 0.625 | 2/3 [0.21, 0.94] | 0.625 |
| en | 2 | 2/2 [0.34, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 0.500 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 33 | 31/33 [0.80, 0.98] | 0.818 | 5/6 [0.44, 0.97] | 0.788 |
| typos | 13 | 11/13 [0.58, 0.96] | 0.769 | 2/4 [0.15, 0.85] | 0.769 |
| non_native | 8 | 8/8 [0.68, 1.00] | 1.000 | 5/5 [0.57, 1.00] | 0.375 |
| dialect | 6 | 6/6 [0.61, 1.00] | 0.833 | 1/1 [0.21, 1.00] | 0.833 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 30 | 26/30 [0.70, 0.95] | 0.800 | 5/7 [0.36, 0.92] | 0.767 |
| web_form | 15 | 15/15 [0.80, 1.00] | 0.867 | 8/8 [0.68, 1.00] | 0.467 |
| hin_mail | 8 | 8/8 [0.68, 1.00] | 0.875 | – | 0.875 |
| fax | 7 | 7/7 [0.65, 1.00] | 0.857 | 0/1 [0.00, 0.79] | 1.000 |

**By generator**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| claude | 32 | 30/32 [0.80, 0.98] | 0.781 | 6/9 [0.35, 0.88] | 0.812 |
| codex | 28 | 26/28 [0.77, 0.98] | 0.893 | 7/7 [0.65, 1.00] | 0.643 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 42 | 39/42 [0.81, 0.98] | 0.857 | – | 0.952 |
| acute_incidental | 9 | 9/9 [0.70, 1.00] | 0.778 | 7/9 [0.45, 0.94] | 0.222 |
| acute_explicit | 7 | 7/7 [0.65, 1.00] | 0.857 | 6/7 [0.49, 0.97] | 0.143 |
| medical_trap | 2 | 1/2 [0.09, 0.91] | 0.500 | – | 0.500 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 208 | 145 | 124 | 0.855 | 0.596 | 0.703 |
| fields.amount | 6 | 6 | 6 | 1.000 | 1.000 | 1.000 |
| fields.appointment_action | 9 | 1 | 1 | 1.000 | 0.111 | 0.200 |
| fields.certificate_type | 7 | 0 | 0 | – | 0.000 | 0.000 |
| fields.creditor | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| fields.examination_date | 3 | 4 | 2 | 0.500 | 0.667 | 0.571 |
| fields.existing_appointment | 3 | 0 | 0 | – | 0.000 | 0.000 |
| fields.insurer_reference | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| fields.invoice_number | 6 | 4 | 4 | 1.000 | 0.667 | 0.800 |
| fields.medication | 9 | 7 | 6 | 0.857 | 0.667 | 0.750 |
| fields.period | 6 | 2 | 1 | 0.500 | 0.167 | 0.250 |
| fields.pharmacy | 6 | 5 | 5 | 1.000 | 0.833 | 0.909 |
| fields.referral_reason | 5 | 3 | 2 | 0.667 | 0.400 | 0.500 |
| fields.referring_institution | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.referring_physician | 4 | 5 | 3 | 0.600 | 0.750 | 0.667 |
| fields.report_type | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| fields.requested_dates | 9 | 3 | 1 | 0.333 | 0.111 | 0.167 |
| fields.requested_document | 5 | 4 | 2 | 0.500 | 0.400 | 0.444 |
| fields.sender_institution | 5 | 1 | 1 | 1.000 | 0.200 | 0.333 |
| fields.topic | 10 | 4 | 0 | 0.000 | 0.000 | 0.000 |
| patient.ahv_number | 6 | 6 | 6 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 39 | 31 | 31 | 1.000 | 0.795 | 0.886 |
| patient.insurer | 4 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| patient.name | 53 | 46 | 42 | 0.913 | 0.792 | 0.848 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| syn-044 | it | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-065 | fr | typos | referral_in / none / False | referral_in / today / True | {'referral_in': 3} |  |
| syn-072 | fr | dialect | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| syn-079 | de | typos | other / today / True | other / none / False | {'other': 3} |  |
| syn-085 | de | clean | appointment / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-098 | de | clean | other / this_week / False | other / none / False | {'other': 3} |  |
| syn-103 | de | typos | other / this_week / False | appointment / this_week / False | {'appointment': 3} |  |
| syn-120 | de | clean | other / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-154 | fr | clean | appointment / today / True | appointment / none / False | {'appointment': 3} |  |
| syn-163 | it | typos | other / none / False | appointment / none / False | {'appointment': 3} |  |
| syn-168 | it | clean | billing / this_week / False | billing / none / False | {'billing': 3} |  |
| syn-180 | it | typos | appointment / today / True | appointment / none / False | {'appointment': 3} |  |
