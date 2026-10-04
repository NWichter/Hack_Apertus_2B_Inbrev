# Fresh clone on Linux

Date: 2026-10-04. A fresh `git clone` of this repository inside a Docker-in-Docker container
(`docker:27-dind`, Alpine 3.21, Docker 27.5.1, Compose 2.33, GNU Make 4.4.1; on a Windows laptop through
WSL2, CPU only). Nothing from the working copy was used except `track_2b/.env` for `make run`
(endpoint values, removed afterwards) and the GGUF weights, copied into `track_2b/models/` as
`docs/RUNNING.md` describes (SHA-256 checked).

| Step | Result | Log |
| --- | --- | --- |
| clone | 0 untracked files | `fresh-clone.log` |
| `make test` (repo root) | 22 passed | `fresh-clone.log` |
| `make run` (repo root) | health 200, `POST /v1/triage` on seed-001 end to end (report_received, today, doctor), UI 200 | `fresh-clone.log` |
| `make run-local` (repo root), commit `0536ccd` | stack up after 184 s, app only on the internal network, egress blocked (DNS, TCP, HTTPS), model loaded after 1,254 s; **the triage request hit the gateway timeout (504 after 900 s)**: three samples on this CPU took longer | `fresh-clone.log` |
| fix `621c3e9` | local stack uses `LOCAL_INBREV_SAMPLES` (default 1, as the report argues for CPU), gateway and client wait 1,800 s | – |
| `make run-local` again | seed-001 correct with 1 sample (report_received, today, doctor), 757 s for the request; the model container from the first attempt was still busy with the abandoned three-sample request, because `make stop` did not stop the `local` profile (fixed in `647bd30`) | `fresh-clone-recheck.log` |

Problems found and fixed on the way: `make run-local` was missing in the root Makefile
(`No rule to make target`, fixed in `0536ccd`); pytest cache warning in the read-only image
(`-p no:cacheprovider`); the 504 and `make stop` above. The CPU speed in nested Docker on a busy
laptop (about 0.3 tokens/s) is far below the earlier offline run (`evidence/offline/`); no GPU was
available.
