# Inbrev evaluation

Gold: `swiss_practice_inbox.jsonl`, n = 30

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| majority | 0.200 | 0.037 | 0.000 | – | 0.000 | – | 0.533 | 1.000 | 0.200 | 0.000 | – | – |
| keywords | 0.833 | 0.786 | 1.000 | 1.000 | 1.000 | 0.833 | 0.533 | 0.867 | 0.846 | 0.000 | – | – |
| tfidf_logreg | 0.200 | 0.037 | 0.000 | – | 0.000 | – | 0.400 | 1.000 | 0.200 | 0.000 | – | – |
| swiss-p2-8b | 0.767 | 0.757 | 1.000 | 1.000 | 1.000 | 1.000 | 0.467 | 0.833 | 0.880 | 0.762 | 1335/625 | 1.543 |
| swiss-p3-8b | 0.800 | 0.787 | 1.000 | 1.000 | 1.000 | 1.000 | 0.467 | 0.833 | 0.920 | 0.681 | 1537/575 | 1.402 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| majority | 6/30 [0.10, 0.37] | 0/4 [0.00, 0.49] | – | 0/5 [0.00, 0.43] | 16/30 [0.36, 0.70] | 30/30 [0.89, 1.00] |
| keywords | 25/30 [0.66, 0.93] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | 5/5 [0.57, 1.00] | 16/30 [0.36, 0.70] | 26/30 [0.70, 0.95] |
| tfidf_logreg | 6/30 [0.10, 0.37] | 0/4 [0.00, 0.49] | – | 0/5 [0.00, 0.43] | 12/30 [0.25, 0.58] | 30/30 [0.89, 1.00] |
| swiss-p2-8b | 23/30 [0.59, 0.88] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | 5/5 [0.57, 1.00] | 14/30 [0.30, 0.64] | 25/30 [0.66, 0.93] |
| swiss-p3-8b | 24/30 [0.63, 0.90] | 4/4 [0.51, 1.00] | 4/4 [0.51, 1.00] | 5/5 [0.57, 1.00] | 14/30 [0.30, 0.64] | 25/30 [0.66, 0.93] |

## swiss-p2-8b

Safety missed: none · abstain on gold-ambiguous: 1/2 · all-correct on covered: 0.320

Ops: `{"errors": 0, "invalid_samples": 0, "samples": 90, "sample_error_kinds": [], "prompt_tokens_mean": 1334.8666666666666, "completion_tokens_mean": 625.1333333333333, "latency_mean_s": 1.5428333333333333, "latency_p95_s": 2.09, "quote_status": {"route:exact": 87, "dropped": 35, "exact": 288, "fuzzy": 3, "normalized": 4, "route:normalized": 3}, "lexical_only_safety": 0}`

Route F1: report_received 0.33, appointment 1.00, prescription_request 1.00, insurer 0.73, referral_in 1.00, certificate_request 0.80, billing 0.67, spam_marketing 1.00, other 0.29

Confusions (gold->pred): other->report_received ×4, billing->insurer ×1, other->insurer ×1, certificate_request->insurer ×1

