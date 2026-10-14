# Validation report

Generated 2026-10-15T01:29:20

| File | Rows |
| --- | --- |
| `holdout2-v0.jsonl` | 146 |

**Errors:** 0 · **Warnings:** 6

## Distributions

### Generator

| Value | n |
| --- | --- |
| gemma | 146 |

### Route

| Value | n |
| --- | --- |
| appointment | 22 |
| report_received | 22 |
| insurer | 19 |
| prescription_request | 18 |
| certificate_request | 15 |
| referral_in | 15 |
| other | 13 |
| billing | 11 |
| spam_marketing | 11 |

### Deadline

| Value | n |
| --- | --- |
| today | 54 |
| none | 50 |
| this_week | 42 |

### Safety flag

| Value | n |
| --- | --- |
| False | 132 |
| True | 14 |

### Abstain

| Value | n |
| --- | --- |
| False | 139 |
| True | 7 |

### Language

| Value | n |
| --- | --- |
| de | 81 |
| fr | 37 |
| it | 22 |
| en | 6 |

### Channel

| Value | n |
| --- | --- |
| email | 69 |
| hin_mail | 29 |
| fax | 24 |
| web_form | 24 |

### Writing level

| Value | n |
| --- | --- |
| clean | 94 |
| typos | 38 |
| non_native | 8 |
| dialect | 6 |

### Review flag

| Value | n |
| --- | --- |
| False | 146 |

### Edited by

| Value | n |
| --- | --- |
| - | 145 |
| generate_openrouter.py | 1 |

## Errors

None.

## Warnings

| Check | n |
| --- | --- |
| evidence | 3 |
| duplicate | 2 |
| fiction | 1 |

| message_id | check | detail |
| --- | --- | --- |
| ho2-022 | evidence | patient.insurer = 'AstraCare Versicherung' has no evidence quote |
| ho2-049 | evidence | patient.insurer = 'Assurance Santé Valais' has no evidence quote |
| ho2-050 | evidence | patient.insurance_number = '99283' has no evidence quote |
| ho2-075 | duplicate | same opening sentence in ['ho2-075', 'ho2-146']: 'ich überweise ihnen hiermit herrn marc steiner, geb.' |
| ho2-076 | fiction | check hospital name: Ospedale Regionale San |
| ho2-077 | duplicate | same opening sentence in ['ho2-077', 'ho2-111']: 'anliegen: grüezi mitenand.' |

