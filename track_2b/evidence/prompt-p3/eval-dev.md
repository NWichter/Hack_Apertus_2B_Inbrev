# Inbrev evaluation

Gold: `dev.jsonl`, n = 60

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| majority | 0.333 | 0.056 | 0.000 | – | 0.000 | – | 0.350 | 1.000 | 0.333 | 0.000 | – | – |
| keywords | 0.683 | 0.726 | 0.667 | 0.750 | 0.579 | 0.500 | 0.667 | 1.000 | 0.683 | 0.000 | – | – |
| tfidf_logreg | 0.600 | 0.624 | 0.111 | 0.333 | 0.684 | 0.722 | 0.500 | 1.000 | 0.600 | 0.000 | – | – |
| dev-p2-8b | 0.650 | 0.725 | 0.778 | 0.778 | 0.895 | 0.850 | 0.833 | 0.983 | 0.661 | 0.695 | 1434/657 | 1.628 |
| dev-p3-8b | 0.850 | 0.890 | 0.778 | 0.778 | 0.895 | 0.850 | 0.817 | 0.983 | 0.847 | 0.712 | 1636/626 | 1.515 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| majority | 20/60 [0.23, 0.46] | 0/9 [0.00, 0.30] | – | 0/19 [0.00, 0.17] | 21/60 [0.24, 0.48] | 60/60 [0.94, 1.00] |
| keywords | 41/60 [0.56, 0.79] | 6/9 [0.35, 0.88] | 6/8 [0.41, 0.93] | 11/19 [0.36, 0.77] | 40/60 [0.54, 0.77] | 60/60 [0.94, 1.00] |
| tfidf_logreg | 36/60 [0.47, 0.71] | 1/9 [0.02, 0.43] | 1/3 [0.06, 0.79] | 13/19 [0.46, 0.85] | 30/60 [0.38, 0.62] | 60/60 [0.94, 1.00] |
| dev-p2-8b | 39/60 [0.52, 0.76] | 7/9 [0.45, 0.94] | 7/9 [0.45, 0.94] | 17/19 [0.69, 0.97] | 50/60 [0.72, 0.91] | 59/60 [0.91, 1.00] |
| dev-p3-8b | 51/60 [0.74, 0.92] | 7/9 [0.45, 0.94] | 7/9 [0.45, 0.94] | 17/19 [0.69, 0.97] | 49/60 [0.70, 0.89] | 59/60 [0.91, 1.00] |

## dev-p2-8b

