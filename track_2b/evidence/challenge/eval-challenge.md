# Inbrev evaluation

Gold: `challenge.v1.jsonl`, n = 115

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| majority | 0.174 | 0.033 | 0.000 | – | 1.000 | 0.513 | 0.513 | 1.000 | 0.174 | 0.000 | – | – |
| keywords | 0.757 | 0.759 | 0.705 | 0.886 | 0.763 | 0.763 | 0.748 | 0.696 | 0.738 | 0.000 | – | – |
| tfidf_logreg | 0.730 | 0.700 | 0.886 | 0.907 | 0.881 | 0.776 | 0.670 | 0.626 | 0.708 | 0.000 | – | – |
| chl-p3-8b | 0.896 | 0.902 | 0.932 | 0.911 | 0.949 | 0.949 | 0.930 | 0.609 | 0.900 | 0.782 | 1586/631 | 1.489 |
| chl-p3-70b | 0.922 | 0.927 | 1.000 | 0.917 | 0.983 | 0.935 | 0.939 | 0.539 | 0.887 | 0.811 | 1586/986 | 9.116 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| majority | 20/115 [0.12, 0.25] | 0/44 [0.00, 0.08] | – | 59/59 [0.94, 1.00] | 59/115 [0.42, 0.60] | 115/115 [0.97, 1.00] |
| keywords | 87/115 [0.67, 0.83] | 31/44 [0.56, 0.82] | 31/35 [0.74, 0.95] | 45/59 [0.64, 0.85] | 86/115 [0.66, 0.82] | 80/115 [0.61, 0.77] |
| tfidf_logreg | 84/115 [0.64, 0.80] | 39/44 [0.76, 0.95] | 39/43 [0.78, 0.96] | 52/59 [0.77, 0.94] | 77/115 [0.58, 0.75] | 72/115 [0.53, 0.71] |
| chl-p3-8b | 103/115 [0.83, 0.94] | 41/44 [0.82, 0.98] | 41/45 [0.79, 0.96] | 56/59 [0.86, 0.98] | 107/115 [0.87, 0.96] | 70/115 [0.52, 0.69] |
| chl-p3-70b | 106/115 [0.86, 0.96] | 44/44 [0.92, 1.00] | 44/48 [0.80, 0.97] | 58/59 [0.91, 1.00] | 108/115 [0.88, 0.97] | 62/115 [0.45, 0.63] |

## chl-p3-8b

Safety missed: chl-098, chl-105, chl-119 · abstain on gold-ambiguous: 0/4 · all-correct on covered: 0.829

Ops: `{"errors": 0, "invalid_samples": 2, "samples": 345, "sample_error_kinds": [["json: Unterminated string starting at", 2]], "prompt_tokens_mean": 1585.8260869565217, "completion_tokens_mean": 630.5130434782609, "latency_mean_s": 1.4888434782608695, "latency_p95_s": 2.297, "quote_status": {"route:exact": 336, "exact": 1282, "dropped": 93, "fuzzy": 32, "route:fuzzy": 4, "normalized": 18, "route:missing": 3}, "lexical_only_safety": 7}`

Route F1: report_received 0.77, appointment 1.00, prescription_request 1.00, insurer 0.83, referral_in 1.00, certificate_request 1.00, billing 0.90, spam_marketing 1.00, other 0.62

Confusions (gold->pred): other->report_received ×6, other->insurer ×4, billing->insurer ×1, other->billing ×1

