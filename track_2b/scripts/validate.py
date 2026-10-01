"""Validate gold-set JSONL files and write a Markdown report.

python scripts/validate.py --grid grid.jsonl --report validation-report.md claude.jsonl codex.jsonl

Errors: schema, label differs from grid, evidence not verbatim, required evidence
missing, deadline_date inconsistent, valid AHV check digit, non-fictitious e-mail
domain or phone number, "ß" in German text, duplicate ids or bodies.
Warnings: language looks different, known real brand/institution, near-duplicates,
values without evidence, valid IBAN checksum.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "schema" / "triage_result.schema.json"
GRID_LABEL_KEYS = [
    "route",
    "deadline",
    "deadline_date",
    "assignee",
    "safety_flag",
    "abstain",
]
GRID_TOP_KEYS = ["language", "channel", "received_at"]

STOPWORDS = {
    "de": "und der die das ich nicht mit für ist ein eine sie wir bitte den dem zu auf von haben ihr ihre sehr wie noch auch bei grüsse freundliche".split(),
    "fr": "et le la les je pas avec pour est un une vous nous merci de du des au votre vos ce cette mon ma salutations bonjour".split(),
    "it": "e il la le che non con per è un una lei noi grazie di del della al suo sua mi ho sono cordiali saluti buongiorno".split(),
    "en": "and the is i not with for a an you we please of to your thank my have would be this are kind regards".split(),
}

REAL_NAMES = [
    "Helsana",
    "CSS",
    "Swica",
    "SWICA",
    "Sanitas",
    "Visana",
    "Groupe Mutuel",
    "Assura",
    "KPT",
    "Atupri",
    "ÖKK",
    "Sympany",
    "EGK",
    "Suva",
    "SUVA",
    "Unilabs",
    "Synlab",
    "Viollier",
    "Dianalabs",
    "Medisupport",
    "Bioanalytica",
    "Inselspital",
    "CHUV",
    "HUG",
    "USZ",
    "Universitätsspital",
    "Hirslanden",
    "Triemli",
    "Medgate",
    "Santé24",
    "Galenica",
    "Amavita",
    "Sun Store",
    "TopPharm",
    "Pfizer",
    "Novartis",
    "Roche",
    "Sandoz",
    "Mepha",
    "Spirig",
    "Bayer",
    "Sanofi",
    "Vifor",
    "Takeda",
    "Ente Ospedaliero",
    "Dafalgan",
    "Panadol",
    "Voltaren",
    "Pantozol",
    "Xarelto",
    "Eliquis",
    "Ozempic",
    "Marcoumar",
    "Brufen",
    "Irfen",
    "Algifor",
    "Novalgin",
    "Sortis",
    "Nexium",
    "Aspirin",
    "Seresta",
    "Temesta",
    "Concor",
]
REAL_RE = re.compile(r"\b(" + "|".join(re.escape(n) for n in REAL_NAMES) + r")\b")
HOSPITAL_RE = re.compile(
    r"\b(Kantonsspital|Hôpital cantonal|Ospedale [Rr]egionale|Ospedale cantonale)\s+[A-ZÄÖÜ]\w+"
)

EMAIL_RE = re.compile(r"[\w.+-]+@((?:[\w-]+\.)+[A-Za-z]{2,})")
URL_RE = re.compile(r"\b(?:https?://|www\.)([\w.-]+\.[A-Za-z]{2,})")
PHONE_RE = re.compile(
    r"(?<![\d.])(?:\+41[\s.]?\d{2}|0\d{2})[\s./-]?(\d{3})[\s.-]?\d{2}[\s.-]?\d{2}(?![\d.])"
)
AHV_RE = re.compile(r"\b756\.?\d{4}\.?\d{4}\.?\d{2}\b")
IBAN_RE = re.compile(r"\bCH\d{2}(?:\s?[0-9A-Z]{4}){4}\s?[0-9A-Z]\b")


def ean13_valid(digits: str) -> bool:
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
    return (10 - total % 10) % 10 == int(digits[12])


def iban_valid(iban: str) -> bool:
    s = iban.replace(" ", "")
    s = s[4:] + s[:4]
    num = "".join(str(int(c, 36)) for c in s)
    return int(num) % 97 == 1


def detect_language(text: str) -> tuple[str, dict[str, int]]:
    tokens = re.findall(r"[a-zàâäçéèêëîïôöùûüß']+", text.lower())
    tokens = [t.split("'")[-1] for t in tokens]
    scores = {
        lang: sum(1 for t in tokens if t in words) for lang, words in STOPWORDS.items()
    }
    return max(scores, key=scores.get), scores


def shingles(text: str, k: int = 5) -> set[str]:
    t = re.sub(r"\s+", " ", text.lower())
    return {t[i : i + k] for i in range(max(0, len(t) - k + 1))}


def flatten_values(label: dict) -> list[tuple[str, str]]:
    out = []
    for group in ("patient", "fields"):
        for k, v in (label.get(group) or {}).items():
            if isinstance(v, str) and v.strip():
                out.append((f"{group}.{k}", v))
    return out


class Report:
    def __init__(self) -> None:
        self.errors: list[tuple[str, str, str]] = []
        self.warnings: list[tuple[str, str, str]] = []

    def err(self, mid: str, check: str, msg: str) -> None:
        self.errors.append((mid, check, msg))

    def warn(self, mid: str, check: str, msg: str) -> None:
        self.warnings.append((mid, check, msg))


def check_row(
    row: dict, spec: dict | None, validator: Draft202012Validator, rep: Report
) -> None:
    mid = row.get("message_id", "?")
    for key in [
        "message_id",
        "language",
        "channel",
        "sender",
        "received_at",
        "subject",
        "body",
        "label",
    ]:
        if row.get(key) in (None, ""):
            rep.err(mid, "format", f"missing top-level key `{key}`")
    label = row.get("label") or {}
    text = f"{row.get('subject', '')}\n{row.get('body', '')}"

    result = {"message_id": mid, "language": row.get("language")}
    result.update(
        {k: v for k, v in label.items() if k in validator.schema["properties"]}
    )
    for e in validator.iter_errors(result):
        rep.err(mid, "schema", f"{'/'.join(map(str, e.path)) or '(root)'}: {e.message}")
    extra = set(label) - set(validator.schema["properties"])
    if extra:
        rep.err(mid, "schema", f"unknown label keys: {sorted(extra)}")

    if spec is None:
        rep.err(mid, "grid", "message_id not in grid")
    else:
        for k in GRID_LABEL_KEYS:
            if label.get(k) != spec["label"].get(k):
                rep.err(
                    mid,
                    "grid",
                    f"label.{k} = {label.get(k)!r}, grid = {spec['label'].get(k)!r}",
                )
        for k in GRID_TOP_KEYS:
            if row.get(k) != spec.get(k):
                rep.err(mid, "grid", f"{k} = {row.get(k)!r}, grid = {spec.get(k)!r}")
        if row.get("generator") and row.get("generator") != spec.get("generator"):
            rep.err(
                mid,
                "grid",
                f"generator {row.get('generator')} != grid {spec.get('generator')}",
            )
        if spec.get("ahv_number") and spec["ahv_number"] not in text:
            rep.err(mid, "grid", f"spec AHV {spec['ahv_number']} not used in text")

    evidence = label.get("evidence") or []
    ev_fields = Counter()
    for ev in evidence:
        q = ev.get("quote", "")
        ev_fields[ev.get("field")] += 1
        if not q or q not in text:
            rep.err(mid, "evidence", f"quote not verbatim ({ev.get('field')}): {q!r}")
    if not ev_fields["route"]:
        rep.err(mid, "evidence", "no evidence for route")
    if label.get("deadline_date") and not ev_fields["deadline"]:
        rep.err(mid, "evidence", "deadline_date set but no evidence for deadline")
    if label.get("safety_flag") and not ev_fields["safety_flag"]:
        rep.err(mid, "evidence", "safety_flag true but no evidence for safety_flag")
    for field, value in flatten_values(label):
        if not ev_fields[field]:
            rep.warn(mid, "evidence", f"{field} = {value!r} has no evidence quote")

    try:
        recv = datetime.fromisoformat(row.get("received_at", "")).date()
        dd = label.get("deadline_date")
        if dd:
            delta = (date.fromisoformat(dd) - recv).days
            ok = {
                "today": 0 <= delta <= 1,
                "this_week": 2 <= delta <= 7,
                "none": delta > 7,
            }.get(label.get("deadline"), False)
            if not ok:
                rep.err(
                    mid,
                    "deadline",
                    f"deadline {label.get('deadline')} but deadline_date is {delta} days after received_at",
                )
    except (TypeError, ValueError) as exc:
        rep.err(mid, "deadline", f"bad date: {exc}")
    if (
        label.get("route") == "report_received" or label.get("safety_flag")
    ) and label.get("deadline") != "today":
        rep.err(
            mid, "deadline", "report_received / safety_flag must have deadline today"
        )

    lang = row.get("language")
    guess, scores = detect_language(text)
    if lang and guess != lang and scores.get(guess, 0) > scores.get(lang, 0) + 1:
        rep.warn(
            mid, "language", f"labelled {lang}, stopwords suggest {guess} {scores}"
        )
    if lang == "de" and "ß" in text:
        rep.err(mid, "swiss", "German text contains ß")

    full = f"{row.get('sender', '')}\n{text}"
    for m in AHV_RE.finditer(full):
        digits = re.sub(r"\D", "", m.group(0))
        if ean13_valid(digits):
            rep.err(mid, "fiction", f"AHV number with VALID check digit: {m.group(0)}")
        if spec is not None and m.group(0) != spec.get("ahv_number"):
            rep.warn(
                mid, "fiction", f"AHV number not taken from the grid: {m.group(0)}"
            )
    for m in EMAIL_RE.finditer(full):
        if not m.group(1).lower().endswith(".example"):
            rep.err(mid, "fiction", f"e-mail domain not fictitious: {m.group(0)}")
    for m in URL_RE.finditer(full):
        if not m.group(1).lower().endswith(".example"):
            rep.warn(mid, "fiction", f"URL not fictitious: {m.group(0)}")
    for m in PHONE_RE.finditer(full):
        if m.group(1) != "000":
            rep.err(mid, "fiction", f"phone number outside the 000 block: {m.group(0)}")
    for m in IBAN_RE.finditer(full):
        if iban_valid(m.group(0)):
            rep.warn(mid, "fiction", f"IBAN with valid checksum: {m.group(0)}")
    for m in REAL_RE.finditer(full):
        rep.warn(mid, "fiction", f"possible real brand/institution: {m.group(0)}")
    for m in HOSPITAL_RE.finditer(full):
        rep.warn(mid, "fiction", f"check hospital name: {m.group(0)}")


def check_duplicates(
    rows: list[dict], rep: Report, threshold: float
) -> list[tuple[str, str, float]]:
    ids = Counter(r.get("message_id") for r in rows)
    for mid, n in ids.items():
        if n > 1:
            rep.err(mid, "duplicate", f"message_id appears {n} times")
    bodies = defaultdict(list)
    for r in rows:
        bodies[re.sub(r"\s+", " ", (r.get("body") or "").strip().lower())].append(
            r["message_id"]
        )
    for group in bodies.values():
        if len(group) > 1:
            rep.err(group[0], "duplicate", f"identical body: {group}")
    openings = defaultdict(list)
    for r in rows:
        lines = [
            ln.strip()
            for ln in (r.get("body") or "").splitlines()
            if len(ln.strip()) >= 45 and re.search(r"[.!?]", ln)
        ]
        first = (
            re.split(r"(?<=[.!?])\s", lines[0], maxsplit=1)[0].lower() if lines else ""
        )
        if len(first) > 25:
            openings[first].append(r["message_id"])
    for first, group in openings.items():
        if len(group) > 1:
            rep.warn(
                group[0],
                "duplicate",
                f"same opening sentence in {group}: {first[:60]!r}",
            )
    sh = [(r["message_id"], shingles(r.get("body") or "")) for r in rows]
    pairs = []
    for i in range(len(sh)):
        for j in range(i + 1, len(sh)):
            a, b = sh[i][1], sh[j][1]
            if not a or not b:
                continue
            jac = len(a & b) / len(a | b)
            if jac >= threshold:
                pairs.append((sh[i][0], sh[j][0], jac))
                rep.warn(sh[i][0], "near_duplicate", f"{sh[j][0]} Jaccard {jac:.2f}")
    return pairs


def write_report(path: Path, files: list[Path], rows: list[dict], rep: Report) -> None:
    lines = [
        "# Validation report",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    lines += ["| File | Rows |", "| --- | --- |"]
    by_file = Counter(r["_file"] for r in rows)
    lines += [f"| `{f.name}` | {by_file[f.name]} |" for f in files]
    lines += [
        "",
        f"**Errors:** {len(rep.errors)} · **Warnings:** {len(rep.warnings)}",
        "",
    ]

    def dist(title: str, fn) -> None:
        nonlocal lines
        c = Counter(fn(r) for r in rows)
        lines += [f"### {title}", "", "| Value | n |", "| --- | --- |"]
        lines += [
            f"| {k} | {v} |"
            for k, v in sorted(c.items(), key=lambda kv: (-kv[1], str(kv[0])))
        ]
        lines.append("")

    lines += ["## Distributions", ""]
    dist("Generator", lambda r: r.get("generator"))
    dist("Route", lambda r: r["label"].get("route"))
    dist("Deadline", lambda r: r["label"].get("deadline"))
    dist("Safety flag", lambda r: r["label"].get("safety_flag"))
    dist("Abstain", lambda r: r["label"].get("abstain"))
    dist("Language", lambda r: r.get("language"))
    dist("Channel", lambda r: r.get("channel"))
    dist("Writing level", lambda r: (r.get("meta") or {}).get("writing_level"))
    dist("Review flag", lambda r: bool(r.get("review_flag")))
    dist("Edited by", lambda r: r.get("edited_by") or "-")

    for title, items in (("Errors", rep.errors), ("Warnings", rep.warnings)):
        lines += [f"## {title}", ""]
        if not items:
            lines += ["None.", ""]
            continue
        by_check = Counter(c for _, c, _ in items)
        lines += (
            ["| Check | n |", "| --- | --- |"]
            + [f"| {c} | {n} |" for c, n in by_check.most_common()]
            + [""]
        )
        lines += ["| message_id | check | detail |", "| --- | --- | --- |"]
        for mid, check, msg in sorted(items):
            lines.append(f"| {mid} | {check} | {msg.replace('|', '/')} |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--grid", type=Path, required=True)
    ap.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    ap.add_argument("--report", type=Path, default=Path("validation-report.md"))
    ap.add_argument("--near-dup", type=float, default=0.5)
    args = ap.parse_args()

    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    grid = {}
    for line in args.grid.read_text(encoding="utf-8").splitlines():
        if line.strip():
            s = json.loads(line)
            grid[s["message_id"]] = s

    rep = Report()
    rows = []
    for f in args.files:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                rep.err(f"{f.name}:{n}", "json", str(exc))
                continue
            row["_file"] = f.name
            rows.append(row)
            check_row(row, grid.get(row.get("message_id")), validator, rep)
    check_duplicates(rows, rep, args.near_dup)
    write_report(args.report, args.files, rows, rep)
    print(
        f"{len(rows)} rows, {len(rep.errors)} errors, {len(rep.warnings)} warnings -> {args.report}"
    )
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
