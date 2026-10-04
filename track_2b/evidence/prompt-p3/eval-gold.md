# Inbrev evaluation

Gold: `merged.v0.jsonl`, n = 180

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| majority | 0.144 | 0.028 | 0.000 | – | 0.000 | – | 0.367 | 1.000 | 0.144 | 0.000 | – | – |
| keywords | 0.794 | 0.763 | 0.438 | 0.318 | 0.760 | 0.585 | 0.678 | 0.878 | 0.797 | 0.000 | – | – |
| tfidf_logreg | 0.828 | 0.821 | 0.125 | 1.000 | 0.660 | 0.786 | 0.683 | 0.989 | 0.831 | 0.000 | – | – |
| gold-p2-8b | 0.878 | 0.839 | 0.812 | 0.464 | 0.880 | 0.772 | 0.822 | 0.811 | 0.904 | 0.743 | 1398/646 | 1.548 |
| gold-p3-8b | 0.944 | 0.943 | 0.812 | 0.464 | 0.880 | 0.800 | 0.839 | 0.839 | 0.940 | 0.708 | 1600/618 | 1.493 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| majority | 26/180 [0.10, 0.20] | 0/16 [0.00, 0.19] | – | 0/50 [0.00, 0.07] | 66/180 [0.30, 0.44] | 180/180 [0.98, 1.00] |
| keywords | 143/180 [0.73, 0.85] | 7/16 [0.23, 0.67] | 7/22 [0.16, 0.53] | 38/50 [0.63, 0.86] | 122/180 [0.61, 0.74] | 158/180 [0.82, 0.92] |
| tfidf_logreg | 149/180 [0.77, 0.88] | 2/16 [0.03, 0.36] | 2/2 [0.34, 1.00] | 33/50 [0.52, 0.78] | 123/180 [0.61, 0.75] | 178/180 [0.96, 1.00] |
| gold-p2-8b | 158/180 [0.82, 0.92] | 13/16 [0.57, 0.93] | 13/28 [0.30, 0.64] | 44/50 [0.76, 0.94] | 148/180 [0.76, 0.87] | 146/180 [0.75, 0.86] |
| gold-p3-8b | 170/180 [0.90, 0.97] | 13/16 [0.57, 0.93] | 13/28 [0.30, 0.64] | 44/50 [0.76, 0.94] | 151/180 [0.78, 0.89] | 151/180 [0.78, 0.89] |

## gold-p2-8b

Safety missed: syn-079, syn-154, syn-180 · abstain on gold-ambiguous: 1/9 · all-correct on covered: 0.788

Ops: `{"errors": 0, "invalid_samples": 2, "samples": 540, "sample_error_kinds": [["json: Unterminated string starting at", 2]], "prompt_tokens_mean": 1398.0277777777778, "completion_tokens_mean": 645.9, "latency_mean_s": 1.5481555555555555, "latency_p95_s": 2.452, "quote_status": {"route:exact": 520, "exact": 1761, "dropped": 290, "normalized": 14, "fuzzy": 62, "route:fuzzy": 10, "route:missing": 8}, "lexical_only_safety": 17}`

Route F1: report_received 0.91, appointment 0.92, prescription_request 0.96, insurer 0.92, referral_in 0.97, certificate_request 0.86, billing 0.93, spam_marketing 0.88, other 0.19

Confusions (gold->pred): other->certificate_request ×6, other->report_received ×5, spam_marketing->other ×3, billing->insurer ×2, appointment->prescription_request ×2, other->appointment ×2, other->insurer ×1, referral_in->insurer ×1