Coverage curve: ≥0.67: cov 1.00 acc 0.896, ≥1.00: cov 0.98 acc 0.903

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 57 | 50/57 [0.77, 0.94] | 0.947 | 24/26 [0.76, 0.98] | 0.579 |
| fr | 31 | 27/31 [0.71, 0.95] | 0.935 | 10/10 [0.72, 1.00] | 0.613 |
| it | 21 | 20/21 [0.77, 0.99] | 0.857 | 5/6 [0.44, 0.97] | 0.667 |
| en | 6 | 6/6 [0.61, 1.00] | 1.000 | 2/2 [0.34, 1.00] | 0.667 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 46 | 42/46 [0.80, 0.97] | 0.957 | 9/9 [0.70, 1.00] | 0.761 |
| typos | 32 | 28/32 [0.72, 0.95] | 0.969 | 10/11 [0.62, 0.98] | 0.656 |
| dialect | 19 | 15/19 [0.57, 0.91] | 0.789 | 11/12 [0.65, 0.99] | 0.368 |
| non_native | 18 | 18/18 [0.82, 1.00] | 0.944 | 11/12 [0.65, 0.99] | 0.389 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 57 | 49/57 [0.75, 0.93] | 0.930 | 24/26 [0.76, 0.98] | 0.579 |
| web_form | 22 | 20/22 [0.72, 0.97] | 0.909 | 14/15 [0.70, 0.99] | 0.318 |
| fax | 18 | 17/18 [0.74, 0.99] | 0.889 | 3/3 [0.44, 1.00] | 0.778 |
| hin_mail | 18 | 17/18 [0.74, 0.99] | 1.000 | – | 0.889 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| medical_trap | 39 | 35/39 [0.76, 0.96] | 0.923 | – | 0.897 |
| none | 32 | 29/32 [0.76, 0.97] | 0.938 | – | 1.000 |
| acute_incidental | 27 | 26/27 [0.82, 0.99] | 0.889 | 24/27 [0.72, 0.96] | 0.111 |
| acute_explicit | 17 | 13/17 [0.53, 0.90] | 1.000 | 17/17 [0.82, 1.00] | 0.000 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 509 | 376 | 346 | 0.920 | 0.680 | 0.782 |
| fields.amount | 9 | 9 | 9 | 1.000 | 1.000 | 1.000 |
| fields.appointment_action | 20 | 1 | 1 | 1.000 | 0.050 | 0.095 |
| fields.certificate_type | 15 | 1 | 1 | 1.000 | 0.067 | 0.125 |
| fields.creditor | 9 | 8 | 8 | 1.000 | 0.889 | 0.941 |
| fields.examination_date | 10 | 10 | 9 | 0.900 | 0.900 | 0.900 |
| fields.existing_appointment | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.insurer_reference | 12 | 10 | 9 | 0.900 | 0.750 | 0.818 |
| fields.invoice_number | 10 | 5 | 5 | 1.000 | 0.500 | 0.667 |
| fields.medication | 16 | 15 | 15 | 1.000 | 0.938 | 0.968 |
| fields.period | 12 | 6 | 4 | 0.667 | 0.333 | 0.444 |
| fields.pharmacy | 16 | 10 | 10 | 1.000 | 0.625 | 0.769 |
| fields.referral_reason | 8 | 7 | 6 | 0.857 | 0.750 | 0.800 |
| fields.referring_physician | 8 | 8 | 8 | 1.000 | 1.000 | 1.000 |
| fields.report_type | 10 | 10 | 6 | 0.600 | 0.600 | 0.600 |
| fields.requested_dates | 17 | 9 | 6 | 0.667 | 0.353 | 0.462 |
| fields.requested_document | 12 | 14 | 10 | 0.714 | 0.833 | 0.769 |
| fields.secondary_route | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.sender_institution | 10 | 5 | 5 | 1.000 | 0.500 | 0.667 |
| fields.topic | 20 | 3 | 2 | 0.667 | 0.100 | 0.174 |
| patient.ahv_number | 10 | 15 | 10 | 0.667 | 1.000 | 0.800 |
| patient.birth_date | 86 | 82 | 82 | 1.000 | 0.953 | 0.976 |
| patient.insurance_number | 47 | 33 | 32 | 0.970 | 0.681 | 0.800 |
| patient.insurer | 47 | 28 | 28 | 1.000 | 0.596 | 0.747 |
| patient.name | 103 | 87 | 80 | 0.920 | 0.777 | 0.842 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| chl-001 | it | clean | other / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| chl-002 | it | dialect | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| chl-007 | fr | clean | other / today / True | report_received / today / True | {'report_received': 3} |  |
| chl-014 | it | dialect | appointment / none / False | appointment / today / True | {'appointment': 3} |  |
| chl-018 | de | dialect | other / this_week / False | report_received / today / False | {'report_received': 3} |  |
| chl-030 | de | typos | other / none / False | insurer / none / False | {'insurer': 3} |  |
| chl-034 | de | typos | other / today / True | report_received / today / True | {'report_received': 3} |  |
| chl-039 | fr | clean | billing / this_week / False | insurer / this_week / False | {'insurer': 2} |  |
| chl-048 | fr | clean | insurer / this_week / False | insurer / none / False | {'insurer': 3} |  |
| chl-049 | fr | typos | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| chl-052 | de | typos | other / this_week / False | billing / this_week / False | {'billing': 3} |  |
| chl-053 | de | dialect | other / today / True | report_received / today / True | {'report_received': 3} |  |
| chl-063 | fr | clean | referral_in / none / False | referral_in / today / True | {'referral_in': 3} |  |
| chl-080 | de | clean | other / none / False | insurer / none / False | {'insurer': 3} |  |
| chl-098 | it | typos | certificate_request / today / True | certificate_request / none / False | {'certificate_request': 3} |  |
| chl-100 | de | dialect | other / today / True | report_received / today / True (abstain) | {'other': 1, 'report_received': 2} | samples disagree on route (0.67) |
| chl-104 | it | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| chl-105 | de | dialect | certificate_request / today / True | certificate_request / none / False | {'certificate_request': 3} |  |
| chl-114 | fr | dialect | other / today / True | report_received / today / True | {'report_received': 3} |  |
| chl-119 | de | non_native | prescription_request / today / True | prescription_request / none / False | {'prescription_request': 3} |  |
| chl-120 | fr | typos | other / this_week / False | insurer / this_week / False | {'insurer': 3} |  |

