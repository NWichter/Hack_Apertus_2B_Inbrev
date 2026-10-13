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

Paired Q4 (native) vs BF16 (one sample, p3): same route on 27 of 30, same clinical flag on 29 of 30
(Q4 misses `syn-118` in addition). `cost-vulkan.md`: at 62.7 s per message one box sorts about 57 messages
per hour; the full-cost line (CHF 11.69 per 1,000 at 60 messages a day) is dominated by the box, not by
energy (CHF 0.17). The cloud-VM rows in that file assume the iGPU time on a CPU VM and do not apply.

## Challenge set on local Q4

See the section below once the run is complete.
