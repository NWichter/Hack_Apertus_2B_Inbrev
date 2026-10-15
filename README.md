# Inbrev: sovereign inbox triage for Swiss medical practices

Team Apertool · Hack Apertus 2026 · Track 2B (Own Project). Project root: [`track_2b/`](track_2b/).

Inbrev sorts the inbox of a Swiss general practice with **Apertus**, on the practice's own hardware: nine
administrative routes, the administrative deadline, the person in charge, and patient and case fields, each
backed by a verbatim quote from the message. In its default mode it does not assess clinical content: a message that may describe
symptoms leaves automation and goes to "A person decides", unranked, together with messages the model is unsure about.

## Judges start here

| What | Where |
| --- | --- |
| Technical report (6 pages) | [`track_2b/Apertool_Report.pdf`](track_2b/Apertool_Report.pdf), source [`track_2b/technical_report.md`](track_2b/technical_report.md) |
| Run it | `make run` from this folder (Docker). With `track_2b/.env` (`LLM_NAME`, `LLM_BASE_URL`, `LLM_API_KEY`) the web app at http://127.0.0.1:8000 triages with your Apertus endpoint. **Without credentials** the app still starts, says so in its header and shows stored results for the 12 seed messages, marked as stored. |
| Run it offline | `make run-local`: llama.cpp with local Apertus 8B Q4 weights and Inbrev on a Docker network without internet access ([`track_2b/docs/RUNNING.md`](track_2b/docs/RUNNING.md)); `make offline-eval` runs the same offline pipeline on the 12 seed messages (command for the logged 30-message run: [`track_2b/evidence/offline/README.md`](track_2b/evidence/offline/README.md)) |
| Tests | `make test` (35 unit tests, `--network none`) |
| Test texts | [`track_2b/data/synthetic/`](track_2b/data/synthetic/): all 543 generated test messages with their grid labels (synthetic v0, labels from the seeded grid, published without human review). The 367 messages that two open models labelled blind are the gold, open-generator, challenge and Swiss practice sets (180 + 42 + 115 + 30); hold-out 2 (146) was labelled blind separately, the dev split (60) not |
| Evidence for every number | [`track_2b/evidence/`](track_2b/evidence/): logs, predictions and reports per study (`offline`, `prompt-p3`, `challenge`, `agreement`, `gap`, `holdout2`, `route`, `peers`, `fax`, `parhaf`, `native`, `value`, `fresh-clone`) |
| Demo video (under 2 min) | `website/media/video.mp4` |

**Key results** (synthetic test data, [[NIKLAS-PRÜFUNG: readme-ergebnisse – Klammer über den Key results]]; details and intervals in the report):

- Gold set (180 messages; the second check was chosen on a separate dev split and measured here once, the shipped
  default was then fixed after seeing this result, see the report): with the default configuration no message with clinical
  content ran automatically (16 of 16 synthetic cases leave automation, 95 % CI 0.81–1.00), 170 of 180 routes are right, 40 of 180 messages go to a person.
- Keyword rules catch 7 of 16 clinical messages; Apertus 8B beats them on routes 32 to 5 (McNemar p = 7·10⁻⁶).
- Two other small open models in the same pipeline route better than Apertus 8B (177 vs 170 of 180); the report says
  what that costs and why we still use Apertus.
- Offline: Q4 weights, no internet access, egress test logged in the Docker CPU run; 192 s per message on a laptop CPU, 62.7 s on its integrated GPU
  (both before the symptom pass); with the symptom pass (default) the iGPU needs 71.8 s per message
  and excludes 16 of 16 clinical messages on a 30-message subset (`track_2b/evidence/native/`).

| Mode | What it does |
| --- | --- |
| **Second opinion** (`INBREV_SECOND_OPINION_MODEL=apertus-v1.5-70b`, off by default) | Available as an option for practices with 70B access (e.g. a Swiss cloud): when the keyword rules choose another route, Apertus 70B is asked; if it disagrees, a person decides. On hold-out 2 it lowers wrong routes that run automatically from 5 to 3 of 146, to 2 with prompt p4 and few-shot examples (`track_2b/evidence/route/`). |
| **Triage mode** (default) | Administrative sorting only. **Safety net:** the model's flag, a multilingual keyword net and a second narrow 8B check for current complaints take a message out of automation; no ranking by severity. All reported numbers use this mode. |
| **Clinical research mode** (`INBREV_MODE=clinical-triage`, off by default) | Adds a keyword-based urgency hint to flagged messages. Research prototype without an intended medical purpose, not validated, not certified. |

The switches in [`track_2b/docs/RUNNING.md`](track_2b/docs/RUNNING.md) also work with `make run` (set them in `track_2b/.env`; exceptions are listed there).
The project website (`website/`) contains the pitch (`website/pitch/`) and the report as `website/report.pdf`.

## License

All Hack Apertus projects are open-sourced. Please check our Terms & Conditions for specific licensing details (6. What you build is open source): https://hackapertus.ch/terms-and-conditions

Inbrev follows § 6 of these terms:

| Part | License | File |
| --- | --- | --- |
| Code (`track_2b/src`, `track_2b/scripts`, `track_2b/tests`, website) | Apache-2.0 | [`LICENSE`](LICENSE) |
| Documentation and technical report (`README.md`, `track_2b/technical_report.md`, `track_2b/report/`, `track_2b/docs/`) | CC-BY-4.0 | [`LICENSE-docs`](LICENSE-docs) |
| Submitted dataset (`track_2b/data/`: seed messages, Swiss practice set, generated test sets in `synthetic/`, taxonomy, schema) | CDLA-Permissive-2.0 | [`track_2b/data/LICENSE`](track_2b/data/LICENSE) |

Third-party material keeps its own licence and is not relicensed:

- External datasets used only for local checks (`sweatSmile/medical-symptom-triage`, `ale-dp/german-english-email-ticket-classification`, `PortalPal-AI/Portal-Messaging-Topics`, `lavita/ChatDoctor-HealthCareMagic-100k`) are not in the repository and keep the licences stated on their dataset cards (see `track_2b/data/README.md`). They are not covered by CDLA-Permissive-2.0.
- The GraSCCo report set (`track_2b/data/grascco/`) contains letters from GraSCCo v1.1 (Modersohn et al. 2022, doi:10.5281/zenodo.18874981), licensed CC BY 4.0 on Zenodo; it keeps that licence (attribution and list of changes in `track_2b/data/grascco/README.md`).
- The PARHAF report set (`track_2b/data/parhaf/`) contains French clinical reports from PARHAF (HealthDataHub, CC BY 4.0 / Licence Ouverte Etalab 2.0); it keeps that licence (source and changes in `track_2b/data/parhaf/README.md`).
- The offline run uses the community GGUF `Colby/apertus-v1.5-8b-text-Q4_K_M-GGUF` (Apache-2.0); the weights are downloaded, not stored in the repository (`track_2b/docs/RUNNING.md`).
