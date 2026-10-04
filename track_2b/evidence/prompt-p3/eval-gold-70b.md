# Inbrev evaluation

Gold: `merged.v0.jsonl`, n = 180

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gold-70b | 0.906 | 0.887 | 0.938 | 0.500 | 0.940 | 0.770 | 0.850 | 0.939 | 0.941 | 0.834 | 1398/967 | 10.741 |
| gold-p3-70b | 0.956 | 0.956 | 0.938 | 0.500 | 0.940 | 0.783 | 0.867 | 0.978 | 0.955 | 0.838 | 1600/923 | 8.891 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| gold-70b | 163/180 [0.85, 0.94] | 15/16 [0.72, 0.99] | 15/30 [0.33, 0.67] | 47/50 [0.84, 0.98] | 153/180 [0.79, 0.89] | 169/180 [0.89, 0.97] |
| gold-p3-70b | 172/180 [0.91, 0.98] | 15/16 [0.72, 0.99] | 15/30 [0.33, 0.67] | 47/50 [0.84, 0.98] | 156/180 [0.81, 0.91] | 176/180 [0.94, 0.99] |

## gold-70b

Safety missed: syn-079 · abstain on gold-ambiguous: 1/9 · all-correct on covered: 0.787

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 540, "sample_error_kinds": [], "prompt_tokens_mean": 1398.0277777777778, "completion_tokens_mean": 966.9777777777778, "latency_mean_s": 10.740616666666666, "latency_p95_s": 15.535, "quote_status": {"route:exact": 457, "exact": 2062, "dropped": 292, "normalized": 29, "route:missing": 42, "fuzzy": 68, "route:normalized": 22, "route:fuzzy": 19}, "lexical_only_safety": 16}`

Route F1: report_received 0.91, appointment 0.91, prescription_request 0.96, insurer 0.88, referral_in 1.00, certificate_request 0.95, billing 0.90, spam_marketing 1.00, other 0.48

Confusions (gold->pred): other->report_received ×5, billing->insurer ×3, other->appointment ×3, appointment->prescription_request ×2, other->insurer ×2, other->certificate_request ×1, insurer->certificate_request ×1

Coverage curve: ≥0.33: cov 1.00 acc 0.906, ≥0.67: cov 0.99 acc 0.916, ≥1.00: cov 0.96 acc 0.942

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 99 | 91/99 [0.85, 0.96] | 0.848 | 6/7 [0.49, 0.97] | 0.949 |
| fr | 45 | 43/45 [0.85, 0.99] | 0.822 | 3/3 [0.44, 1.00] | 0.933 |
| it | 27 | 22/27 [0.63, 0.92] | 0.926 | 5/5 [0.57, 1.00] | 0.963 |
| en | 9 | 7/9 [0.45, 0.94] | 0.778 | 1/1 [0.21, 1.00] | 0.778 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 112 | 101/112 [0.83, 0.94] | 0.893 | 6/6 [0.61, 1.00] | 0.938 |
| typos | 37 | 33/37 [0.75, 0.96] | 0.757 | 3/4 [0.30, 0.95] | 0.946 |
| non_native | 17 | 15/17 [0.66, 0.97] | 0.882 | 5/5 [0.57, 1.00] | 0.882 |
| dialect | 14 | 14/14 [0.78, 1.00] | 0.714 | 1/1 [0.21, 1.00] | 1.000 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 83 | 73/83 [0.79, 0.93] | 0.807 | 6/7 [0.49, 0.97] | 0.952 |
| hin_mail | 37 | 36/37 [0.86, 1.00] | 0.892 | – | 0.946 |
| fax | 30 | 29/30 [0.83, 0.99] | 0.933 | 1/1 [0.21, 1.00] | 0.967 |
| web_form | 30 | 25/30 [0.66, 0.93] | 0.833 | 8/8 [0.68, 1.00] | 0.867 |

**By generator**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| codex | 90 | 84/90 [0.86, 0.97] | 0.878 | 7/7 [0.65, 1.00] | 0.967 |
| claude | 90 | 79/90 [0.79, 0.93] | 0.822 | 8/9 [0.57, 0.98] | 0.911 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 150 | 139/150 [0.87, 0.96] | 0.860 | – | 0.953 |
| medical_trap | 14 | 12/14 [0.60, 0.96] | 0.643 | – | 0.929 |
| acute_incidental | 9 | 9/9 [0.70, 1.00] | 0.889 | 8/9 [0.57, 0.98] | 1.000 |
| acute_explicit | 7 | 3/7 [0.16, 0.75] | 1.000 | 7/7 [0.65, 1.00] | 0.571 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 662 | 578 | 517 | 0.894 | 0.781 | 0.834 |
| fields.amount | 15 | 10 | 8 | 0.800 | 0.533 | 0.640 |
| fields.appointment_action | 25 | 21 | 18 | 0.857 | 0.720 | 0.783 |
| fields.certificate_type | 18 | 6 | 3 | 0.500 | 0.167 | 0.250 |
| fields.creditor | 8 | 11 | 8 | 0.727 | 1.000 | 0.842 |
| fields.examination_date | 23 | 22 | 18 | 0.818 | 0.783 | 0.800 |
| fields.existing_appointment | 9 | 6 | 6 | 1.000 | 0.667 | 0.800 |
| fields.insurer_reference | 23 | 22 | 19 | 0.864 | 0.826 | 0.844 |
| fields.invoice_number | 16 | 12 | 12 | 1.000 | 0.750 | 0.857 |
| fields.medication | 23 | 23 | 21 | 0.913 | 0.913 | 0.913 |
| fields.period | 12 | 10 | 4 | 0.400 | 0.333 | 0.364 |
| fields.pharmacy | 17 | 17 | 16 | 0.941 | 0.941 | 0.941 |
| fields.referral_reason | 18 | 8 | 4 | 0.500 | 0.222 | 0.308 |
| fields.referring_institution | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.referring_physician | 17 | 15 | 15 | 1.000 | 0.882 | 0.938 |
| fields.report_type | 26 | 25 | 17 | 0.680 | 0.654 | 0.667 |
| fields.requested_dates | 26 | 15 | 9 | 0.600 | 0.346 | 0.439 |
| fields.requested_document | 24 | 16 | 11 | 0.688 | 0.458 | 0.550 |
| fields.sender_institution | 26 | 21 | 21 | 1.000 | 0.808 | 0.894 |
| fields.topic | 16 | 0 | 0 | – | 0.000 | 0.000 |
| patient.ahv_number | 21 | 21 | 21 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 115 | 115 | 115 | 1.000 | 1.000 | 1.000 |
| patient.insurance_number | 4 | 1 | 1 | 1.000 | 0.250 | 0.400 |
| patient.insurer | 20 | 22 | 14 | 0.636 | 0.700 | 0.667 |
| patient.name | 159 | 159 | 156 | 0.981 | 0.981 | 0.981 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| syn-001 | de | non_native | other / today / True | report_received / today / True (abstain) | {'report_received': 2, 'other': 1} | samples disagree on route (0.67) |
| syn-002 | fr | dialect | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-007 | de | clean | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-012 | fr | clean | other / none / False | certificate_request / none / False (abstain) | {'certificate_request': 1, 'report_received': 1, 'insurer': 1} | samples disagree on route (0.33) |
| syn-013 | de | clean | billing / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-025 | de | clean | appointment / today / False | appointment / today / True | {'appointment': 3} |  |
| syn-027 | de | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-031 | de | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-036 | de | typos | certificate_request / this_week / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-044 | it | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-048 | en | clean | referral_in / none / False | referral_in / today / True (abstain) | {'referral_in': 3} | no verifiable evidence for route |
| syn-049 | fr | dialect | appointment / none / False | appointment / today / True | {'appointment': 3} |  |
| syn-050 | fr | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-053 | de | dialect | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-054 | de | clean | other / today / True | report_received / today / True (abstain) | {'report_received': 2, 'other': 1} | samples disagree on route (0.67) |
| syn-056 | en | clean | billing / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-059 | en | clean | insurer / this_week / False | insurer / none / False | {'insurer': 3} |  |
| syn-060 | fr | non_native | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-063 | it | clean | other / today / True | report_received / today / True | {'report_received': 3} |  |
| syn-065 | fr | typos | referral_in / none / False | referral_in / today / True | {'referral_in': 3} |  |
| syn-066 | it | typos | other / none / False | report_received / today / False (abstain) | {'other': 1, 'report_received': 2} | samples disagree on route (0.67) |
| syn-071 | de | clean | spam_marketing / none / False | spam_marketing / today / False | {'spam_marketing': 3} |  |
| syn-079 | de | typos | other / today / True | other / none / False | {'other': 3} |  |
| syn-085 | de | clean | appointment / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-097 | de | clean | spam_marketing / none / False | spam_marketing / today / False | {'spam_marketing': 3} |  |
| syn-098 | de | clean | other / this_week / False | appointment / none / False (abstain) | {'appointment': 2, 'insurer': 1} | samples disagree on route (0.67) |
| syn-100 | de | typos | appointment / today / False | appointment / none / False | {'appointment': 3} |  |
| syn-103 | de | typos | other / this_week / False | appointment / this_week / False | {'appointment': 3} |  |
| syn-107 | fr | typos | insurer / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-108 | de | clean | insurer / this_week / False | certificate_request / this_week / False | {'certificate_request': 3} |  |
| syn-115 | de | typos | insurer / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-120 | de | clean | other / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-127 | de | non_native | prescription_request / today / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-129 | it | typos | billing / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-132 | en | clean | other / none / False | insurer / none / False (abstain) | {'insurer': 1, 'other': 1, 'report_received': 1} | samples disagree on route (0.33) |
| syn-134 | de | dialect | appointment / none / False | appointment / this_week / False | {'appointment': 3} |  |
| syn-138 | de | typos | referral_in / this_week / False | referral_in / today / True | {'referral_in': 3} |  |
| syn-155 | de | clean | certificate_request / none / False | certificate_request / this_week / False | {'certificate_request': 3} |  |
| syn-156 | fr | typos | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-157 | fr | clean | other / this_week / False | other / none / False | {'other': 3} |  |

## gold-p3-70b

Safety missed: syn-079 · abstain on gold-ambiguous: 1/9 · all-correct on covered: 0.807

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 540, "sample_error_kinds": [], "prompt_tokens_mean": 1600.0277777777778, "completion_tokens_mean": 922.9, "latency_mean_s": 8.890777777777778, "latency_p95_s": 12.508, "quote_status": {"route:exact": 451, "exact": 2025, "dropped": 241, "fuzzy": 76, "route:missing": 43, "normalized": 24, "route:fuzzy": 25, "route:normalized": 21}, "lexical_only_safety": 16}`

