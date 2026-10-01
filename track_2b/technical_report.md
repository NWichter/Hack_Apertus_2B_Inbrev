# Technical report — Inbrev

A deeper write-up than the README: what you built, how it works, and what the
numbers say.

- **Track:** Track 2B — Inbrev
- **Event:** Online
- **Team:** Apertool — Niklas Wichter
- **Demo:** [TBD: link to video]

_Draft of 1 October 2026. Values marked [TBD] are not measured yet; numbers without that mark are measured or cited._

## 1. Summary

Swiss general practitioners spend more and more time on administration: 9.5 hours per week in 2025, up from 8.6 in 2020, and every additional administrative hour raises the odds of stress [@zeller2026workforce]. Physicians in private practice report 54 minutes per day for requests from authorities and insurers alone [@golder2025fmh]. Much of this arrives through the practice inbox, which US studies measure as a time block of its own (85 minutes per day, 243 messages per week) [@arndt2017tethered; @taiseale2019inbasket]. Patient messages fall under professional secrecy, which binds physicians and their assistants alike [@schweiz1937stgb], so sending them to a foreign cloud model is not an option.

Inbrev sorts the inbox of a Swiss practice locally with Apertus. It assigns each message to one of nine administrative routes, derives the administrative deadline and the person in charge, extracts patient and case fields, and backs every decision with a verbatim quote from the message. It never assesses clinical urgency: a message that may describe acute symptoms is flagged and handed to a person at once, and a message the model is unsure about goes to a person instead of being guessed. Headline result: [TBD: safety recall and "today" recall at coverage X %, route macro-F1, CHF per 1,000 messages].

## 2. Architecture

Inbrev is a fixed pipeline, not an agent. Small local models are reliable on narrowly cut tasks and weak on complex ones [@xu2026small], so the model does only what rules cannot: read free text in four languages and point to the passage that supports a decision.

1. **Intake.** E-mail (`.eml`, including PDF attachments), HIN mail, fax pages as PDF or image (Tesseract OCR for German, French and Italian), web forms.
2. **Apertus with an enforced JSON schema** [@willard2023outlines; @geng2023grammar]. The schema orders each quote before its decision (route quote → route, safety quote → flag, deadline quote → date). Three samples are drawn in one request.
3. **Deterministic checks per sample.** Every quote must occur in the message: verbatim, after case and whitespace folding, or at least 90 % similar to one span; the evidence shown to a person is always the original text, never the model's copy. Language models often cite incompletely [@gao2023citations], and Apertus showed low faithfulness in production use [@kruckenberg2026liip], so a value without a verifiable quote is dropped. Dates must match their quote; AHV numbers must occur in the text; fields that do not belong to the chosen route are removed.
4. **Rules instead of model judgement where possible.** The deadline category is computed in code from the quoted date and the time of receipt; without a quoted date or time there is no deadline. The assignee follows from the route. A safety flag always means "doctor, today".
5. **Vote and abstention.** Route and fields by majority over the samples; the safety flag is raised if any sample or a multilingual lexical net fires. Agreement across samples is used as the uncertainty signal instead of a verbalised confidence, which is overconfident [@xiong2024uncertainty; @wang2023selfconsistency]. If the samples disagree, the model marks the message as ambiguous, or no route evidence survives, Inbrev abstains: a person decides [@wen2025abstention].
6. **Output.** A sorted inbox (web UI: safety first, then "a person decides", then today, this week, no deadline), a JSON result per message following `data/schema/triage_result.schema.json`, an API under `/v1/`, and an audit log that stores a hash and the decision, not the text. Reply drafts are fixed templates for administrative routes only; no model-written text reaches patients.

[TBD: Figure 1, architecture diagram in `docs/` with the practice boundary.]

### Target architecture (mandatory)

Inbrev is built for **a) on-premise** and **b) air-gapped** operation; **c) a sovereign Swiss cloud** is an option for single-doctor practices.

