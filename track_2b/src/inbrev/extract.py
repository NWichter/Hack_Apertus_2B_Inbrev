"""Deterministic extractors and text helpers. No model involved."""

from __future__ import annotations

import difflib
import html
import re
import unicodedata
from datetime import date, datetime

AHV_RE = re.compile(r"\b756[.\s]?\d{4}[.\s]?\d{4}[.\s]?\d{2}\b")
DATE_RE = re.compile(r"\b(\d{1,2})\.\s?(\d{1,2})\.\s?(\d{4}|\d{2})\b")
ISO_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")

STOPWORDS = {
    "de": "und der die das ich nicht mit für ist ein eine sie wir bitte den dem zu auf von haben ihr ihre sehr wie noch auch bei grüsse freundliche".split(),
    "fr": "et le la les je pas avec pour est un une vous nous merci de du des au votre vos ce cette mon ma salutations bonjour".split(),
    "it": "e il la le che non con per è un una lei noi grazie di del della al suo sua mi ho sono cordiali saluti buongiorno".split(),
    "en": "and the is i not with for a an you we please of to your thank my have would be this are kind regards".split(),
}


def source_text(subject: str | None, body: str | None) -> str:
    return f"{subject or ''}\n{body or ''}"


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip()


def fold(s: str) -> str:
    """Lowercase, whitespace-normalised, typographic quotes and dashes unified."""
    s = norm_ws(s).lower()
    return (
        s.replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("«", '"')
        .replace("»", '"')
        .replace("–", "-")
        .replace("—", "-")
    )


FUZZY_MIN_RATIO = 0.9
FUZZY_MIN_LEN = 8


def clean_quote(quote: str | None) -> str:
    """Undo artefacts seen in model output: HTML entities, wrapping quotes, the string 'null'."""
    if not quote:
        return ""
    q = html.unescape(html.unescape(quote)).strip()
    while len(q) >= 2 and q[0] in "\"'«“" and q[-1] in "\"'»”":
        q = q[1:-1].strip()
    q = q.lstrip("\"'").strip()
    return "" if q.lower() in {"null", "none", "n/a"} else q


def find_quote(quote: str, text: str) -> tuple[str, tuple[int, int] | None]:
    """Locate a model quote in the source text.

    'exact': verbatim substring. 'normalized': equal after case, whitespace and
    typographic folding. 'fuzzy': at least 90 % similar to one span (copy errors
    such as a wrong umlaut). The span always points into the original text, so the
    evidence shown to a human is the real wording, never the model's copy.
    """
    quote = clean_quote(quote)
    if not quote:
        return "missing", None
    i = text.find(quote)
    if i >= 0:
        return "exact", (i, i + len(quote))
    q = fold(quote)
    if not q:
        return "missing", None
    folded, mapping = _folded_with_map(text)
    j = folded.find(q)
    if j >= 0:
        return "normalized", _span(mapping, j, len(q))
    if len(q) < FUZZY_MIN_LEN:
        return "missing", None
    best, best_j, best_len = 0.0, -1, 0
    sm = difflib.SequenceMatcher(autojunk=False)
    sm.set_seq2(q)
    for length in {len(q), len(q) - 1, len(q) + 1}:
        for start in range(0, max(1, len(folded) - length + 1)):
            sm.set_seq1(folded[start : start + length])
            if (
                sm.real_quick_ratio() < FUZZY_MIN_RATIO
                or sm.quick_ratio() < FUZZY_MIN_RATIO
            ):
                continue
            r = sm.ratio()
            if r > best:
                best, best_j, best_len = r, start, length
    if best >= FUZZY_MIN_RATIO:
        return "fuzzy", _span(mapping, best_j, best_len)
    return "missing", None


def quote_span_text(quote: str, text: str) -> tuple[str, str | None]:
    status, span = find_quote(quote, text)
    return status, (text[span[0] : span[1]] if span else None)


def _span(mapping: list[int], j: int, n: int) -> tuple[int, int]:
    return mapping[j], mapping[min(j + n - 1, len(mapping) - 1)] + 1


def _folded_with_map(text: str) -> tuple[str, list[int]]:
    mapping: list[int] = []
    folded_chars: list[str] = []
    prev_space = False
    for idx, ch in enumerate(text):
        if ch.isspace():
            if prev_space or not folded_chars:
                continue
            folded_chars.append(" ")
            mapping.append(idx)
            prev_space = True
            continue
        prev_space = False
        f = fold(ch) or ch
        for c in f:
            folded_chars.append(c)
            mapping.append(idx)
    return "".join(folded_chars), mapping


def ahv_numbers(text: str) -> list[str]:
    out = []
    for m in AHV_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group())
        out.append(f"{digits[:3]}.{digits[3:7]}.{digits[7:11]}.{digits[11:]}")
    return out


def ahv_check_digit_valid(ahv: str) -> bool:
    d = re.sub(r"\D", "", ahv)
    if len(d) != 13:
        return False
    total = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(d[:12]))
    return (10 - total % 10) % 10 == int(d[12])


def parse_date(s: str | None) -> date | None:
    if not s:
        return None
    m = ISO_RE.search(s)
    if m:
        try:
            return date(int(m[1]), int(m[2]), int(m[3]))
        except ValueError:
            return None
    m = DATE_RE.search(s)
    if m:
        y = int(m[3])
        if y < 100:
            y += 2000 if y < 50 else 1900
        try:
            return date(y, int(m[2]), int(m[1]))
        except ValueError:
            return None
    return None


def dates_in(text: str) -> list[date]:
    out = []
    for m in DATE_RE.finditer(text):
        d = parse_date(m.group())
        if d:
            out.append(d)
    return out


def parse_received(received_at: str | None) -> datetime | None:
    if not received_at:
        return None
    try:
        return datetime.fromisoformat(received_at)
    except ValueError:
        return None


def deadline_from_date(deadline_date: date, received: date) -> str:
    delta = (deadline_date - received).days
    if delta <= 1:
        return "today"
    if delta <= 7:
        return "this_week"
    return "none"


def detect_language(text: str) -> str:
    words = re.findall(r"[a-zàâäçéèêëîïôöùûüœß']+", text.lower())
    scores = {
        lang: sum(w in sw for w in words)
        for lang, sw in ((k, set(v)) for k, v in STOPWORDS.items())
    }
    return max(scores, key=scores.get) if any(scores.values()) else "de"
