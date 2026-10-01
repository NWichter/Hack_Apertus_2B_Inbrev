from __future__ import annotations

from functools import lru_cache

import yaml

from .config import REPO_DATA

PATIENT_KEYS = ["name", "birth_date", "insurance_number", "ahv_number", "insurer"]
DEADLINES = ["today", "this_week", "none"]
ASSIGNEES = ["mpa", "doctor", "admin"]
LANGUAGES = ["de", "fr", "it", "en"]


@lru_cache
def load() -> dict:
    return yaml.safe_load((REPO_DATA / "taxonomy.yaml").read_text(encoding="utf-8"))


def routes() -> list[str]:
    return list(load()["routes"])


def assignee_for(route: str, safety_flag: bool = False) -> str:
    if safety_flag:
        return "doctor"
    return load()["routes"][route]["assignee"]


def route_fields(route: str) -> list[str]:
    return list(load()["routes"][route].get("fields") or [])


def all_fields() -> list[str]:
    seen: list[str] = []
    for r in routes():
        for f in route_fields(r):
            if f not in seen:
                seen.append(f)
    return seen
