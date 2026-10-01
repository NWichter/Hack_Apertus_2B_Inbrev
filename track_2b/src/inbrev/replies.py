"""Fixed reply templates for administrative routes. No model text goes out to patients."""

from __future__ import annotations

TEMPLATES = {
    "appointment": {
        "de": "Guten Tag{name}\n\nVielen Dank für Ihre Nachricht zu Ihrem Termin. Wir melden uns so bald wie möglich mit einem Vorschlag.\n\nFreundliche Grüsse\nIhr Praxisteam",
        "fr": "Bonjour{name}\n\nMerci pour votre message concernant votre rendez-vous. Nous vous recontactons au plus vite avec une proposition.\n\nMeilleures salutations\nVotre cabinet",
        "it": "Buongiorno{name}\n\nGrazie per il suo messaggio riguardo all'appuntamento. La ricontatteremo al più presto con una proposta.\n\nCordiali saluti\nIl suo studio medico",
        "en": "Hello{name}\n\nThank you for your message about your appointment. We will get back to you with a proposal as soon as possible.\n\nKind regards\nYour practice team",
    },
    "prescription_request": {
        "de": "Guten Tag{name}\n\nIhre Rezeptanfrage{item} ist bei uns eingegangen. Die Ärztin prüft sie; wir melden uns, sobald das Rezept bereit ist.\n\nFreundliche Grüsse\nIhr Praxisteam",
        "fr": "Bonjour{name}\n\nVotre demande d'ordonnance{item} nous est bien parvenue. Le médecin la vérifie; nous vous informons dès qu'elle est prête.\n\nMeilleures salutations\nVotre cabinet",
        "it": "Buongiorno{name}\n\nAbbiamo ricevuto la sua richiesta di ricetta{item}. Il medico la verifica; la informeremo quando sarà pronta.\n\nCordiali saluti\nIl suo studio medico",
        "en": "Hello{name}\n\nWe have received your prescription request{item}. The doctor will review it; we will let you know when it is ready.\n\nKind regards\nYour practice team",
    },
    "certificate_request": {
        "de": "Guten Tag{name}\n\nIhre Anfrage für ein Zeugnis ist bei uns eingegangen. Wir melden uns, falls wir weitere Angaben brauchen.\n\nFreundliche Grüsse\nIhr Praxisteam",
        "fr": "Bonjour{name}\n\nVotre demande de certificat nous est bien parvenue. Nous vous contactons si nous avons besoin d'informations supplémentaires.\n\nMeilleures salutations\nVotre cabinet",
        "it": "Buongiorno{name}\n\nAbbiamo ricevuto la sua richiesta di certificato. La contatteremo se servono altre informazioni.\n\nCordiali saluti\nIl suo studio medico",
        "en": "Hello{name}\n\nWe have received your certificate request. We will contact you if we need more information.\n\nKind regards\nYour practice team",
    },
    "billing": {
        "de": "Guten Tag\n\nVielen Dank für Ihre Nachricht{item}. Unsere Administration prüft sie und meldet sich bei Ihnen.\n\nFreundliche Grüsse\nIhr Praxisteam",
        "fr": "Bonjour\n\nMerci pour votre message{item}. Notre administration le vérifie et revient vers vous.\n\nMeilleures salutations\nVotre cabinet",
        "it": "Buongiorno\n\nGrazie per il suo messaggio{item}. La nostra amministrazione lo verifica e la ricontatterà.\n\nCordiali saluti\nIl suo studio medico",
        "en": "Hello\n\nThank you for your message{item}. Our administration will review it and get back to you.\n\nKind regards\nYour practice team",
    },
}

ITEM_FIELD = {"prescription_request": "medication", "billing": "invoice_number"}


def reply_draft(
    route: str, language: str | None, patient: dict, fields: dict
) -> str | None:
    by_lang = TEMPLATES.get(route)
    if not by_lang:
        return None
    tpl = by_lang.get(language or "de", by_lang["de"])
    name = f" {patient['name']}" if patient.get("name") else ""
    item_value = fields.get(ITEM_FIELD.get(route, ""), None)
    item = f" ({item_value})" if item_value else ""
    return tpl.format(name=name, item=item)
