"""OCR rendered fax pages (scripts/render_fax.py) with Inbrev's own fax intake and measure CER.

Runs where Tesseract is installed, i.e. in the Inbrev image:
  docker run --rm --network none -v "$PWD:/work" -w /work -e PYTHONPATH=/work/src inbrev:latest \
      python scripts/ocr_fax_set.py GOLD.jsonl FAXDIR --out runs/fax/ocr-messages.jsonl

Output: the gold rows with subject and body replaced by what ingest.from_fax read from the page
(labels unchanged), plus `ocr` = {cer, chars_ref, chars_ocr}. CER = Levenshtein distance between
the page text (subject, blank line, body) and the OCR text, divided by the reference length,
after collapsing whitespace. The OCR text also contains the fax header line and stamps that the
reference lacks, so CER is an upper bound for the message text. cer_mean is the unweighted mean of
page CERs; cer_corpus is total distance / total reference characters.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

from inbrev.ingest import from_fax


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("gold", type=Path)
    ap.add_argument("faxdir", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    rows = [
        json.loads(x)
        for x in a.gold.read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    out, cers, missing, dist, refs = [], [], [], 0, 0
    for r in rows:
        png = a.faxdir / f"{r['message_id']}.png"
        if not png.exists():
            missing.append(r["message_id"])
            continue
        msg = from_fax(png.read_bytes(), png.name)
        ref = norm(f"{r.get('subject', '')}\n\n{r.get('body', '')}")
        hyp = norm(msg["body"])
        d = levenshtein(ref, hyp)
        dist, refs = dist + d, refs + len(ref)
        cer = d / max(1, len(ref))
        cers.append(cer)
        row = dict(r)
        row.update({"subject": msg["subject"], "body": msg["body"], "channel": "fax"})
        row["ocr"] = {
            "cer": round(cer, 4),
            "chars_ref": len(ref),
            "chars_ocr": len(hyp),
        }
        out.append(row)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "pages": len(out),
                "missing_pages": missing,
                "cer_corpus": round(dist / max(1, refs), 4),
                "cer_mean": round(statistics.mean(cers), 4) if cers else None,
                "cer_median": round(statistics.median(cers), 4) if cers else None,
                "cer_max": round(max(cers), 4) if cers else None,
            }
        )
    )


if __name__ == "__main__":
    main()