Coverage curve: ≥0.50: cov 1.00 acc 0.878, ≥0.67: cov 0.99 acc 0.883, ≥1.00: cov 0.98 acc 0.898

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 99 | 89/99 [0.82, 0.94] | 0.859 | 6/7 [0.49, 0.97] | 0.848 |
| fr | 45 | 39/45 [0.74, 0.94] | 0.733 | 2/3 [0.21, 0.94] | 0.778 |
| it | 27 | 22/27 [0.63, 0.92] | 0.852 | 4/5 [0.38, 0.96] | 0.778 |
| en | 9 | 8/9 [0.57, 0.98] | 0.778 | 1/1 [0.21, 1.00] | 0.667 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 112 | 99/112 [0.81, 0.93] | 0.866 | 5/6 [0.44, 0.97] | 0.848 |
| typos | 37 | 31/37 [0.69, 0.92] | 0.730 | 2/4 [0.15, 0.85] | 0.811 |
| non_native | 17 | 14/17 [0.59, 0.94] | 0.824 | 5/5 [0.57, 1.00] | 0.706 |
| dialect | 14 | 14/14 [0.78, 1.00] | 0.714 | 1/1 [0.21, 1.00] | 0.643 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 83 | 68/83 [0.72, 0.89] | 0.771 | 5/7 [0.36, 0.92] | 0.819 |
| hin_mail | 37 | 37/37 [0.91, 1.00] | 0.892 | – | 0.811 |
| fax | 30 | 30/30 [0.89, 1.00] | 0.900 | 0/1 [0.00, 0.79] | 1.000 |
| web_form | 30 | 23/30 [0.59, 0.88] | 0.800 | 8/8 [0.68, 1.00] | 0.600 |