## chl-p3-70b

Safety missed: none · abstain on gold-ambiguous: 1/4 · all-correct on covered: 0.823

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 345, "sample_error_kinds": [], "prompt_tokens_mean": 1585.8260869565217, "completion_tokens_mean": 985.695652173913, "latency_mean_s": 9.116295652173912, "latency_p95_s": 12.045, "quote_status": {"route:exact": 305, "exact": 1475, "dropped": 125, "fuzzy": 39, "route:missing": 26, "normalized": 17, "route:normalized": 2, "route:fuzzy": 12}, "lexical_only_safety": 7}`

Route F1: report_received 0.91, appointment 0.95, prescription_request 1.00, insurer 0.89, referral_in 0.93, certificate_request 0.97, billing 0.90, spam_marketing 1.00, other 0.79

Confusions (gold->pred): other->report_received ×2, other->insurer ×2, other->certificate_request ×1, billing->insurer ×1, other->billing ×1, referral_in->appointment ×1, other->appointment ×1

Coverage curve: ≥0.67: cov 1.00 acc 0.922, ≥1.00: cov 0.97 acc 0.928

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 57 | 51/57 [0.79, 0.95] | 0.965 | 26/26 [0.87, 1.00] | 0.526 |
| fr | 31 | 29/31 [0.79, 0.98] | 0.871 | 10/10 [0.72, 1.00] | 0.548 |
| it | 21 | 21/21 [0.85, 1.00] | 0.952 | 6/6 [0.61, 1.00] | 0.571 |
| en | 6 | 5/6 [0.44, 0.97] | 1.000 | 2/2 [0.34, 1.00] | 0.500 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 46 | 43/46 [0.82, 0.98] | 0.935 | 9/9 [0.70, 1.00] | 0.674 |
| typos | 32 | 28/32 [0.72, 0.95] | 0.938 | 11/11 [0.74, 1.00] | 0.594 |
| dialect | 19 | 17/19 [0.69, 0.97] | 0.895 | 12/12 [0.76, 1.00] | 0.316 |
| non_native | 18 | 18/18 [0.82, 1.00] | 1.000 | 12/12 [0.76, 1.00] | 0.333 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 57 | 52/57 [0.81, 0.96] | 0.947 | 26/26 [0.87, 1.00] | 0.526 |
| web_form | 22 | 21/22 [0.78, 0.99] | 0.955 | 15/15 [0.80, 1.00] | 0.182 |
| fax | 18 | 16/18 [0.67, 0.97] | 0.889 | 3/3 [0.44, 1.00] | 0.722 |
| hin_mail | 18 | 17/18 [0.74, 0.99] | 0.944 | – | 0.833 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| medical_trap | 39 | 34/39 [0.73, 0.94] | 0.897 | – | 0.872 |
| none | 32 | 30/32 [0.80, 0.98] | 0.906 | – | 0.875 |
| acute_incidental | 27 | 26/27 [0.82, 0.99] | 1.000 | 27/27 [0.88, 1.00] | 0.000 |
| acute_explicit | 17 | 16/17 [0.73, 0.99] | 1.000 | 17/17 [0.82, 1.00] | 0.000 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 509 | 436 | 383 | 0.878 | 0.752 | 0.811 |
| fields.amount | 9 | 8 | 7 | 0.875 | 0.778 | 0.824 |
| fields.appointment_action | 20 | 15 | 13 | 0.867 | 0.650 | 0.743 |
| fields.certificate_type | 15 | 10 | 6 | 0.600 | 0.400 | 0.480 |
| fields.creditor | 9 | 7 | 7 | 1.000 | 0.778 | 0.875 |
| fields.examination_date | 10 | 8 | 8 | 1.000 | 0.800 | 0.889 |
| fields.existing_appointment | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.insurer_reference | 12 | 13 | 9 | 0.692 | 0.750 | 0.720 |
| fields.invoice_number | 10 | 9 | 9 | 1.000 | 0.900 | 0.947 |
| fields.medication | 16 | 16 | 15 | 0.938 | 0.938 | 0.938 |
| fields.period | 12 | 9 | 3 | 0.333 | 0.250 | 0.286 |
| fields.pharmacy | 16 | 14 | 14 | 1.000 | 0.875 | 0.933 |
| fields.referral_reason | 8 | 5 | 5 | 1.000 | 0.625 | 0.769 |
| fields.referring_physician | 8 | 4 | 4 | 1.000 | 0.500 | 0.667 |
| fields.report_type | 10 | 8 | 4 | 0.500 | 0.400 | 0.444 |
| fields.requested_dates | 17 | 14 | 6 | 0.429 | 0.353 | 0.387 |
| fields.requested_document | 12 | 8 | 4 | 0.500 | 0.333 | 0.400 |
| fields.secondary_route | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.sender_institution | 10 | 6 | 6 | 1.000 | 0.600 | 0.750 |
| fields.topic | 20 | 0 | 0 | – | 0.000 | 0.000 |
| patient.ahv_number | 10 | 15 | 10 | 0.667 | 1.000 | 0.800 |
| patient.birth_date | 86 | 86 | 86 | 1.000 | 1.000 | 1.000 |
| patient.insurance_number | 47 | 34 | 33 | 0.971 | 0.702 | 0.815 |
| patient.insurer | 47 | 42 | 37 | 0.881 | 0.787 | 0.831 |
| patient.name | 103 | 105 | 97 | 0.924 | 0.942 | 0.933 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| chl-014 | it | dialect | appointment / none / False | appointment / today / True | {'appointment': 3} |  |
| chl-018 | de | dialect | other / this_week / False | report_received / today / False | {'report_received': 3} |  |
| chl-020 | fr | typos | certificate_request / none / False | certificate_request / this_week / False | {'certificate_request': 3} |  |
| chl-030 | de | typos | other / none / False | certificate_request / none / False | {'certificate_request': 3} |  |
| chl-034 | de | typos | other / today / True | report_received / today / True | {'report_received': 3} |  |
| chl-036 | de | clean | spam_marketing / none / False | spam_marketing / today / False | {'spam_marketing': 3} |  |
| chl-039 | fr | clean | billing / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| chl-049 | fr | typos | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| chl-052 | de | typos | other / this_week / False | billing / this_week / False | {'billing': 3} |  |
| chl-057 | fr | clean | prescription_request / today / False | prescription_request / none / False | {'prescription_request': 3} |  |
| chl-060 | en | clean | referral_in / today / False | appointment / today / False | {'appointment': 3} |  |
| chl-063 | fr | clean | referral_in / none / False | referral_in / today / True | {'referral_in': 3} |  |
| chl-080 | de | clean | other / none / False | insurer / none / False | {'insurer': 3} |  |
| chl-100 | de | dialect | other / today / True | appointment / today / True (abstain) | {'appointment': 2, 'other': 1} | samples disagree on route (0.67) |
| chl-104 | it | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| chl-115 | fr | typos | certificate_request / none / False | certificate_request / this_week / False | {'certificate_request': 3} |  |
| chl-120 | fr | typos | other / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
