# Running Inbrev

Inbrev sorts the inbox of a Swiss general practice by handling route and administrative
deadline. It never assesses clinical content: a message that may contain symptoms is excluded
from automation (`safety_flag`) and lands in "A person decides", together with messages Inbrev is
unsure about, ordered by time of receipt and without any ranking by severity.

## Two modes

| Mode | How | What it does | Status |
| --- | --- | --- | --- |
| **Triage mode** (default) | nothing to set | Administrative sorting: route, deadline, assignee, fields with verbatim evidence. Safety net: a message that may contain symptoms leaves automation and goes to "A person decides" with deadline today, **without any ranking by severity**. Reply drafts only for administrative routes. | All reported numbers |
| **Clinical research mode** | `INBREV_MODE=clinical-triage` or `--mode clinical-triage` | Same as triage mode, plus a keyword-based urgency hint in the style of the Emergency Severity Index (`clinical_triage` in the JSON) for flagged messages; the app shows it as a labelled research hint. | Off by default. Research prototype, not a medical device, not certified, not validated; clinical use would need an MDR/MDSW conformity assessment |

The header of the web app shows which mode is active.

## Quick start (Docker)

```bash
cp .env.example .env        # set LLM_NAME, LLM_BASE_URL, LLM_API_KEY (any OpenAI-compatible Apertus endpoint)
make run                    # web app on http://127.0.0.1:8000
```

| Target               | What it does                                                                                               |
| -------------------- | ---------------------------------------------------------------------------------------------------------- |
| `make run`           | Builds the image and starts the web app against `LLM_BASE_URL`                                             |
| `make run-local`     | Starts `llama.cpp` with a local Apertus GGUF and Inbrev on an internal network without internet; a small nginx gateway is the only container that also sits on the host network, so the UI is reachable at http://127.0.0.1:8000 |
| `make offline-eval`  | Full triage with the local GGUF on the internal network, egress test, SHA-256 of the weights, `docker inspect`, memory samples, evaluation (`scripts/run_offline_eval.sh`) |
| `make test`          | Unit tests inside the image with `--network none`                                                          |
| `make offline-check` | Tests plus the non-LLM baselines with `--network none`                                                     |
| `make triage-seed`   | Triages the 12 seed messages against the configured endpoint                                               |

All targets also work from the repository root (`make run-local` there calls `make -C track_2b run-local`).
Checked on a fresh clone in a Linux container (Docker 27, Alpine, GNU Make 4.4): `make test`, `make run` and
`make run-local` (see `evidence/fresh-clone/`).

## Offline run with local weights

```bash
mkdir -p models
curl -L -o models/apertus-v1.5-8b-text-Q4_K_M.gguf   https://huggingface.co/Colby/apertus-v1.5-8b-text-Q4_K_M-GGUF/resolve/248ec68a63e219e3f061e4c946fc8a20d63b9975/apertus-v1.5-8b-text-q4_k_m.gguf
sha256sum models/*.gguf    # a037df8d87ff6caacee794ee85f55342f2152e0d359b7389033300c3bee5f299
make offline-eval          # seed set; GOLD=path/to/messages.jsonl for another file
```

The GGUF is a community Q4_K_M quantisation of the text weights of `swiss-ai/Apertus-v1.5-8B`
(Apache-2.0; Track 2 allows community GGUF builds). llama.cpp accepts only one completion per request, so Inbrev
sends the three samples as three requests (`INBREV_SPLIT_SAMPLES`, automatic on HTTP 400).
On Docker Desktop for Windows, reading the weights from a bind mount is very slow; copy them once
into a volume and set `MODELS_SRC=models`:

```bash
docker volume create inbrev-models
docker run --rm -v "$PWD/models:/src:ro" -v inbrev-models:/models alpine cp /src/apertus-v1.5-8b-text-Q4_K_M.gguf /models/
MODELS_SRC=models make offline-eval
```

## Reading mail from an IMAP mailbox

The practice mail server, or HIN mail through an IMAP bridge (not tested with HIN), can feed Inbrev directly.
Read-only by default: messages are fetched with `BODY.PEEK`, nothing is deleted or moved.

```bash
INBREV_IMAP_PASSWORD=... python -m inbrev fetch-imap --host mail.praxis.example --user praxis --out runs/inbox.jsonl
python -m inbrev triage runs/inbox.jsonl --out runs/inbox.triaged.jsonl
```

Options: `--security ssl|starttls|plain`, `--port`, `--folder`, `--all` (not only unseen), `--mark-seen`, `--limit`.
In the web app, set `INBREV_IMAP_HOST`, `INBREV_IMAP_USER`, `INBREV_IMAP_PASSWORD` (optional `INBREV_IMAP_PORT`,
`INBREV_IMAP_SECURITY`, `INBREV_IMAP_FOLDER`); a "Fetch mail" button then appears (`POST /v1/inbox/fetch`).
`scripts/imap_check.sh` tests the import against a local GreenMail server on an internal Docker network
(log: `evidence/imap/imap-check.log`).