Safety missed: dev-021, dev-046 · abstain on gold-ambiguous: 0/3 · all-correct on covered: 0.576

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 180, "sample_error_kinds": [], "prompt_tokens_mean": 1433.9833333333333, "completion_tokens_mean": 657.05, "latency_mean_s": 1.6276333333333333, "latency_p95_s": 2.398, "quote_status": {"route:exact": 160, "exact": 578, "dropped": 101, "normalized": 32, "fuzzy": 26, "route:missing": 7, "route:fuzzy": 11, "route:normalized": 2}, "lexical_only_safety": 3}`

Route F1: report_received 0.80, appointment 0.86, prescription_request 1.00, insurer 0.86, referral_in 0.80, certificate_request 0.55, billing 1.00, spam_marketing 0.67, other 0.00

Confusions (gold->pred): other->certificate_request ×10, other->report_received ×3, other->appointment ×2, other->referral_in ×2, other->insurer ×2, other->spam_marketing ×1, spam_marketing->other ×1

Coverage curve: ≥0.67: cov 1.00 acc 0.650, ≥1.00: cov 0.98 acc 0.661

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 33 | 24/33 [0.56, 0.85] | 0.909 | 3/4 [0.30, 0.95] | 1.000 |
| fr | 15 | 8/15 [0.30, 0.75] | 0.800 | 3/3 [0.44, 1.00] | 0.933 |
| it | 9 | 6/9 [0.35, 0.88] | 0.556 | 1/2 [0.09, 0.91] | 1.000 |
| en | 3 | 1/3 [0.06, 0.79] | 1.000 | – | 1.000 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 33 | 20/33 [0.44, 0.75] | 0.848 | 3/3 [0.44, 1.00] | 0.970 |
| typos | 16 | 11/16 [0.44, 0.86] | 0.812 | 4/5 [0.38, 0.96] | 1.000 |
| non_native | 6 | 5/6 [0.44, 0.97] | 1.000 | 0/1 [0.00, 0.79] | 1.000 |
| dialect | 5 | 3/5 [0.23, 0.88] | 0.600 | – | 1.000 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 33 | 19/33 [0.41, 0.73] | 0.818 | 3/4 [0.30, 0.95] | 1.000 |
| hin_mail | 10 | 8/10 [0.49, 0.94] | 0.700 | – | 1.000 |
| web_form | 9 | 5/9 [0.27, 0.81] | 1.000 | 4/4 [0.51, 1.00] | 0.889 |
| fax | 8 | 7/8 [0.53, 0.98] | 0.875 | 0/1 [0.00, 0.79] | 1.000 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 46 | 31/46 [0.53, 0.79] | 0.826 | – | 1.000 |
| medical_trap | 5 | 3/5 [0.23, 0.88] | 0.800 | – | 1.000 |
| acute_explicit | 5 | 2/5 [0.12, 0.77] | 1.000 | 5/5 [0.57, 1.00] | 0.800 |
| acute_incidental | 4 | 3/4 [0.30, 0.95] | 0.750 | 2/4 [0.15, 0.85] | 1.000 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 221 | 156 | 131 | 0.840 | 0.593 | 0.695 |
| fields.amount | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| fields.appointment_action | 6 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| fields.certificate_type | 6 | 3 | 1 | 0.333 | 0.167 | 0.222 |
| fields.creditor | 4 | 3 | 2 | 0.667 | 0.500 | 0.571 |
| fields.examination_date | 6 | 7 | 5 | 0.714 | 0.833 | 0.769 |
| fields.insurer_reference | 6 | 0 | 0 | – | 0.000 | 0.000 |
| fields.invoice_number | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| fields.medication | 5 | 4 | 3 | 0.750 | 0.600 | 0.667 |
| fields.period | 5 | 2 | 1 | 0.500 | 0.200 | 0.286 |
| fields.pharmacy | 5 | 3 | 2 | 0.667 | 0.400 | 0.500 |
| fields.referral_reason | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| fields.referring_physician | 4 | 3 | 3 | 1.000 | 0.750 | 0.857 |
| fields.report_type | 6 | 4 | 2 | 0.500 | 0.333 | 0.400 |
| fields.requested_dates | 6 | 2 | 2 | 1.000 | 0.333 | 0.500 |
| fields.requested_document | 6 | 8 | 4 | 0.500 | 0.667 | 0.571 |
| fields.sender_institution | 6 | 8 | 6 | 0.750 | 1.000 | 0.857 |
| fields.topic | 20 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| patient.ahv_number | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 49 | 43 | 43 | 1.000 | 0.878 | 0.935 |
| patient.insurance_number | 2 | 2 | 2 | 1.000 | 1.000 | 1.000 |
| patient.insurer | 7 | 4 | 1 | 0.250 | 0.143 | 0.182 |
| patient.name | 56 | 42 | 38 | 0.905 | 0.679 | 0.776 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| dev-004 | fr | clean | other / none / False | report_received / today / False | {'report_received': 3} |  |
| dev-005 | de | dialect | other / none / False | certificate_request / none / False | {'certificate_request': 3} |  |
| dev-006 | fr | typos | other / today / True | report_received / today / True | {'report_received': 3} |  |
| dev-008 | it | clean | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| dev-011 | fr | typos | other / this_week / False | certificate_request / this_week / False | {'certificate_request': 3} |  |
| dev-012 | it | clean | other / this_week / False | certificate_request / this_week / False | {'certificate_request': 3} |  |
| dev-019 | fr | clean | other / today / True | spam_marketing / today / True (abstain) | {'spam_marketing': 2, 'certificate_request': 1} | samples disagree on route (0.67) |
| dev-020 | it | typos | referral_in / this_week / False | referral_in / none / False | {'referral_in': 3} |  |
| dev-021 | it | typos | prescription_request / today / True | prescription_request / none / False | {'prescription_request': 3} |  |
| dev-024 | fr | clean | other / none / False | report_received / today / True | {'report_received': 3} |  |
| dev-026 | de | typos | other / today / False | appointment / none / False | {'appointment': 3} |  |
| dev-028 | it | clean | other / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| dev-034 | it | clean | other / today / True | certificate_request / today / True | {'certificate_request': 3} |  |
| dev-035 | de | clean | other / today / False | referral_in / today / False | {'referral_in': 3} |  |
| dev-037 | en | clean | other / none / False | certificate_request / none / False | {'certificate_request': 3} |  |
| dev-038 | de | dialect | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| dev-042 | fr | clean | other / this_week / False | referral_in / none / False | {'referral_in': 3} |  |
| dev-045 | de | clean | other / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| dev-046 | de | non_native | certificate_request / today / True | certificate_request / today / False | {'certificate_request': 3} |  |
| dev-047 | de | typos | other / none / False | certificate_request / none / False | {'certificate_request': 3} |  |
| dev-048 | de | clean | other / none / False | insurer / none / False | {'insurer': 3} |  |
| dev-049 | de | dialect | other / this_week / False | appointment / none / False | {'appointment': 3} |  |
| dev-051 | fr | clean | other / none / False | certificate_request / none / False | {'certificate_request': 3} |  |
| dev-056 | en | clean | spam_marketing / none / False | other / none / False | {'other': 3} |  |
| dev-057 | de | typos | other / today / True | certificate_request / today / True | {'certificate_request': 3} |  |
| dev-058 | de | non_native | other / none / False | certificate_request / none / False | {'certificate_request': 3} |  |

## dev-p3-8b

Safety missed: dev-021, dev-046 · abstain on gold-ambiguous: 0/3 · all-correct on covered: 0.712

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 180, "sample_error_kinds": [], "prompt_tokens_mean": 1635.9833333333333, "completion_tokens_mean": 625.5166666666667, "latency_mean_s": 1.5149166666666667, "latency_p95_s": 2.422, "quote_status": {"route:exact": 163, "exact": 540, "dropped": 100, "normalized": 25, "fuzzy": 23, "route:fuzzy": 9, "route:missing": 8}, "lexical_only_safety": 3}`

