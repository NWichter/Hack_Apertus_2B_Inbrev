# Data

All messages, people, practices and identifiers in this folder are **fictional**.
AHV numbers follow the official format but carry an invalid check digit on purpose.
No real patient data is used anywhere in this project.

| Path                               | Content                                                                         |
| ---------------------------------- | ------------------------------------------------------------------------------- |
| `taxonomy.yaml`                    | Routes, deadlines, assignees and the safety flag, with definitions              |
| `schema/triage_result.schema.json` | JSON Schema of one triage result (also used for constrained decoding)           |
| `seed/messages.seed.jsonl`         | 12 handwritten seed messages (DE/FR/IT; e-mail, fax, web form) with gold labels |

## Gold set (planned, ~300 messages)

| Part           | Share | How it is made                                                                                                                                                                                                                                                   | Why                                             |
| -------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| Template-based | ~60 % | Structures of public form types (cost approval, lab report layout, referral, sick-note request) filled with controlled variables (sender type, route, deadline, language, formality, typos); wording by a different model family than Apertus, prompt documented | Coverage and control                            |
| Handwritten    | ~20 % | Written by hand, deliberately messy: typos, mixed topics, non-native German, FR/IT                                                                                                                                                                               | Realism; guards against measuring the generator |
| Fax / scan     | ~20 % | Templates rendered to PDF, printed and scanned or degraded (skew, noise, stamps)                                                                                                                                                                                 | OCR path                                        |

Labels: route, deadline, assignee, safety flag, patient and route fields, each with a verbatim evidence quote.
A subset (≥ 60 messages) is labelled twice, 48 h apart, blind; agreement is reported as Cohen's κ.

## Record format (`*.jsonl`)

```json
{
  "message_id": "seed-004",
  "language": "de",
  "channel": "email | fax | web_form",
  "sender": "…",
  "subject": "…",
  "body": "…",
  "source": "handwritten_seed | template | scan",
  "label": { "route": "insurer", "deadline": "this_week", "assignee": "admin", "safety_flag": false, "abstain": false,
             "patient": { … }, "fields": { … }, "evidence": [ { "field": "deadline", "quote": "bis 08.10.2026" } ] }
}
```

Every `quote` must be a substring of `subject + "\n" + body`; the evaluation checks this.

## Licence

Data: CDLA-Permissive-2.0. Larger working files (scans, model outputs) are kept outside the repository and passed in via `DATA_DIR`.
