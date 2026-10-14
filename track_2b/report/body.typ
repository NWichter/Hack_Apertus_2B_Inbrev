- #strong[Demo video (under 2 min):] `website/media/video.mp4` in the
  repository; public link in the submission form

#emph[Version of 14 October 2026. Every number is measured or cited;
what is not measured yet is named as such. Measured numbers come from
synthetic data whose labels have not yet been reviewed by a person.]

= 1. Summary
<summary>
Swiss general practitioners spend more and more time on administration:
9.5 hours per week in 2025, up from 8.6 in 2020, and every additional
administrative hour raises the odds of stress @zeller2026workforce.
Physicians in private practice report 54 minutes per day for requests
from authorities and insurers alone @golder2025fmh. Much of this arrives
through the practice inbox @arndt2017tethered. Patient messages fall
under professional secrecy, which binds physicians and their assistants
alike @schweiz1937stgb, so sending them to a foreign cloud model is not
an option.

Inbrev sorts the inbox of a Swiss practice locally with Apertus. It
assigns each message to one of nine administrative routes, derives the
administrative deadline and the person in charge, extracts patient and
case fields, and backs every decision with a verbatim quote from the
message. It never assesses clinical content: a message that may describe
symptoms leaves automation and goes to a person, in the same queue as
messages the model is unsure about, without any ranking by severity.
Results (Apertus 8B; synthetic data, labels not reviewed by a person):

- #strong[Gold set, 180 messages, default configuration] (prompt p3 plus
  a second, narrow 8B check for current complaints, chosen on a dev
  split and then measured once here): all 16 messages with clinical
  content leave automation (keyword rules: 7), 170 of 180 routes are
  right, 140 of 180 messages run automatically and 40 go to a person.
  Before the second check: 13 of 16 and 151 automatic.
- #strong[Clinical challenge set] (115 messages, 44 clinical, 39 medical
  traps, written after p3 was frozen; later part of the dev split for
  the second check): p3 alone excludes 41 of 44 with 8B, 44 of 44 with
  70B, keyword rules 31 of 44.
- #strong[Labels:] two open-weights models labelled all 367 test
  messages blind; they agree with our labels on clinical content (κ
  0.97--0.98) and route (κ 0.93), and scoring against their labels does
  not change the ranking against the keyword rules. No person has
  reviewed labels yet.
- #strong[Other models:] Qwen3.5-9B and Ministral 8B in the identical
  pipeline route better than Apertus 8B (177 vs 170 of 180, wrong routes
  that run automatically 1 vs 8); §5 says why we still use Apertus.
  Clinical reports written by people are routed right (GraSCCo 40/40,
  PARHAF 37/38).
- #strong[Offline and cost:] with local Q4 weights Inbrev runs on a
  Docker network without internet access (192 s per message on a laptop
  CPU, 62.7 s natively on its integrated GPU); a mini PC costs about CHF
  12 per 1,000 messages at 60 a day.

= 2. Architecture
<architecture>
Inbrev is a fixed pipeline, not an agent. Small local models are
reliable on narrowly cut tasks and weak on complex ones @xu2026small, so
the model does only what rules cannot: read free text in four languages
and point to the passage that supports a decision.

+ #strong[Intake.] E-mail (`.eml` or IMAP, read-only, including PDF
  attachments), HIN mail, fax pages as PDF or image (Tesseract OCR for
  German, French and Italian), web forms.
+ #strong[Apertus with an enforced JSON schema]
  @willard2023outlines@geng2023grammar. The schema orders each quote
  before its decision (route quote → route, safety quote → flag,
  deadline quote → date). Three samples are drawn in one request.
+ #strong[Deterministic checks per sample.] Every quote must occur in
  the message: verbatim, after case and whitespace folding, or at least
  90 % similar to one span; the evidence shown to a person is always the
  original text, never the model's copy. Language models often cite
  incompletely @gao2023citations, and Apertus showed low faithfulness in
  production use @kruckenberg2026liip, so a value without a verifiable
  quote is dropped. Dates must match their quote; AHV numbers must occur
  in the text; fields that do not belong to the chosen route are
  removed.
+ #strong[Rules instead of model judgement where possible.] The deadline
  category is computed in code from the quoted date and the time of
  receipt; without a quoted date or time there is no deadline. The
  assignee follows from the route. A safety flag always means "doctor,
  today".
