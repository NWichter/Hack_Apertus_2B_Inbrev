# Technical report — Inbrev

A deeper write-up than the README: what you built, how it works, and what the
numbers say.

- **Track:** Track 2B — Inbrev
- **Event:** Online
- **Team:** Apertool — Niklas Wichter
- **Demo:** [TBD: link to video]

_Version of 4 October 2026. Every number is measured or cited; what is not measured yet is named as such. Measured numbers come from synthetic data whose labels have not yet been reviewed by a person._

## 1. Summary

Swiss general practitioners spend more and more time on administration: 9.5 hours per week in 2025, up from 8.6 in 2020, and every additional administrative hour raises the odds of stress [@zeller2026workforce]. Physicians in private practice report 54 minutes per day for requests from authorities and insurers alone [@golder2025fmh]. Much of this arrives through the practice inbox, which US studies measure as a time block of its own (85 minutes per day, 243 messages per week) [@arndt2017tethered; @taiseale2019inbasket]. Patient messages fall under professional secrecy, which binds physicians and their assistants alike [@schweiz1937stgb], so sending them to a foreign cloud model is not an option.

Inbrev sorts the inbox of a Swiss practice locally with Apertus. It assigns each message to one of nine administrative routes, derives the administrative deadline and the person in charge, extracts patient and case fields, and backs every decision with a verbatim quote from the message. It never assesses clinical content: a message that may contain symptoms is excluded from automation and handed to a person, in the same queue as messages the model is unsure about, without any ranking by severity. Headline result on 180 synthetic messages (labels not yet reviewed by a person): with Apertus 8B, Inbrev excludes 13 of 16 messages with clinical content from automation (clinical exclusion recall, also called safety-net recall, 0.81, 95 % CI 0.57–0.93; keyword rules 7 of 16) and finds 43 of 50 "today" deadlines (0.86) while 96 % of the messages run without a person; route macro-F1 is 0.85. A single Apertus answer without the checks finds 9 of 16. Apertus 70B finds 15 of 16. Inbrev uses about 1,400 input and 640 output tokens per message with 8B. Three checks against our own bias: on 42 messages written by an open-weights model (Nemotron) the results hold (route 38 of 42, clinical exclusion 8 of 8); a rules-first hybrid saves 48 % of the model calls but loses 3 of the 13 clinical cases, because 5 of 16 clinical messages look like plain administration to keyword rules; on 40 German clinical letters from GraSCCo the route is right 40 of 40. Run fully offline (llama.cpp, Q4 GGUF, CPU only, Docker network without internet access), Inbrev matches the endpoint on the same 30 messages (same route on 28, same clinical flag on 29) at 192 s per message on a 28-W laptop CPU, which is about CHF 12 per 1,000 messages on a mini PC at 60 messages a day.

## 2. Architecture

Inbrev is a fixed pipeline, not an agent. Small local models are reliable on narrowly cut tasks and weak on complex ones [@xu2026small], so the model does only what rules cannot: read free text in four languages and point to the passage that supports a decision.

1. **Intake.** E-mail (`.eml`, including PDF attachments), HIN mail, fax pages as PDF or image (Tesseract OCR for German, French and Italian), web forms.
2. **Apertus with an enforced JSON schema** [@willard2023outlines; @geng2023grammar]. The schema orders each quote before its decision (route quote → route, safety quote → flag, deadline quote → date). Three samples are drawn in one request.
3. **Deterministic checks per sample.** Every quote must occur in the message: verbatim, after case and whitespace folding, or at least 90 % similar to one span; the evidence shown to a person is always the original text, never the model's copy. Language models often cite incompletely [@gao2023citations], and Apertus showed low faithfulness in production use [@kruckenberg2026liip], so a value without a verifiable quote is dropped. Dates must match their quote; AHV numbers must occur in the text; fields that do not belong to the chosen route are removed.
4. **Rules instead of model judgement where possible.** The deadline category is computed in code from the quoted date and the time of receipt; without a quoted date or time there is no deadline. The assignee follows from the route. A safety flag always means "doctor, today".
5. **Vote and abstention.** Route and fields by majority over the samples; the safety flag is raised if any sample or a multilingual lexical net fires. Agreement across samples is used as the uncertainty signal instead of a verbalised confidence, which is overconfident [@xiong2024uncertainty; @wang2023selfconsistency]. If the samples disagree, the model marks the message as ambiguous, or no route evidence survives, Inbrev abstains: a person decides [@wen2025abstention].
6. **Output.** A sorted inbox (web UI: "a person decides" for unsure messages and messages with clinical content, by time of receipt and without a ranking among them; then today, this week, no deadline), a JSON result per message following `data/schema/triage_result.schema.json`, an API under `/v1/`, and an audit log that stores a hash and the decision, not the text. Reply drafts are fixed templates for administrative routes only; no model-written text reaches patients.

