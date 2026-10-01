"""Lexical safety net: flags wording that may describe acute symptoms.

High recall on purpose. It never ranks severity; a hit only means
"a human looks at this now". Used as a baseline and as an OR-guard next to the model.
"""

from __future__ import annotations

import re

PATTERNS = {
    "de": [
        r"brust\w*\s*schmerz",
        r"schmerz\w* (in|auf) der brust",
        r"druck auf der brust",
        r"engegef(ü|ue)hl",
        r"atemnot",
        r"keine luft",
        r"luft (fehlt|bekomm)",
        r"fehlt (ihm|ihr|mir) (die )?luft",
        r"kurzatmig",
        r"atmet schwer",
        r"bewusstlos",
        r"ohnmacht",
        r"kollabiert",
        r"l(ä|ae)hmung",
        r"gel(ä|ae)hmt",
        r"h(ä|ae)ngende[sr]? (mund|gesicht)",
        r"sprachst(ö|oe)rung",
        r"kann nicht (mehr )?(richtig )?sprechen",
        r"spricht (verwaschen|undeutlich)",
        r"starke blutung",
        r"blutet (stark|seit)",
        r"blut erbroch",
        r"suizid",
        r"selbstmord",
        r"(mir|sich) (etwas|was) an(zu)?tun",
        r"nicht mehr leben",
        r"lebensm(ü|ue)de",
        r"krampfanfall",
        r"krampft",
        r"allergische reaktion",
        r"zunge (schwillt|geschwollen)",
        r"hohes fieber",
        r"fieber (über|von) (39|40|41)",
        r"(39|40|41)[.,]\d? ?°",
        r"starke kopfschmerzen.{0,30}pl(ö|oe)tzlich",
        r"pl(ö|oe)tzlich\w* .{0,40}(schwach|taub|sehst(ö|oe)r|kopfschmerz)",
        r"notfall",
    ],
    "fr": [
        r"douleur\w* (dans la|à la|thoracique|à la poitrine)",
        r"oppression",
        r"mal à respirer",
        r"du mal à respirer",
        r"essouffl",
        r"souffle court",
        r"perte de connaissance",
        r"évanoui",
        r"paralys",
        r"trouble\w* de la parole",
        r"n'arrive (plus )?à parler",
        r"saign\w* (abondamment|beaucoup|fort)",
        r"hémorragie",
        r"suicid",
        r"en finir",
        r"plus envie de vivre",
        r"convulsion",
        r"crise d'épilepsie",
        r"réaction allergique",
        r"gonflement de la (langue|gorge)",
        r"forte fièvre",
        r"fièvre (de|à) (39|40|41)",
        r"urgence",
    ],
    "it": [
        r"dolor\w* (al|nel) petto",
        r"dolore toracico",
        r"oppressione",
        r"fiato corto",
        r"mancanza di (fiato|respiro)",
        r"fatica a respirare",
        r"non riesc\w* a respirare",
        r"svenut",
        r"perso conoscenza",
        r"paralisi",
        r"non riesce a parlare",
        r"parla male all'improvviso",
        r"sanguin\w* (molto|tanto|forte)",
        r"emorragia",
        r"suicid",
        r"farla finita",
        r"non voglio più vivere",
        r"convulsion",
        r"reazione allergica",
        r"febbre alta",
        r"febbre (a|di) (39|40|41)",
        r"urgenza",
    ],
    "en": [
        r"chest pain",
        r"pain in (my|his|her|the) chest",
        r"tight\w* (in )?(my |the )?chest",
        r"short(ness)? of breath",
        r"can'?t breathe",
        r"trouble breathing",
        r"difficulty breathing",
        r"fainted",
        r"unconscious",
        r"passed out",
        r"paraly",
        r"slurred speech",
        r"face (is )?drooping",
        r"heavy bleeding",
        r"bleeding heavily",
        r"suicid",
        r"kill myself",
        r"end my life",
        r"seizure",
        r"allergic reaction",
        r"swollen (tongue|throat)",
        r"high fever",
        r"emergency",
    ],
}

_COMPILED = [
    (lang, re.compile(p, re.IGNORECASE)) for lang, ps in PATTERNS.items() for p in ps
]



def lexical_hits(text: str) -> list[tuple[str, int, int]]:
    hits = []
    for _lang, rx in _COMPILED:
        for m in rx.finditer(text):
            hits.append((m.group(), m.start(), m.end()))
    hits.sort(key=lambda h: h[1])
    return hits


def lexical_flag(text: str) -> bool:
    return bool(lexical_hits(text))