+ #strong[Vote and abstention.] Route and fields by majority over the
  samples; the safety flag is raised if any sample or a multilingual
  lexical net fires. Agreement across samples is used as the uncertainty
  signal instead of a verbalised confidence, which is overconfident
  @xiong2024uncertainty@wang2023selfconsistency. A second, short 8B call
  (default since 13 October) asks only whether someone describes a
  current complaint and must quote it; one verified yes out of three
  samples also raises the flag (not for reports, which go to the doctor
  anyway). If the samples disagree, the model marks the message as
  ambiguous, or no route evidence survives, Inbrev abstains: a person
  decides @wen2025abstention.
+ #strong[Output.] A sorted inbox (web UI: "a person decides" for unsure
  messages and messages with clinical content, by time of receipt and
  without a ranking among them; then today, this week, no deadline), a
  JSON result per message following
  `data/schema/triage_result.schema.json`, an API under `/v1/`, and an
  audit log that stores a hash and the decision, not the text. Reply
  drafts are fixed templates for administrative routes only; no
  model-written text reaches patients.

== Target architecture (mandatory)
<target-architecture-mandatory>
Inbrev is built for #strong[a) on-premise] and #strong[b) air-gapped]
operation; #strong[c) a sovereign Swiss cloud] is an option for
single-doctor practices.

Health data are sensitive personal data under the Swiss Data Protection
Act, which also requires data protection by design and allows processing
by third parties only where no duty of secrecy forbids it
@schweiz2020dsg. A system whose data never leave the practice avoids the
question. Open weights that run on the practice's own hardware also keep
the model auditable @riedemann2024open@apertus2025.

#figure(
  align(center)[#table(
    columns: (13.57%, 86.43%),
    align: (auto,auto,),
    table.header([Phase], [Dependencies],),
    table.hline(),
    [Build time], [Docker images (Python, llama.cpp), Python packages,
    Tesseract language data, Apertus weights from Hugging Face
    (checksum)],
    [Runtime], [none; the model is reached over an internal Docker
    network without internet access. Optional: IMAP mail pick-up],
  )]
  , kind: table
  )

#strong[Offline run with local weights.] `make offline-eval`
(`scripts/run_offline_eval.sh`) starts llama.cpp with a community
Q4\_K\_M GGUF of the Apertus 8B text weights (Apache-2.0; Track 2 allows
GGUF builds) and Inbrev on a Docker network with `internal: true`\; only
an optional nginx gateway for the web UI also sits on the host network.
The log records the SHA-256 of the loaded weights (equal to the Hugging
Face LFS hash, revision `248ec68`), `docker inspect` of both containers,
an egress test from the Inbrev container (DNS, TCP to 1.1.1.1:443 and
HTTPS all fail) and a control on the default network (all succeed),
memory samples and the evaluation. llama.cpp rejects `n` \> 1 (HTTP
400), so Inbrev falls back to one request per sample. On a 28-W laptop
CPU (Ryzen 7 PRO 8840U, Docker Desktop) the model needs 6.2 GiB RAM and
Inbrev 167 MiB; results are in §5. The run is in `evidence/offline/`.

= 3. Use of Apertus
<use-of-apertus>
- #strong[Model:] swiss-ai/Apertus-v1.5-8B for inference;
  Apertus-v1.5-70B as a comparison, recommended where the hardware
  allows it (§5) @apertus2025
- #strong[How it is used:] inference (classification and extraction with
  an enforced JSON schema, three samples per message; one on a CPU)
- #strong[Where it runs:] development and evaluation on the Hack Apertus
  endpoint (OpenAI-compatible, vLLM behind a LiteLLM proxy); target
  deployment on local weights (llama.cpp, GGUF Q4) inside the practice,
  measured offline on a CPU (§2, §5)

Settings: temperature 0.7 for the three samples, at most 900 output
tokens, thinking off by default because it lowers instruction following
@wiegand2026apertusbench\; thinking is measured as an ablation. The
system prompt (p2; p3 since 4 October, see section 5) lists the routes
with short multilingual cues, the rules for safety, deadlines and
quotes, and an output format with placeholders only.