### Target architecture (mandatory)

Inbrev is built for **a) on-premise** and **b) air-gapped** operation; **c) a sovereign Swiss cloud** is an option for single-doctor practices.

Health data are sensitive personal data under the Swiss Data Protection Act, which also requires data protection by design and allows processing by third parties only where no duty of secrecy forbids it [@schweiz2020dsg]. A system whose data never leave the practice avoids the question. Open weights that run on the practice's own hardware also keep the model auditable [@riedemann2024open; @apertus2025].

| Phase | Dependencies                                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Build time | Docker images (Python, llama.cpp), Python packages, Tesseract language data, Apertus weights from Hugging Face (checksum) |
| Runtime    | none; the model is reached over an internal Docker network without internet access. Optional: mail pick-up from HIN       |

**Offline run with local weights.** `make offline-eval` (`scripts/run_offline_eval.sh`) starts llama.cpp with a community Q4_K_M GGUF of the Apertus 8B text weights (Apache-2.0; Track 2 allows GGUF builds) and Inbrev on a Docker network with `internal: true`; only an optional nginx gateway for the web UI also sits on the host network. The log records the SHA-256 of the loaded weights (equal to the Hugging Face LFS hash, revision `248ec68`), `docker inspect` of both containers, an egress test from the Inbrev container (DNS, TCP to 1.1.1.1:443 and HTTPS all fail) and a control on the default network (all succeed), memory samples and the evaluation. llama.cpp rejects `n` > 1 (HTTP 400), so Inbrev falls back to one request per sample. On a 28-W laptop CPU (Ryzen 7 PRO 8840U, Docker Desktop) the model needs 6.2 GiB RAM and Inbrev 167 MiB; results are in §5. The run is in `evidence/offline/`.

## 3. Use of Apertus

- **Model:** swiss-ai/Apertus-v1.5-8B for inference; Apertus-v1.5-70B only as a comparison [@apertus2025]
- **How it is used:** inference (classification and extraction with an enforced JSON schema, three samples per message; one on a CPU)
- **Where it runs:** development and evaluation on the Hack Apertus endpoint (OpenAI-compatible, vLLM behind a LiteLLM proxy); target deployment on local weights (llama.cpp, GGUF Q4) inside the practice, measured offline on a CPU (§2, §5)

Settings: temperature 0.7 for the three samples, at most 900 output tokens, thinking off by default because it lowers instruction following [@wiegand2026apertusbench]; thinking is measured as an ablation. The system prompt (version p2) lists the routes with short multilingual cues, the rules for safety, deadlines and quotes, and an output format with placeholders only.

Two observations shaped the prompt. With the schema enforced but no format example in the prompt, the 8B model got stuck in a loop of whitespace inside the JSON until the token limit; the 70B model did not. A compact format example fixes this, but both models then copied concrete example values (a clear appointment request came back as `"other"`, the value in the example), so the example uses placeholders only. In a first run on twelve seed messages, the 8B model often set the deadline "today" without any date in the text, copied capital umlauts incorrectly, HTML-escaped quotes and filled fields of other routes; the checks in step 3 and 4 of the pipeline handle these cases.

## 4. Data

All messages, people, practices and identifiers are fictional; AHV numbers have a valid format and an invalid check digit. No real patient data is used. Licence: CDLA-Permissive-2.0.

