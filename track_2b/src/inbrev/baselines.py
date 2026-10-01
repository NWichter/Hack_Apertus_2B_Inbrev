"""Non-LLM baselines: majority class, keyword rules, TF-IDF + logistic regression."""

from __future__ import annotations

import re
from collections import Counter

from . import taxonomy
from .extract import dates_in, deadline_from_date, parse_received, source_text
from .pipeline import DEFAULT_RECEIVED
from .safety import lexical_flag

KEYWORDS = {
    "spam_marketing": r"webinar|newsletter|angebot|rabatt|aktion|offre|promotion|sconto|offerta|discount|abmelden|désinscri|disiscri|unsubscribe|jetzt anmelden|inscrivez|iscriviti",
    "billing": r"rechnung|mahnung|zahlung|betrag|facture|rappel de paiement|paiement|fattura|sollecito|pagamento|invoice|payment|chf\s?\d",
    "insurer": r"kostengutsprache|versicher|iv-stelle|taggeld|krankenkasse|caisse-maladie|assurance|office ai|assicura|cassa malati|ufficio ai|insurer|insurance",
    "referral_in": r"zuweisung|überweis|zuweisen|wir weisen|adress(e|ons)|nous vous adressons|invio|inviamo|vi invio|referral|refer",
    "certificate_request": r"zeugnis|arbeitsunfähig|bestätigung|attest|certificat|certificato|arbeitgeber|sick note|certificate",
    "prescription_request": r"rezept|medikament|tabletten|ordonnance|médicament|ricetta|farmac|prescription|apotheke|pharmacie",
    "report_received": r"befund|laborbericht|austrittsbericht|bericht|résultat|rapport|lettre de sortie|referto|rapporto|lettera di dimissione|report|results",
    "appointment": r"termin|rendez-vous|rdv|appuntamento|appointment|verschieben|absagen|annuler|spostare|disdire",
}
_KW = {r: re.compile(p, re.IGNORECASE) for r, p in KEYWORDS.items()}


def _result(message: dict, route: str, deadline: str, safety: bool) -> dict:
    if safety:
        deadline = "today"
    return {
        "message_id": message["message_id"],
        "route": route,
        "deadline": deadline,
        "deadline_date": None,
        "assignee": taxonomy.assignee_for(route, safety),
        "safety_flag": safety,
        "abstain": False,
        "confidence": 1.0,
        "patient": {k: None for k in taxonomy.PATIENT_KEYS},
        "fields": {},
        "evidence": [],
    }


def majority(gold: list[dict]) -> list[dict]:
    route = Counter(g["label"]["route"] for g in gold).most_common(1)[0][0]
    deadline = Counter(g["label"]["deadline"] for g in gold).most_common(1)[0][0]
    return [_result(g, route, deadline, False) for g in gold]


def keyword_route(text: str) -> str:
    counts = {r: len(rx.findall(text)) for r, rx in _KW.items()}
    best = max(counts, key=counts.get)
    return best if counts[best] else "other"


def rule_deadline(text: str, route: str, received_at: str | None) -> str:
    if route == "report_received":
        return "today"
    received = (parse_received(received_at) or DEFAULT_RECEIVED).date()
    future = sorted(d for d in dates_in(text) if (d - received).days >= 0)
    return deadline_from_date(future[0], received) if future else "none"


def keywords(gold: list[dict]) -> list[dict]:
    out = []
    for g in gold:
        text = source_text(g.get("subject"), g.get("body"))
        route = keyword_route(text)
        out.append(
            _result(
                g,
                route,
                rule_deadline(text, route, g.get("received_at")),
                lexical_flag(text),
            )
        )
    return out


def tfidf_logreg(gold: list[dict], folds: int = 5, seed: int = 2026) -> list[dict]:
    """Cross-validated predictions: each message is predicted by a model that never saw it."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.pipeline import make_pipeline

    texts = [source_text(g.get("subject"), g.get("body")) for g in gold]
    targets = {
        "route": [g["label"]["route"] for g in gold],
        "deadline": [g["label"]["deadline"] for g in gold],
        "safety": [str(g["label"]["safety_flag"]) for g in gold],
    }
    preds: dict[str, list] = {k: [None] * len(gold) for k in targets}
    for key, y in targets.items():
        if min(Counter(y).values()) < 2:
            preds[key] = [Counter(y).most_common(1)[0][0]] * len(gold)
            continue
        n_splits = min(folds, min(Counter(y).values()))
        skf = StratifiedKFold(
            n_splits=max(2, n_splits), shuffle=True, random_state=seed
        )
        for train, test in skf.split(texts, y):
            model = make_pipeline(
                TfidfVectorizer(
                    analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True, min_df=2
                ),
                LogisticRegression(max_iter=2000, class_weight="balanced", C=5.0),
            )
            model.fit([texts[i] for i in train], [y[i] for i in train])
            for i, p in zip(test, model.predict([texts[i] for i in test])):
                preds[key][i] = p
    return [
        _result(
            g, preds["route"][i], preds["deadline"][i], preds["safety"][i] == "True"
        )
        for i, g in enumerate(gold)
    ]


BASELINES = {"majority": majority, "keywords": keywords, "tfidf_logreg": tfidf_logreg}
