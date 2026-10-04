"""Neutralise the last real organisation names in the Swiss practice set and add
per-row provenance. Idempotent; labels (route, deadline, assignee, safety flag,
abstain) are not touched.

    python scripts/annotate_swiss_set.py [data/ood/swiss_practice_inbox.jsonl]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PATH = (
    Path(__file__).resolve().parents[1] / "data" / "ood" / "swiss_practice_inbox.jsonl"
)

# Real organisation -> fictitious replacement, applied to sender, subject, body and label strings.
NEUTRALISE = {
    "swiss-prx-0010": [("Pharmacie Sun Store de Nyon", "Pharmacie Exemple de Nyon")],
    "swiss-prx-0017": [
        ("OSPEDALE REGIONALE DI BELLINZONA E VALLI", "OSPEDALE ESEMPIO"),
        ("Ospedale Regionale di Bellinzona e Valli", "Ospedale Esempio"),
    ],
    "swiss-prx-0021": [
        ("LABOR VIOLLIER AG", "LABOR BEISPIEL AG"),
        ("Labor Viollier AG", "Labor Beispiel AG"),
    ],
    "swiss-prx-0022": [
        ("Coop Vitality Apotheke am Bahnhof Bern", "Apotheke Beispiel am Bahnhof Bern")
    ],
    "swiss-prx-0002": [("Bahnhof-Apotheke in Aarau", "Apotheke Beispiel in Aarau")],
    "swiss-prx-0016": [("Farmacia San Nicolao di Lugano", "Farmacia Esempio di Lugano")],
    "swiss-prx-0029": [("Farmacia Pedemonte di Bellinzona", "Farmacia Esempio di Bellinzona")],
}

# What the Codex session changed per row (diff of the unedited first version in the
# gitignored data/external/swiss_practice_inbox.jsonl against commit fecd8d2).
CODEX_EDITS = {
    "0001": "e-mail domain",
    "0002": "pharma brand name removed",
    "0003": "hospital name",
    "0004": "e-mail domain, insurer name",
    "0005": "e-mail domain",
    "0006": "e-mail domain",
    "0007": "e-mail domain",
    "0008": "e-mail domain",
    "0009": "e-mail domain",
    "0010": "e-mail domain",
    "0011": "e-mail domain, hospital name",
    "0012": "e-mail domain, insurer name",
    "0013": "e-mail domain",
    "0014": "e-mail domain",
    "0015": "e-mail domain",
    "0016": "e-mail domain",
    "0017": None,
    "0018": "e-mail domain, insurer name",
    "0019": "e-mail domain",
    "0020": "e-mail domain",
    "0021": None,
    "0022": "e-mail domain",
    "0023": "e-mail domain",
    "0024": "e-mail domain, disability-insurance office name",
    "0025": "e-mail domain",
    "0026": "e-mail domain",
    "0027": None,
    "0028": None,
    "0029": "e-mail domain, pharma brand name removed",
    "0030": None,
}


def _replace(obj, pairs):
    if isinstance(obj, str):
        for old, new in pairs:
            obj = obj.replace(old, new)
        return obj
    if isinstance(obj, list):
        return [_replace(x, pairs) for x in obj]
    if isinstance(obj, dict):
        return {k: _replace(v, pairs) for k, v in obj.items()}
    return obj


def provenance(mid: str) -> dict:
    edits = [
        {
            "by": "codex",
            "model": "gpt-6.1-sol",
            "date": "2026-10-03",
            "change": "replaced real e-mail domains and organisation names with fictitious ones"
            + (
                f" ({CODEX_EDITS[mid[-4:]]})"
                if CODEX_EDITS[mid[-4:]]
                else " (no change in this row)"
            ),
            "evidence": "git-ai authorship note on commit fecd8d2 (codex session 01a1039c, model gpt-6.1-sol)",
        }
    ]
    if mid in NEUTRALISE:
        edits.append(
            {
                "by": "claude",
                "model": "claude-opus-5-5",
                "date": "2026-10-04",
                "change": "replaced a real Swiss organisation name with a fictitious one; labels unchanged",
                "evidence": "scripts/annotate_swiss_set.py",
            }
        )
    return {
        "generator": "gemini",
        "generator_tool": "antigravity-cli",
        "generator_model": "gemini-3.8-flash",
        "generated_at": "2026-10-03T04:54Z",
        "generation_prompt": "not recorded",
        "generation_evidence": (
            "Antigravity CLI session 5208082a: write_to_file steps 92 and 94 at 04:54:13Z and "
            "04:54:43Z (UTC) into data/external/swiss_practice_inbox.jsonl; model name from the "
            "session's conversation database"
        ),
        "labels_by": "same Gemini session as the text",
        "edits": edits,
        "human_review": False,
        "license": "CDLA-Permissive-2.0",
    }


def main(path: Path) -> None:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    out = []
    for r in rows:
        mid = r["message_id"]
        if mid in NEUTRALISE:
            r = _replace(r, NEUTRALISE[mid])
        r["provenance"] = provenance(mid)
        text = (r.get("subject") or "") + "\n" + (r.get("body") or "")
        for e in r["label"].get("evidence", []):
            assert e["quote"] in text, (mid, e["quote"])
        out.append(r)
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8"
    )
    print(json.dumps({"rows": len(out), "neutralised": sorted(NEUTRALISE)}))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else PATH)
