# Cost per 1,000 messages (CHF, excl. VAT)

Local CPU run: n = 30, 192.2 s per message (1 sample(s)), median latency 163.0 s, p95 417.3 s, 267 output tokens per message, 19 messages per hour, 450 per day on one box.

| Setup | CHF per 1,000 messages | Basis |
| --- | --- | --- |
| On-prem CPU box, energy only (measured time x 39 W) | 0.52 | 2.08 kWh per 1,000 messages |
| On-prem CPU box, full cost at 60 messages/day | 12.04 | depreciation + idle power + energy |
| Swiss cloud CPU VM (Infomaniak 8 vCPU), billed only while sorting | 2.39 | assumes our measured CPU time; other CPU, not measured |
| Swiss cloud CPU VM kept on 24/7, per practice | 17.92 | 32 CHF per month |
| Swiss cloud GPU VM (Infomaniak L4) kept on 24/7, per practice | 119.40 | 215 CHF per month; throughput not measured |
| Swiss token API at the Apertus 70B price, tokens measured in `gold-8b.jsonl` | 2.59 | 1398 in / 644 out tokens per message |
| Swiss token API at the Apertus 70B price, tokens measured in `gold-70b.jsonl` | 3.40 | 1398 in / 967 out tokens per message |

Inputs:

- `electricity_chf_kwh` = 0.2511: ElCom 2026, median category C2 (small business), strompreis.elcom.admin.ch
- `box_power_w` = 39.0: ServeTheHome 2024, ASRock 4X4 BOX-8840U sustained load 38-39 W
- `box_idle_w` = 8.0: ServeTheHome 2024, idle 6.5-9 W
- `box_chf` = 704.0: barebone CHF 554 (digitec search result, not verified) + 32 GB RAM and SSD, assumed CHF 150
- `box_years` = 3.0: assumed depreciation period
- `infomaniak_cpu_chf_h` = 0.0448: Infomaniak Public Cloud a8_ram32 (8 vCPU, 32 GB), price list 2026-10-04
- `infomaniak_l4_chf_h` = 0.2985: Infomaniak Public Cloud nvl4_a8_ram16 (NVIDIA L4), price list 2026-10-04
- `infomaniak_70b_in_chf_mtok` = 0.7: Infomaniak AI Services, swiss-ai/Apertus-v1.5-70B input, 2026-10-04
- `infomaniak_70b_out_chf_mtok` = 2.5: Infomaniak AI Services, swiss-ai/Apertus-v1.5-70B output, 2026-10-04
- `messages_per_day` = 60.0: assumption for one practice, to be checked in interviews