Route F1: report_received 0.92, appointment 0.86, prescription_request 1.00, insurer 0.92, referral_in 0.80, certificate_request 0.80, billing 1.00, spam_marketing 1.00, other 0.71

Confusions (gold->pred): other->certificate_request ×3, other->referral_in ×2, other->appointment ×2, other->report_received ×1, other->insurer ×1

Coverage curve: ≥1.00: cov 1.00 acc 0.850

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 33 | 28/33 [0.69, 0.93] | 0.939 | 3/4 [0.30, 0.95] | 1.000 |
| fr | 15 | 13/15 [0.62, 0.96] | 0.667 | 3/3 [0.44, 1.00] | 0.933 |
| it | 9 | 7/9 [0.45, 0.94] | 0.556 | 1/2 [0.09, 0.91] | 1.000 |
| en | 3 | 3/3 [0.44, 1.00] | 1.000 | – | 1.000 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 33 | 27/33 [0.66, 0.91] | 0.818 | 3/3 [0.44, 1.00] | 0.970 |
| typos | 16 | 14/16 [0.64, 0.97] | 0.750 | 4/5 [0.38, 0.96] | 1.000 |
| non_native | 6 | 6/6 [0.61, 1.00] | 1.000 | 0/1 [0.00, 0.79] | 1.000 |
| dialect | 5 | 4/5 [0.38, 0.96] | 0.800 | – | 1.000 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 33 | 27/33 [0.66, 0.91] | 0.788 | 3/4 [0.30, 0.95] | 1.000 |
| hin_mail | 10 | 8/10 [0.49, 0.94] | 0.700 | – | 1.000 |
| web_form | 9 | 8/9 [0.57, 0.98] | 1.000 | 4/4 [0.51, 1.00] | 0.889 |
| fax | 8 | 8/8 [0.68, 1.00] | 0.875 | 0/1 [0.00, 0.79] | 1.000 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 46 | 39/46 [0.72, 0.92] | 0.804 | – | 1.000 |
| medical_trap | 5 | 4/5 [0.38, 0.96] | 0.800 | – | 1.000 |
| acute_explicit | 5 | 4/5 [0.38, 0.96] | 1.000 | 5/5 [0.57, 1.00] | 0.800 |
| acute_incidental | 4 | 4/4 [0.51, 1.00] | 0.750 | 2/4 [0.15, 0.85] | 1.000 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 221 | 150 | 132 | 0.880 | 0.597 | 0.712 |
| fields.amount | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| fields.appointment_action | 6 | 0 | 0 | – | 0.000 | 0.000 |
| fields.certificate_type | 6 | 2 | 1 | 0.500 | 0.167 | 0.250 |
| fields.creditor | 4 | 3 | 2 | 0.667 | 0.500 | 0.571 |
| fields.examination_date | 6 | 6 | 5 | 0.833 | 0.833 | 0.833 |
| fields.insurer_reference | 6 | 0 | 0 | – | 0.000 | 0.000 |
| fields.invoice_number | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| fields.medication | 5 | 5 | 3 | 0.600 | 0.600 | 0.600 |
| fields.period | 5 | 2 | 1 | 0.500 | 0.200 | 0.286 |
| fields.pharmacy | 5 | 1 | 1 | 1.000 | 0.200 | 0.333 |
| fields.referral_reason | 4 | 5 | 4 | 0.800 | 1.000 | 0.889 |
| fields.referring_physician | 4 | 3 | 3 | 1.000 | 0.750 | 0.857 |
| fields.report_type | 6 | 4 | 2 | 0.500 | 0.333 | 0.400 |
| fields.requested_dates | 6 | 4 | 3 | 0.750 | 0.500 | 0.600 |
| fields.requested_document | 6 | 6 | 4 | 0.667 | 0.667 | 0.667 |
| fields.sender_institution | 6 | 7 | 6 | 0.857 | 1.000 | 0.923 |
| fields.topic | 20 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| patient.ahv_number | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 49 | 45 | 45 | 1.000 | 0.918 | 0.957 |
| patient.insurance_number | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| patient.insurer | 7 | 1 | 1 | 1.000 | 0.143 | 0.250 |
| patient.name | 56 | 42 | 38 | 0.905 | 0.679 | 0.776 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| dev-004 | fr | clean | other / none / False | report_received / today / False | {'report_received': 3} |  |
| dev-007 | fr | clean | certificate_request / none / False | certificate_request / this_week / False | {'certificate_request': 3} |  |
| dev-008 | it | clean | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| dev-011 | fr | typos | other / this_week / False | other / none / False | {'other': 3} |  |
| dev-012 | it | clean | other / this_week / False | certificate_request / this_week / False | {'certificate_request': 3} |  |
| dev-020 | it | typos | referral_in / this_week / False | referral_in / none / False | {'referral_in': 3} |  |
| dev-021 | it | typos | prescription_request / today / True | prescription_request / none / False | {'prescription_request': 3} |  |
| dev-024 | fr | clean | other / none / False | referral_in / today / True | {'referral_in': 3} |  |
| dev-026 | de | typos | other / today / False | appointment / none / False | {'appointment': 3} |  |
| dev-028 | it | clean | other / none / False | other / today / True | {'other': 3} |  |
| dev-034 | it | clean | other / today / True | certificate_request / today / True | {'certificate_request': 3} |  |
| dev-035 | de | clean | other / today / False | referral_in / today / False | {'referral_in': 3} |  |
| dev-042 | fr | clean | other / this_week / False | other / none / False | {'other': 3} |  |
| dev-045 | de | clean | other / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| dev-046 | de | non_native | certificate_request / today / True | certificate_request / today / False | {'certificate_request': 3} |  |
| dev-047 | de | typos | other / none / False | certificate_request / none / False | {'certificate_request': 3} |  |
| dev-049 | de | dialect | other / this_week / False | appointment / none / False | {'appointment': 3} |  |
