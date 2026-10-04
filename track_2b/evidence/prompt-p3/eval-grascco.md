# Inbrev evaluation

Gold: `messages.jsonl`, n = 40

| Setup | Route acc | Route macro-F1 | Safety recall | Safety precision | Today recall | Today precision | Deadline acc | Coverage | Route acc (covered) | Field F1 | Tokens in/out | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| majority | 1.000 | 1.000 | – | – | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | – | – |
| keywords | 1.000 | 1.000 | – | 0.000 | 1.000 | 1.000 | 1.000 | 0.825 | 1.000 | 0.000 | – | – |
| tfidf_logreg | 1.000 | 1.000 | – | – | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | – | – |
| grascco-p2-8b | 1.000 | 1.000 | – | 0.000 | 1.000 | 1.000 | 1.000 | 0.825 | 1.000 | 0.602 | 2475/1231 | 5.035 |
| grascco-p3-8b | 1.000 | 1.000 | – | 0.000 | 1.000 | 1.000 | 1.000 | 0.825 | 1.000 | 0.580 | 2677/1164 | 5.754 |

95 % Wilson intervals (k/n [low, high]):

| Setup | Route acc | Safety recall | Safety precision | Today recall | Deadline acc | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| majority | 40/40 [0.91, 1.00] | – | – | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |
| keywords | 40/40 [0.91, 1.00] | – | 0/7 [0.00, 0.35] | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] | 33/40 [0.68, 0.91] |
| tfidf_logreg | 40/40 [0.91, 1.00] | – | – | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |
| grascco-p2-8b | 40/40 [0.91, 1.00] | – | 0/7 [0.00, 0.35] | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] | 33/40 [0.68, 0.91] |
| grascco-p3-8b | 40/40 [0.91, 1.00] | – | 0/7 [0.00, 0.35] | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] | 33/40 [0.68, 0.91] |

## grascco-p2-8b

Safety missed: none · abstain on gold-ambiguous: 0/0 · all-correct on covered: 1.000

Ops: `{"errors": 0, "invalid_samples": 3, "samples": 120, "sample_error_kinds": [["truncated", 3]], "prompt_tokens_mean": 2474.625, "completion_tokens_mean": 1231.3, "latency_mean_s": 5.035275, "latency_p95_s": 9.699, "quote_status": {"route:exact": 117, "exact": 557, "dropped": 92, "normalized": 19, "fuzzy": 37}, "lexical_only_safety": 6}`

Route F1: report_received 1.00

Confusions (gold->pred): 

Coverage curve: ≥1.00: cov 1.00 acc 1.000

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| hin_mail | 14 | 14/14 [0.78, 1.00] | 1.000 | – | 1.000 |
| fax | 13 | 13/13 [0.77, 1.00] | 1.000 | – | 0.692 |
| email | 13 | 13/13 [0.77, 1.00] | 1.000 | – | 0.769 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 80 | 166 | 74 | 0.446 | 0.925 | 0.602 |
| fields.examination_date | 0 | 32 | 0 | 0.000 | – | 0.000 |
| fields.report_type | 40 | 39 | 38 | 0.974 | 0.950 | 0.962 |
| fields.sender_institution | 40 | 39 | 36 | 0.923 | 0.900 | 0.911 |
| patient.birth_date | 0 | 27 | 0 | 0.000 | – | 0.000 |
| patient.insurer | 0 | 1 | 0 | 0.000 | – | 0.000 |
| patient.name | 0 | 28 | 0 | 0.000 | – | 0.000 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| grascco-003 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-021 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-023 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-026 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-029 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-036 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-038 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |

## grascco-p3-8b

Safety missed: none · abstain on gold-ambiguous: 0/0 · all-correct on covered: 1.000

Ops: `{"errors": 0, "invalid_samples": 3, "samples": 120, "sample_error_kinds": [["truncated", 3]], "prompt_tokens_mean": 2676.625, "completion_tokens_mean": 1164.425, "latency_mean_s": 5.7542, "latency_p95_s": 19.721, "quote_status": {"route:exact": 117, "exact": 575, "dropped": 74, "fuzzy": 37, "normalized": 11}, "lexical_only_safety": 6}`

Route F1: report_received 1.00

Confusions (gold->pred): 

Coverage curve: ≥1.00: cov 1.00 acc 1.000

**By channel**

| group | n | route acc [95 % CI] | deadline acc | safety recall [95 % CI] | coverage |
| --- | --- | --- | --- | --- | --- |
| hin_mail | 14 | 14/14 [0.78, 1.00] | 1.000 | – | 1.000 |
| fax | 13 | 13/13 [0.77, 1.00] | 1.000 | – | 0.692 |
| email | 13 | 13/13 [0.77, 1.00] | 1.000 | – | 0.769 |

**Fields**

| field | gold | pred | match | P | R | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 80 | 175 | 74 | 0.423 | 0.925 | 0.580 |
| fields.examination_date | 0 | 32 | 0 | 0.000 | – | 0.000 |
| fields.report_type | 40 | 40 | 38 | 0.950 | 0.950 | 0.950 |
| fields.sender_institution | 40 | 39 | 36 | 0.923 | 0.900 | 0.911 |
| patient.birth_date | 0 | 30 | 0 | 0.000 | – | 0.000 |
| patient.insurance_number | 0 | 1 | 0 | 0.000 | – | 0.000 |
| patient.insurer | 0 | 3 | 0 | 0.000 | – | 0.000 |
| patient.name | 0 | 30 | 0 | 0.000 | – | 0.000 |

**Errors (route, deadline or safety wrong)**

| id | lang | level | gold route/deadline/safety | predicted | votes | abstain reasons |
| --- | --- | --- | --- | --- | --- | --- |
| grascco-003 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-021 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-023 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-026 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-029 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-036 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
| grascco-038 | de |  | report_received / today / False | report_received / today / True | {'report_received': 3} |  |
