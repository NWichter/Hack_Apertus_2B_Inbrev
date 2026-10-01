"""Build the deterministic specification grid for the synthetic gold set.

Every spec fixes the gold labels (route, deadline, deadline_date, assignee,
safety_flag, abstain) before any text is generated. Generators only write
text that matches a spec; they never choose labels.

Usage: python scripts/make_grid.py [--out grid.jsonl] [--n 180] [--seed 2026]
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

ROUTE_COUNTS = {
    "report_received": 26,
    "appointment": 26,
    "prescription_request": 22,
    "insurer": 24,
    "referral_in": 18,
    "certificate_request": 18,
    "billing": 16,
    "spam_marketing": 14,
    "other": 16,
}

ASSIGNEE = {
    "report_received": "doctor",
    "appointment": "mpa",
    "prescription_request": "mpa",
    "insurer": "admin",
    "referral_in": "mpa",
    "certificate_request": "mpa",
    "billing": "admin",
    "spam_marketing": "admin",
    "other": "mpa",
}

# Slots per route for safety cases. acute_* -> safety_flag true; medical_trap -> false.
SAFETY_SLOTS = {
    "acute_explicit": {"other": 4, "appointment": 3},
    "acute_incidental": {
        "appointment": 2,
        "prescription_request": 3,
        "certificate_request": 2,
        "billing": 1,
        "other": 1,
    },
    "medical_trap": {
        "report_received": 4,
        "appointment": 3,
        "prescription_request": 2,
        "insurer": 2,
        "certificate_request": 1,
        "other": 2,
    },
}

LANG_COUNTS = {"de": 99, "fr": 45, "it": 27, "en": 9}

DEADLINE_WEIGHTS = {
    "appointment": {"today": 20, "this_week": 40, "none": 40},
    "prescription_request": {"today": 20, "this_week": 55, "none": 25},
    "insurer": {"today": 10, "this_week": 45, "none": 45},
    "referral_in": {"today": 10, "this_week": 30, "none": 60},
    "certificate_request": {"today": 25, "this_week": 50, "none": 25},
    "billing": {"today": 5, "this_week": 45, "none": 50},
    "spam_marketing": {"none": 100},
    "other": {"today": 10, "this_week": 30, "none": 60},
}

# Share of "none" deadlines that still carry an explicit date more than 7 days out.
FAR_DATE_SHARE = {"insurer": 0.6, "billing": 0.5, "referral_in": 0.2, "other": 0.2}

SENDER_TYPES = {
    "report_received": {"lab": 45, "hospital": 30, "specialist": 20, "radiology": 5},
    "appointment": {"patient": 75, "relative": 15, "specialist_office": 10},
    "prescription_request": {
        "patient": 60,
        "relative": 15,
        "pharmacy": 15,
        "nursing_home": 10,
    },
    "insurer": {
        "health_insurer": 45,
        "iv_office": 20,
        "accident_insurer": 15,
        "daily_allowance_insurer": 20,
    },
    "referral_in": {"referring_physician": 55, "hospital": 30, "specialist": 15},
    "certificate_request": {"patient": 65, "employer": 20, "school": 10, "relative": 5},
    "billing": {
        "supplier": 35,
        "patient": 35,
        "health_insurer": 20,
        "billing_service": 10,
    },
    "spam_marketing": {"pharma": 50, "vendor": 35, "event_organizer": 15},
    "other": {
        "patient": 45,
        "authority": 20,
        "relative": 15,
        "employer": 10,
        "colleague": 10,
    },
}

PERSONAL = {"patient", "relative"}

CHANNELS = {
    "personal": {"email": 60, "web_form": 35, "fax": 5},
    "lab": {"hin_mail": 60, "fax": 25, "email": 15},
    "radiology": {"hin_mail": 60, "fax": 25, "email": 15},
    "hospital": {"hin_mail": 60, "fax": 30, "email": 10},
    "specialist": {"hin_mail": 55, "fax": 35, "email": 10},
    "specialist_office": {"hin_mail": 40, "email": 40, "fax": 20},
    "referring_physician": {"hin_mail": 55, "fax": 35, "email": 10},
    "health_insurer": {"fax": 35, "hin_mail": 30, "email": 35},
    "iv_office": {"fax": 40, "hin_mail": 30, "email": 30},
    "accident_insurer": {"fax": 35, "hin_mail": 30, "email": 35},
    "daily_allowance_insurer": {"fax": 35, "hin_mail": 25, "email": 40},
    "pharmacy": {"fax": 40, "hin_mail": 40, "email": 20},
    "nursing_home": {"fax": 40, "hin_mail": 30, "email": 30},
    "employer": {"email": 70, "fax": 15, "web_form": 15},
    "school": {"email": 80, "web_form": 20},
    "supplier": {"email": 80, "fax": 20},
    "billing_service": {"email": 70, "fax": 30},
    "pharma": {"email": 100},
    "vendor": {"email": 100},
    "event_organizer": {"email": 100},
    "authority": {"email": 50, "fax": 30, "hin_mail": 20},
    "colleague": {"hin_mail": 70, "email": 30},
}

FORMALITY = {
    "personal": {"informal": 40, "neutral": 40, "formal": 20},
    "institution": {"formal": 80, "neutral": 20},
}

WRITING_LEVEL = {
    "personal": {"clean": 35, "typos": 30, "non_native": 20, "dialect": 15},
    "institution": {"clean": 85, "typos": 15},
}

MIXED_N = 18
ABSTAIN_N = 9
MIXED_ROUTES = [
    "appointment",
    "prescription_request",
    "certificate_request",
    "billing",
    "other",
    "referral_in",
]
ABSTAIN_ROUTES = [
    "appointment",
    "prescription_request",
    "certificate_request",
    "billing",
    "other",
    "insurer",
]
SECONDARY = {
    "appointment": ["prescription_request", "certificate_request", "other"],
    "prescription_request": ["appointment", "certificate_request", "billing"],
    "certificate_request": ["appointment", "prescription_request", "insurer"],
    "billing": ["appointment", "other", "insurer"],
    "other": ["appointment", "prescription_request", "billing"],
    "referral_in": ["appointment", "report_received"],
    "insurer": ["billing", "certificate_request", "other"],
}

AHV_ROUTES = {
    "insurer": 0.6,
    "certificate_request": 0.1,
    "billing": 0.1,
    "report_received": 0.1,
    "referral_in": 0.15,
}

START = date(2026, 10, 1)
END = date(2026, 10, 16)
WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def pick(rng: random.Random, weights: dict[str, int]) -> str:
    keys = list(weights)
    return rng.choices(keys, weights=[weights[k] for k in keys])[0]


def ean13_check(digits12: str) -> int:
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits12))
    return (10 - total % 10) % 10


def invalid_ahv(rng: random.Random) -> str:
    body = "756" + "".join(str(rng.randint(0, 9)) for _ in range(9))
    good = ean13_check(body)
    bad = (good + rng.randint(1, 9)) % 10
    d = body + str(bad)
    return f"{d[0:3]}.{d[3:7]}.{d[7:11]}.{d[11:13]}"


def received_at(rng: random.Random, channel: str) -> datetime:
    days = [START + timedelta(days=i) for i in range((END - START).days + 1)]
    weekdays = [d for d in days if d.weekday() < 5]
    day = rng.choice(weekdays if rng.random() < 0.9 else days)
    hour = (
        rng.randint(6, 22) if channel in {"email", "web_form"} else rng.randint(7, 18)
    )
    return datetime(day.year, day.month, day.day, hour, rng.randint(0, 59))


def build(n_seed: int) -> list[dict]:
    rng = random.Random(n_seed)

    routes: list[str] = [r for r, c in ROUTE_COUNTS.items() for _ in range(c)]
    specs = [{"route": r} for r in routes]

    for case, per_route in SAFETY_SLOTS.items():
        for route, count in per_route.items():
            free = [s for s in specs if s["route"] == route and "safety_case" not in s]
            for s in rng.sample(free, count):
                s["safety_case"] = case
    for s in specs:
        s.setdefault("safety_case", "none")

    pool = [
        s for s in specs if s["route"] in ABSTAIN_ROUTES and s["safety_case"] == "none"
    ]
    for s in rng.sample(pool, ABSTAIN_N):
        s["abstain"] = True
    pool = [s for s in specs if s["route"] in MIXED_ROUTES and not s.get("abstain")]
    for s in rng.sample(pool, MIXED_N):
        s["mixed_topic"] = True

    langs = [l for l, c in LANG_COUNTS.items() for _ in range(c)]
    rng.shuffle(langs)
    rng.shuffle(specs)
    for s, lang in zip(specs, langs):
        s["language"] = lang

    out = []
    for i, s in enumerate(specs, start=1):
        route = s["route"]
        safety_case = s["safety_case"]
        safety = safety_case in {"acute_explicit", "acute_incidental"}
        sender_weights = SENDER_TYPES[route]
        if safety_case in {"acute_explicit", "acute_incidental"}:
            sender_weights = {"patient": 70, "relative": 30}
        sender_type = pick(rng, sender_weights)
        kind = "personal" if sender_type in PERSONAL else "institution"
        channel = pick(rng, CHANNELS["personal" if kind == "personal" else sender_type])
        recv = received_at(rng, channel)

        deadline_date = None
        if route == "report_received" or safety:
            deadline = "today"
        else:
            deadline = pick(rng, DEADLINE_WEIGHTS[route])
            if deadline == "today":
                deadline_date = recv.date() + timedelta(days=rng.randint(0, 1))
            elif deadline == "this_week":
                deadline_date = recv.date() + timedelta(days=rng.randint(2, 7))
            elif rng.random() < FAR_DATE_SHARE.get(route, 0.0):
                deadline_date = recv.date() + timedelta(days=rng.randint(10, 35))

        mixed = bool(s.get("mixed_topic"))
        abstain = bool(s.get("abstain"))
        secondary = rng.choice(SECONDARY[route]) if (mixed or abstain) else None

        ahv = None
        if (
            route in AHV_ROUTES
            and sender_type not in {"supplier", "billing_service"}
            and rng.random() < AHV_ROUTES[route]
        ):
            ahv = invalid_ahv(rng)

        spec = {
            "message_id": f"syn-{i:03d}",
            "language": s["language"],
            "channel": channel,
            "sender_type": sender_type,
            "received_at": recv.strftime("%Y-%m-%dT%H:%M"),
            "received_weekday": WEEKDAYS[recv.weekday()],
            "formality": pick(rng, FORMALITY[kind]),
            "writing_level": pick(rng, WRITING_LEVEL[kind]),
            "mixed_topic": mixed,
            "secondary_route": secondary if mixed else None,
            "abstain_alternative_route": secondary if abstain else None,
            "safety_case": safety_case,
            "spam_fake_urgency": route == "spam_marketing" and rng.random() < 0.35,
            "include_birth_date": route != "spam_marketing"
            and sender_type not in {"supplier", "billing_service"}
            and rng.random() < 0.7,
            "ahv_number": ahv,
            "label": {
                "route": route,
                "deadline": deadline,
                "deadline_date": deadline_date.isoformat() if deadline_date else None,
                "deadline_weekday": WEEKDAYS[deadline_date.weekday()]
                if deadline_date
                else None,
                "assignee": "doctor" if safety else ASSIGNEE[route],
                "safety_flag": safety,
                "abstain": abstain,
            },
        }
        out.append(spec)

    assign_generators(out)
    return out


def balance_keys(spec: dict) -> list[tuple[str, object]]:
    return [
        ("route", spec["label"]["route"]),
        ("safety_case", spec["safety_case"]),
        ("abstain", spec["label"]["abstain"]),
        ("mixed", spec["mixed_topic"]),
        ("language", spec["language"]),
        ("writing_level", spec["writing_level"]),
        ("channel", spec["channel"]),
        ("deadline", spec["label"]["deadline"]),
        ("formality", spec["formality"]),
    ]


def assign_generators(specs: list[dict]) -> None:
    """Greedy split into two equal halves, balanced over every grid variable."""
    gens = ("claude", "codex")
    half = len(specs) // 2
    counts = {g: {} for g in gens}
    sizes = {g: 0 for g in gens}
    order = sorted(
        specs,
        key=lambda x: (
            x["label"]["route"],
            x["safety_case"],
            x["label"]["abstain"],
            x["mixed_topic"],
            x["message_id"],
        ),
    )
    for j, spec in enumerate(order):
        keys = balance_keys(spec)
        open_gens = [g for g in gens if sizes[g] < half + (len(specs) % 2)]
        score = {g: sum(counts[g].get(k, 0) for k in keys) for g in open_gens}
        best = min(score.values())
        tied = [g for g in open_gens if score[g] == best]
        g = tied[j % len(tied)]
        spec["generator"] = g
        sizes[g] += 1
        for k in keys:
            counts[g][k] = counts[g].get(k, 0) + 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="grid.jsonl")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    specs = build(args.seed)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for spec in specs:
            f.write(json.dumps(spec, ensure_ascii=False) + "\n")
    print(f"wrote {len(specs)} specs to {path}")


if __name__ == "__main__":
    main()