- **Seed:** 12 messages (German, French, Italian; e-mail, fax, web form) with gold labels, in the repository. Claude (`claude-opus-5-5`) wrote them one by one in an agent session, not a person; they served as the development set for the prompt and the checks.
- **Synthetic part (v0):** 180 messages. Labels are fixed by a seeded grid _before_ any text exists (route, deadline, assignee, safety flag, abstain, language, channel, writing level, mixed topics, safety traps); two generator families write the text from one documented prompt, 90 messages each (Claude and GPT-5.5). Apertus neither writes nor labels data, because models recognise and prefer their own text [@panickssery2024selfpref]. Distribution: German 99, French 45, Italian 27, English 9; 16 messages with clinical content that must leave automation (7 explicit, 9 mentioned in passing) and 14 traps that sound medical but need no clinical reading; 9 genuinely ambiguous messages. A validator checks schema, verbatim quotes, date consistency, invalid AHV check digits, fictitious domains and phone numbers, and near-duplicates.
- **Swiss practice set:** 30 messages (`data/ood/`), text and labels written by an Antigravity agent session (Gemini, `gemini-3.8-flash`) on 3 October; Codex (`gpt-6.1-sol`) replaced real e-mail domains and organisation names the same day, and on 4 October the last four real organisation names were replaced by fictitious ones (`scripts/annotate_swiss_set.py`). Every row now records generator, model, date, edits and evidence in a `provenance` field; the generation prompt was not recorded and no person has reviewed the labels.
- **Open-generator set:** 42 messages from a fresh seeded grid (seed 2027, 8 with clinical content, 7 traps), text by an open-weights model, NVIDIA Nemotron 3 Ultra [@nvidia2026nemotron], through OpenRouter with the same prompt minus all example values; 3 of 45 rows failed validation and were dropped. Nobody tuned prompt, checks or lexicon on it. It tests whether the results depend on the closed generators.
- **GraSCCo report set:** 40 of the 63 synthetic German clinical letters of GraSCCo v1.1 (CC BY 4.0 on Zenodo, the authors also state CC0) [@modersohn2022grascco], verbatim (5 shortened at a paragraph end) behind a fixed one-line cover note, as realistic long `report_received` messages (`data/grascco/`). Labels follow one rule: route `report_received`, deadline today, no clinical flag. The letters are German and Austrian, not Swiss.
- **External datasets** (Hugging Face) were downloaded only for local stress tests, are not redistributed and give no reported number; `data/README.md` lists each source and why it is or is not used.
- **Human review, prepared:** `tools/review/` is an offline HTML tool for a blind pass over all messages, a second blind pass over 60 fixed messages (all 16 clinical cases) after 48 hours, and Cohen's κ [@cohen1960kappa] (intra-rater and against the generator labels), exported as `review_log.jsonl` and recomputed by `tools/review/kappa.py`. Not done yet. Also planned: about 60 handwritten messages and rendered fax pages for the OCR path.

Closed models (Claude, GPT-5.5 via Codex, Gemini via Antigravity) wrote or edited test data and code during development only, and an open-weights model (Nemotron) wrote the third test set; at runtime Inbrev calls only Apertus.

Synthetic data can miss the distribution of real mail [@long2024synthetic]; the gap between the generated and the handwritten part is reported.

## 5. Evaluation

The main numbers are the clinical exclusion recall (share of messages with clinical content that the safety net takes out of automation; "safety" in the tables) and the recall of the deadline "today", reported together with the share of messages that run without a person (coverage). Messages with clinical content are rare, so recall and precision are reported instead of accuracy [@saito2015precision], and the coverage–accuracy curve follows selective classification [@geifman2017selective]. Further metrics: route accuracy and macro-F1, deadline accuracy, field F1, evidence faithfulness (share of model quotes found in the message) [@rashkin2023attribution], tokens, latency and cost; all broken down by language, writing level, channel and generator.

