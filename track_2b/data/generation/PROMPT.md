# Generation prompt (synthetic part, v0)

`prompt_version: v0.1` · used on 2026-10-01

Both generators receive exactly the same prompt: the block **Generator prompt** below,
followed by `SPECS (JSONL):` and the spec lines of one batch from `grid.jsonl`
(built by `scripts/make_grid.py`, seed 2026). The only difference is the delivery
wrapper (last section): where the generator writes its output.

Apertus is the model under test and is never used to generate or label data.

| Generator | Model                                           | Invocation                                                                                                                                                                                                                                                         |
| --------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| claude    | `claude-opus-5-5` (Claude Code)                 | prompt and specs in the session context, output written as JSONL                                                                                                                                                                                                   |
| codex     | `gpt-5.5`, reasoning `high` (codex-cli 0.155.1) | `codex exec --skip-git-repo-check --ignore-user-config -m gpt-5.5 -c model_reasoning_effort="high" -c windows.sandbox="elevated" -s workspace-write -C <dir> -o <batch>.last.txt - < <batch>.prompt.txt` (prompt on stdin, 6 batches of 15 specs, run in parallel) |

Known leak: the example amounts in the prompt ("CHF 1'240.50", "CHF 418.60") and example
names ("Spital Unterseetal", "Krankenkasse Alpina", "Caisse-maladie Lémanis") were reused by
codex. Three repeated amounts were changed afterwards (`edited_by: claude`); the names were kept.
A later prompt version should drop concrete examples.

The labels (`route`, `deadline`, `deadline_date`, `assignee`, `safety_flag`, `abstain`) are
fixed by the grid **before** generation. Generators write text that fits the labels; they
choose only sender, wording, patient data, route fields and evidence quotes.

## Generator prompt

