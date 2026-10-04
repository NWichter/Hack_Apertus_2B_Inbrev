# Data

All messages, people, practices, organisations and identifiers in the files committed to this
folder are **fictional**, except four real Swiss organisation names in the Swiss practice set
(see below). AHV numbers follow the official format but carry an invalid check digit
on purpose. No real patient data is committed. Optional external datasets are downloaded into
`external/` (gitignored, see below); one of them contains real, de-identified patient questions and
is never committed or used for a reported number.

| Path                               | Content                                                                         |
| ---------------------------------- | ------------------------------------------------------------------------------- |
| `taxonomy.yaml`                    | Routes, deadlines, assignees and the safety flag, with definitions              |
| `schema/triage_result.schema.json` | JSON Schema of one triage result (also used for constrained decoding)           |
| `seed/messages.seed.jsonl`         | 12 seed messages (DE/FR/IT; e-mail, fax, web form) with gold labels, written by Claude (see below) |
| `generation/PROMPT.md`             | Exact generation prompt for the synthetic part (both generators)                |
| `ood/swiss_practice_inbox.jsonl`   | 30 synthetic Swiss practice messages (DE/FR/IT/EN), `.example` e-mail domains (see below) |
| `external/` (gitignored)           | Optional external datasets, downloaded by `scripts/adapt_external_data.py`      |

## Seed messages (`seed/`)

The 12 seed messages were **not written by a person**. Claude (`claude-opus-5-5`, Claude Code agent
session) wrote them and their labels on 2026-10-01 (about 14:20 CEST) as a Python script that
emitted the JSONL file; on the same day it replaced a real insurer name with `KV Beispiel AG`. The
value `source: handwritten_seed` means "written one by one, not from the grid", not "written by
hand". Rows carry no generator, date or review fields. Evidence quotes were checked by script to
be verbatim; no person has reviewed the labels. The seeds were used to develop prompt p2 and the
checks, so they are a development set, not a held-out test set.

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
  Codex (`gpt-5.5`). The split is roughly balanced over the grid variables (largest gaps: English
  6 vs 3, safety cases 9 vs 7, Claude vs Codex). The prompt is in
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

30 messages and labels written by an Antigravity agent session (Google Gemini, not Apertus) on
2026-10-03 at about 06:54 CEST; no generation prompt or model version was recorded. On the evening
of 2026-10-03 a Codex session (`gpt-6.1-sol`, per the git-ai authorship note of commit `fecd8d2`)
replaced real e-mail domains and insurer, hospital and IV-office names with fictitious ones
(`KV Beispiel AG`, `*.example`). Four rows still name real Swiss organisations: `swiss-prx-0010`
(Sun Store pharmacy), `swiss-prx-0017` (Ospedale Regionale di Bellinzona e Valli),
`swiss-prx-0021` (Labor Viollier AG) and `swiss-prx-0022` (Coop Vitality). Rows carry no
generator, date or review fields and no `received_at`, so deadline labels cannot be checked
against a time of receipt. Labels have not been reviewed by a person. Used as a small extra check,
not as gold data. The unedited first version (real domains) exists only in the gitignored
`external/` folder.

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

## Sources and provenance

Who or what made each dataset, why it is used and whether it is redistributed. Licences: see the
table above and the Licence section below.

| Dataset | Made by / source | Rows | In this repository? | Why it is used | Used for |
| --- | --- | --- | --- | --- | --- |
| Seed (`seed/`) | Claude `claude-opus-5-5`, 2026-10-01; labels by the same session | 12 | yes | Development set for prompt and checks | Seed row in the report (8B, prompt p1) |
| Synthetic v0 (`$DATA_DIR/gold-set/merged.v0.jsonl`) | Grid `make_grid.py --seed 2026`; text by Claude `claude-opus-5-5` (90) and Codex `gpt-5.5` (90), 2026-10-01, prompt v0.1 | 180 | no (outside, `DATA_DIR`) | Main evaluation set; labels fixed before text | Main table (8B, 70B, baselines) |
| Swiss practice set (`ood/`) | Antigravity (Gemini) session, 2026-10-03; edited by Codex `gpt-6.1-sol` | 30 | yes | Small extra check with practice-style mail | Swiss row in the report (8B, 70B, keywords) |
| `sweatSmile/medical-symptom-triage` (https://huggingface.co/datasets/sweatSmile/medical-symptom-triage), split `validation` | Third party | 278 downloaded | no, local only | English symptom texts with urgency labels as an out-of-domain safety stress test | 10 cases sent to Apertus 8B on 2026-10-02 (local `runs/ood_eval_10`, plus one test call); no reported number |
| `ale-dp/german-english-email-ticket-classification` (https://huggingface.co/datasets/ale-dp/german-english-email-ticket-classification) | Third party | 699 downloaded | no, local only | German support tickets for administrative wording | Baselines only; no reported number |
| `PortalPal-AI/Portal-Messaging-Topics` (https://huggingface.co/datasets/PortalPal-AI/Portal-Messaging-Topics) | Third party | topic list | no, local only | Compare the route taxonomy with patient-portal topics | Not used in any run |
| `lavita/ChatDoctor-HealthCareMagic-100k` (https://huggingface.co/datasets/lavita/ChatDoctor-HealthCareMagic-100k) | Third party | 250 downloaded | no, local only | Excluded from evaluation: real (de-identified) patient questions, no licence declared, English clinical Q&A rather than practice administration | No stored run shows it was sent to a model; no number |

The four third-party files were downloaded on 2026-10-02 (about 21:00 CEST) from the `main`
revision via `resolve/main` or the Hugging Face datasets-server rows API; no commit hash was
recorded, so a new download may differ. A copy of `jonas-is-coding/german-emails` (2,576 rows) was
downloaded at the same time; no script reads it and no number uses it. GraSCCo (Zenodo) was
considered as a template source for `report_received` but has not been downloaded or used.
Closed models (Claude, GPT-5.5/Codex, Gemini/Antigravity) were used only to write or edit test
data and code during development; Inbrev itself calls only Apertus.

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