Results on the synthetic set v0 (n = 180; 16 safety cases, 50 "today" deadlines; labels not yet reviewed by a person). Baselines without a language model; TF-IDF with five-fold cross-validation. Both Apertus rows run the full pipeline (schema, three samples at T = 0.7, checks, vote), prompt p2, on the Hack Apertus endpoint on 3 October 2026. Coverage is the share of messages Inbrev handles without "a person decides". The row "one sample, no checks" needs no new model call: it scores the first of the three stored 8B samples as the model wrote it, without quote checks, lexical net, vote or abstention (`scripts/ablation_first_sample.py`).

| Setup | Route acc. | Route F1 | Safety rec. | Safety prec. | Today rec. | Deadl. acc. | Coverage |
| ------------------------------ | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| Majority class | 0.14 | 0.03 | 0.00 | – | 0.00 | 0.37 | 1.00 |
| Keyword rules + lexical net | 0.79 | 0.76 | 0.44 | 0.32 | 0.76 | 0.68 | 1.00 |
| TF-IDF + logistic regression | 0.83 | 0.82 | 0.13 | 1.00 | 0.66 | 0.68 | 1.00 |
| 8B, one sample, no checks | 0.87 | 0.84 | 0.56 | 1.00 | 0.70 | 0.67 | 1.00 |
| **Inbrev 8B** (schema, checks, vote) | 0.88 | 0.85 | 0.81 | 0.46 | 0.86 | 0.82 | 0.96 |
| Inbrev 70B | 0.91 | 0.89 | 0.94 | 0.50 | 0.94 | 0.85 | 0.94 |

With 95 % Wilson intervals: safety recall 13/16 = 0.81 [0.57, 0.93] for 8B and 15/16 = 0.94 [0.72, 0.99] for 70B, against 9/16 = 0.56 [0.33, 0.77] for a single 8B answer without checks and 7/16 = 0.44 [0.23, 0.67] for the keyword rules; route accuracy 159/180 = 0.88 [0.83, 0.92] for 8B, 163/180 = 0.91 [0.85, 0.94] for 70B and 143/180 = 0.79 [0.73, 0.85] for the keyword rules. With 16 cases the intervals are wide, and the 8B–70B difference is not significant (exact McNemar p = 0.50). Of the gain over a single answer, three samples, where a flag from any one counts, add two cases (11/16 without the lexical net) and the lexical net two more. The net is tuned for recall: about half of the flags are false alarms (15 of 28 for 8B, 15 of 30 for 70B; all of them come from the lexical net, none from the model), which costs a doctor a glance, not a missed case. Recall differs by generator (8B: 7/7 [0.65, 1.00] of the cases written by GPT-5.5, 6/9 [0.35, 0.88] of those written by Claude; route 79/90 and 80/90), so the set partly measures its authors; the open-generator set below is the control. The target of 0.95 is not reached with 8B. Field F1 is 0.73 for 8B and 0.83 for 70B (paired bootstrap p < 0.001), the only metric where 70B is clearly better; the checks drop 309 of 2,086 values that 8B extracted (15 %). Mean latency per message (three samples in one request) was 3.0 s for 8B and 10.7 s for 70B on the shared endpoint.

The baselines already route 79–83 % of the synthetic messages correctly, so the route alone does not justify a language model on this set. They fail where it matters: they find at most 44 % of the messages with clinical content. For context only, not as a direct comparison: a clinical triage model guided by a triage manual reached a sensitivity of 0.98 [@liu2025emergency], and a deployed acuity classifier ran at 0.63 [@yang2024prioritization].

**Where Apertus beats the rules, and where not.** Paired on the 180 messages, 8B is right where the rules are wrong 27 times and the reverse 11 times (exact McNemar p = 0.014; 70B: 31 vs 11, p = 0.003). The model wins on insurer mail (24/24 vs 16/24), marketing (11/14 vs 4/14) and symptoms mentioned in passing (7/9 vs 3/9); it loses on "other" (3/16 vs 9/16), where it pushes vague messages into a specific route, and on billing (14/16 vs 15/16). A rules-first hybrid, where the keyword rules decide whenever exactly one route family matches and the lexical net is silent and Apertus decides otherwise, needs the model for only 94 of 180 messages but drops to route 152/180 and clinical exclusion 10/16: 5 of the 16 clinical messages look like plain administration to the rules (one keyword family, no lexicon hit); on the Nemotron set the hybrid drops 2 of 8. We therefore keep Apertus on every message (`scripts/compare_hybrid.py`).

