from __future__ import annotations

import json
import os
from datetime import datetime

from . import taxonomy
from .extract import parse_received

PROMPT_VERSIONS = ("p2", "p3")
PROMPT_VERSION = os.getenv("INBREV_PROMPT", "p3")
if PROMPT_VERSION not in PROMPT_VERSIONS:
    raise ValueError(f"INBREV_PROMPT must be one of {PROMPT_VERSIONS}")

ROUTE_HINTS = {
    "report_received": "a lab result, imaging report, discharge letter or specialist report ARRIVES for the doctor (Befund, Laborbericht, Austrittsbericht; résultats, rapport, lettre de sortie; referto, rapporto)",
    "appointment": "book, move or cancel an appointment (Termin; rendez-vous; appuntamento)",
    "prescription_request": "repeat prescription or medication request, also from a pharmacy or nursing home (Rezept; ordonnance; ricetta)",
    "insurer": "health, accident, disability (IV/AI) or daily-allowance insurer asks for something: cost approval (Kostengutsprache), medical report, form, query",
    "referral_in": "another physician or hospital refers a patient TO this practice (Zuweisung, Überweisung; adressage; invio)",
    "certificate_request": "sick note (Arbeitsunfähigkeitszeugnis, Arztzeugnis; certificat médical; certificato medico) or another confirmation, also when an employer or school asks",
    "billing": "invoice, payment reminder (Mahnung), billing question, from suppliers, patients or insurers",
    "spam_marketing": "advertising, newsletter, pharma marketing, webinar, software or product offer",
    "other": "anything else: records request, authority letter, general question, or a person describing how they feel without another request",
}

# p3: only the route boundaries of "other" change; developed on a separate dev set
# (track_2b/evidence/prompt-p3/), never on the test sets.
ROUTE_HINTS_P3 = {
    **ROUTE_HINTS,
    "certificate_request": "someone asks the practice to WRITE a sick note (Arbeitsunfähigkeitszeugnis, Arztzeugnis; certificat médical; certificato medico) or another confirmation, also an employer or school",
    "other": "anything else, for example: a patient or another practice asks for a COPY or TRANSFER of the medical record (Krankengeschichte, Patientenakte, dossier médical, cartella clinica, medical records); a whole patient file sent over because the patient changes doctor; an authority letter; a general question (vaccination advice, how a relative is doing); a patient asking for a referral to a therapist or specialist elsewhere; a person only describing symptoms or asking what to do",
}

RULES_P3 = """
- A request for a copy or transfer of medical records is "other", not "certificate_request", "report_received" or "referral_in". "certificate_request" needs a request for a certificate, attestation or confirmation that the doctor has to write.
- "referral_in" only when a physician or hospital sends a patient TO this practice. A patient asking this practice for a referral elsewhere is "other".
- A person who describes symptoms and asks what to do, without asking for an appointment, prescription or certificate, is "other"; the safety rules below still apply."""

SYSTEM_TEMPLATE = """You sort the inbox of a Swiss general practice. Messages are in German, French, Italian or English.
Your job is ADMINISTRATIVE: decide the handling route, the administrative deadline and whether a human must look at the message at once. You never judge clinical severity and never give medical advice.

ROUTES (pick exactly one, the MAIN request):
{routes}

RULES
- Several requests in one message: choose the main one (comes first, takes most space, or is named as the main reason).
- An insurer asking the practice for a report or form is "insurer", not "report_received". A physician referring a patient who also wants a first appointment is "referral_in". A daily-allowance insurer asking for a sick-leave confirmation is "insurer".{extra_rules}
- safety_flag is true if the sender describes possibly acute symptoms that are happening NOW, even in passing (e.g. "PS: since this morning my chest feels tight"): chest pain or pressure, breathing problems, fainting, sudden weakness, numbness or speech problems, heavy bleeding, severe allergic reaction, seizure, suicidal thoughts, high fever in a small child. It is false for past or treated events, stable chronic conditions, family history, lab values in a report, an insurer asking about an old event, or a sender stating there is no emergency.
- deadline_date: the date by which the practice must act, as YYYY-MM-DD, computed from the received date (e.g. "morgen", "bis Freitag", "d'ici jeudi", "entro venerdì"). null if the text sets no date for the practice.
- deadline: only from a date or time expression in the text (quote it in deadline_quote). Without such an expression the deadline is "none". "today" if action is needed today or tomorrow, "this_week" if within 2 to 7 days, "none" if there is no deadline or it is more than 7 days away. A report arriving for the doctor is always "today". If safety_flag is true, deadline is "today". Urgency in advertising ("nur heute") is "none".
- ambiguous: true only if a careful practice assistant could not decide between two routes from the text alone.
- route_quote is required: the words that show the request (the subject line counts).
- Every *_quote and every quote in "extracted" is copied EXACTLY from the message: 2 to 15 consecutive words, same spelling, same capital letters and umlauts, same typos, no translation, no paraphrase, no HTML escaping. Use null when there is nothing to quote.
- extracted: values that appear in the message. Allowed fields: {fields}. Dates as YYYY-MM-DD, names as "First Last", AHV numbers (756.xxxx.xxxx.xx) as patient.ahv_number, fields.appointment_action as book, move or cancel. List only fields that have a value in the text; never write null or empty values, never list a field twice. An empty list [] is fine.

OUTPUT: one compact JSON object with these keys in this order:
{{"language":"<de|fr|it|en>","route_quote":"<quote>","route":"<route>","ambiguous":<true|false>,"safety_quote":<"quote" or null>,"safety_flag":<true|false>,"deadline_quote":<"quote" or null>,"deadline_date":<"YYYY-MM-DD" or null>,"deadline":"<today|this_week|none>","extracted":[{{"field":"<field>","value":"<value>","quote":"<quote>"}}]}}"""

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def extractable_fields() -> list[str]:
    return [f"patient.{k}" for k in taxonomy.PATIENT_KEYS] + [
        f"fields.{f}" for f in taxonomy.all_fields()
    ]