**By generator**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| codex | 90 | 79/90 [0.79, 0.93] | 0.867 | 7/7 [0.65, 1.00] | 0.767 |
| claude | 90 | 79/90 [0.79, 0.93] | 0.778 | 6/9 [0.35, 0.88] | 0.856 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 150 | 134/150 [0.83, 0.93] | 0.847 | – | 0.907 |
| medical_trap | 14 | 12/14 [0.60, 0.96] | 0.571 | – | 0.500 |
| acute_incidental | 9 | 9/9 [0.70, 1.00] | 0.778 | 7/9 [0.45, 0.94] | 0.222 |
| acute_explicit | 7 | 3/7 [0.16, 0.75] | 0.857 | 6/7 [0.49, 0.97] | 0.143 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 662 | 469 | 420 | 0.896 | 0.634 | 0.743 |
| fields.amount | 15 | 13 | 13 | 1.000 | 0.867 | 0.929 |
| fields.appointment_action | 25 | 5 | 4 | 0.800 | 0.160 | 0.267 |
| fields.certificate_type | 18 | 7 | 4 | 0.571 | 0.222 | 0.320 |
| fields.creditor | 8 | 9 | 7 | 0.778 | 0.875 | 0.824 |
| fields.examination_date | 23 | 24 | 19 | 0.792 | 0.826 | 0.809 |
| fields.existing_appointment | 9 | 2 | 2 | 1.000 | 0.222 | 0.364 |
| fields.insurer_reference | 23 | 10 | 9 | 0.900 | 0.391 | 0.545 |
| fields.invoice_number | 16 | 11 | 11 | 1.000 | 0.688 | 0.815 |
| fields.medication | 23 | 19 | 17 | 0.895 | 0.739 | 0.810 |
| fields.period | 12 | 8 | 7 | 0.875 | 0.583 | 0.700 |
| fields.pharmacy | 17 | 15 | 14 | 0.933 | 0.824 | 0.875 |
| fields.referral_reason | 18 | 12 | 4 | 0.333 | 0.222 | 0.267 |
| fields.referring_institution | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.referring_physician | 17 | 17 | 14 | 0.824 | 0.824 | 0.824 |
| fields.report_type | 26 | 23 | 18 | 0.783 | 0.692 | 0.735 |
| fields.requested_dates | 26 | 10 | 8 | 0.800 | 0.308 | 0.444 |
| fields.requested_document | 24 | 16 | 14 | 0.875 | 0.583 | 0.700 |
| fields.sender_institution | 26 | 16 | 16 | 1.000 | 0.615 | 0.762 |
| fields.topic | 16 | 3 | 0 | 0.000 | 0.000 | 0.000 |
| patient.ahv_number | 21 | 21 | 21 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 115 | 93 | 93 | 1.000 | 0.809 | 0.894 |
| patient.insurance_number | 4 | 2 | 1 | 0.500 | 0.250 | 0.333 |
| patient.insurer | 20 | 15 | 11 | 0.733 | 0.550 | 0.629 |
| patient.name | 159 | 118 | 113 | 0.958 | 0.711 | 0.816 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| syn-001 | de | non_native | other / today / True | report_received / today / True | {'report_received': 3} |  |
| syn-002 | fr | dialect | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-006 | it | non_native | appointment / today / False | appointment / none / False | {'appointment': 3} |  |
| syn-007 | de | clean | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-012 | fr | clean | other / none / False | certificate_request / none / False (abstain) | {'certificate_request': 1, 'insurer': 1} | samples disagree on route (0.50) |
| syn-013 | de | clean | billing / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-016 | fr | typos | other / none / False | certificate_request / none / False | {'certificate_request': 3} |  |
| syn-020 | de | typos | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-025 | de | clean | appointment / today / False | appointment / today / True | {'appointment': 3} |  |
| syn-027 | de | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-028 | fr | clean | insurer / none / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-031 | de | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-036 | de | typos | certificate_request / this_week / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-040 | en | clean | appointment / today / False | appointment / none / False | {'appointment': 3} |  |
| syn-044 | it | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-048 | en | clean | referral_in / none / False | referral_in / today / True | {'referral_in': 3} |  |
| syn-049 | fr | dialect | appointment / none / False | appointment / today / True | {'appointment': 3} |  |
| syn-050 | fr | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-053 | de | dialect | prescription_request / this_week / False | prescription_request / none / False (abstain) | {'prescription_request': 3} | no verifiable evidence for route |
| syn-054 | de | clean | other / today / True | report_received / today / True | {'report_received': 3} |  |
| syn-060 | fr | non_native | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-062 | de | clean | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-063 | it | clean | other / today / True | report_received / today / True | {'report_received': 3} |  |
| syn-064 | de | clean | spam_marketing / none / False | other / none / False | {'other': 3} |  |
| syn-065 | fr | typos | referral_in / none / False | referral_in / today / True | {'referral_in': 3} |  |
| syn-066 | it | typos | other / none / False | certificate_request / none / False | {'certificate_request': 3} |  |
| syn-067 | de | clean | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| syn-070 | de | typos | spam_marketing / none / False | other / none / False | {'other': 3} |  |
| syn-072 | fr | dialect | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| syn-079 | de | typos | other / today / True | other / none / False | {'other': 3} |  |
| syn-085 | de | clean | appointment / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-098 | de | clean | other / this_week / False | report_received / today / False | {'report_received': 3} |  |
| syn-100 | de | typos | appointment / today / False | appointment / none / False | {'appointment': 3} |  |
| syn-103 | de | typos | other / this_week / False | appointment / this_week / False | {'appointment': 3} |  |
| syn-107 | fr | typos | insurer / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-112 | fr | clean | spam_marketing / none / False | other / none / False (abstain) | {'other': 2, 'spam_marketing': 1} | samples disagree on route (0.67) |
| syn-115 | de | typos | insurer / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-120 | de | clean | other / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-124 | fr | clean | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| syn-126 | de | non_native | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |

## gold-p3-8b