| Further sets (Inbrev 8B, full pipeline) | n | Route acc. | Clinical excl. | Today rec. | Keyword rules route / clinical |
| --- | --- | --- | --- | --- | --- |
| Open generator (Nemotron) | 42 | 38/42 [0.78, 0.96] | 8/8 [0.68, 1.00] | 17/18 | 32/42 / 6/8 |
| GraSCCo clinical letters | 40 | 40/40 [0.91, 1.00] | – (7 false flags) | 40/40 | 40/40 / – (7 false flags) |

On the Nemotron set 70B scores the same route accuracy (38/42) and also 8/8. On GraSCCo, 6 of the 7 false flags come from the lexical net alone (e.g. negated "Suizidalität" in a psychiatric letter), one from the model; the cost is a doctor's glance at a report that goes to the doctor anyway.

**One sample is nearly as good as three.** Replaying the stored 8B run with only the first sample, but with checks, lexical net and abstention, gives route 157/180, clinical exclusion 12/16 and coverage 0.98, against 159/180, 13/16 and 0.96 with three samples (`scripts/replay_k_samples.py`, no new model call). Most of the gain over a single raw answer (9/16) comes from the checks and the net, not from sampling. The CPU deployment therefore uses one sample.

**Offline on a CPU.** On 30 of the 180 messages (all 16 with clinical content plus 14 drawn over the routes), the offline stack with Q4 weights and one sample routes 24/30 [0.63, 0.90] and excludes 11/16 [0.44, 0.86] clinical messages; the endpoint (BF16, one sample) gives 23/30 and 12/16 on the same messages, three samples 24/30 and 13/16, the keyword rules 23/30 and 7/16. Paired, Q4 and BF16 agree on the route for 28 of 30 messages and on the clinical flag for 29 of 30 (Q4 misses one more), so quantisation costs little here; the subset is small and over-weights clinical cases. Wall time was 5,765 s for 30 messages (192 s per message, median 163 s, p95 417 s), about 19 messages per hour, on a laptop that was also running other work; Q4 wrote 267 output tokens per sample against 213 at the endpoint.

**Cost.** From the measured time and cited prices (excl. VAT; `scripts/cost_model.py`, `evidence/offline/`): a mini PC with the same CPU draws 38–39 W under sustained load [@kennedy2024box], so 1,000 messages need about 2.1 kWh, CHF 0.52 at the 2026 Swiss median for small businesses [@elcom2026]. With the box (about CHF 700, three years) and idle power, a practice with 60 messages a day pays about CHF 12 per 1,000 messages, roughly CHF 22 a month; the box would sort up to 450 messages a day. For single practices without hardware, a Swiss cloud VM with 8 vCPU costs CHF 0.0448 per hour [@infomaniak2026cloud] (CHF 2.39 per 1,000 messages if billed only while sorting, CHF 32 a month if always on; other CPU, not measured). A Swiss token API at the listed Apertus 70B price (CHF 0.70 / 2.50 per million input / output tokens [@infomaniak2026ai]; 8B is not listed) would cost CHF 2.59 per 1,000 messages with the 8B token counts and CHF 3.40 with 70B. Not measured: GPU latency in the practice and the staff time saved.

Two small sets are reported separately because they are too small to rank systems. On the 12 seed messages (1 case with clinical content; prompt p1, run on 1 October), Inbrev with 8B routes 10 of 12 correctly (0.83, macro-F1 0.82), the keyword rules 11 of 12. On the 30 Swiss practice messages (4 cases with clinical content; `data/ood/`, labels not reviewed; run again on 4 October after the names were neutralised, 60 model calls), 8B routes 23 of 30 correctly (0.77 [0.59, 0.88], macro-F1 0.76), 70B 27 of 30 (0.90 [0.74, 0.97]; McNemar p = 0.125), the keyword rules 25 of 30 (0.83): on this set the keyword rules route better than 8B. All three take the 4 cases out of automation; 70B hands 4 messages to a person, including both ambiguous ones, 8B none. Deadline accuracy is low for all (0.47 for both models, 0.53 for the keyword rules), partly because the rows carry no time of receipt.

