# Label review by a person

Date: 2026-10-16. Reviewer: one person from the team (not a clinician). Tool: a static review page built from `tools/review/` (no network access); export version `ff2c147d64`. No label was changed by this review: every score in the report still uses the original labels.

## Part A: blind re-labelling

60 of 60 messages of a fixed sample from the 180-message gold set: all 16 messages with clinical content plus 44 drawn with seed 2026 (`select_pass2` in `tools/review/kappa.py`). Clinical content is therefore over-represented; κ holds for this sample, not for the gold set as a whole. The person saw only the message, never our label or a model label.

### Person vs our labels (Cohen's κ, 95 % CI: κ ± 1.96·SE)

| field | n | agreement | κ | 95% CI |
|---|---:|---:|---:|---:|
| route | 60 | 0.983 | 0.981 | [0.944, 1.000] |
| deadline | 60 | 1.000 | 1.000 | [1.000, 1.000] |
| safety_flag | 60 | 1.000 | 1.000 | [1.000, 1.000] |

2 of 60 messages differ in at least one of route, deadline, safety flag, abstain (abstain 1, route 1).

## Part B: disputed messages

The 36 messages where at least one of the two open-weights annotators disagreed with our label (`../agreement/`). The review page asks for a blind label first, then shows our label and both model labels; the person decided which one fits the written rules.

Decided: 36 of 36 · our label right 27 · model label right 9 · text does not fit the rules 0.

## Part C: disputed messages of hold-out 2 (optional)

Decided: 19 of 19 · our label right 15 · model label right 4 · text does not fit the rules 0.

## Files

- `review_log.jsonl`: part A in the format of `tools/review/kappa.py` (person's label and our label per message); recompute with `python tools/review/kappa.py evidence/review/review_log.jsonl`.
- `decisions.jsonl`: parts B and C, one decision per message (`null` = not decided).

Message texts and the reviewer's free-text notes are not included (the generated texts stay outside the repository until they are released).
