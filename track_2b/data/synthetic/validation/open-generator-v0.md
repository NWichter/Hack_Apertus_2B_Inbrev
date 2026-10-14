# Validation report

Generated 2026-10-15T01:29:18

| File | Rows |
| --- | --- |
| `open-generator-v0.jsonl` | 42 |

**Errors:** 0 · **Warnings:** 1

## Distributions

### Generator

| Value | n |
| --- | --- |
| nemotron | 42 |

### Route

| Value | n |
| --- | --- |
| appointment | 7 |
| prescription_request | 6 |
| report_received | 6 |
| certificate_request | 5 |
| insurer | 5 |
| referral_in | 4 |
| billing | 3 |
| other | 3 |
| spam_marketing | 3 |

### Deadline

| Value | n |
| --- | --- |
| today | 18 |
| this_week | 15 |
| none | 9 |

### Safety flag

| Value | n |
| --- | --- |
| False | 34 |
| True | 8 |

### Abstain

| Value | n |
| --- | --- |
| False | 40 |
| True | 2 |

### Language

| Value | n |
| --- | --- |
| de | 23 |
| fr | 10 |
| it | 7 |
| en | 2 |

### Channel

| Value | n |
| --- | --- |
| email | 19 |
| web_form | 10 |
| hin_mail | 9 |
| fax | 4 |

### Writing level

| Value | n |
| --- | --- |
| clean | 27 |
| typos | 8 |
| non_native | 4 |
| dialect | 3 |

### Review flag

| Value | n |
| --- | --- |
| False | 33 |
| True | 9 |

### Edited by

| Value | n |
| --- | --- |
| - | 32 |
| claude | 9 |
| generate_openrouter.py | 1 |

## Errors

None.

## Warnings

| Check | n |
| --- | --- |
| evidence | 1 |

| message_id | check | detail |
| --- | --- | --- |
| nem-004 | evidence | fields.creditor = 'Praxis' has no evidence quote |