= 4. Data
<data>
All messages, people, practices and identifiers are fictional; AHV
numbers have a valid format and an invalid check digit. No real patient
data is used. Licence: CDLA-Permissive-2.0.

- #strong[Seed:] 12 messages (German, French, Italian; e-mail, fax, web
  form) with gold labels, in the repository. Claude (`claude-opus-5-5`)
  wrote them one by one in an agent session, not a person; they served
  as the development set for the prompt and the checks.
- #strong[Synthetic part (v0):] 180 messages. Labels are fixed by a
  seeded grid #emph[before] any text exists; two generator families
  write the text from one documented prompt, 90 messages each (Claude
  and GPT-5.5). Apertus neither writes nor labels data
  @panickssery2024selfpref. German 99, French 45, Italian 27, English 9;
  16 messages with clinical content (7 explicit, 9 in passing), 14
  medical traps, 9 ambiguous messages. A validator checks schema,
  verbatim quotes, dates, invalid AHV check digits, fictitious domains
  and near-duplicates.
- #strong[Swiss practice set:] 30 messages (`data/ood/`), text and
  labels by an Antigravity agent session (Gemini, `gemini-3.8-flash`) on
  3 October; real organisation names and domains were later replaced by
  fictitious ones (`scripts/annotate_swiss_set.py`); each row records
  its edits in `provenance`\; the generation prompt was not recorded.
- #strong[Open-generator set:] 42 messages from a fresh seeded grid
  (seed 2027, 8 with clinical content, 7 traps), text by an open-weights
  model, NVIDIA Nemotron 3 Ultra @nvidia2026nemotron, through OpenRouter
  with the same prompt minus all example values; 3 of 45 rows failed
  validation and were dropped. Nobody tuned prompt, checks or lexicon on
  it. It tests whether the results depend on the closed generators.
- #strong[GraSCCo report set:] 40 of the 63 synthetic German clinical
  letters of GraSCCo v1.1 (CC BY 4.0 on Zenodo, the authors also state
  CC0) @modersohn2022grascco, verbatim (5 shortened at a paragraph end)
  behind a fixed one-line cover note, as realistic long
  `report_received` messages (`data/grascco/`). Labels follow one rule:
  route `report_received`, deadline today, no clinical flag. The letters
  are German and Austrian, not Swiss.
- #strong[Clinical-exclusion challenge set:] 115 messages from a new
  seeded grid (seed 5151), 44 with clinical content (17 explicit, 27 in
  passing), 39 medical traps (negations, past events, chronic
  conditions), more typos and dialect; text by Nemotron 3 Ultra (open
  weights, free tier), written on 13 October after prompt, checks and
  lexical net were frozen (`evidence/challenge/`). It was unseen for p3,
  but it is part of the dev split on which the second check was chosen,
  so it is not a hold-out for that check.
- #strong[PARHAF report set:] 38 French clinical reports from PARHAF
  (fictitious cases written by resident physicians; CC BY 4.0 / Etalab
  2.0), verbatim behind a fixed cover note, same rule as GraSCCo
  (`data/parhaf/`).
- #strong[External datasets] (Hugging Face) were downloaded only for
  local stress tests, are not redistributed and give no reported number;
  `data/README.md` lists each source and why it is or is not used.
- #strong[Label check without people (yet):] two open-weights models,
  Nemotron 3 Super and gpt-oss-120b, labelled all 367 test messages
  blind from the written rules, seeing only the message
  (`scripts/annotate_open_models.py`, USD 0.06). They are not human
  annotators: agreement shows that the rules can be applied
  consistently, not that labels are right. The 36 disputed messages are
  the review queue for a person; `tools/review/` (Cohen's κ
  @cohen1960kappa) is ready, the human review has not happened yet.

Closed models (Claude, GPT-5.5 via Codex, Gemini via Antigravity) wrote
or edited test data and code during development only, and reviewed
drafts. Open-weights models have three supporting roles: Nemotron 3
Ultra wrote the Nemotron, dev and challenge sets; Nemotron 3 Super and
gpt-oss-120b are the second annotators; Qwen3.5-9B and Ministral 8B run
once in the Inbrev pipeline as a comparison (Llama 3.1 8B was tried, but
the provider rate-limited it). At runtime Inbrev calls only Apertus.

