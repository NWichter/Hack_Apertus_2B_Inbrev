# Generated test sets (synthetic v0, published without human review)

These are the message texts behind every reported number on generated data. **All messages are
synthetic and fictional. The labels come from the seeded grid that was fixed before any text was
written; no person had reviewed them when they were published on 15 October** (a later review, if any, is in
`../../evidence/review/`; it does not change these files). Two open-weights models labelled the same texts blind as a
consistency check (`../../evidence/agreement/`, `../../evidence/holdout2/`); nothing was relabelled.
Apertus, the model under test, wrote no text and no label.

| File | Rows (clinical) | Text written by | Used for | SHA-256 |
| --- | --- | --- | --- | --- |
| `gold-v0.jsonl` | 180 (16) | Claude `claude-opus-5-5` (90) and OpenAI `gpt-5.5` via Codex CLI (90), 2026-10-01 | Main table, report §5 | `366cbb9d1a926fc8d4bb5d88a79db6d906c514d32a31e81ba9388408e272a2b9` |
| `open-generator-v0.jsonl` | 42 (8) | NVIDIA Nemotron 3 Ultra (open weights), 2026-10-04 | Generator control | `d8a7464a92910fb78ba041f29b254df7709eb85c220ac90b8d8eb150ca5d9ca6` |
| `dev-v0.jsonl` | 60 (9) | NVIDIA Nemotron 3 Ultra, 2026-10-04 | Dev split for prompt p3 and the symptom pass | `d911976b16675289a3c0f765f6e09aa408460b1d49e74f266ab1a478b8698b39` |
| `challenge-v1.jsonl` | 115 (44) | NVIDIA Nemotron 3 Ultra, 2026-10-13 | Clinical-exclusion challenge set | `eed58c8a98334f4ff3e516f5524fc946450ce120a8485e08e75a04089b9fb995` |
| `holdout2-v0.jsonl` | 146 (14) | Google Gemma 4 31B, 2026-10-14 | Hold-out 2 and route study, frozen before any run | `306225ba66a5a10b864e1c9e0eb56fd2a3246e73fb06f90f42dcf2b0be0d6142` |

The hashes are those of the files used for the runs (hold-out 2: same hash as in
`../../evidence/holdout2/FREEZE.md`). The files are stored byte for byte (`.gitattributes`: no line-ending conversion).
Every row has `generator`, `generator_model`, `generated_at`, `prompt_version` and the grid `label`;
some rows carry `review_flag` / `review_reason` or `edited_by` from the automatic checks.
Generation prompts: `../generation/PROMPT.md` and `../../scripts/generate_openrouter.py`.

## Checks before publication (15 October 2026)

- **No real personal data.** `scripts/validate.py` on all five files: 0 errors (AHV numbers with invalid
  check digits, e-mail domains `.example`, phone numbers in the fictional `000` block, no valid IBAN).
  Warnings (`validation/`, one report per file): values without an evidence quote (24), AHV numbers not taken from the
  grid but still with invalid check digits (5), names of real institutions such as Suva or a regional hospital (3),
  near-duplicate openings (2), one language mismatch. No real persons.
- **Redistribution of the generator outputs.** Anthropic (commercial terms) and OpenAI (terms of use)
  assign the outputs to the user; the NVIDIA Open Model License states that NVIDIA claims no ownership of
  outputs; Gemma 4 is released under Apache-2.0. None of the texts comes from an external dataset.
- **Size.** The five files together are about 1 MB; `data/` stays far below 100 MB.

Licence: CDLA-Permissive-2.0 like the rest of this folder (`../LICENSE`).

## Reproduce a number

```bash
python -m inbrev replay data/synthetic/gold-v0.jsonl evidence/gap/holdout-predictions/gold-8b-sym.jsonl --out runs/gold.replay.jsonl
python -m inbrev eval data/synthetic/gold-v0.jsonl runs/gold.replay.jsonl --baselines
```
