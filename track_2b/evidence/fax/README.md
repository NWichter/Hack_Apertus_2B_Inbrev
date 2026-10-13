# Fax path end to end: rendered pages → Tesseract OCR → Inbrev

Date: 2026-10-13. 60 gold v0 messages (`scripts/select_subset.py --n 60 --seed 2026`: all 16 with clinical
content plus 44 drawn over the routes) were rendered as degraded fax pages (`scripts/render_fax.py`, seed 7:
skew, blur, speckle, threshold, stamps on 40 %; `render-manifest.jsonl`). The pages were read by Inbrev's own
fax intake (`ingest.from_fax`, Tesseract deu+fra+ita) inside the Inbrev image with `--network none`
(`scripts/ocr_fax_set.py`), then triaged by Apertus 8B (endpoint, p3, 3 samples). Rendered pages are synthetic,
not real scans.

| | Clean text (same 60) | Fax pages via OCR |
| --- | --- | --- |
| Character error rate | – | corpus 0.27, median page 0.21 (upper bound: the OCR text also contains the fax header line and stamps) |
| Unreadable pages (empty OCR) | – | 3 of 60, all three abstained ("a person decides") |
| Route | 56/60 [0.84, 0.97] | 50/60 [0.72, 0.91] |
| Clinical flag | 13/16 | 12/16 |
| Clinical messages out of automation (flag or abstain) | 13/16 | 13/16 (the unreadable clinical page abstained) |
| Today recall | 18/21 | 19/21 |
| Abstained | 2 | 6 |

Same route on 54 of 60, same clinical flag on 55 of 60. OCR costs about 6 routes in 60 and moves unreadable
pages to a person instead of guessing. Files: `fax60-p3-8b.jsonl`, `fax60-report.md`.
