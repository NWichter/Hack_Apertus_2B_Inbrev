# Label review tool

A local page for checking the gold-set labels by hand. The labels in the gold set were written by the
generator models and nobody has checked them yet. This tool records a human decision for each message
and measures how far the human agrees with the generator labels and with themself.

- `index.html`: the review page. It is one static file with no network access. Open it by double-click.
- `kappa.py`: computes the same statistics offline from the exported log (standard library only).

Gold data stays outside the repo. You choose the file in the page; the page reads it locally.

## Workflow

1. Open `index.html` and enter your reviewer initials.
2. Choose the gold JSONL (for example `merged.v0.jsonl`, `data/seed/messages.seed.jsonl` or
   `data/ood/*.jsonl`). To continue earlier work, also choose an exported `review_log.jsonl`.
   The browser also keeps your progress in local storage, keyed by the SHA-256 of the gold file.
3. **Pass 1** (all messages). Set route, deadline, safety flag ("clinical content – a person must
   read it"), abstain/ambiguous and an optional note.
   - `blind` mode (default): the gold label is hidden.
   - `check` mode: the gold label and its evidence quotes are shown and prefilled. Confirm or correct.
4. **Pass 2** (intra-rater). 60 messages, blind, in a shuffled order. The sample is deterministic
   (seed 2026): all messages with gold `safety_flag=true` (if there are at most 60), the rest drawn at
   random. Start pass 2 at least 48 h after pass 1. The page warns but does not block.
5. **Export** writes `review_log.jsonl`. Keep it next to the gold data, not in the repo.
6. **Statistics** shows κ, the changed gold labels and a list of all differences.

Keys: `1`–`9` route, `T`/`W`/`N` deadline, `S` safety flag, `A` abstain, `/` note, `Enter` save and
next, `C` confirm gold (check mode), `←`/`→` previous/next, `U` next unlabelled message.

## Export format

One JSON object per line, one line per decision. Saving a message again appends a new line; the latest
line per `message_id` and `pass` (by `labelled_at`) counts.

```json
{"message_id": "syn-001", "pass": 1, "mode": "blind", "route": "other", "deadline": "today",
 "safety_flag": true, "abstain": false, "note": "", "reviewer": "NW",
 "labelled_at": "2026-10-04T09:12:31.204Z", "gold_route": "other", "gold_deadline": "today",
 "gold_safety_flag": true, "gold_abstain": false, "source_file_sha256": "366c…"}
```

`mode` is `blind` or `check` in pass 1 and always `blind` in pass 2. The `gold_*` fields are copied from
the gold file at labelling time. `source_file_sha256` identifies the exact gold file.

## κ computation

Cohen's κ = (p_o − p_e) / (1 − p_e), where p_o is the observed agreement and p_e the agreement expected
from the two marginal distributions. The 95% confidence interval is κ ± 1.96·SE with the approximation
SE = √(p_o(1 − p_o) / (n(1 − p_e)²)), clipped to [−1, 1]. If p_e = 1 (both sides use one category
only), κ is undefined and shown as `n/a`.

Comparisons, for route, deadline and safety_flag:

- **Intra-rater**: pass 1 vs pass 2 on the messages labelled in both passes (n ≤ 60).
- **Human vs gold**: pass 1 vs the generator label, for all modes and separately for blind mode only
  (check mode shows the gold label, so it is biased towards agreement).

"Changed gold labels" counts the pass-1 messages that differ from gold in at least one of route,
deadline, safety_flag or abstain.

```sh
python kappa.py review_log.jsonl
python kappa.py review_log.jsonl --gold merged.v0.jsonl
```

Without `--gold`, the script uses the `gold_*` fields in the log. With `--gold`, it takes the gold
labels from that file, warns if its SHA-256 differs from the log, and checks that the pass-2 messages
belong to the expected seed-2026 sample. The output is Markdown. κ was checked against
`sklearn.metrics.cohen_kappa_score`.