def system_prompt(version: str | None = None) -> str:
    version = version or PROMPT_VERSION
    hints = ROUTE_HINTS_P3 if version == "p3" else ROUTE_HINTS
    routes = "\n".join(f"- {r}: {hints[r]}" for r in taxonomy.routes())
    text = SYSTEM_TEMPLATE.format(
        routes=routes,
        fields=", ".join(extractable_fields()),
        extra_rules=RULES_P3 if version == "p3" else "",
    )
    if VARIANT == "safety_first":
        old = '{"language":"<de|fr|it|en>","route_quote":"<quote>","route":"<route>","ambiguous":<true|false>,"safety_quote":<"quote" or null>,"safety_flag":<true|false>,'
        new = '{"language":"<de|fr|it|en>","safety_quote":<"quote" or null>,"safety_flag":<true|false>,"route_quote":"<quote>","route":"<route>","ambiguous":<true|false>,'
        if old not in text:
            raise RuntimeError("safety_first: output line not found")
        text = text.replace(old, new)
    return text


def user_prompt(message: dict, default_received: datetime) -> str:
    received = parse_received(message.get("received_at")) or default_received
    lines = [
        f"Received: {WEEKDAYS[received.weekday()]}, {received:%Y-%m-%d %H:%M}",
        f"Channel: {message.get('channel') or 'email'}",
        f"From: {message.get('sender') or ''}",
        f"Subject: {message.get('subject') or ''}",
        "",
        message.get("body") or "",
    ]
    return "\n".join(lines)


def output_schema() -> dict:
    schema = _output_schema()
    if VARIANT == "safety_first":
        schema["required"] = list(SAFETY_FIRST_ORDER)
        schema["properties"] = {k: schema["properties"][k] for k in SAFETY_FIRST_ORDER}
    return schema


def _output_schema() -> dict:
    nullable_str = {"type": ["string", "null"]}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "language",
            "route_quote",
            "route",
            "ambiguous",
            "safety_quote",
            "safety_flag",
            "deadline_quote",
            "deadline_date",
            "deadline",
            "extracted",
        ],
        "properties": {
            "language": {"enum": taxonomy.LANGUAGES},
            "route_quote": {"type": "string"},
            "route": {"enum": taxonomy.routes()},
            "ambiguous": {"type": "boolean"},
            "safety_quote": nullable_str,
            "safety_flag": {"type": "boolean"},
            "deadline_quote": nullable_str,
            "deadline_date": {
                "anyOf": [
                    {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                    {"type": "null"},
                ]
            },
            "deadline": {"enum": taxonomy.DEADLINES},
            "extracted": {
                "type": "array",
                "maxItems": 14,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["field", "value", "quote"],
                    "properties": {
                        "field": {"enum": extractable_fields()},
                        "value": {"type": "string"},
                        "quote": {"type": "string"},
                    },
                },
            },
        },
    }


# Experimental variants for the gap study (13 Oct 2026), chosen on the dev split only:
#   safety_first: the schema asks for safety_quote/safety_flag before the route.
#   fewshot: four short fictional examples (written for this purpose, not from any test or dev set).
VARIANT = os.getenv("INBREV_PROMPT_VARIANT", "")

SAFETY_FIRST_ORDER = [
    "language",
    "safety_quote",
    "safety_flag",
    "route_quote",
    "route",
    "ambiguous",
    "deadline_quote",
    "deadline_date",
    "deadline",
    "extracted",
]