Route F1: report_received 1.00, appointment 0.92, prescription_request 0.96, insurer 0.92, referral_in 1.00, certificate_request 0.97, billing 0.90, spam_marketing 1.00, other 0.93

Confusions (gold->pred): billing->insurer ×3, appointment->prescription_request ×2, other->appointment ×2, insurer->certificate_request ×1

Coverage curve: ≥0.67: cov 1.00 acc 0.956, ≥1.00: cov 0.99 acc 0.955

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 99 | 95/99 [0.90, 0.98] | 0.869 | 6/7 [0.49, 0.97] | 0.980 |
| fr | 45 | 45/45 [0.92, 1.00] | 0.844 | 3/3 [0.44, 1.00] | 1.000 |
| it | 27 | 24/27 [0.72, 0.96] | 0.926 | 5/5 [0.57, 1.00] | 0.963 |
| en | 9 | 8/9 [0.57, 0.98] | 0.778 | 1/1 [0.21, 1.00] | 0.889 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 112 | 107/112 [0.90, 0.98] | 0.902 | 6/6 [0.61, 1.00] | 0.964 |
| typos | 37 | 34/37 [0.79, 0.97] | 0.784 | 3/4 [0.30, 0.95] | 1.000 |
| non_native | 17 | 17/17 [0.82, 1.00] | 0.882 | 5/5 [0.57, 1.00] | 1.000 |
| dialect | 14 | 14/14 [0.78, 1.00] | 0.786 | 1/1 [0.21, 1.00] | 1.000 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 83 | 78/83 [0.87, 0.97] | 0.831 | 6/7 [0.49, 0.97] | 1.000 |
| hin_mail | 37 | 36/37 [0.86, 1.00] | 0.892 | – | 0.946 |
| fax | 30 | 29/30 [0.83, 0.99] | 0.933 | 1/1 [0.21, 1.00] | 0.967 |
| web_form | 30 | 29/30 [0.83, 0.99] | 0.867 | 8/8 [0.68, 1.00] | 0.967 |

