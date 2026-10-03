#!/usr/bin/env python3
"""Download external datasets and adapt them to Inbrev's JSONL format.

Raw external data is never committed: it is downloaded into data/external/
(gitignored) with `--download`. Labels produced here are heuristic mappings
(e.g. every symptom-triage case becomes route "other"), not human gold labels.
No number in the technical report comes from these sets.

Sources (licence as stated on the dataset card, checked 2026-10-03):
- triage: sweatSmile/medical-symptom-triage -- no licence declared on the card
- german_emails: ale-dp/german-english-email-ticket-classification -- CC-BY-NC-4.0
  (IT support tickets, not practice mail)
- healthcaremagic: lavita/ChatDoctor-HealthCareMagic-100k -- no licence declared;
  contains real, de-identified patient questions scraped from HealthCareMagic.
  Download only with --include-real-patient-text; never commit or redistribute.
- portal_topics: PortalPal-AI/Portal-Messaging-Topics -- CC-BY-NC-4.0 (topic list only)
- swiss_practice: data/ood/swiss_practice_inbox.jsonl -- synthetic, written with an
  LLM coding assistant (not Apertus); fictitious people, organisations and domains;
  labels not yet reviewed by a person
- degraded_ocr: synthetic OCR noise applied to the Swiss practice set
"""

import json
import csv
import argparse
import random
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXTERNAL_DIR = BASE_DIR / "data" / "external"
OOD_DIR = BASE_DIR / "data" / "ood"
SEED_DIR = BASE_DIR / "data" / "seed"

# Add src to sys.path to access inbrev helpers if available
sys.path.insert(0, str(BASE_DIR / "src"))
try:
    from inbrev.safety import lexical_flag
except ImportError:

    def lexical_flag(text: str) -> bool:
        keywords = [
            "chest pain",
            "breath",
            "faint",
            "bleed",
            "emergency",
            "suicid",
            "notfall",
            "atemnot",
        ]
        t = text.lower()
        return any(k in t for k in keywords)


OCR_CONFUSIONS = [
    ("rn", "m"),
    ("m", "rn"),
    ("cl", "d"),
    ("vv", "w"),
    ("l", "1"),
    ("1", "l"),
    ("0", "O"),
    ("O", "0"),
    ("5", "S"),
    ("S", "5"),
    ("8", "B"),
    ("c", "e"),
    ("ä", "ae"),
    ("ö", "oe"),
    ("ü", "ue"),
    ("é", "e"),
    ("è", "e"),
    ("à", "a"),
]

SPECKLE_CHARS = [".", ",", "'", "-", "~", "^", "_", "/"]
ILLEGIBLE_TAGS = {
    "de": ["[unleserlich]", "[...]", "[?]"],
    "fr": ["[illisible]", "[...]", "[?]"],
    "it": ["[illeggibile]", "[...]", "[?]"],
    "en": ["[illegible]", "[...]", "[?]"],
}


