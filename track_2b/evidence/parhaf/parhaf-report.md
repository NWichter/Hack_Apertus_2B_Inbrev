# Inbrev evaluation

Gold: `messages.jsonl`, n = 38

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| majority | 1.000 | 1.000 | – | – | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | – | – |
| keywords | 0.079 | 0.029 | – | 0.000 | 0.526 | 1.000 | 0.526 | 0.553 | 0.143 | 0.000 | – | – |
| tfidf_logreg | 1.000 | 1.000 | – | – | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | – | – |
| parhaf-p3-8b | 0.974 | 0.493 | – | 0.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 0.724 | 2177/966 | 2.188 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| majority | 38/38 [0.91, 1.00] | – | – | 38/38 [0.91, 1.00] | 38/38 [0.91, 1.00] | 38/38 [0.91, 1.00] |
| keywords | 3/38 [0.03, 0.21] | – | 0/17 [0.00, 0.18] | 20/38 [0.37, 0.68] | 20/38 [0.37, 0.68] | 21/38 [0.40, 0.70] |
| tfidf_logreg | 38/38 [0.91, 1.00] | – | – | 38/38 [0.91, 1.00] | 38/38 [0.91, 1.00] | 38/38 [0.91, 1.00] |
| parhaf-p3-8b | 37/38 [0.87, 1.00] | – | 0/17 [0.00, 0.18] | 38/38 [0.91, 1.00] | 38/38 [0.91, 1.00] | 21/38 [0.40, 0.70] |

## parhaf-p3-8b

Safety missed: none · abstain on gold-ambiguous: 0/0 · all-correct on covered: 1.000

Ops: `{"errors": 0, "invalid_samples": 1, "samples": 114, "sample_error_kinds": [["truncated", 1]], "prompt_tokens_mean": 2176.6315789473683, "completion_tokens_mean": 966.0263157894736, "latency_mean_s": 2.1876052631578946, "latency_p95_s": 3.426, "quote_status": {"route:exact": 113, "exact": 436, "fuzzy": 11, "dropped": 57, "normalized": 5}, "lexical_only_safety": 16}`

Route F1: report_received 0.99, referral_in 0.00

Confusions (gold->pred): report_received->referral_in ×1

Coverage curve: ≥0.67: cov 1.00 acc 0.974, ≥1.00: cov 0.97 acc 1.000

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| hin_mail | 13 | 13/13 [0.77, 1.00] | 1.000 | – | 0.538 |
| fax | 13 | 13/13 [0.77, 1.00] | 1.000 | – | 0.769 |
| email | 12 | 11/12 [0.65, 0.99] | 1.000 | – | 0.333 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 76 | 123 | 72 | 0.585 | 0.947 | 0.724 |
| fields.examination_date | 0 | 25 | 0 | 0.000 | – | 0.000 |
| fields.report_type | 38 | 35 | 35 | 1.000 | 0.921 | 0.959 |
| fields.sender_institution | 38 | 37 | 37 | 1.000 | 0.974 | 0.987 |
| patient.name | 0 | 26 | 0 | 0.000 | – | 0.000 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| parhaf-002 | fr |  | report_received / today / False | referral_in / today / True (abstain) | {'referral_in': 2, 'report_received': 1} | samples disagree on route (0.67) |
| parhaf-003 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-005 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-007 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-015 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-017 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-021 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-023 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-024 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-027 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-028 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-029 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-030 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-032 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-034 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 2} |  |
| parhaf-035 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| parhaf-036 | fr |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
