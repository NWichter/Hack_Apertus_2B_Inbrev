# Running Inbrev

Inbrev sorts the inbox of a Swiss general practice by handling route and administrative
deadline. It never assesses clinical urgency: a message that may describe acute symptoms is
flagged and handed to a person (`safety_flag`).

## Quick start (Docker)

```bash
cp .env.example .env        # set LLM_NAME, LLM_BASE_URL, LLM_API_KEY (any OpenAI-compatible Apertus endpoint)
make run                    # web app on http://127.0.0.1:8000
```

| Target               | What it does                                                                                               |
| -------------------- | ---------------------------------------------------------------------------------------------------------- |
| `make run`           | Builds the image and starts the web app against `LLM_BASE_URL`                                             |
| `make run-local`     | Also starts `llama.cpp` with a local Apertus GGUF from `./models/` on an internal network without internet |
| `make test`          | Unit tests inside the image with `--network none`                                                          |
| `make offline-check` | Tests plus the non-LLM baselines with `--network none`                                                     |
| `make triage-seed`   | Triages the 12 seed messages against the configured endpoint                                               |

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

## Configuration

| Variable               | Default              | Meaning                                             |
| ---------------------- | -------------------- | --------------------------------------------------- |
| `LLM_NAME`             | `apertus-v1.5-8b`    | Model name at the endpoint                          |
| `LLM_BASE_URL`         | `http://llm:8080/v1` | OpenAI-compatible endpoint                          |
| `LLM_API_KEY`          | `none`               | Key for the endpoint                                |
| `INBREV_SAMPLES`       | `3`                  | Samples per message (self-consistency)              |
| `INBREV_TEMPERATURE`   | `0.7`                | Sampling temperature when samples > 1               |
| `INBREV_SAFETY_MODE`   | `or`                 | `llm`, `lexical` or `or`                            |
| `INBREV_ABSTAIN_BELOW` | `0.99`               | Route agreement needed to run without a person      |
| `INBREV_CONCURRENCY`   | `3`                  | Parallel requests                                   |
| `INBREV_PRECOMPUTED`   | –                    | JSONL of stored predictions to show without a model |