Synthetic data can miss the distribution of real mail
@long2024synthetic\; only the GraSCCo and PARHAF reports were written by
people, and they cover a single route.

= 5. Evaluation
<evaluation>
The main numbers are the clinical exclusion recall (share of messages
with clinical content that the safety net takes out of automation;
"safety" in the tables), the recall of the deadline "today" and the
share of messages that run without a person (coverage). Clinical
messages are rare, so recall and precision are reported instead of
accuracy @saito2015precision. Further metrics: route macro-F1, deadline
accuracy, field F1, evidence faithfulness @rashkin2023attribution,
tokens, latency and cost.

Results on the synthetic set v0 (n = 180; 16 clinical cases, 50 "today"
deadlines). TF-IDF uses five-fold cross-validation. Inbrev rows run the
full pipeline (schema, three samples at T = 0.7, checks, vote) on the
Hack Apertus endpoint, p2 on 3 October, p3 on 4 October, p3 with the
second check (default) on 13 October. Coverage counts messages that are
neither abstained nor flagged, at most 164 of 180. "One sample, no
checks" scores the first stored 8B sample as written, without checks,
net, vote or abstention (`scripts/ablation_first_sample.py`).

#figure(
  align(center)[#table(
    columns: (30%, 10%, 10%, 10%, 10%, 10%, 10%, 10%),
    align: (auto,auto,auto,auto,auto,auto,auto,auto,),
    table.header([Setup], [Route acc.], [Route F1], [Safety
      rec.], [Safety prec.], [Today rec.], [Deadl. acc.], [Coverage],),
    table.hline(),
    [Majority
    class], [0.14], [0.03], [0.00], [--], [0.00], [0.37], [1.00],
    [Keyword rules + lexical
    net], [0.79], [0.76], [0.44], [0.32], [0.76], [0.68], [0.88],
    [TF-IDF + logistic
    regression], [0.83], [0.82], [0.13], [1.00], [0.66], [0.68], [0.99],
    [8B, one sample, no
    checks], [0.87], [0.84], [0.56], [1.00], [0.70], [0.67], [0.95],
    [Inbrev 8B, p2 (schema, checks,
    vote)], [0.88], [0.85], [0.81], [0.46], [0.86], [0.82], [0.81],
    [Inbrev 70B,
    p2], [0.91], [0.89], [0.94], [0.50], [0.94], [0.85], [0.79],
    [Inbrev 8B,
    p3], [0.94], [0.94], [0.81], [0.46], [0.88], [0.84], [0.84],
    [#strong[Inbrev 8B, p3 + second check]
    (default)], [0.94], [0.94], [1.00], [0.41], [0.94], [0.81], [0.78],
    [Inbrev 70B,
    p3], [0.96], [0.96], [0.94], [0.50], [0.94], [0.87], [0.82],
  )]
  , kind: table
  )

With 95 % Wilson intervals (p2): clinical exclusion 13/16 \[0.57, 0.93\]
for 8B and 15/16 \[0.72, 0.99\] for 70B (McNemar p = 0.50), against 9/16
\[0.33, 0.77\] for a single 8B answer without checks and 7/16 \[0.23,
0.67\] for the keyword rules. Three samples add two cases (11/16 without
the lexical net), the net two more; it is tuned for recall, and about
half of the flags on this set are false alarms from the net (15 of 28
for 8B), which costs a doctor a glance, not a missed case. Recall
differs by generator (8B: 7/7 for texts by GPT-5.5, 6/9 by Claude), so
the set partly measures its authors; the open-generator and challenge
sets are the control. Field F1 is 0.73 for 8B and 0.83 for 70B; mean
latency per message 3.0 s and 10.7 s on the shared endpoint.

The baselines already route 79--83 % of the synthetic messages
correctly, so the route alone does not justify a language model on this
set. They fail where it matters: they find at most 44 % of the messages
with clinical content.

#strong[Where Apertus beats the rules.] Paired on the 180 messages, 8B
is right where the rules are wrong 27 times and the reverse 11 times
with p2 (McNemar p = 0.014), 32 and 5 times with p3 (p = 7·10⁻⁶): it
wins on insurer mail, marketing and symptoms mentioned in passing. A
rules-first hybrid (rules decide when exactly one route family matches
and the net is silent) needs the model for 94 of 180 messages but drops
to clinical exclusion 10/16, because 5 of 16 clinical messages look like
plain administration to the rules; on the challenge set it drops from 41
to 36 of 44. We therefore keep Apertus on every message
(`scripts/compare_hybrid.py`).