def simulate_ocr_degradation(
    text: str,
    severity: str = "medium",
    rng: random.Random | None = None,
    lang: str = "de",
) -> str:
    """
    Simulates OCR and handwriting noise typical of fax transmissions,
    scanned medical prescriptions, and degraded clinical documentation.

    Severity levels:
    - light: Minor scanner skew, occasional character confusions (~3% noise)
    - medium: Multi-generation fax noise, split words, speckles (~8% noise)
    - heavy: Severe handwriting degradation, faded ink, broken lines, illegible sections (~18% noise)
    """
    if not text:
        return ""
    if rng is None:
        rng = random.Random(42)

    noise_prob = {"light": 0.03, "medium": 0.08, "heavy": 0.18}.get(severity, 0.08)
    words = text.split()
    degraded_words = []

    for word in words:
        # Occasional unreadable marker in heavy mode
        if severity == "heavy" and rng.random() < 0.04 and len(word) > 4:
            tags = ILLEGIBLE_TAGS.get(lang, ILLEGIBLE_TAGS["de"])
            degraded_words.append(rng.choice(tags))
            continue

        chars = list(word)
        mod_chars = []
        i = 0
        while i < len(chars):
            # Check for two-character confusion replacements
            if i + 1 < len(chars):
                pair = chars[i] + chars[i + 1]
                found_pair = False
                for orig, repl in OCR_CONFUSIONS:
                    if (
                        len(orig) == 2
                        and pair.lower() == orig
                        and rng.random() < noise_prob * 1.5
                    ):
                        mod_chars.append(repl.upper() if pair.isupper() else repl)
                        i += 2
                        found_pair = True
                        break
                if found_pair:
                    continue

            ch = chars[i]
            # Single character confusion
            matched_conf = False
            for orig, repl in OCR_CONFUSIONS:
                if len(orig) == 1 and ch.lower() == orig and rng.random() < noise_prob:
                    mod_chars.append(repl.upper() if ch.isupper() else repl)
                    matched_conf = True
                    break

            if not matched_conf:
                # Speckle noise insertion
                if rng.random() < noise_prob * 0.4:
                    mod_chars.append(rng.choice(SPECKLE_CHARS))
                # Dropout (faded ink)
                if severity == "heavy" and rng.random() < noise_prob * 0.3:
                    pass  # skip character
                else:
                    mod_chars.append(ch)
            i += 1

        w = "".join(mod_chars)

        # Word splitting (spaces inserted inside words due to poor stroke connection)
        if (
            (severity in ["medium", "heavy"])
            and len(w) > 6
            and rng.random() < noise_prob * 0.7
        ):
            split_pt = rng.randint(2, len(w) - 2)
            w = w[:split_pt] + " " + w[split_pt:]

        degraded_words.append(w)

    result = " ".join(degraded_words)
    # Line noise artifact in heavy mode
    if severity == "heavy" and rng.random() < 0.2:
        result = result + "\n[FAX-TRANSMISSION LINE ERROR: 0xFD4]"
    return result


def adapt_triage(
    input_path: Path, output_path: Path | None = None, limit: int = 150
) -> list[dict]:
    """
    Converts medical symptom triage cases into Inbrev evaluation records.
    Maps:
      - Emergency / Urgent -> safety_flag: True, deadline: "today", assignee: "doctor"
      - Routine -> safety_flag: False, deadline: "this_week", assignee: "mpa"
    """
    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if limit and idx >= limit:
                break
            row = json.loads(line)
            urgency = row.get("urgency", "Routine")
            is_emergency = urgency in ["Emergency", "Urgent"]

            body_text = row.get("input", "").strip()
            if not body_text:
                continue

            rec = {
                "message_id": f"ext-triage-{idx + 1:04d}",
                "language": "en",  # Triage dataset is English
                "channel": "web_form",
                "sender": f"patient_{idx + 1}@example.com",
                "subject": f"Medical inquiry: {row.get('specialty', 'General')}",
                "body": body_text,
                "source": "external_medical_symptom_triage",
                "label": {
                    "route": "other",
                    "deadline": "today" if is_emergency else "this_week",
                    "assignee": "doctor" if is_emergency else "mpa",
                    "safety_flag": is_emergency,
                    "abstain": False,
                    "patient": {},
                    "fields": {
                        "urgency_source": urgency,
                        "specialty": row.get("specialty", ""),
                    },
                    "evidence": [],
                },
            }
            records.append(rec)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as out:
            for r in records:
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Exported {len(records)} records from Triage dataset to {output_path}")
    return records


def adapt_german_emails(
    input_path: Path, output_path: Path | None = None, limit: int = 150
) -> list[dict]:
    """
    Converts German email ticket classification cases into Inbrev evaluation records.
    """
    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            if limit and idx >= limit:
                break

            prio = row.get("priority", "low").lower()
            subject = row.get("subject", "").strip()
            body = row.get("body", "").strip()
            lang = row.get("language", "de").lower()

            # Map deadline based on ticket priority
            if prio == "high":
                deadline = "today"
            elif prio == "medium":
                deadline = "this_week"
            else:
                deadline = "none"

            text_comb = (subject + " " + body).lower()
            is_billing = any(
                w in text_comb
                for w in [
                    "rechnung",
                    "kosten",
                    "gebühr",
                    "überweisung",
                    "mahnung",
                    "rechnungsbetrag",
                ]
            )

            rec = {
                "message_id": f"ext-email-{idx + 1:04d}",
                "language": lang,
                "channel": "email",
                "sender": f"kontakt_{idx + 1}@example.com",
                "subject": subject,
                "body": body,
                "source": "external_german_email_classification",
                "label": {
                    "route": "billing" if is_billing else "other",
                    "deadline": deadline,
                    "assignee": "admin",
                    "safety_flag": False,
                    "abstain": False,
                    "patient": {},
                    "fields": {
                        "ticket_type": row.get("type", ""),
                        "queue": row.get("queue", ""),
                    },
                    "evidence": [],
                },
            }
            records.append(rec)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as out:
            for r in records:
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(
            f"Exported {len(records)} records from German Emails dataset to {output_path}"
        )
    return records