**By generator**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| codex | 90 | 88/90 [0.92, 0.99] | 0.889 | 7/7 [0.65, 1.00] | 0.978 |
| claude | 90 | 84/90 [0.86, 0.97] | 0.844 | 8/9 [0.57, 0.98] | 0.978 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 150 | 142/150 [0.90, 0.97] | 0.887 | – | 0.980 |
| medical_trap | 14 | 14/14 [0.78, 1.00] | 0.571 | – | 0.929 |
| acute_incidental | 9 | 9/9 [0.70, 1.00] | 0.889 | 8/9 [0.57, 0.98] | 1.000 |
| acute_explicit | 7 | 7/7 [0.65, 1.00] | 1.000 | 7/7 [0.65, 1.00] | 1.000 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 662 | 565 | 514 | 0.910 | 0.776 | 0.838 |
| fields.amount | 15 | 10 | 8 | 0.800 | 0.533 | 0.640 |
| fields.appointment_action | 25 | 19 | 18 | 0.947 | 0.720 | 0.818 |
| fields.certificate_type | 18 | 4 | 2 | 0.500 | 0.111 | 0.182 |
| fields.creditor | 8 | 10 | 7 | 0.700 | 0.875 | 0.778 |
| fields.examination_date | 23 | 21 | 19 | 0.905 | 0.826 | 0.864 |
| fields.existing_appointment | 9 | 5 | 5 | 1.000 | 0.556 | 0.714 |
| fields.insurer_reference | 23 | 22 | 18 | 0.818 | 0.783 | 0.800 |
| fields.invoice_number | 16 | 13 | 13 | 1.000 | 0.812 | 0.897 |
| fields.medication | 23 | 22 | 19 | 0.864 | 0.826 | 0.844 |
| fields.period | 12 | 6 | 1 | 0.167 | 0.083 | 0.111 |
| fields.pharmacy | 17 | 15 | 15 | 1.000 | 0.882 | 0.938 |
| fields.referral_reason | 18 | 8 | 5 | 0.625 | 0.278 | 0.385 |
| fields.referring_institution | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.referring_physician | 17 | 14 | 13 | 0.929 | 0.765 | 0.839 |
| fields.report_type | 26 | 23 | 17 | 0.739 | 0.654 | 0.694 |
| fields.requested_dates | 26 | 15 | 11 | 0.733 | 0.423 | 0.537 |
| fields.requested_document | 24 | 16 | 10 | 0.625 | 0.417 | 0.500 |
| fields.sender_institution | 26 | 21 | 20 | 0.952 | 0.769 | 0.851 |
| fields.topic | 16 | 0 | 0 | – | 0.000 | 0.000 |
| patient.ahv_number | 21 | 21 | 21 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 115 | 115 | 115 | 1.000 | 1.000 | 1.000 |
| patient.insurance_number | 4 | 4 | 2 | 0.500 | 0.500 | 0.500 |
| patient.insurer | 20 | 20 | 17 | 0.850 | 0.850 | 0.850 |
| patient.name | 159 | 161 | 158 | 0.981 | 0.994 | 0.987 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| syn-002 | fr | dialect | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-007 | de | clean | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-013 | de | clean | billing / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-025 | de | clean | appointment / today / False | appointment / today / True | {'appointment': 3} |  |
| syn-027 | de | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-031 | de | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-036 | de | typos | certificate_request / this_week / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-044 | it | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-048 | en | clean | referral_in / none / False | referral_in / today / True (abstain) | {'referral_in': 3} | no verifiable evidence for route |
| syn-049 | fr | dialect | appointment / none / False | appointment / today / True | {'appointment': 3} |  |
| syn-050 | fr | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-053 | de | dialect | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-056 | en | clean | billing / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-059 | en | clean | insurer / this_week / False | insurer / none / False | {'insurer': 3} |  |
| syn-060 | fr | non_native | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-062 | de | clean | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-065 | fr | typos | referral_in / none / False | referral_in / today / True | {'referral_in': 3} |  |
| syn-071 | de | clean | spam_marketing / none / False | spam_marketing / today / False | {'spam_marketing': 3} |  |
| syn-079 | de | typos | other / today / True | other / none / False | {'other': 3} |  |
| syn-082 | it | clean | spam_marketing / none / False | spam_marketing / today / False | {'spam_marketing': 3} |  |
| syn-085 | de | clean | appointment / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-098 | de | clean | other / this_week / False | other / none / False | {'other': 3} |  |
| syn-100 | de | typos | appointment / today / False | appointment / none / False | {'appointment': 3} |  |
| syn-103 | de | typos | other / this_week / False | appointment / this_week / False | {'appointment': 3} |  |
| syn-107 | fr | typos | insurer / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-108 | de | clean | insurer / this_week / False | certificate_request / this_week / False | {'certificate_request': 3} |  |
| syn-115 | de | typos | insurer / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-120 | de | clean | other / this_week / False | other / today / True | {'other': 3} |  |
| syn-127 | de | non_native | prescription_request / today / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-129 | it | typos | billing / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-138 | de | typos | referral_in / this_week / False | referral_in / today / True | {'referral_in': 3} |  |
| syn-156 | fr | typos | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-159 | fr | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-163 | it | typos | other / none / False | appointment / none / False | {'appointment': 3} |  |
| syn-174 | it | clean | appointment / today / False | prescription_request / today / False | {'prescription_request': 3} |  |