#figure(
  align(center)[#table(
    columns: (20%, 20%, 20%, 20%, 20%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Further sets (Inbrev 8B, p3 unless
      noted)], [n], [Route acc.], [Clinical excl.], [Keyword rules route
      \/ clinical],),
    table.hline(),
    [#strong[Challenge set] (8B, written after p3)], [115], [103/115
    \[0.83, 0.94\]], [#strong[41/44 \[0.82, 0.98\]]], [87/115 / 31/44],
    [#strong[Challenge set, 70B]], [115], [106/115 \[0.86,
    0.96\]], [#strong[44/44 \[0.92, 1.00\]]], [--],
    [Open generator (Nemotron)], [42], [39/42 \[0.81, 0.98\]], [8/8
    \[0.68, 1.00\]], [32/42 / 6/8],
    [GraSCCo letters (German, p2)], [40], [40/40 \[0.91, 1.00\]], [-- (7
    false flags)], [40/40 / --],
    [PARHAF reports (French)], [38], [37/38 \[0.87, 1.00\]], [-- (17
    false flags)], [3/38 / --],
    [Rendered fax pages via OCR (gold subset)], [60], [50/60 \[0.72,
    0.91\]], [12/16 flagged, 13/16 out of automation], [--],
  )]
  , kind: table
  )

#strong[Challenge set.] The 44 clinical messages narrow the interval of
the main metric: 8B 41/44, against 31/44 for the keyword rules (10 vs 0
discordant, exact McNemar p = 0.002), 70B 44/44 (8B vs 70B p = 0.25). Of
71 non-clinical messages, including 39 traps, 8B and 70B each flag 4
(precision 0.91 and 0.92). Route: 8B wins 20 vs 4 against the rules (p =
0.0015). A TF-IDF classifier cross-validated on the set itself reaches
39/44 (an in-domain reference, not deployable). #strong[Reports.] On
GraSCCo and PARHAF the false flags come almost only from the lexical net
(6 of 7; 16 of 17, mostly "urgence" in emergency department reports);
Apertus itself flags 1 of 38 French reports. Each costs a doctor's
glance at a report that goes to the doctor anyway; we did not retune the
net on these test sets. #strong[Fax.] 60 gold messages rendered as
degraded fax pages and read by Inbrev's own Tesseract intake (character
error rate 0.27, upper bound): the route falls from 56 to 50 of 60, the
3 unreadable pages abstain, and 13 of 16 clinical messages still leave
automation, as on clean text (`evidence/fax/`).

#strong[Label source.] Two open-weights models labelled all 367 messages
of the four generated sets blind (§4). Cohen's κ with our grid labels is
0.93 for the route and 0.97--0.98 for clinical content (gold and
challenge: no disagreement on clinical content), 0.60--0.90 for the
deadline and 0.40--0.42 for "ambiguous". Scored against either model or
the majority of three, Inbrev 8B routes 167--169 of 180 gold messages
(170 against the grid) and keeps 13/16; on every set the ranking against
the keyword rules is unchanged (`evidence/agreement/`).