def adapt_healthcaremagic(
    input_path: Path, output_path: Path | None = None, limit: int = 150
) -> list[dict]:
    """
    Converts HealthCareMagic patient questions into Inbrev records.
    Labels come from the lexical safety net and keyword rules, so they are heuristic.
    """
    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if limit and idx >= limit:
                break
            row = json.loads(line)
            inp_text = row.get("input", "").strip()
            if not inp_text:
                continue

            is_acute = lexical_flag(inp_text)
            text_lower = inp_text.lower()
            is_prescription = any(
                w in text_lower
                for w in [
                    "prescription",
                    "medication",
                    "pill",
                    "tablet",
                    "dose",
                    "dosage",
                    "taking ",
                    "refill",
                    "rezept",
                ]
            )

            if is_acute:
                route = "other"
                deadline = "today"
                assignee = "doctor"
                safety = True
            elif is_prescription:
                route = "prescription_request"
                deadline = "this_week"
                assignee = "doctor"
                safety = False
            else:
                route = "other"
                deadline = "this_week"
                assignee = "doctor"
                safety = False

            rec = {
                "message_id": f"ext-hcm-{idx + 1:04d}",
                "language": "en",
                "channel": "web_form",
                "sender": f"patient_hcm_{idx + 1}@example.com",
                "subject": "Patient Medical Inquiry",
                "body": inp_text,
                "source": "external_healthcaremagic",
                "label": {
                    "route": route,
                    "deadline": deadline,
                    "assignee": assignee,
                    "safety_flag": safety,
                    "abstain": False,
                    "patient": {},
                    "fields": {},
                    "evidence": [],
                },
            }
            records.append(rec)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as out:
            for r in records:
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(
            f"Exported {len(records)} records from HealthCareMagic dataset to {output_path}"
        )
    return records


def adapt_swiss_practice(
    input_path: Path, output_path: Path | None = None, limit: int = 50
) -> list[dict]:
    """
    Loads the synthetic Swiss practice inbox set (fictitious; appointments, prescriptions,
    referrals, certificates, insurer queries, billing, acute cases).
    """
    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if limit and idx >= limit:
                break
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

    if output_path:
        with open(output_path, "w", encoding="utf-8") as out:
            for r in records:
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Exported {len(records)} Swiss practice inbox records to {output_path}")
    return records


