# Hack Apertus — project template

Template repository for [Hack Apertus](https://hackapertus.ch/) submissions.
Every project keeps almost the same layout, so organizers and judges find the
same things in the same place.

## Select your track

This repository holds one example project per track:

- `track_1a/`
- `track_1b/`
- `track_2a/`
- `track_2b/`

Keep the directory for the track you are competing in **exactly as it is** —
don't rename it or move its files — and delete the other track directories.
That directory is your project root. Keep the files and directories as shown
below.

## The structure

| Path | What it is |
| --- | --- |
| `README.md` | The challenge description and submission requirements for your track |
| `technical_report.md` | The deeper write-up: architecture, evaluation, limitations |
| `Makefile` | `make run` must spin up your project |
| `src/` | Your code |
| `data/` | Datasets — `track_1a`, `track_2a` and `track_2b` only; max. 100 MB |
| `findings/` | Issue files — `track_1a` only |
| `docs/` | Diagrams, notes, longer write-ups |

## Run it

Judges run `make run` from the root of the project, on a clean checkout:

```bash
make run
```

`make run` is expected to run the project using Docker, since that
is how the judges will run it.
- If you used other local open-weight models, include instructions for running the project in your technical report.
- Use the following environment variables:
```
LLM_NAME — name and version of the model
LLM_BASE_URL — endpoint base URL
LLM_API_KEY — your API key
```

## Getting started

1. Click **Use this template** to create your own repository.
2. Delete the other track directories. Don't rename or restructure yours.
3. Read its `README.md` and fill in `technical_report.md`.
4. Make `make run` work from the root of the project, on a clean checkout.

The project website (`website/`) embeds the demo video (`website/media/video.mp4`, subtitles `website/media/video.vtt`).

## License

All Hack Apertus projects are open-sourced. Please check our Terms & Conditions for specific licensing details (6. What you build is open source): https://hackapertus.ch/terms-and-conditions

Inbrev follows § 6 of these terms:

| Part | License | File |
| --- | --- | --- |
| Code (`track_2b/src`, `track_2b/scripts`, `track_2b/tests`, website) | Apache-2.0 | [`LICENSE`](LICENSE) |
| Documentation and technical report (`README.md`, `track_2b/technical_report.md`, `track_2b/report/`, `track_2b/docs/`) | CC-BY-4.0 | [`LICENSE-docs`](LICENSE-docs) |
| Submitted dataset (`track_2b/data/`: seed messages, Swiss practice set, taxonomy, schema) | CDLA-Permissive-2.0 | [`track_2b/data/LICENSE`](track_2b/data/LICENSE) |

Third-party material keeps its own licence and is not relicensed:

- External datasets used only for local checks (`sweatSmile/medical-symptom-triage`, `ale-dp/german-english-email-ticket-classification`, `PortalPal-AI/Portal-Messaging-Topics`, `lavita/ChatDoctor-HealthCareMagic-100k`) are not in the repository and keep the licences stated on their dataset cards (see `track_2b/data/README.md`). They are not covered by CDLA-Permissive-2.0.
- The GraSCCo report set (`track_2b/data/grascco/`) contains letters from GraSCCo v1.1 (Modersohn et al. 2022, doi:10.5281/zenodo.18874981), licensed CC BY 4.0 on Zenodo; it keeps that licence (attribution and list of changes in `track_2b/data/grascco/README.md`).
- The offline run uses the community GGUF `Colby/apertus-v1.5-8b-text-Q4_K_M-GGUF` (Apache-2.0); the weights are downloaded, not stored in the repository (`track_2b/docs/RUNNING.md`).
