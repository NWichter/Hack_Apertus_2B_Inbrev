# Local Q4 weights without Docker Desktop (native llama.cpp, laptop iGPU)

Date: 2026-10-13. `scripts/run_native_llamacpp.ps1` runs the same llama.cpp build as the Docker offline
stack (b11382, commit 11fe021) natively on Windows with the same Q4_K_M GGUF (SHA-256 checked,
`a037df8d…`), llama-server bound to 127.0.0.1, one sample at temperature 0, prompt p3.
This measures speed and quality of the local weights on the practice-class hardware; it is **not** the
air-gapped proof (that is `make offline-eval`, `../offline/`, Docker network without internet).

Hardware: the same laptop, AMD Ryzen 7 PRO 8840U, Radeon 780M iGPU through Vulkan (no NVIDIA GPU here).
`llama-bench` (pp1024 / tg128, 2 repetitions): Vulkan 82.7 / 4.8 tokens per second, CPU 8 threads 20.1 / 3.5.

## Same 30 gold messages as the Docker CPU run (16 clinical + 14)

| Setup | Route | Clinical flag | Time per message |
| --- | --- | --- | --- |
| Docker Desktop, CPU, Q4, p2 (`../offline/`, 4 Oct) | 24/30 | 11/16 | 192 s |
| Native, Vulkan iGPU, Q4, p3 (`gold30-q4-vulkan.log`) | 25/30 [0.66, 0.93] | 11/16 [0.44, 0.86] | **62.7 s** (median 67.9, p95 84.9) |
| Endpoint BF16, p3, first sample only (replay) | 28/30 | 12/16 | – |
| **Native, Vulkan iGPU, Q4, p3 + symptom pass (default), 15 Oct** (`gold30-q4-vulkan-sym.log`) | 25/30 [0.66, 0.93] | **16/16** [0.81, 1.00] | **71.8 s** (median 69.3, p95 87.4) |

Paired Q4 (native) vs BF16 (one sample, p3): same route on 27 of 30, same clinical flag on 29 of 30
(Q4 misses `syn-118` in addition). `cost-vulkan.md`: at 62.7 s per message one box sorts about 57 messages
per hour; the full-cost line (CHF 11.69 per 1,000 at 60 messages a day) is dominated by the box, not by
energy (CHF 0.17). The cloud-VM rows in that file assume the iGPU time on a CPU VM and do not apply.

## Challenge set on local Q4 (115 messages, 44 clinical)

Same native setup, one sample at temperature 0 (`chl-q4-vulkan.jsonl`). The run was interrupted twice: the
llama-server process stopped without a log message (at least the second time it was ended from outside because the
laptop had almost no free RAM left and another session needed it);
rows with connection errors were removed and the run resumed (`*.part1-3.log`). The last 39 messages ran with
`-c 4096` instead of 8192 to save memory (prompts are about 1,600 tokens, so nothing was truncated); they took
46.4 s per message. All 115 rows are valid model answers.

| Setup | Route | Clinical exclusion | Today recall |
| --- | --- | --- | --- |
| Endpoint BF16, 3 samples (default) | 103/115 [0.83, 0.94] | 41/44 [0.82, 0.98] | 56/59 |
| Endpoint BF16, first sample only (replay) | 104/115 [0.84, 0.95] | 40/44 [0.79, 0.96] | 55/59 |
| **Local Q4, 1 sample (deployable configuration)** | **99/115 [0.79, 0.91]** | **38/44 [0.73, 0.94]** | 53/59 |

Paired Q4 vs BF16 one sample (`chl-compare.md`): route 0 vs 5 discordant (p = 0.06), clinical 1 vs 3 (p = 0.63).
Quantisation costs a few routes (mostly "other": 5/20 vs 10/20) and possibly clinical cases; the deployable
configuration catches 38 of 44 (keyword rules 31 of 44).

## Default configuration on local Q4 (15 October)

Same 30 messages, same native setup (llama.cpp b11382, Vulkan, `-c 4096`), prompt p3 with the symptom pass that is the
default since 13 October (`INBREV_SYMPTOM_CHECK=1`, one sample per call, temperature 0): two calls per message.
Clinical exclusion 16/16 (without the pass 11/16), route 25/30 (unchanged), 71.8 s per message wall time
(+9 s against 62.7 s without the pass; `gold30-sym-report.md` lists 64.0 s, the mean latency of the main call only), no failed symptom call. The subset holds all 16 clinical gold messages, so the
automatic share is low here (10 of 30; 4 of the 14 non-clinical messages go to a person). Files: `gold30-q4-vulkan-sym.jsonl`,
`gold30-q4-vulkan-sym.log`, `gold30-sym-report.md` (both runs side by side).
