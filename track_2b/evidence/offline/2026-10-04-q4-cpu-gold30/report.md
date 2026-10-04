# Inbrev evaluation

Gold: `gold-subset30.jsonl`, n = 30

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| majority | 0.233 | 0.042 | 0.000 | – | 1.000 | 0.567 | 0.567 | 1.000 | 0.233 | 0.000 | – | – |
| keywords | 0.767 | 0.725 | 0.438 | 0.700 | 0.529 | 0.750 | 0.500 | 1.000 | 0.767 | 0.000 | – | – |
| tfidf_logreg | 0.233 | 0.042 | 0.750 | 0.750 | 0.882 | 0.750 | 0.767 | 1.000 | 0.233 | 0.000 | – | – |
| predictions | 0.800 | 0.814 | 0.688 | 0.786 | 0.765 | 0.812 | 0.700 | 1.000 | 0.800 | 0.651 | 1382/267 | 191.897 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| majority | 7/30 [0.12, 0.41] | 0/16 [0.00, 0.19] | – | 17/17 [0.82, 1.00] | 17/30 [0.39, 0.73] | 30/30 [0.89, 1.00] |
| keywords | 23/30 [0.59, 0.88] | 7/16 [0.23, 0.67] | 7/10 [0.40, 0.89] | 9/17 [0.31, 0.74] | 15/30 [0.33, 0.67] | 30/30 [0.89, 1.00] |
| tfidf_logreg | 7/30 [0.12, 0.41] | 12/16 [0.51, 0.90] | 12/16 [0.51, 0.90] | 15/17 [0.66, 0.97] | 23/30 [0.59, 0.88] | 30/30 [0.89, 1.00] |
| predictions | 24/30 [0.63, 0.90] | 11/16 [0.44, 0.86] | 11/14 [0.52, 0.92] | 13/17 [0.53, 0.90] | 21/30 [0.52, 0.83] | 30/30 [0.89, 1.00] |

## predictions