Coverage curve: ≥1.00: cov 1.00 acc 0.767

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 13 | 9/13 [0.42, 0.87] | 0.462 | 2/2 [0.34, 1.00] | 0.769 |
| fr | 8 | 6/8 [0.41, 0.93] | 0.375 | 1/1 [0.21, 1.00] | 0.875 |
| it | 7 | 6/7 [0.49, 0.97] | 0.429 | 1/1 [0.21, 1.00] | 0.857 |
| en | 2 | 2/2 [0.34, 1.00] | 1.000 | – | 1.000 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 25 | 18/25 [0.52, 0.86] | 0.480 | 4/4 [0.51, 1.00] | 0.800 |
| fax | 3 | 3/3 [0.44, 1.00] | 0.333 | – | 1.000 |
| web_form | 2 | 2/2 [0.34, 1.00] | 0.500 | – | 1.000 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 118 | 84 | 77 | 0.917 | 0.653 | 0.762 |
| fields.amount | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| fields.appointment_action | 5 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| fields.certificate_type | 3 | 0 | 0 | – | 0.000 | 0.000 |
| fields.creditor | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| fields.examination_date | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.existing_appointment | 3 | 1 | 1 | 1.000 | 0.333 | 0.500 |
| fields.insurer_reference | 4 | 3 | 3 | 1.000 | 0.750 | 0.857 |
| fields.invoice_number | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| fields.medication | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| fields.period | 3 | 0 | 0 | – | 0.000 | 0.000 |
| fields.pharmacy | 5 | 4 | 4 | 1.000 | 0.800 | 0.889 |
| fields.referral_reason | 3 | 3 | 3 | 1.000 | 1.000 | 1.000 |
| fields.referring_physician | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.report_type | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.requested_dates | 5 | 2 | 2 | 1.000 | 0.400 | 0.571 |
| fields.requested_document | 4 | 7 | 3 | 0.429 | 0.750 | 0.545 |
| fields.sender_institution | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.topic | 6 | 0 | 0 | – | 0.000 | 0.000 |
| patient.ahv_number | 6 | 6 | 6 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 26 | 21 | 21 | 1.000 | 0.808 | 0.894 |
| patient.insurance_number | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| patient.insurer | 0 | 2 | 0 | 0.000 | – | 0.000 |
| patient.name | 27 | 22 | 22 | 1.000 | 0.815 | 0.898 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| swiss-prx-0001 | de |  | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| swiss-prx-0002 | de |  | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| swiss-prx-0003 | de |  | referral_in / this_week / False | referral_in / none / False | {'referral_in': 3} |  |
| swiss-prx-0004 | de |  | insurer / this_week / False | insurer / none / False | {'insurer': 3} |  |
| swiss-prx-0005 | de |  | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| swiss-prx-0006 | de |  | billing / this_week / False | insurer / none / False | {'insurer': 3} |  |
| swiss-prx-0007 | de |  | other / today / True | report_received / today / True | {'report_received': 3} |  |
| swiss-prx-0009 | fr |  | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| swiss-prx-0010 | fr |  | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| swiss-prx-0013 | fr |  | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| swiss-prx-0014 | fr |  | other / today / True | report_received / today / True | {'report_received': 3} |  |
| swiss-prx-0015 | it |  | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| swiss-prx-0016 | it |  | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| swiss-prx-0017 | it |  | referral_in / this_week / False | referral_in / none / False | {'referral_in': 3} |  |
| swiss-prx-0019 | it |  | other / today / True | report_received / today / True | {'report_received': 3} |  |
| swiss-prx-0022 | de |  | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| swiss-prx-0023 | de |  | other / none / False | insurer / none / False | {'insurer': 3} |  |
| swiss-prx-0025 | de |  | other / today / True | report_received / today / True | {'report_received': 3} |  |
| swiss-prx-0026 | fr |  | certificate_request / this_week / False | insurer / none / False | {'insurer': 3} |  |
| swiss-prx-0027 | fr |  | billing / this_week / False | billing / none / False | {'billing': 3} |  |
| swiss-prx-0029 | it |  | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |

## swiss-p3-8b

Safety missed: none · abstain on gold-ambiguous: 1/2 · all-correct on covered: 0.320

Ops: `{"errors": 0, "invalid_samples": 1, "samples": 90, "sample_error_kinds": [["json: Unterminated string starting at", 1]], "prompt_tokens_mean": 1536.8666666666666, "completion_tokens_mean": 574.9333333333333, "latency_mean_s": 1.4017666666666666, "latency_p95_s": 2.071, "quote_status": {"route:exact": 88, "dropped": 39, "exact": 237, "fuzzy": 2, "normalized": 3, "route:normalized": 1}, "lexical_only_safety": 0}`

Route F1: report_received 0.33, appointment 1.00, prescription_request 1.00, insurer 0.80, referral_in 1.00, certificate_request 1.00, billing 0.67, spam_marketing 1.00, other 0.29

Confusions (gold->pred): other->report_received ×4, billing->insurer ×1, other->insurer ×1

Coverage curve: ≥0.67: cov 1.00 acc 0.800, ≥1.00: cov 0.97 acc 0.828

