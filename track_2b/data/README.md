# Data

All messages, people, practices, organisations and identifiers in the files committed to this
folder are **fictional**. AHV numbers follow the official format but carry an invalid check digit
on purpose. No real patient data is committed. Optional external datasets are downloaded into
`external/` (gitignored, see below); one of them contains real, de-identified patient questions and
is never committed or used for a reported number.

| Path                               | Content                                                                         |
| ---------------------------------- | ------------------------------------------------------------------------------- |
| `taxonomy.yaml`                    | Routes, deadlines, assignees and the safety flag, with definitions              |
| `schema/triage_result.schema.json` | JSON Schema of one triage result (also used for constrained decoding)           |
| `seed/messages.seed.jsonl`         | 12 handwritten seed messages (DE/FR/IT; e-mail, fax, web form) with gold labels |
| `generation/PROMPT.md`             | Exact generation prompt for the synthetic part (both generators)                |
| `ood/swiss_practice_inbox.jsonl`   | 30 synthetic Swiss practice messages (DE/FR/IT/EN), fictitious senders/domains  |
| `external/` (gitignored)           | Optional external datasets, downloaded by `scripts/adapt_external_data.py`      |

## Gold set (planned, ~300 messages)

| Part           | Share | How it is made                                                                                                                                                                                                                                                   | Why                                             |
| -------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| Template-based | ~60 % | Structures of public form types (cost approval, lab report layout, referral, sick-note request) filled with controlled variables (sender type, route, deadline, language, formality, typos); wording by a different model family than Apertus, prompt documented | Coverage and control                            |
| Handwritten    | ~20 % | Written by hand, deliberately messy: typos, mixed topics, non-native German, FR/IT                                                                                                                                                                               | Realism; guards against measuring the generator |
| Fax / scan     | ~20 % | Templates rendered to PDF, printed and scanned or degraded (skew, noise, stamps)                                                                                                                                                                                 | OCR path                                        |

Labels: route, deadline, assignee, safety flag, patient and route fields, each with a verbatim evidence quote.
A subset (≥ 60 messages) is labelled twice, 48 h apart, blind; agreement is reported as Cohen's κ.

## Synthetic part (v0)

180 template-based messages, generated on 2026-10-01. Apertus, the model under test, neither
generates nor labels any of them.

- **Labels before text.** `scripts/make_grid.py` (seed 2026) builds 180 specs and fixes route,
  deadline, deadline date, assignee, safety flag and abstain _before_ any text exists. It also
  fixes language (de 99, fr 45, it 27, en 9), channel (email, hin_mail, fax, web_form), sender type,
  formality and writing level (clean, typos, non-native, dialect). Mixed topics (18), genuinely
  ambiguous messages with `abstain: true` (9), safety cases (16 true: explicit and mentioned in
  passing) and 14 traps that sound medical but are not acute are fixed in the grid too.
- **Two generator families, one prompt.** 90 messages by Claude (`claude-opus-5-5`), 90 by OpenAI
  Codex (`gpt-5.5`). The split is balanced over all grid variables. The prompt is in
  `generation/PROMPT.md`. Every row records `generator`, `generator_model`, `generated_at` and
  `prompt_version`.
- **Checks.** `scripts/validate.py` checks each row against the grid and the schema. It also checks
  that evidence quotes are verbatim, that deadline dates are consistent, that AHV check digits are
  invalid, that e-mail domains are `.example` and phone numbers use the `000` block, and it looks
  for near-duplicates. Minimal fixes to generated rows carry `edited_by`. Rows whose label does
  not clearly follow from the text carry `review_flag` and `review_reason`; they are not relabelled.
- **Status: human review pending.** No label has been checked by a person yet. The files live
  outside the repository (`$DATA_DIR/gold-set/`).

Extra record fields in this part: `sender_type`, `received_at` (deadlines are relative to it),
`meta` (grid variables), the generator fields above, and the optional review fields. Channel
`hin_mail` and source `synthetic` are added to the values listed below.

`scripts/render_fax.py` renders selected rows as degraded fax pages (PNG and PDF: skew, noise,
stamp) for the OCR path. Dependencies: `scripts/requirements.txt`.

## Synthetic Swiss practice set (`ood/`)

30 messages written with an LLM coding assistant (not Apertus) on 2026-10-02/03, then edited so
that every organisation and e-mail domain is fictitious (`KV Beispiel AG`, `*.example`). Labels
have not been reviewed by a person yet. Used as a small extra check, not as gold data.

## External datasets (not in the repository)

`python scripts/adapt_external_data.py --download` fetches raw data into `external/`; adapters then
map it to the record format below with **heuristic** labels (e.g. every symptom-triage case becomes
route `other`). Licences as stated on the dataset cards (checked 2026-10-03):

| Dataset                                             | Licence on the card | Note                                                                |
| --------------------------------------------------- | ------------------- | ------------------------------------------------------------------- |
| `sweatSmile/medical-symptom-triage`                 | none declared       | English symptom descriptions with urgency labels                    |
| `ale-dp/german-english-email-ticket-classification` | CC-BY-NC-4.0        | IT support tickets, not practice mail                               |
| `PortalPal-AI/Portal-Messaging-Topics`              | CC-BY-NC-4.0        | Topic list only                                                     |
| `lavita/ChatDoctor-HealthCareMagic-100k`            | none declared       | Real de-identified patient questions; only with `--include-real-patient-text`, never committed |

No number in the technical report is computed on these sets.

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

The full text is in [`LICENSE`](LICENSE). It covers the files of this folder that are in the repository. The external datasets above (`external/`, not in the repository) are not covered and keep the licences stated on their dataset cards.
