# Validation report

Generated 2026-10-15T01:29:19

| File | Rows |
| --- | --- |
| `dev-v0.jsonl` | 60 |

**Errors:** 0 · **Warnings:** 7

## Distributions

### Generator

| Value | n |
| --- | --- |
| nemotron | 60 |

### Route

| Value | n |
| --- | --- |
| other | 20 |
| appointment | 6 |
| certificate_request | 6 |
| insurer | 6 |
| report_received | 6 |
| prescription_request | 5 |
| billing | 4 |
| referral_in | 4 |
| spam_marketing | 3 |

### Deadline

| Value | n |
| --- | --- |
| none | 21 |
| this_week | 20 |
| today | 19 |

### Safety flag

| Value | n |
| --- | --- |
| False | 51 |
| True | 9 |

### Abstain

| Value | n |
| --- | --- |
| False | 57 |
| True | 3 |

### Language

| Value | n |
| --- | --- |
| de | 33 |
| fr | 15 |
| it | 9 |
| en | 3 |

### Channel

| Value | n |
| --- | --- |
| email | 33 |
| hin_mail | 10 |
| web_form | 9 |
| fax | 8 |

### Writing level

| Value | n |
| --- | --- |
| clean | 33 |
| typos | 16 |
| non_native | 6 |
| dialect | 5 |

### Review flag

| Value | n |
| --- | --- |
| False | 60 |

### Edited by

| Value | n |
| --- | --- |
| - | 57 |
| generate_openrouter.py | 3 |

## Errors

None.

## Warnings

| Check | n |
| --- | --- |
| evidence | 5 |
| fiction | 2 |

| message_id | check | detail |
| --- | --- | --- |
| dev-003 | fiction | possible real brand/institution: Suva |
| dev-003 | fiction | possible real brand/institution: Suva |
| dev-009 | evidence | patient.insurer = 'IV-Amt Bern' has no evidence quote |
| dev-011 | evidence | fields.topic = 'records_request' has no evidence quote |
| dev-012 | evidence | fields.topic = 'certificate_for_insurance' has no evidence quote |
| dev-022 | evidence | fields.creditor = 'Praxis Dr. med. Hans Berger' has no evidence quote |
| dev-027 | evidence | fields.creditor = 'Medical practice' has no evidence quote |

