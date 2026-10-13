# Value model: staff time and money per practice (assumptions, not measured)

Measured on `merged.v0.jsonl` with `gold-8b-sym.jsonl` (n = 180): automatic share 0.78 (neither abstained nor flagged; the MPA only checks the suggestion and its quote, `review_s`), of which wrongly routed 0.044 of all messages; false clinical flags 0.128 of all messages; clinical messages missed 0 of 16 (not priced: a missed clinical message is a safety risk that this model does not offset against staff time; safety is reported separately and is the reason every flagged or unsure message goes to a person).

| Scenario | MPA minutes saved per day | Doctor minutes for false flags per day | Net CHF per day | Net CHF per month | Break-even manual time per message |
| --- | --- | --- | --- | --- | --- |
| cautious | 3 | 3.8 | -12 | -242 | 77 s |
| base | 32 | 3.8 | 17 | 349 | 33 s |
| favourable | 160 | 3.8 | 152 | 3193 | 16 s |

Break-even: the manual handling time per message at which the net CHF value (MPA time saved minus doctor time for false flags minus running cost) is zero in that scenario. These are scenario projections from assumptions, not measured savings and not confidence bounds.

Model: saved = messages × automatic share × (manual − review) − messages × wrongly-routed × manual; cost = false flags × doctor glance + Inbrev running cost.

| Assumption | cautious | base | favourable | unit | basis |
| --- | --- | --- | --- | --- | --- |
| `messages_per_day` | 30 | 60 | 120 | messages | assumption for a 2-3 doctor practice; to be asked in interviews |
| `manual_s` | 30 | 60 | 120 | s per message | MPA reads, decides route and deadline, forwards; assumption, to be timed (guide part C) |
| `review_s` | 20 | 15 | 10 | s per message | MPA checks an automatic suggestion with its quote; assumption, to be timed |
| `false_flag_doctor_s` | 60 | 30 | 15 | s per false flag | doctor glance at a message wrongly flagged as clinical; assumption |
| `mpa_chf_h` | 40 | 50 | 60 | CHF per hour | MPA full employer cost; assumption (project spec), no sourced wage table |
| `doctor_chf_h` | 200 | 150 | 120 | CHF per hour | GP time value; assumption |
| `inbrev_chf_per_1000` | 30 | 12 | 6 | CHF per 1,000 messages | on-prem box, scripts/cost_model.py (CHF 12 at 60/day); low/high scale with volume, assumption |
| `workdays_per_month` | 21 | 21 | 21 | days | assumption |
