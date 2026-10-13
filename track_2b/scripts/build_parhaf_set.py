#!/usr/bin/env python3
"""Build a French report_received test set from PARHAF (clinical reports written by physicians).

PARHAF (HealthDataHub, 2026) holds 4,254 fictitious French patient cases whose reports were
written by hand by resident physicians. This script wraps 40 of them, verbatim (long ones cut at
a paragraph end), into Inbrev inbox messages with fixed labels. No text is written by a model;
every choice is deterministic (seed 2026). Needs pandas + pyarrow to read the parquet file.

python scripts/build_parhaf_set.py --parquet PARHAF-train.parquet --out data/parhaf/messages.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

SEED = 2026
MIN_CHARS = 400
MAX_CHARS = 6000
PER_TYPE = {"CRH": 12, "CRC": 10, "CRO": 6, "ANAPATH": 6, "URGENCES": 6}

SOURCE_INFO = {
    "source": "PARHAF",
    "dataset": "PARHAF (HealthDataHub), train split",
    "license": "CC-BY-4.0 / Licence Ouverte Etalab 2.0",
    "license_url": "https://creativecommons.org/licenses/by/4.0/",
    "url": "https://huggingface.co/datasets/HealthDataHub/PARHAF",
    "paper": "arXiv:2603.20494",
    "note": "Fictitious patient cases; reports written by hand by resident physicians (dataset card). French health system, not Swiss.",
}

REPORT_NAMES = {
    "CRH": "compte rendu d'hospitalisation",
    "CRC": "compte rendu de consultation",
    "CRO": "compte rendu opératoire",
    "ANAPATH": "compte rendu d'anatomopathologie",
    "URGENCES": "compte rendu des urgences",
}
INSTITUTIONS = [
    ("Hôpital Exemple-sur-Lac", "hopital-exemple-lac"),
    ("Clinique du Val Fictif", "clinique-val-fictif"),
    ("Centre hospitalier de Montexemple", "ch-montexemple"),
    ("Hôpital régional de la Broye-Exemple", "hr-broye-exemple"),
]
SUBJECTS = [
    "{rt}",
    "Transmission : {rt}",
    "{rt} concernant votre patient(e)",
    "Envoi du {rt}",
]
WRAPPERS = {
    "hin_mail": [
        "Bonjour,\n\nNous vous transmettons ci-dessous le {rt} de votre patient(e), établi par {inst}.\n\nMeilleures salutations\nSecrétariat médical\n\n",
        "Chère Consœur, cher Confrère,\n\nVeuillez trouver ci-après le {rt} ({inst}) pour la suite de la prise en charge.\n\nAvec nos salutations confraternelles\nSecrétariat\n\n",
    ],
    "fax": ["TÉLÉCOPIE\nExpéditeur : {inst}\nPages : {pages}\n\nObjet : {rt}\n\n"],
    "email": [
        "Madame, Monsieur,\n\nVous trouverez ci-dessous le {rt} de {inst}. Nous restons à votre disposition pour toute question.\n\nMeilleures salutations\nSecrétariat\n\n",
    ],
}
CHANNELS = ["hin_mail", "fax", "email"]


def docs_of(row) -> list[tuple[str, str]]:
    d = row["documents"]
    types, texts = list(d["type"]), list(d["text"])
    return [(str(t), str(x)) for t, x in zip(types, texts)]


def shorten(text: str) -> tuple[str, bool]:
    text = text.strip()
    if len(text) <= MAX_CHARS:
        return text, False
    cut = text[:MAX_CHARS]
    for sep in ("\n\n", "\n", ". "):
        i = cut.rfind(sep)
        if i > MIN_CHARS:
            return cut[: i + (1 if sep == ". " else 0)].rstrip(), True
    return cut.rstrip(), True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    df = pd.read_parquet(a.parquet)
    rng = random.Random(SEED)
    pool: dict[str, list] = {k: [] for k in PER_TYPE}
    for _, row in df.iterrows():
        for dtype, text in docs_of(row):
            if dtype in pool and MIN_CHARS <= len(text.strip()):
                pool[dtype].append((row["id"], dtype, text))
                break
    picked = []
    for dtype, n in PER_TYPE.items():
        cands = sorted(pool[dtype], key=lambda x: x[0])
        picked += rng.sample(cands, min(n, len(cands)))
    rng.shuffle(picked)
    start = date(2026, 10, 5)
    rows = []
    for i, (case_id, dtype, text) in enumerate(picked, start=1):
        kept, truncated = shorten(text)
        inst, slug = rng.choice(INSTITUTIONS)
        channel = rng.choice(CHANNELS)
        rt = REPORT_NAMES[dtype]
        wrapper = rng.choice(WRAPPERS[channel]).format(
            rt=rt, inst=inst, pages=1 + len(kept) // 2500
        )
        subject = rng.choice(SUBJECTS).format(rt=rt[0].upper() + rt[1:])
        day = start + timedelta(days=rng.randint(0, 9))
        while day.weekday() >= 5:
            day += timedelta(days=1)
        recv = datetime(
            day.year, day.month, day.day, rng.randint(7, 17), rng.randint(0, 59)
        )
        sender = (
            f"Secrétariat {inst} <secretariat@{slug}.hin.example>"
            if channel == "hin_mail"
            else (
                f"{inst}, fax 022 000 {rng.randint(10, 99)} {rng.randint(10, 99)}"
                if channel == "fax"
                else f"Secrétariat {inst} <secretariat@{slug}.example>"
            )
        )
        rows.append(
            {
                "message_id": f"parhaf-{i:03d}",
                "language": "fr",
                "channel": channel,
                "sender_type": "hospital",
                "sender": sender,
                "received_at": recv.strftime("%Y-%m-%dT%H:%M"),
                "subject": subject,
                "body": wrapper + kept,
                "source": "parhaf",
                "label": {
                    "route": "report_received",
                    "deadline": "today",
                    "deadline_date": None,
                    "assignee": "doctor",
                    "safety_flag": False,
                    "abstain": False,
                    "patient": {},
                    "fields": {"report_type": rt, "sender_institution": inst},
                    "evidence": [
                        {"field": "route", "quote": subject},
                        {"field": "fields.sender_institution", "quote": inst},
                    ],
                },
                "provenance": {
                    **SOURCE_INFO,
                    "original_id": case_id,
                    "original_type": dtype,
                    "original_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "original_chars": len(text.strip()),
                    "kept_chars": len(kept),
                    "truncated": truncated,
                    "changes": "first report of the case; surrounding whitespace removed; fictitious cover text, subject, sender and received_at added by template",
                    "labels_by": "fixed rule in scripts/build_parhaf_set.py, not reviewed by a person",
                    "human_review": False,
                },
            }
        )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "written": len(rows),
                "by_type": {
                    k: sum(r["provenance"]["original_type"] == k for r in rows)
                    for k in PER_TYPE
                },
                "truncated": sum(r["provenance"]["truncated"] for r in rows),
            }
        )
    )


if __name__ == "__main__":
    main()
