# Hold-out 2: frozen before any Inbrev run (14 October 2026)

No Inbrev model (Apertus or comparison) has seen these messages when this file was committed.

- **Grid:** `scripts/generate_openrouter.py grid --seed 7373 --prefix ho2 --preset holdout2` (`grid-holdout2.jsonl`):
  the gold v0 distribution scaled to 150 messages (routes 22/22/18/20/15/15/13/12/13, 14 clinical, 12 medical traps,
  7 ambiguous, 15 mixed; DE 83, FR 37, IT 23, EN 7). Labels are fixed by the grid before any text exists.
- **Text:** `google/gemma-4-31b-it` (open weights) via OpenRouter, the same generator prompt as the Nemotron sets
  (`PROMPT-v0.2-gemma.txt`), USD 0.047 (`generation-log.json`). Gemma has not been used before as generator, annotator
  or comparison model in this project. 146 of 150 specs passed validation (4 dropped after three attempts):
  14 clinical (6 explicit, 8 in passing), 12 traps, 120 plain; DE 81, FR 37, IT 22, EN 6.
- **Second labels (open models, not people):** Nemotron 3 Super (free) and gpt-oss-120b (reasoning low, USD 0.010),
  blind from the written rules (`scripts/annotate_open_models.py`). **19 of 146 are disputed** (at least one model differs
  from the grid on route or clinical content; in 7 both models agree against the grid), listed in `disputed-ids.txt`;
  the 127 others in `undisputed-ids.txt`. Results are reported on all 146 and on the 127 undisputed messages.
  Nothing was relabelled.
- The message texts were kept outside the repository during the study; since 15 October they are published unreviewed as `../../data/synthetic/holdout2-v0.jsonl` (same SHA-256).

| File | SHA-256 |
| --- | --- |
| `holdout2.jsonl` (texts and grid labels; now `data/synthetic/holdout2-v0.jsonl`) | `306225ba66a5a10b864e1c9e0eb56fd2a3246e73fb06f90f42dcf2b0be0d6142` |
| `grid-holdout2.jsonl` | `97d1ea7e0b066d21cefa452ce6f93ba2a8657c172749eaf7b0f39208315d7710` |
| `ho2-nemotron-super.jsonl` | `253bf3b9b7d6a111c5099284f100ae8d292f28df2cd8678511e52673dc54e815` |
| `ho2-gpt-oss-120b.jsonl` | `c79bdae5a720322ddd979606b8f6377dba2e26cfccf0c86a6e4d58e2780bad7d` |
| `disputed-ids.txt` | `992b7c2ca1298f18627a97113b0a086251f0b5f073f3811ae5e7fb8494facb58` |