## Pipeline

```
message (e-mail, HIN mail, fax PDF/image via Tesseract, web form)
  -> Apertus, JSON schema enforced, n = 3 samples in one call
  -> deterministic checks per sample
       quotes must exist in the message (exact, normalised or >= 90 % similar; the shown evidence is always the original text)
       dates must match their quote; AHV numbers must appear in the text
       deadline computed in code from the quoted date and the received time; no quote -> no deadline
       fields outside the chosen route are dropped
  -> vote over samples (route majority, field majority, safety = any sample OR lexical net)
  -> abstain ("a person decides") if samples disagree, the model marks the message ambiguous,
     or no route evidence survives
  -> sorted inbox, JSON result (data/schema/triage_result.schema.json), audit log (hash + decision, no text)
```

Assignee follows from the route (`data/taxonomy.yaml`); a safety flag always means doctor and today.
Reply drafts are fixed templates for administrative routes only; no model text is sent to patients.

## CLI

```bash
python -m inbrev triage data/seed/messages.seed.jsonl --out runs/seed.jsonl [--model apertus-v1.5-70b] [--samples 1 --temperature 0] [--thinking] [--no-schema]
python -m inbrev replay data/seed/messages.seed.jsonl runs/seed.jsonl --out runs/seed.replay.jsonl   # re-run the checks on stored raw output, no model call
python -m inbrev eval data/seed/messages.seed.jsonl runs/seed.jsonl --baselines --report runs/report.md
python -m inbrev serve
```

`eval` reports route accuracy and macro-F1, safety and "today" recall/precision, deadline accuracy,
coverage (share handled without a person), accuracy on covered messages, field F1, tokens and
latency, with breakdowns by language, writing level, channel and generator.

## API (`/v1/`)

| Method | Path                   | Purpose                                         |
| ------ | ---------------------- | ----------------------------------------------- |
| GET    | `/v1/health`           | Model, endpoint host, settings                  |
| POST   | `/v1/triage`           | Triage one message (JSON) and return the result |
| POST   | `/v1/upload`           | Upload `.eml`, PDF, image or text; triage it    |
| GET    | `/v1/inbox`            | Current inbox, sorted                           |
| POST   | `/v1/inbox/load/{set}` | Load a demo inbox (`seed`, optional `gold`)     |
| POST   | `/v1/inbox/sort`       | Triage all pending messages                     |
| POST   | `/v1/inbox/fetch`      | Read new mail from the configured IMAP mailbox  |

## Configuration

| Variable               | Default              | Meaning                                             |
| ---------------------- | -------------------- | --------------------------------------------------- |
| `LLM_NAME`             | `apertus-v1.5-8b`    | Model name at the endpoint                          |
| `LLM_BASE_URL`         | `http://llm:8080/v1` | OpenAI-compatible endpoint                          |
| `LLM_API_KEY`          | `none`               | Key for the endpoint                                |
| `INBREV_SAMPLES`       | `3`                  | Samples per message (self-consistency)              |
| `LOCAL_INBREV_SAMPLES` | `1`                  | Samples per message in `make run-local` / `make offline-eval` (CPU; the one-sample ablation in the report) |
| `INBREV_TEMPERATURE`   | `0.7`                | Sampling temperature when samples > 1               |
| `INBREV_SAFETY_MODE`   | `or`                 | `llm`, `lexical` or `or`                            |
| `INBREV_ABSTAIN_BELOW` | `0.99`               | Route agreement needed to run without a person      |
| `INBREV_CONCURRENCY`   | `3`                  | Parallel requests                                   |
| `INBREV_SPLIT_SAMPLES` | `auto`               | `on`: one request per sample; `auto`: switch on HTTP 400 for `n` > 1 |
| `INBREV_PRECOMPUTED`   | –                    | JSONL of stored predictions to show without a model |
| `INBREV_MODE`          | `admin`              | `admin` (triage mode) or `clinical-triage` (research mode) |
| `INBREV_PROMPT`        | `p3`                 | System prompt version; `p2` reproduces runs before 4 October 2026 (`evidence/prompt-p3/`) |
| `INBREV_SYMPTOM_CHECK` | `1`                | Second 8B call per message that only asks whether someone describes a current complaint (verified quote); a yes takes the message out of automation. `0` reproduces runs before 13 October 2026 (`evidence/gap/`) |
| `INBREV_RULES_GATE`  | `0`                | `1`: a person decides when the keyword rules choose another route than the model (fewer unnoticed wrong routes, many more messages to a person) |
| `INBREV_IMAP_*`        | –                    | Mailbox for "Fetch mail" (see above)                |