#strong[Other open models, and why Apertus anyway.] In the identical
pipeline (prompt p3, checks, three samples) on the gold set, Qwen3.5-9B
and Ministral 8B both route 177/180 and exclude 16/16 clinical messages,
against 170/180 and 13/16 for Apertus 8B (route p = 0.04, clinical p =
0.25) and 172/180 and 15/16 for Apertus 70B (Llama 3.1 8B: provider rate
limit, no result; `evidence/peers/`), although the prompt was developed
with Apertus. With prompt p3 alone, errors that pass automation
unnoticed (wrong route, or clinical content without a flag) are 9 + 3
for Apertus 8B, 8 + 1 for 70B and 1 + 0 for both comparison models. We
then tried to close this gap with Apertus only, choosing on a dev split
(175 messages, rule fixed before the hold-out run, `evidence/gap/`): a
safety-first schema order (worse), five samples (no effect) and few-shot
examples (partial) were dropped; the symptom pass above reached 0
unnoticed clinical messages on dev. Measured once on the gold set,
Apertus 8B with the symptom pass lets through 8 + 0 at 40 messages for a
person (Qwen 1 + 0 at 38); adding a gate that sends a message to a
person when keyword rules choose another route gives 4 + 0 at 69. The
clinical part of the gap is closed, the route part only narrowed, and
only by more human work. #strong[Deviation from the fixed rule:] the
rule, written before the hold-out run, picked the second check plus the
rules gate; after seeing the hold-out we ship the second check alone as
default and the gate as an option (`INBREV_RULES_GATE=1`), because the
gate sends 69 instead of 40 of 180 messages to a person. Both results
are reported (`evidence/gap/`). A second round on a fresh hold-out (146
messages written by Gemma 4 31B, frozen with hashes before any run, plan
fixed on the earlier sets; `evidence/route/`) targeted the routes:
sharper route descriptions and few-shot examples alone change nothing (5
wrong routes run automatically, 39--42 to a person); with them, asking
70B when the keyword rules disagree lowers this to 2 at 43, available as
an option for practices with 70B access (e.g.~a Swiss cloud;
`INBREV_SECOND_OPINION_MODEL`, off by default). Qwen3.5-9B: 0 at 24.
Local execution, the quote checks and the unranked safety net work with
any open model and are no argument for Apertus. What is specific to
Apertus: it was pretrained only on openly available data with robots.txt
opt-outs applied retroactively and personal data filtered, all training
artefacts are released @apertus2025, and the developers publish a
dataset catalogue, an EU training-content summary and an EU Code of
Practice statement (github.com/swiss-ai/apertus-data-transparency), the
kind of documentation the EU AI Act asks of general-purpose model
providers @eu2024aiact\; we did not check equivalent documents for the
comparison models. A Swiss practice that must justify under the DSG and
professional secrecy which model reads patient mail @schweiz2020dsg can
point to this provenance. That is a trade-off, not a free choice: the
measured price is 7 more wrong routes in 180 that reach automation, or
more human work to catch them. Inbrev talks to any OpenAI-compatible
endpoint, so a practice can choose otherwise; with Apertus we recommend
70B where the hardware allows it. This is not legal advice.

#strong[Prompt p3 for "other".] p3 only sharpens route boundaries
("other": copy of records, referral elsewhere, symptoms only). It was
developed on a separate dev set (60 Nemotron messages; "other" p2 0/20,
p3 11/20), frozen after one dev run, then run once on every test set:
gold route 158 → 170/180 (McNemar p = 0.002; two p2 runs differ on 3
routes), no clinical case lost (`evidence/prompt-p3/`).

#strong[One sample is nearly as good as three.] Replaying the stored 8B
run with only the first sample (checks, net and abstention kept) gives
route 157/180 and clinical exclusion 12/16 against 159/180 and 13/16
(`scripts/replay_k_samples.py`). The gain over a raw answer (9/16) comes
mostly from checks and net, so local deployments use one sample.

#strong[Offline on a CPU.] On 30 of the 180 messages (all 16 clinical
plus 14), the offline Docker stack with Q4 weights and one sample (p2)
routes 24/30 and excludes 11/16; the endpoint (BF16, one sample) 23/30
and 12/16; Q4 and BF16 agree on the route for 28 and on the flag for 29
of 30. Wall time was 192 s per message on a laptop CPU. The same build
and weights natively on the laptop's integrated GPU (Vulkan,
`scripts/run_native_llamacpp.ps1`) need 62.7 s per message (p95 85 s);
on the challenge set this configuration (Q4, one sample, without the
symptom pass) excludes 38 of 44 clinical messages against 40/44 for one
BF16 sample (`evidence/native/`). These native runs measure speed and
quality; the air-gap proof remains the Docker run. The symptom pass adds
one short call per message; its local cost is not measured yet.