A unit test covers the OCR failure path: when a fax is so degraded that no quote can be found in the text, the checks drop every value and Inbrev abstains instead of filling fields. Not measured yet: OCR on rendered fax pages, latency on a GPU in the practice, and the time to sort 30 messages by hand versus with Inbrev.

## 6. Limitations

- The synthetic set partly measures its generators; the strong surface baselines suggest it is easier to separate than real mail. The handwritten part is the stronger test [@long2024synthetic; @panickssery2024selfpref].
- One person labels; agreement is intra-rater κ, not inter-rater.
- **Regulatory boundary.** Software that automatically reprioritises by clinical criticality based on patient data qualifies as medical device software [@mdcg2025software]; in Switzerland classification follows Annex VIII of the EU MDR [@schweiz2020mepv; @eu2017mdr]. Inbrev therefore never orders by severity in its default mode: the safety flag only takes a message out of automation and puts it in the same "a person decides" queue as unsure messages, ordered by time of receipt. Intended purpose: sorting administrative mail; messages with clinical content are not processed automatically. The final classification depends on the written intended purpose; this is not legal advice.
- **Optional research mode.** `--mode clinical-triage` (off by default, not in the web inbox) adds a keyword-based hint in the style of the Emergency Severity Index to flagged messages. It is an optional research mode, not a medical device and not certified; it has not been validated. Any clinical use would require an MDR/MDSW conformity assessment first. All numbers in this report use the default administrative mode.
- Enforced formats can cost reasoning quality [@tam2024format]; three samples triple the output tokens.
- No measurement on real practice data; US inbox figures transfer only partly. The GraSCCo letters are real-style clinical text, but German and Austrian; the Nemotron set reuses our label grid and prompt.
- The offline numbers come from a quantised model (Q4_K_M) on a shared laptop CPU; the BF16 numbers from the hackathon endpoint. Both are reported side by side on the same messages.

## 7. Reproducibility

`make run` starts the web app against `LLM_BASE_URL`; `make run-local` runs llama.cpp with local weights and Inbrev on an internal network; `make offline-eval` repeats the offline run with its log; `make test` and `make offline-check` run the tests and the non-LLM evaluation with `--network none`. `scripts/compare_hybrid.py`, `scripts/replay_k_samples.py` and `scripts/cost_model.py` recompute the rules comparison, the one-sample ablation and the cost table from stored runs; every rate in the report carries a 95 % Wilson interval in the `eval` output. `python -m inbrev triage|replay|eval` reproduces every number: `replay` re-applies the deterministic checks to stored raw model output, so changes to the checks are measured without new model calls. The grid for the synthetic set is seeded (2026), cross-validation uses seed 2026. Model runs: `apertus-v1.5-8b` and `apertus-v1.5-70b` as named by the Hack Apertus endpoint (3 October for the 180-message set, 4 October for the Swiss set); the endpoint does not expose the Hugging Face revision. The 180-message set is not in the repository yet; it follows after human review.

## 8. Next steps

- Five to ten interviews with practice assistants and practice owners: real volume, category mix, share of fax; a pilot in a group practice.
- Connectors for HIN mail and practice software; a data protection impact assessment template [@schweiz2020dsg].
- For Germany and Austria, check the EU AI Act; it classifies the system as high-risk only if it is a medical device [@eu2024aiact].

## License

Creative Commons Attribution 4.0 (CC-BY-4.0). All HackApertus projects are open-sourced. Code: Apache-2.0. Data (seed and Swiss practice messages in `data/`): CDLA-Permissive-2.0. External datasets used only for local checks are not redistributed and keep their own licences.

## References