Safety missed: syn-079, syn-118, syn-146, syn-154, syn-180 · abstain on gold-ambiguous: 0/3 · all-correct on covered: 0.500

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 30, "sample_error_kinds": [], "prompt_tokens_mean": 1382.2, "completion_tokens_mean": 266.53333333333336, "latency_mean_s": 191.8971, "latency_p95_s": 417.252, "quote_status": {"route:exact": 29, "exact": 91, "dropped": 26, "route:fuzzy": 1, "fuzzy": 1, "normalized": 1}, "lexical_only_safety": 4}`

Route F1: report_received 0.40, appointment 0.92, prescription_request 0.89, insurer 0.67, referral_in 1.00, certificate_request 1.00, billing 1.00, spam_marketing 1.00, other 0.44

Confusions (gold->pred): other->report_received ×3, other->insurer ×2, appointment->prescription_request ×1

Coverage curve: ≥1.00: cov 1.00 acc 0.800

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 15 | 11/15 [0.48, 0.89] | 0.733 | 6/7 [0.49, 0.97] | 1.000 |
| it | 9 | 8/9 [0.57, 0.98] | 0.778 | 3/5 [0.23, 0.88] | 1.000 |
| fr | 5 | 4/5 [0.38, 0.96] | 0.400 | 1/3 [0.06, 0.79] | 1.000 |
| en | 1 | 1/1 [0.21, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 1.000 |

**By writing_level**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| clean | 16 | 12/16 [0.51, 0.90] | 0.688 | 5/6 [0.44, 0.97] | 1.000 |
| non_native | 6 | 4/6 [0.30, 0.90] | 0.667 | 3/5 [0.23, 0.88] | 1.000 |
| typos | 6 | 6/6 [0.61, 1.00] | 0.667 | 2/4 [0.15, 0.85] | 1.000 |
| dialect | 2 | 2/2 [0.34, 1.00] | 1.000 | 1/1 [0.21, 1.00] | 1.000 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 14 | 10/14 [0.45, 0.88] | 0.643 | 4/7 [0.25, 0.84] | 1.000 |
| web_form | 10 | 8/10 [0.49, 0.94] | 0.800 | 7/8 [0.53, 0.98] | 1.000 |
| hin_mail | 4 | 4/4 [0.51, 1.00] | 0.750 | – | 1.000 |
| fax | 2 | 2/2 [0.34, 1.00] | 0.500 | 0/1 [0.00, 0.79] | 1.000 |

**By generator**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| claude | 17 | 14/17 [0.59, 0.94] | 0.706 | 5/9 [0.27, 0.81] | 1.000 |
| codex | 13 | 10/13 [0.50, 0.92] | 0.692 | 6/7 [0.49, 0.97] | 1.000 |

**By safety_case**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| none | 12 | 11/12 [0.65, 0.99] | 0.750 | – | 1.000 |
| acute_incidental | 9 | 9/9 [0.70, 1.00] | 0.556 | 5/9 [0.27, 0.81] | 1.000 |
| acute_explicit | 7 | 3/7 [0.16, 0.75] | 1.000 | 6/7 [0.49, 0.97] | 1.000 |
| medical_trap | 2 | 1/2 [0.09, 0.91] | 0.000 | – | 1.000 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 107 | 65 | 56 | 0.862 | 0.523 | 0.651 |
| fields.amount | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.appointment_action | 6 | 1 | 1 | 1.000 | 0.167 | 0.286 |
| fields.certificate_type | 4 | 0 | 0 | – | 0.000 | 0.000 |
| fields.creditor | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| fields.existing_appointment | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| fields.insurer_reference | 2 | 0 | 0 | – | 0.000 | 0.000 |
| fields.invoice_number | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.medication | 5 | 3 | 3 | 1.000 | 0.600 | 0.750 |
| fields.period | 4 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| fields.pharmacy | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.referral_reason | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.referring_physician | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.report_type | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.requested_dates | 6 | 3 | 2 | 0.667 | 0.333 | 0.444 |
| fields.requested_document | 2 | 2 | 1 | 0.500 | 0.500 | 0.500 |
| fields.sender_institution | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.topic | 7 | 0 | 0 | – | 0.000 | 0.000 |
| patient.ahv_number | 4 | 4 | 4 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 21 | 14 | 14 | 1.000 | 0.667 | 0.800 |
| patient.insurer | 2 | 2 | 0 | 0.000 | 0.000 | 0.000 |
| patient.name | 27 | 23 | 19 | 0.826 | 0.704 | 0.760 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| syn-001 | de | non_native | other / today / True | report_received / today / True | {'report_received': 1} |  |
| syn-044 | it | clean | certificate_request / none / False | certificate_request / today / True | {'certificate_request': 1} |  |
| syn-054 | de | clean | other / today / True | report_received / today / True | {'report_received': 1} |  |
| syn-062 | de | clean | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 1} |  |
| syn-063 | it | clean | other / today / True | report_received / today / True | {'report_received': 1} |  |
| syn-065 | fr | typos | referral_in / none / False | referral_in / today / True | {'referral_in': 1} |  |
| syn-079 | de | typos | other / today / True | other / none / False | {'other': 1} |  |
| syn-085 | de | clean | appointment / this_week / False | prescription_request / this_week / False | {'prescription_request': 1} |  |
| syn-098 | de | clean | other / this_week / False | other / none / False | {'other': 1} |  |
| syn-118 | it | non_native | certificate_request / today / True | certificate_request / none / False | {'certificate_request': 1} |  |
| syn-120 | de | clean | other / this_week / False | insurer / today / True | {'insurer': 1} |  |
| syn-146 | fr | non_native | prescription_request / today / True | prescription_request / none / False | {'prescription_request': 1} |  |
| syn-154 | fr | clean | appointment / today / True | appointment / none / False | {'appointment': 1} |  |
| syn-173 | fr | non_native | other / today / True | insurer / today / True | {'insurer': 1} |  |
| syn-180 | it | typos | appointment / today / True | appointment / today / False | {'appointment': 1} |  |
