# Apertus vs. keyword rules vs. rules-first hybrid

Gold `messages.jsonl`, predictions `grascco-p3-8b.jsonl`, n = 40

| Setup | Model calls | Route acc | Macro-F1 | Clinical exclusion recall | Today recall | Deadline acc |
| --- | --- | --- | --- | --- | --- | --- |
| Keyword rules | 0 | 40/40 [0.91, 1.00] | 1.000 | – | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |
| Inbrev (Apertus) | 40 | 40/40 [0.91, 1.00] | 1.000 | – | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |
| Hybrid: rules if clear, else Apertus | 22 | 40/40 [0.91, 1.00] | 1.000 | – | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] |

Route, paired: Apertus right and rules wrong 0, rules right and Apertus wrong 0, exact McNemar p = 1.

Rules are clear on 18 of 40 messages: route correct rules 18/18 [0.82, 1.00], Apertus 18/18 [0.82, 1.00]. Safety cases among them (missed by the hybrid unless Apertus is asked): none.

**By gold route**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| report_received | 40 | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] | – | – |

**By writing level**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| None | 40 | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] | – | – |

**Mixed topics**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| None | 40 | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] | – | – |

**By safety case type**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| None | 40 | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] | – | – |

**By language**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| de | 40 | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] | – | – |

**By generator**

| group | n | rules route | Apertus route | rules clinical excl. | Apertus clinical excl. |
| --- | --- | --- | --- | --- | --- |
| grascco | 40 | 40/40 [0.91, 1.00] | 40/40 [0.91, 1.00] | – | – |