#strong[Cost.] From measured time and cited prices (excl. VAT;
`scripts/cost_model.py`): a mini PC with the same CPU draws 38--39 W
under load @kennedy2024box, about 2.1 kWh or CHF 0.52 per 1,000 messages
at 192 s each @elcom2026. With the box (about CHF 700, three years) and
idle power, a practice with 60 messages a day pays about CHF 12 per
1,000 messages, roughly CHF 22 a month. #strong[Value.] Staff time saved
is not measured. `scripts/value_model.py` multiplies measured shares of
the default configuration (78 % automatic, 4.4 % automatic but wrongly
routed, 12.8 % false clinical flags) with assumed volumes and handling
times (`evidence/value/`). At 60 messages a day, 60 s by hand and 15 s
to check a suggestion, an MPA saves about 32 minutes a day, net CHF 349
a month after doctor time for false flags and running cost (all
assumed); the cautious case loses CHF 242 a month; break-even is 33 s of
manual handling per message. Practice interviews with a timing trial
will replace the assumptions.

Not measured yet: latency on an NVIDIA GPU
(`scripts/run_native_llamacpp.ps1 -Backend cuda` is prepared) and the
time to sort messages by hand versus with Inbrev.

= 6. Limitations
<limitations>
- The synthetic set partly measures its generators; the strong surface
  baselines suggest it is easier to separate than real mail. Messages
  written by people (practice staff or patients) would be the stronger
  test; none are in the evaluation yet
  @long2024synthetic@panickssery2024selfpref.
- No person has reviewed the labels yet. The second labels come from two
  open-weights models (§4, §5), which measure whether the written rules
  are applied consistently, not clinical correctness; one is from the
  same family as the generator of two sets.
- #strong[Regulatory boundary.] Software that automatically
  reprioritises by clinical criticality based on patient data qualifies
  as medical device software @mdcg2025software\; in Switzerland
  classification follows Annex VIII of the EU MDR
  @schweiz2020mepv@eu2017mdr. Inbrev therefore never orders by severity
  in its default mode: the safety flag only takes a message out of
  automation and puts it in the same "a person decides" queue as unsure
  messages, ordered by time of receipt. Intended purpose: sorting
  administrative mail; messages with clinical content are not processed
  automatically. The final classification depends on the written
  intended purpose; this is not legal advice.
- #strong[Optional research mode.] `--mode clinical-triage` (off by
  default; the app then shows a labelled research hint) adds a
  keyword-based hint in the style of the Emergency Severity Index to
  flagged messages. It is an optional research mode without an intended
  medical purpose and not certified; it has not been validated. Any
  clinical use would require an MDR/MDSW conformity assessment first.
  All numbers in this report use the default administrative mode.
- No measurement on real practice data; US inbox figures transfer only
  partly. The GraSCCo letters are real-style clinical text, but German
  and Austrian; the Nemotron set reuses our label grid and prompt.
- The offline numbers come from a quantised model (Q4\_K\_M) on a shared
  laptop CPU; the BF16 numbers from the hackathon endpoint. Both are
  reported side by side on the same messages.

= 7. Reproducibility
<reproducibility>
`make run` starts the web app against `LLM_BASE_URL`\; `make run-local`
runs llama.cpp with local weights and Inbrev on an internal network;
`make offline-eval` repeats the offline run with its log; `make test`
runs the 34 unit tests with `--network none`. `scripts/agreement.py`,
`value_model.py`, `compare_hybrid.py`, `replay_k_samples.py` and
`cost_model.py` recompute agreement, value, rules comparison, ablation
and cost from stored runs and annotations;
`python -m inbrev triage|replay|eval` reproduces the numbers from the
stored runs, with 95 % Wilson intervals. Grids and cross-validation are
seeded. Model runs use `apertus-v1.5-8b` and `apertus-v1.5-70b` as named
by the Hack Apertus endpoint (3, 4 and 13 October), which does not
expose the Hugging Face revision. The generated test texts follow in the
repository after human review; predictions, grids and annotations are in
`evidence/`.

= 8. Next steps
<next-steps>
- Five to ten interviews with practice assistants and practice owners:
  real volume, category mix, share of fax; a pilot in a group practice.
- HIN connection (the IMAP import is tested against a local test server
  only) and practice software; a data protection impact assessment
  template @schweiz2020dsg.

= License
<license>
Creative Commons Attribution 4.0 (CC-BY-4.0). All HackApertus projects
are open-sourced. Code: Apache-2.0. Data (seed and Swiss practice
messages in `data/`): CDLA-Permissive-2.0. External datasets used only
for local checks are not redistributed and keep their own licences.

= References
<references>