```text
You write synthetic test messages for the inbox of a Swiss general practice
(Hausarztpraxis / cabinet de médecine générale / studio medico). The messages are
the evaluation set of a triage system that routes each message by handling path and
administrative deadline. Each message must look like real practice mail, but every
person, practice, institution, address, phone number and identifier is invented.

For every SPEC line you get, write exactly one message and output one JSON object.

=== Labels are fixed ===
Each spec contains "label" with route, deadline, deadline_date, assignee,
safety_flag and abstain. Copy these values unchanged. Write the message so that a
careful medical practice assistant (MPA) would assign exactly these labels from the
text alone. Never change a label to fit your text; change the text instead.

Routes:
- report_received: lab result, imaging report, discharge letter or specialist report
  arrives for the doctor. Deadline is always "today" by rule; no deadline text needed.
- appointment: book, move or cancel an appointment.
- prescription_request: repeat prescription or medication request.
- insurer: cost approval (Kostengutsprache), insurer query, IV (disability insurance)
  report request, daily allowance (Krankentaggeld) or accident insurer form.
- referral_in: another physician or hospital refers a patient to this practice.
- certificate_request: sick note (Arbeitsunfähigkeitszeugnis / certificat médical /
  certificato medico) or another confirmation.
- billing: invoice, reminder, billing question (from supplier, patient, insurer).
- spam_marketing: advertising, newsletter, pharma marketing, webinars, software offers.
- other: anything else (records request, authority letter, general question ...).

Deadline (administrative, relative to "received_at"):
- today: action needed today or tomorrow (deadline_date = received date or +1 day).
- this_week: action needed within 2 to 7 days (deadline_date in that window).
- none: no deadline, or a deadline more than 7 days away.
If label.deadline_date is not null, the text MUST contain that date, either written
as DD.MM.YYYY / DD.MM. or as an unambiguous relative expression that resolves to it
from received_at ("morgen", "bis Freitag", "d'ici jeudi", "entro venerdì"). Use the
given received_weekday and deadline_weekday. If deadline is "none" and deadline_date
is null, the text must not contain any action date within the next 7 days.

Safety (spec field "safety_case"):
- acute_explicit: the sender describes possibly acute symptoms happening now
  (chest pain, breathing problems, sudden weakness or speech problems, heavy bleeding,
  severe allergic reaction, suicidal thoughts, high fever in a small child ...).
  safety_flag is true, deadline today, assignee doctor.
- acute_incidental: the message is mainly administrative (the given route), but the
  sender mentions such a current symptom in passing ("PS: since this morning my chest
  feels tight, probably nothing"). Same labels as acute_explicit except the route.
- medical_trap: the text contains medical or alarming words but describes NO current
  acute situation: a past and treated event, a stable chronic condition, a family
  history, an insurer asking about last year's infarction, a lab report with values,
  "no emergency". safety_flag is false.
- none: ordinary message, no symptoms that could be acute.
Do not judge severity in the text and do not add medical advice.

Other spec fields:
- mixed_topic true: the message contains a second, clearly subordinate request of
  type "secondary_route". The main request (label.route) must clearly dominate
  (comes first, takes most of the text, or is named as the main reason).
- abstain true: write a genuinely ambiguous message: a careful human could not
  decide between label.route and "abstain_alternative_route" from the text alone
  (both asks equally weighted, or the purpose stays unclear). Keep label.route as given.
- spam_fake_urgency true: the advert pushes urgency ("nur noch heute", "dernier jour");
  the deadline label stays "none".
- include_birth_date true: give the patient's birth date in the text.
- ahv_number not null: use exactly this AHV number in the text (it has an invalid
  check digit on purpose). Never invent other AHV numbers.
- formality: formal | neutral | informal.
- writing_level: clean; typos (3 to 6 realistic typing errors); non_native (grammar
  and word choice of a non-native speaker); dialect (DE: Swiss German colouring such
  as "Grüezi", "Merci vilmal", "es Rezäpt", "chönd Sie"; FR: Swiss French such as
  "septante", "natel", "bonne journée"; IT: Ticino colouring such as "natel", "ciao").
- channel: email (normal mail); hin_mail (secured professional mail, sender address
  ends in "hin.example"); fax (plain text as OCR would read it: fax header line,
  "Seite 1/1", headings in capitals, sender block); web_form (practice web form:
  lines "Name: ...", "Geburtsdatum: ...", "Anliegen: ...", in the message language).
- sender_type: who writes (patient, relative, lab, hospital, specialist, radiology,
  referring_physician, health_insurer, iv_office, accident_insurer,
  daily_allowance_insurer, pharmacy, nursing_home, employer, school, supplier,
  billing_service, pharma, vendor, event_organizer, authority, colleague,
  specialist_office).

=== Swiss realism ===
- Language of subject and body = spec "language" (de, fr, it, en). German texts use
  Swiss spelling: never "ß", always "ss" (Grüsse, Strasse).
- Dates DD.MM.YYYY, amounts "CHF 1'240.50" or "CHF 418.60", Swiss cantons and
  real town names are allowed for addresses.
- All persons, practices, labs, hospitals, insurers and companies are invented.
  Do not use real brands or institutions (no Helsana, CSS, Swica, Sanitas, Visana,
  Groupe Mutuel, Assura, Concordia, KPT, Suva, Unilabs, Synlab, Viollier, Dianalabs,
  Inselspital, CHUV, HUG, USZ, no real "Kantonsspital <Town>", no real pharma brand).
  Use invented names such as "Labor Aaretal AG", "Spital Unterseetal",
  "Krankenkasse Alpina (fiktiv)", "Caisse-maladie Lémanis". Generic terms
  ("die IV-Stelle", "l'office AI du canton de Vaud") are fine.
- E-mail addresses use domains ending in ".example" (e.g. "a.muster@mail.example",
  "befunde@labor-aaretal.hin.example"). Phone numbers use the unassigned block
  "000": "079 000 12 34", "044 000 56 78", "+41 91 000 22 11".
- Drug names: common generic names (Metformin, Amlodipin, Ibuprofen ...), no brands.
- Vary names, regions and phrasing; no two messages may share the same opening
  sentence. Do not mention that the text is synthetic.
- Length: body 30 to 220 words; fax and reports up to 300 words.

=== Gold annotation ===
- label.patient: {name, birth_date (YYYY-MM-DD), insurance_number, ahv_number,
  insurer}; use null for anything not in the text; {} for spam or when no patient is
  concerned. name as "First Last".
- label.fields: route-specific values as they appear in the text, e.g.
  report_received: report_type, sender_institution, examination_date;
  appointment: appointment_action (book|move|cancel), existing_appointment, requested_dates;
  prescription_request: medication, pharmacy;
  insurer: insurer_reference, requested_document;
  referral_in: referring_physician, referral_reason;
  certificate_request: certificate_type, period;
  billing: invoice_number, amount, creditor;
  other: topic. Use {} when nothing applies.
- label.evidence: list of {"field", "quote"}. Every quote is copied VERBATIM from
  subject + "\n" + body (same case, same typos, same punctuation), 2 to 15 words.
  Required: at least one quote for "route"; one for "deadline" if deadline_date is
  not null; one for "safety_flag" if safety_flag is true; one for each non-null
  patient.* and fields.* value (field names like "patient.name", "fields.medication").
  For mixed_topic, one extra quote with field "secondary_route".

=== Output format ===
One JSON object per spec, one per line (JSONL), UTF-8, no Markdown fences, keys:
{"message_id", "language", "channel", "sender_type", "sender", "received_at",
 "subject", "body", "label": {"route", "deadline", "deadline_date", "assignee",
 "safety_flag", "abstain", "patient", "fields", "evidence"}}
message_id, language, channel, sender_type and received_at are copied from the spec.
"sender" is the display sender (name and address, or fax sender line). Use "\n" for
line breaks inside body. Before finishing, check that every evidence quote is an
exact substring of subject + "\n" + body.
```

## Delivery wrapper

- **codex:** appended after the specs:
  `Write the result to the file <batch>.out.jsonl in the current directory (one line per spec, in spec order). Do not create other files. You may run python to check the quotes.`
- **claude:** the same prompt in the session; output collected in `claude.jsonl`.

## Post-processing

`scripts/assemble.py` adds the grid metadata (`formality`, `writing_level`, `mixed_topic`,
`secondary_route`, `safety_case`, …), `source: "synthetic"`, `generator`,
`generator_model`, `generated_at` and `prompt_version`. `scripts/validate.py` checks the
result against the grid and the schema. Fixes to generated lines are marked
`edited_by: claude`; doubts about a label are marked `review_flag` with a reason and are
never relabelled silently.