Health data are sensitive personal data under the Swiss Data Protection Act, which also requires data protection by design and allows processing by third parties only where no duty of secrecy forbids it [@schweiz2020dsg]. A system whose data never leave the practice avoids the question. Open weights that run on the practice's own hardware also keep the model auditable [@riedemann2024open; @apertus2025].

| Phase      | Dependencies                                                                                                              |
| ---------- | ------------------------------------------------------------------------------------------------------------------------- |
| Build time | Docker images (Python, llama.cpp), Python packages, Tesseract language data, Apertus weights from Hugging Face (checksum) |
| Runtime    | none; the model is reached over an internal Docker network without internet access. Optional: mail pick-up from HIN       |

The unit tests and the non-LLM evaluation run in the image with `docker run --network none`. [TBD: log of a full triage run with local GGUF weights and no network.] For variant c), a blog calculation puts a Swiss API at CHF 0.00335 per request of 3,000 input and 500 output tokens [@pupel2026sovereign].

## 3. Use of Apertus

- **Model:** swiss-ai/Apertus-v1.5-8B for inference; Apertus-v1.5-70B only as a comparison [@apertus2025]
- **How it is used:** inference (classification and extraction with an enforced JSON schema, three samples per message)
- **Where it runs:** development and evaluation on the Hack Apertus endpoint (OpenAI-compatible, vLLM behind a LiteLLM proxy); target deployment on local weights (llama.cpp, GGUF Q4) inside the practice

Settings: temperature 0.7 for the three samples, at most 900 output tokens, thinking off by default because it lowers instruction following [@wiegand2026apertusbench]; thinking is measured as an ablation. The system prompt (version p2) lists the routes with short multilingual cues, the rules for safety, deadlines and quotes, and an output format with placeholders only.

Two observations shaped the prompt. With the schema enforced but no format example in the prompt, the 8B model got stuck in a loop of whitespace inside the JSON until the token limit; the 70B model did not. A compact format example fixes this, but both models then copied concrete example values (a clear appointment request came back as `"other"`, the value in the example), so the example uses placeholders only. In a first run on twelve seed messages, the 8B model often set the deadline "today" without any date in the text, copied capital umlauts incorrectly, HTML-escaped quotes and filled fields of other routes; the checks in step 3 and 4 of the pipeline handle these cases.

## 4. Data

All messages, people, practices and identifiers are fictional; AHV numbers have a valid format and an invalid check digit. No real patient data is used. Licence: CDLA-Permissive-2.0.

- **Seed:** 12 handwritten messages (German, French, Italian; e-mail, fax, web form) with gold labels, in the repository.
- **Synthetic part (v0):** 180 messages. Labels are fixed by a seeded grid _before_ any text exists (route, deadline, assignee, safety flag, abstain, language, channel, writing level, mixed topics, safety traps); two generator families write the text from one documented prompt, 90 messages each (Claude and GPT-5.5). Apertus neither writes nor labels data, because models recognise and prefer their own text [@panickssery2024selfpref]. Distribution: German 99, French 45, Italian 27, English 9; 16 safety cases (7 explicit, 9 mentioned in passing) and 14 traps that sound medical but are not acute; 9 genuinely ambiguous messages. A validator checks schema, verbatim quotes, date consistency, invalid AHV check digits, fictitious domains and phone numbers, and near-duplicates.
- **Planned:** about 60 handwritten, deliberately messy messages and about 60 fax pages rendered with skew, noise and stamps for the OCR path; at least 60 messages relabelled blind after 48 hours to report intra-rater κ [@cohen1960kappa].

Synthetic data can miss the distribution of real mail [@long2024synthetic]; the gap between the generated and the handwritten part is reported.

## 5. Evaluation