FEWSHOT = [
    (
        "Received: Tuesday, 2026-03-10 08:12\nChannel: email\nFrom: Petra Imhof <p.imhof@mail.example>\n"
        "Subject: Rezept Pantoprazol\n\nGuten Tag, könnten Sie mir das Pantoprazol 20 mg wieder verschreiben? "
        "Ich hole es in der Apotheke am Platz ab. Seit gestern Abend habe ich übrigens Druck auf der Brust, "
        "wird schon nichts sein. Gruss P. Imhof",
        '{"language":"de","route_quote":"könnten Sie mir das Pantoprazol 20 mg wieder verschreiben","route":"prescription_request",'
        '"ambiguous":false,"safety_quote":"Seit gestern Abend habe ich übrigens Druck auf der Brust","safety_flag":true,'
        '"deadline_quote":null,"deadline_date":null,"deadline":"today","extracted":[{"field":"fields.medication","value":"Pantoprazol 20 mg","quote":"Pantoprazol 20 mg"}]}',
    ),
    (
        "Received: Monday, 2026-03-09 14:30\nChannel: web_form\nFrom: Formular\nSubject: Anfrage\n\n"
        "Nom: Luc Morand\nDemande: Je déménage à Neuchâtel. Pouvez-vous envoyer mon dossier médical complet "
        "au cabinet du Dr Favre ? Merci.",
        '{"language":"fr","route_quote":"Pouvez-vous envoyer mon dossier médical complet","route":"other","ambiguous":false,'
        '"safety_quote":null,"safety_flag":false,"deadline_quote":null,"deadline_date":null,"deadline":"none",'
        '"extracted":[{"field":"patient.name","value":"Luc Morand","quote":"Luc Morand"}]}',
    ),
    (
        "Received: Wednesday, 2026-03-11 10:05\nChannel: fax\nFrom: Assicurazione Esempio SA\n"
        "Subject: Richiesta rapporto medico\n\nVi chiediamo un rapporto medico sul signor Carlo Neri per la "
        "valutazione del caso. Il paziente ha avuto un infarto nel 2019, oggi stabile. Termine: 20.03.2026.",
        '{"language":"it","route_quote":"Vi chiediamo un rapporto medico","route":"insurer","ambiguous":false,'
        '"safety_quote":null,"safety_flag":false,"deadline_quote":"Termine: 20.03.2026","deadline_date":"2026-03-20",'
        '"deadline":"none","extracted":[{"field":"patient.name","value":"Carlo Neri","quote":"signor Carlo Neri"}]}',
    ),
    (
        "Received: Thursday, 2026-03-12 07:50\nChannel: email\nFrom: Hans Gerber <h.gerber@mail.example>\n"
        "Subject: Termin verschieben\n\nGrüezi, ich muss meinen Termin vom Freitag leider verschieben. "
        "Geht auch nächste Woche am Dienstag? Merci, H. Gerber",
        '{"language":"de","route_quote":"ich muss meinen Termin vom Freitag leider verschieben","route":"appointment",'
        '"ambiguous":false,"safety_quote":null,"safety_flag":false,"deadline_quote":null,"deadline_date":null,'
        '"deadline":"none","extracted":[{"field":"fields.appointment_action","value":"move","quote":"Termin vom Freitag leider verschieben"}]}',
    ),
]


def messages_for(message: dict, default_received: datetime) -> list[dict]:
    msgs = [{"role": "system", "content": system_prompt()}]
    if VARIANT == "fewshot":
        for user, answer in FEWSHOT:
            msgs += [
                {"role": "user", "content": user},
                {"role": "assistant", "content": answer},
            ]
    msgs.append({"role": "user", "content": user_prompt(message, default_received)})
    return msgs


SYMPTOM_SYSTEM = """You read one message sent to a Swiss general practice. You do NOT judge severity and give no advice.
Answer one narrow question: does the message say that a person (the sender, a patient, a relative) has a health complaint that is happening now or started recently (today, since yesterday, in the last days, "last night ... but better now")? Health complaints include pain anywhere, fever, breathing problems, dizziness, fainting, bleeding, vomiting, weakness, numbness, confusion, rash or swelling, low mood or thoughts of self-harm. Count it even if it is mentioned only in passing next to an administrative request, and even if the sender says it is probably nothing.
Answer false for: only past and finished events, stable chronic conditions under control, family history, diagnoses or values listed in a report or form, an insurer or authority asking about an old event, or a text without any complaint.
symptom_quote: 2 to 15 words copied exactly from the message that show the complaint, or null.
OUTPUT: one JSON object {"symptom_quote": <"quote" or null>, "current_symptom": <true|false>}"""


def symptom_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["symptom_quote", "current_symptom"],
        "properties": {
            "symptom_quote": {"type": ["string", "null"]},
            "current_symptom": {"type": "boolean"},
        },
    }


def symptom_messages_for(message: dict, default_received: datetime) -> list[dict]:
    return [
        {"role": "system", "content": SYMPTOM_SYSTEM},
        {"role": "user", "content": user_prompt(message, default_received)},
    ]


def schema_json() -> str:
    return json.dumps(output_schema(), ensure_ascii=False)