def adapt_degraded_ocr(
    input_records: list[dict] | Path,
    output_path: Path | None = None,
    limit: int = 50,
    severity: str = "medium",
    seed: int = 2026,
) -> list[dict]:
    """
    Creates a handwriting and degraded OCR stress-test dataset.
    Simulates OCR artifacts typical of medical prescription notes, faxed hospital reports,
    and handwritten practitioner memos.

    Under heavy degradation where critical evidence spans are broken, evaluates whether
    the pipeline abstains instead of returning values without a verifiable quote.
    """
    if isinstance(input_records, Path):
        with open(input_records, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
    else:
        records = input_records

    rng = random.Random(seed)
    degraded_records = []

    for idx, rec in enumerate(records[:limit]):
        lang = rec.get("language", "de")
        orig_body = rec.get("body", "")
        orig_subject = rec.get("subject", "")

        deg_subject = simulate_ocr_degradation(
            orig_subject, severity=severity, rng=rng, lang=lang
        )
        deg_body = simulate_ocr_degradation(
            orig_body, severity=severity, rng=rng, lang=lang
        )

        # In heavy degradation mode, ground-truth evidence cannot be verified safely by OCR.
        # The expected safe outcome for corrupted text is to abstain or require human review,
        is_heavy = severity == "heavy"
        label = dict(rec.get("label", {}))
        if is_heavy and not label.get("safety_flag"):
            label["abstain"] = True

        new_rec = {
            "message_id": f"deg-{severity[:3]}-{rec.get('message_id', f'{idx + 1:04d}')}",
            "language": lang,
            "channel": "fax" if rec.get("channel") != "fax" else "fax",
            "sender": rec.get("sender", "Unknown"),
            "subject": deg_subject,
            "body": deg_body,
            "source": f"degraded_ocr_{severity}",
            "label": label,
            "metadata": {
                "original_message_id": rec.get("message_id"),
                "degradation_severity": severity,
                "simulated_artifacts": [
                    "char_confusion",
                    "speckle_noise",
                    "whitespace_drift",
                ],
            },
        }
        degraded_records.append(new_rec)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as out:
            for r in degraded_records:
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(
            f"Exported {len(degraded_records)} degraded OCR stress records ({severity}) to {output_path}"
        )
    return degraded_records


def adapt_ood_blend(
    triage_path: Path,
    emails_path: Path,
    swiss_path: Path | None,
    output_path: Path,
    triage_limit: int = 50,
    email_limit: int = 50,
    swiss_limit: int = 30,
) -> list[dict]:
    """
    Combines:
    1. Clinical symptom triage (emergency detection & urgency)
    2. German customer support emails (administrative & billing)
    3. Swiss medical practice inbox cases (prescriptions, referrals, appointments, certificates, insurer queries)
    into a comprehensive, balanced Out-Of-Distribution (OOD) benchmark sample.
    """
    triage_recs = adapt_triage(triage_path, None, limit=triage_limit)
    email_recs = adapt_german_emails(emails_path, None, limit=email_limit)
    swiss_recs = []
    if swiss_path and swiss_path.exists():
        swiss_recs = adapt_swiss_practice(swiss_path, None, limit=swiss_limit)

    blended = triage_recs + email_recs + swiss_recs

    with open(output_path, "w", encoding="utf-8") as out:
        for r in blended:
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(
        f"Exported comprehensive OOD benchmark ({len(triage_recs)} triage + {len(email_recs)} emails + {len(swiss_recs)} Swiss practice = {len(blended)} records) to {output_path}"
    )
    return blended


HF = "https://huggingface.co/datasets"
ROWS_API = "https://datasets-server.huggingface.co/rows"
SOURCES = {
    "triage": {
        "repo": "sweatSmile/medical-symptom-triage",
        "licence": "none declared on the dataset card",
        "rows": ("default", "validation"),
        "file": "medical_symptom_triage_val.jsonl",
    },
    "german_emails": {
        "repo": "ale-dp/german-english-email-ticket-classification",
        "licence": "CC-BY-NC-4.0",
        "url": "german_email_classification.csv",
        "file": "german_email_classification.csv",
    },
    "portal_topics": {
        "repo": "PortalPal-AI/Portal-Messaging-Topics",
        "licence": "CC-BY-NC-4.0",
        "url": "messaging_topics.csv",
        "file": "portal_messaging_topics.csv",
    },
    "healthcaremagic": {
        "repo": "lavita/ChatDoctor-HealthCareMagic-100k",
        "licence": "none declared on the dataset card; real de-identified patient questions",
        "rows": ("default", "train"),
        "file": "healthcaremagic_sample_250.jsonl",
        "max_rows": 250,
        "real_patient_text": True,
    },
}


def download(
    names: list[str], include_real_patient_text: bool = False, max_rows: int = 300
) -> None:
    import urllib.parse
    import urllib.request

    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    for name in names:
        src = SOURCES[name]
        if src.get("real_patient_text") and not include_real_patient_text:
            print(
                f"skip {name}: contains real patient text, pass --include-real-patient-text"
            )
            continue
        out = EXTERNAL_DIR / src["file"]
        print(f"{name}: {src['repo']} (licence: {src['licence']}) -> {out}")
        if "url" in src:
            urllib.request.urlretrieve(
                f"{HF}/{src['repo']}/resolve/main/{src['url']}", out
            )
            continue
        config, split = src["rows"]
        limit = min(max_rows, src.get("max_rows", max_rows))
        rows, offset = [], 0
        while len(rows) < limit:
            q = urllib.parse.urlencode(
                {
                    "dataset": src["repo"],
                    "config": config,
                    "split": split,
                    "offset": offset,
                    "length": min(100, limit - len(rows)),
                }
            )
            with urllib.request.urlopen(f"{ROWS_API}?{q}") as r:
                batch = [x["row"] for x in json.load(r).get("rows", [])]
            if not batch:
                break
            rows += batch
            offset += len(batch)
        out.write_text(
            "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows),
            encoding="utf-8",
        )


def main():
    parser = argparse.ArgumentParser(
        description="Adapt external datasets and generate stress tests for Inbrev evaluation"
    )
    parser.add_argument(
        "--dataset",
        choices=[
            "triage",
            "german_emails",
            "healthcaremagic",
            "swiss_practice",
            "degraded_ocr",
            "ood_blend",
            "all",
        ],
        default="ood_blend",
    )
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument(
        "--download",
        nargs="*",
        choices=sorted(SOURCES),
        default=None,
        help="download raw data into data/external/ (gitignored) first",
    )
    parser.add_argument("--include-real-patient-text", action="store_true")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument(
        "--severity", choices=["light", "medium", "heavy"], default="medium"
    )
    args = parser.parse_args()
    if args.download is not None:
        download(
            args.download or ["triage", "german_emails", "portal_topics"],
            args.include_real_patient_text,
        )
        return

    triage_inp = EXTERNAL_DIR / "medical_symptom_triage_val.jsonl"
    emails_inp = EXTERNAL_DIR / "german_email_classification.csv"
    hcm_inp = EXTERNAL_DIR / "healthcaremagic_sample_250.jsonl"
    swiss_inp = OOD_DIR / "swiss_practice_inbox.jsonl"

    if args.dataset == "triage":
        out = (
            Path(args.output)
            if args.output
            else EXTERNAL_DIR / "adapted_triage_eval.jsonl"
        )
        adapt_triage(triage_inp, out, limit=args.limit)
    elif args.dataset == "german_emails":
        out = (
            Path(args.output)
            if args.output
            else EXTERNAL_DIR / "adapted_german_emails_eval.jsonl"
        )
        adapt_german_emails(emails_inp, out, limit=args.limit)
    elif args.dataset == "healthcaremagic":
        out = (
            Path(args.output)
            if args.output
            else EXTERNAL_DIR / "adapted_healthcaremagic_eval.jsonl"
        )
        adapt_healthcaremagic(hcm_inp, out, limit=args.limit)
    elif args.dataset == "swiss_practice":
        out = (
            Path(args.output)
            if args.output
            else EXTERNAL_DIR / "adapted_swiss_practice_eval.jsonl"
        )
        adapt_swiss_practice(swiss_inp, out, limit=args.limit)
    elif args.dataset == "degraded_ocr":
        out = (
            Path(args.output)
            if args.output
            else EXTERNAL_DIR / f"adapted_degraded_ocr_{args.severity}_eval.jsonl"
        )
        inp = swiss_inp if swiss_inp.exists() else SEED_DIR / "messages.seed.jsonl"
        adapt_degraded_ocr(inp, out, limit=args.limit, severity=args.severity)
    elif args.dataset == "ood_blend":
        out = (
            Path(args.output)
            if args.output
            else EXTERNAL_DIR / "ood_benchmark_sample.jsonl"
        )
        adapt_ood_blend(
            triage_inp,
            emails_inp,
            swiss_inp,
            out,
            triage_limit=args.limit,
            email_limit=args.limit,
            swiss_limit=args.limit,
        )
    elif args.dataset == "all":
        adapt_triage(
            triage_inp, EXTERNAL_DIR / "adapted_triage_eval.jsonl", limit=args.limit
        )
        adapt_german_emails(
            emails_inp,
            EXTERNAL_DIR / "adapted_german_emails_eval.jsonl",
            limit=args.limit,
        )
        adapt_healthcaremagic(
            hcm_inp,
            EXTERNAL_DIR / "adapted_healthcaremagic_eval.jsonl",
            limit=args.limit,
        )
        if swiss_inp.exists():
            adapt_swiss_practice(
                swiss_inp,
                EXTERNAL_DIR / "adapted_swiss_practice_eval.jsonl",
                limit=args.limit,
            )
            adapt_degraded_ocr(
                swiss_inp,
                EXTERNAL_DIR / "adapted_degraded_ocr_heavy_eval.jsonl",
                limit=args.limit,
                severity="heavy",
            )
            adapt_degraded_ocr(
                swiss_inp,
                EXTERNAL_DIR / "adapted_degraded_ocr_medium_eval.jsonl",
                limit=args.limit,
                severity="medium",
            )
        adapt_ood_blend(
            triage_inp,
            emails_inp,
            swiss_inp,
            EXTERNAL_DIR / "ood_benchmark_sample.jsonl",
            triage_limit=args.limit,
            email_limit=args.limit,
            swiss_limit=args.limit,
        )


if __name__ == "__main__":
    main()