The main numbers are the recall of the safety flag and of the deadline "today", reported together with the share of messages that run without a person (coverage). Safety cases are rare, so recall and precision are reported instead of accuracy [@saito2015precision], and the coverage–accuracy curve follows selective classification [@geifman2017selective]. Further metrics: route accuracy and macro-F1, deadline accuracy, field F1, evidence faithfulness (share of model quotes found in the message) [@rashkin2023attribution], tokens, latency and cost; all broken down by language, writing level, channel and generator.

Baselines without a language model, on the synthetic set v0 (n = 180; TF-IDF with five-fold cross-validation):

| Setup                                 | Route acc. | Route macro-F1 | Safety recall | Safety precision | "Today" recall | Deadline acc. |
| ------------------------------------- | ---------- | -------------- | ------------- | ---------------- | -------------- | ------------- |
| Majority class                        | 0.14       | 0.03           | 0.00          | –                | 0.00           | 0.37          |
| Keyword rules + lexical safety net    | 0.79       | 0.76           | 0.44          | 0.32             | 0.76           | 0.68          |
| TF-IDF + logistic regression          | 0.83       | 0.82           | 0.13          | 1.00             | 0.66           | 0.68          |
| Apertus 8B, one sample, no checks     | [TBD]      | [TBD]          | [TBD]         | [TBD]            | [TBD]          | [TBD]         |
| Apertus 70B                           | [TBD]      | [TBD]          | [TBD]         | [TBD]            | [TBD]          | [TBD]         |
| **Inbrev** (8B, schema, checks, vote) | [TBD]      | [TBD]          | [TBD]         | [TBD]            | [TBD]          | [TBD]         |

The baselines already route 83 % of the synthetic messages correctly, so the route alone does not justify a language model on this set. They fail where it matters: they find at most 44 % of the safety cases. For context only, not as a direct comparison: clinical emergency detection with a triage manual reached a sensitivity of 0.98 [@liu2025emergency], and a deployed acuity classifier ran at 0.63 [@yang2024prioritization].

[TBD: Figure 2, coverage–accuracy curve; breakdown by language and writing level; operation and cost per message on GPU and CPU; time to sort 30 messages by hand vs. with Inbrev (n = 1, self-experiment).]

## 6. Limitations

- The synthetic set partly measures its generators; the strong surface baselines suggest it is easier to separate than real mail. The handwritten part is the stronger test [@long2024synthetic; @panickssery2024selfpref].
- One person labels; agreement is intra-rater κ, not inter-rater.
- **Regulatory boundary.** Software that automatically reprioritises by clinical criticality based on patient data qualifies as medical device software [@mdcg2025software]; in Switzerland classification follows Annex VIII of the EU MDR [@schweiz2020mepv; @eu2017mdr]. Inbrev therefore never orders by severity: the safety flag only takes a message out of automation. The final classification depends on the written intended purpose; this is not legal advice.
- Enforced formats can cost reasoning quality [@tam2024format]; three samples triple the output tokens.
- No measurement on real practice data; US inbox figures transfer only partly.

## 7. Reproducibility

`make run` starts the web app against `LLM_BASE_URL`; `make run-local` adds llama.cpp with local weights on an internal network; `make test` and `make offline-check` run the tests and the non-LLM evaluation with `--network none`. `python -m inbrev triage|replay|eval` reproduces every number: `replay` re-applies the deterministic checks to stored raw model output, so changes to the checks are measured without new model calls. The grid for the synthetic set is seeded (2026), cross-validation uses seed 2026. [TBD: hardware, model revision (Hugging Face commit), quantisation, llama.cpp/vLLM version, git commit.]

## 8. Next steps

- Five to ten interviews with practice assistants and practice owners: real volume, category mix, share of fax; a pilot in a group practice.
- Connectors for HIN mail and practice software; a data protection impact assessment template [@schweiz2020dsg].
- For Germany and Austria, check the EU AI Act; it classifies the system as high-risk only if it is a medical device [@eu2024aiact].

## License

Creative Commons Attribution 4.0 (CC-BY-4.0). All HackApertus projects are open-sourced.

## References