Safety missed: syn-079, syn-154, syn-180 · abstain on gold-ambiguous: 1/9 · all-correct on covered: 0.828

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 540, "sample_error_kinds": [], "prompt_tokens_mean": 1600.0277777777778, "completion_tokens_mean": 618.0444444444445, "latency_mean_s": 1.4928444444444444, "latency_p95_s": 2.41, "quote_status": {"route:exact": 527, "exact": 1633, "dropped": 274, "fuzzy": 54, "normalized": 15, "route:fuzzy": 6, "route:missing": 4, "route:normalized": 3}, "lexical_only_safety": 17}`

Route F1: report_received 1.00, appointment 0.92, prescription_request 0.96, insurer 0.91, referral_in 0.97, certificate_request 1.00, billing 0.90, spam_marketing 0.96, other 0.87

Confusions (gold->pred): billing->insurer ×3, appointment->prescription_request ×2, other->appointment ×2, spam_marketing->other ×1, other->insurer ×1, referral_in->insurer ×1

Coverage curve: ≥1.00: cov 1.00 acc 0.944

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 99 | 94/99 [0.89, 0.98] | 0.879 | 6/7 [0.49, 0.97] | 0.869 |
| fr | 45 | 44/45 [0.88, 1.00] | 0.756 | 2/3 [0.21, 0.94] | 0.822 |
| it | 27 | 24/27 [0.72, 0.96] | 0.852 | 4/5 [0.38, 0.96] | 0.778 |
| en | 9 | 8/9 [0.57, 0.98] | 0.778 | 1/1 [0.21, 1.00] | 0.778 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 112 | 106/112 [0.89, 0.98] | 0.884 | 5/6 [0.44, 0.97] | 0.875 |
| typos | 37 | 33/37 [0.75, 0.96] | 0.730 | 2/4 [0.15, 0.85] | 0.811 |
| non_native | 17 | 17/17 [0.82, 1.00] | 0.824 | 5/5 [0.57, 1.00] | 0.706 |
| dialect | 14 | 14/14 [0.78, 1.00] | 0.786 | 1/1 [0.21, 1.00] | 0.786 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 83 | 75/83 [0.82, 0.95] | 0.795 | 5/7 [0.36, 0.92] | 0.855 |
| hin_mail | 37 | 37/37 [0.91, 1.00] | 0.865 | – | 0.811 |
| fax | 30 | 29/30 [0.83, 0.99] | 0.933 | 0/1 [0.00, 0.79] | 1.000 |
| web_form | 30 | 29/30 [0.83, 0.99] | 0.833 | 8/8 [0.68, 1.00] | 0.667 |

**By generator**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| codex | 90 | 85/90 [0.88, 0.98] | 0.867 | 7/7 [0.65, 1.00] | 0.778 |
| claude | 90 | 85/90 [0.88, 0.98] | 0.811 | 6/9 [0.35, 0.88] | 0.900 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 150 | 141/150 [0.89, 0.97] | 0.860 | – | 0.933 |
| medical_trap | 14 | 13/14 [0.69, 0.99] | 0.643 | – | 0.571 |
| acute_incidental | 9 | 9/9 [0.70, 1.00] | 0.778 | 7/9 [0.45, 0.94] | 0.222 |
| acute_explicit | 7 | 7/7 [0.65, 1.00] | 0.857 | 6/7 [0.49, 0.97] | 0.143 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 662 | 443 | 391 | 0.883 | 0.591 | 0.708 |
| fields.amount | 15 | 12 | 12 | 1.000 | 0.800 | 0.889 |
| fields.appointment_action | 25 | 4 | 3 | 0.750 | 0.120 | 0.207 |
| fields.certificate_type | 18 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| fields.creditor | 8 | 9 | 8 | 0.889 | 1.000 | 0.941 |
| fields.examination_date | 23 | 22 | 17 | 0.773 | 0.739 | 0.756 |
| fields.existing_appointment | 9 | 2 | 2 | 1.000 | 0.222 | 0.364 |
| fields.insurer_reference | 23 | 14 | 14 | 1.000 | 0.609 | 0.757 |
| fields.invoice_number | 16 | 9 | 9 | 1.000 | 0.562 | 0.720 |
| fields.medication | 23 | 19 | 17 | 0.895 | 0.739 | 0.810 |
| fields.period | 12 | 4 | 3 | 0.750 | 0.250 | 0.375 |
| fields.pharmacy | 17 | 10 | 9 | 0.900 | 0.529 | 0.667 |
| fields.referral_reason | 18 | 11 | 3 | 0.273 | 0.167 | 0.207 |
| fields.referring_institution | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.referring_physician | 17 | 17 | 14 | 0.824 | 0.824 | 0.824 |
| fields.report_type | 26 | 21 | 17 | 0.810 | 0.654 | 0.723 |
| fields.requested_dates | 26 | 11 | 7 | 0.636 | 0.269 | 0.378 |
| fields.requested_document | 24 | 21 | 14 | 0.667 | 0.583 | 0.622 |
| fields.sender_institution | 26 | 13 | 13 | 1.000 | 0.500 | 0.667 |
| fields.topic | 16 | 7 | 2 | 0.286 | 0.125 | 0.174 |
| patient.ahv_number | 21 | 21 | 21 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 115 | 91 | 91 | 1.000 | 0.791 | 0.883 |
| patient.insurance_number | 4 | 3 | 1 | 0.333 | 0.250 | 0.286 |
| patient.insurer | 20 | 5 | 3 | 0.600 | 0.150 | 0.240 |
| patient.name | 159 | 116 | 111 | 0.957 | 0.698 | 0.807 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| syn-002 | fr | dialect | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-006 | it | non_native | appointment / today / False | appointment / none / False | {'appointment': 3} |  |
| syn-007 | de | clean | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-013 | de | clean | billing / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-025 | de | clean | appointment / today / False | appointment / today / True | {'appointment': 3} |  |
| syn-027 | de | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-031 | de | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-036 | de | typos | certificate_request / this_week / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-040 | en | clean | appointment / today / False | appointment / this_week / False | {'appointment': 3} |  |
| syn-042 | de | typos | referral_in / none / False | referral_in / this_week / False | {'referral_in': 3} |  |
| syn-044 | it | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-048 | en | clean | referral_in / none / False | referral_in / today / True | {'referral_in': 3} |  |
| syn-049 | fr | dialect | appointment / none / False | appointment / today / True | {'appointment': 3} |  |
| syn-050 | fr | clean | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| syn-056 | en | clean | billing / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-060 | fr | non_native | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-065 | fr | typos | referral_in / none / False | referral_in / today / True | {'referral_in': 3} |  |
| syn-067 | de | clean | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| syn-070 | de | typos | spam_marketing / none / False | other / none / False | {'other': 3} |  |
| syn-072 | fr | dialect | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| syn-079 | de | typos | other / today / True | other / none / False | {'other': 3} |  |
| syn-085 | de | clean | appointment / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-098 | de | clean | other / this_week / False | other / none / False | {'other': 3} |  |
| syn-100 | de | typos | appointment / today / False | appointment / none / False | {'appointment': 3} |  |
| syn-103 | de | typos | other / this_week / False | appointment / this_week / False | {'appointment': 3} |  |
| syn-107 | fr | typos | insurer / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-115 | de | typos | insurer / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-120 | de | clean | other / this_week / False | insurer / today / True | {'insurer': 3} |  |
| syn-124 | fr | clean | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| syn-126 | de | non_native | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| syn-129 | it | typos | billing / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-138 | de | typos | referral_in / this_week / False | referral_in / today / True | {'referral_in': 3} |  |
| syn-154 | fr | clean | appointment / today / True | appointment / none / False | {'appointment': 3} |  |
| syn-156 | fr | typos | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| syn-157 | fr | clean | other / this_week / False | other / none / False | {'other': 3} |  |
| syn-159 | fr | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 3} |  |
| syn-163 | it | typos | other / none / False | appointment / none / False | {'appointment': 3} |  |
| syn-165 | fr | clean | referral_in / this_week / False | insurer / this_week / False | {'insurer': 3} |  |
| syn-168 | it | clean | billing / this_week / False | billing / none / False | {'billing': 3} |  |
| syn-174 | it | clean | appointment / today / False | prescription_request / today / False | {'prescription_request': 3} |  |
