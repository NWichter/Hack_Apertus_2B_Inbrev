# Offline runs with local Apertus weights

Each folder is one run of `scripts/run_offline_eval.sh` (`make offline-eval`). Host paths in the
`docker inspect` files are replaced by `<repo>`.

## 2026-10-04-q4-cpu-gold30

| | |
| --- | --- |
| Weights | `Colby/apertus-v1.5-8b-text-Q4_K_M-GGUF` @ `248ec68`, Q4_K_M quantisation of the text weights of `swiss-ai/Apertus-v1.5-8B` (Apache-2.0); SHA-256 `a037df8d87ff6caacee794ee85f55342f2152e0d359b7389033300c3bee5f299`, equal to the Hugging Face LFS hash |
| Server | `ghcr.io/ggml-org/llama.cpp:server@sha256:559ac229…`, `-c 8192 --parallel 1 --jinja --load-mode none`, CPU only |
| Network | `inbrev-offline_practice`, `internal: true`; both containers attached only to it. Egress test from the Inbrev container: DNS, TCP 1.1.1.1:443 and HTTPS fail; the same test on the default bridge succeeds |
| Hardware | Laptop, AMD Ryzen 7 PRO 8840U (8 cores, 28 W TDP), Docker Desktop on Windows (WSL2 VM with 16 vCPU, 15 GB RAM), shared with other containers and desktop work during the run |
| Input | 30 of the 180 synthetic gold v0 messages: all 16 with clinical content plus 14 drawn round-robin over routes (`scripts/select_subset.py --n 30 --seed 2026`) |
| Setting | One sample per message at temperature 0 (the one-sample replay on the full set shows almost no loss, see the report) |
| Time | 5,765 s wall for 30 messages = 192 s per message (median 163 s, p95 417 s); model load from the Docker volume about 17 min |
| Memory | llama.cpp peak 6.2 GiB, Inbrev 167 MiB |

| Same 30 messages | Route | Clinical exclusion | Today recall | Deadline | Not abstained |
| --- | --- | --- | --- | --- | --- |
| Offline, Q4 on CPU, 1 sample | 24/30 [0.63, 0.90] | 11/16 [0.44, 0.86] | 13/17 | 21/30 | 30/30 |
| Endpoint, BF16, 1 sample (replay) | 23/30 [0.59, 0.88] | 12/16 [0.51, 0.90] | 13/17 | 19/30 | 29/30 |
| Endpoint, BF16, 3 samples | 24/30 [0.63, 0.90] | 13/16 [0.57, 0.93] | 14/17 | 19/30 | 28/30 |
| Keyword rules | 23/30 [0.59, 0.88] | 7/16 [0.23, 0.67] | 9/17 | 15/30 | 30/30 |

The last column counts messages without abstention (older definition of "coverage"; `report.md` was written with it). In the report, coverage means neither abstained nor flagged: 16/30 for the offline Q4 run.

Paired Q4 vs. BF16 (1 sample): same route on 28 of 30, same clinical flag on 29 of 30 (Q4 misses
`syn-146`), same deadline on 26 of 30. The subset over-weights clinical cases, so its rates are not
comparable with the full 180. `cost.md` turns the measured time into CHF per 1,000 messages.
