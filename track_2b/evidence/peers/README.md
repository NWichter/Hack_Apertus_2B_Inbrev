# Other open-weights models in the Inbrev pipeline (comparison only)

Date: 2026-10-13. Same code, prompt p3, schema, checks, lexical net, three samples at T = 0.7 (sent as
three single requests), gold v0 (180 messages). Models through OpenRouter, reasoning off
(`INBREV_EXTRA_BODY`). These models are not part of Inbrev; at runtime Inbrev calls only Apertus.

| Model | Route | Clinical exclusion | Today recall | Coverage |
| --- | --- | --- | --- | --- |
| Apertus 8B (endpoint, `../prompt-p3/`) | 170/180 [0.90, 0.97] | 13/16 [0.57, 0.93] | 44/50 | 151/180 |
| Apertus 70B (endpoint) | 172/180 [0.91, 0.98] | 15/16 [0.72, 0.99] | 47/50 | 147/180 |
| Qwen3.5-9B (`qwen/qwen3.5-9b`) | 177/180 [0.95, 0.99] | 16/16 [0.81, 1.00] | 50/50 | 142/180 |
| Ministral 8B (`mistralai/ministral-8b-2512`) | 177/180 [0.95, 0.99] | 16/16 [0.81, 1.00] | 48/50 | 139/180 |

Paired against Apertus 8B (exact McNemar, `compare.md`): route 8 vs 1 discordant for both (p = 0.039),
clinical 3 vs 0 (p = 0.25). Apertus 70B vs Qwen3.5-9B: route p = 0.125, clinical p = 1.
Both comparison models also raise more flags (32 vs 28) and leave fewer messages to automation.

Honest reading: on this synthetic set, two other small open models do better than Apertus 8B in the same
pipeline, although the prompt was developed with Apertus. Llama 3.1 8B was also tried: the provider
returned HTTP 429 ("temporarily rate-limited upstream") on 177 of 180 messages, so no result is reported
for it. Cost (token prices): Qwen ≤ USD 0.11, Ministral ≤ USD 0.15.
