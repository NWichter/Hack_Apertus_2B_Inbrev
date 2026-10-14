# Validation report

Generated 2026-10-15T01:29:19

| File | Rows |
| --- | --- |
| `challenge-v1.jsonl` | 115 |

**Errors:** 0 · **Warnings:** 21

## Distributions

### Generator

| Value | n |
| --- | --- |
| nemotron | 115 |

### Route

| Value | n |
| --- | --- |
| appointment | 20 |
| other | 20 |
| prescription_request | 16 |
| certificate_request | 15 |
| insurer | 12 |
| billing | 10 |
| report_received | 10 |
| referral_in | 8 |
| spam_marketing | 4 |

### Deadline

| Value | n |
| --- | --- |
| today | 59 |
| none | 31 |
| this_week | 25 |

### Safety flag

| Value | n |
| --- | --- |
| False | 71 |
| True | 44 |

### Abstain

| Value | n |
| --- | --- |
| False | 111 |
| True | 4 |

### Language

| Value | n |
| --- | --- |
| de | 57 |
| fr | 31 |
| it | 21 |
| en | 6 |

### Channel

| Value | n |
| --- | --- |
| email | 57 |
| web_form | 22 |
| fax | 18 |
| hin_mail | 18 |

### Writing level

| Value | n |
| --- | --- |
| clean | 46 |
| typos | 32 |
| dialect | 19 |
| non_native | 18 |

### Review flag

| Value | n |
| --- | --- |
| False | 115 |

### Edited by

| Value | n |
| --- | --- |
| - | 113 |
| generate_openrouter.py | 2 |

## Errors

None.

## Warnings

| Check | n |
| --- | --- |
| evidence | 15 |
| fiction | 5 |
| language | 1 |

| message_id | check | detail |
| --- | --- | --- |
| chl-008 | evidence | patient.insurance_number = 'INS-12345' has no evidence quote |
| chl-010 | evidence | patient.insurer = 'SalutePlus' has no evidence quote |
| chl-030 | evidence | fields.secondary_route = 'prescription_request' has no evidence quote |
| chl-039 | evidence | patient.insurer = "Caisse d'Assurance Maladie Valora" has no evidence quote |
| chl-041 | fiction | AHV number not taken from the grid: 756.1234.5678.90 |
| chl-042 | fiction | AHV number not taken from the grid: 756.9876.5432.10 |
| chl-043 | fiction | AHV number not taken from the grid: 756.1111.2222.33 |
| chl-044 | fiction | AHV number not taken from the grid: 756.2222.3333.44 |
| chl-045 | fiction | AHV number not taken from the grid: 756.3333.4444.55 |
| chl-049 | evidence | patient.insurance_number = '555666777' has no evidence quote |
| chl-049 | evidence | patient.insurer = 'Krankenkasse Beispiel' has no evidence quote |
| chl-052 | evidence | patient.insurance_number = '123456789' has no evidence quote |
| chl-052 | evidence | patient.insurer = 'Krankenkasse Muster' has no evidence quote |
| chl-053 | evidence | patient.insurance_number = '987654321' has no evidence quote |
| chl-053 | evidence | patient.insurer = 'Krankenkasse Muster' has no evidence quote |
| chl-054 | evidence | patient.insurance_number = '111222333' has no evidence quote |
| chl-054 | evidence | patient.insurer = 'Krankenkasse Muster' has no evidence quote |
| chl-059 | evidence | patient.insurer = 'Krankenkasse Aargau' has no evidence quote |
| chl-060 | language | labelled en, stopwords suggest de {'de': 4, 'fr': 0, 'it': 0, 'en': 0} |
| chl-087 | evidence | patient.insurer = "Caisse d'indemnités journalières Vaud" has no evidence quote |
| chl-089 | evidence | patient.insurer = 'Krankenkasse Nordostschweiz' has no evidence quote |