**By language**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| de | 13 | 9/13 [0.42, 0.87] | 0.462 | 2/2 [0.34, 1.00] | 0.769 |
| fr | 8 | 7/8 [0.53, 0.98] | 0.375 | 1/1 [0.21, 1.00] | 0.875 |
| it | 7 | 6/7 [0.49, 0.97] | 0.429 | 1/1 [0.21, 1.00] | 0.857 |
| en | 2 | 2/2 [0.34, 1.00] | 1.000 | – | 1.000 |

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| email | 25 | 19/25 [0.57, 0.89] | 0.480 | 4/4 [0.51, 1.00] | 0.800 |
| fax | 3 | 3/3 [0.44, 1.00] | 0.333 | – | 1.000 |
| web_form | 2 | 2/2 [0.34, 1.00] | 0.500 | – | 1.000 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 118 | 67 | 63 | 0.940 | 0.534 | 0.681 |
| fields.amount | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| fields.appointment_action | 5 | 0 | 0 | – | 0.000 | 0.000 |
| fields.certificate_type | 3 | 0 | 0 | – | 0.000 | 0.000 |
| fields.creditor | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| fields.examination_date | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.existing_appointment | 3 | 1 | 1 | 1.000 | 0.333 | 0.500 |
| fields.insurer_reference | 4 | 2 | 2 | 1.000 | 0.500 | 0.667 |
| fields.invoice_number | 2 | 1 | 1 | 1.000 | 0.500 | 0.667 |
| fields.medication | 5 | 5 | 4 | 0.800 | 0.800 | 0.800 |
| fields.period | 3 | 0 | 0 | – | 0.000 | 0.000 |
| fields.pharmacy | 5 | 2 | 2 | 1.000 | 0.400 | 0.571 |
| fields.referral_reason | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.referring_physician | 3 | 2 | 2 | 1.000 | 0.667 | 0.800 |
| fields.report_type | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| fields.requested_dates | 5 | 0 | 0 | – | 0.000 | 0.000 |
| fields.requested_document | 4 | 5 | 3 | 0.600 | 0.750 | 0.667 |
| fields.sender_institution | 1 | 0 | 0 | – | 0.000 | 0.000 |
| fields.topic | 6 | 0 | 0 | – | 0.000 | 0.000 |
| patient.ahv_number | 6 | 6 | 6 | 1.000 | 1.000 | 1.000 |
| patient.birth_date | 26 | 17 | 17 | 1.000 | 0.654 | 0.791 |
| patient.insurance_number | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| patient.insurer | 0 | 1 | 0 | 0.000 | – | 0.000 |
| patient.name | 27 | 18 | 18 | 1.000 | 0.667 | 0.800 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| swiss-prx-0001 | de |  | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| swiss-prx-0002 | de |  | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| swiss-prx-0003 | de |  | referral_in / this_week / False | referral_in / none / False | {'referral_in': 3} |  |
| swiss-prx-0004 | de |  | insurer / this_week / False | insurer / none / False | {'insurer': 3} |  |
| swiss-prx-0005 | de |  | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| swiss-prx-0006 | de |  | billing / this_week / False | insurer / none / False | {'insurer': 3} |  |
| swiss-prx-0007 | de |  | other / today / True | report_received / today / True | {'report_received': 3} |  |
| swiss-prx-0009 | fr |  | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| swiss-prx-0010 | fr |  | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| swiss-prx-0013 | fr |  | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| swiss-prx-0014 | fr |  | other / today / True | report_received / today / True (abstain) | {'report_received': 2, 'other': 1} | samples disagree on route (0.67) |
| swiss-prx-0015 | it |  | appointment / this_week / False | appointment / none / False | {'appointment': 3} |  |
| swiss-prx-0016 | it |  | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| swiss-prx-0017 | it |  | referral_in / this_week / False | referral_in / none / False | {'referral_in': 3} |  |
| swiss-prx-0019 | it |  | other / today / True | report_received / today / True | {'report_received': 3} |  |
| swiss-prx-0022 | de |  | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
| swiss-prx-0023 | de |  | other / none / False | insurer / none / False | {'insurer': 3} |  |
| swiss-prx-0025 | de |  | other / today / True | report_received / today / True | {'report_received': 3} |  |
| swiss-prx-0026 | fr |  | certificate_request / this_week / False | certificate_request / none / False | {'certificate_request': 3} |  |
| swiss-prx-0027 | fr |  | billing / this_week / False | billing / none / False | {'billing': 3} |  |
| swiss-prx-0029 | it |  | prescription_request / this_week / False | prescription_request / none / False | {'prescription_request': 3} |  |
