"""
skill OVOS Geography Practice
Copyright (C) 2026  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

Geography practice: facts ("what is the capital of France") and
interactive quizzes (capitals, continents, country borders) across
the 194 independent UN member states. Fully offline - all data is
bundled as static JSON (see data/countries.json and CREDITS.md for
sourcing/licensing), no external lookups at runtime.

See README.md for the full feature list and example utterances, and
DEVELOPMENT.md for the architecture, data pipeline, and known
simplifications (e.g. capital-name translation coverage, spoken-
article handling) - kept out of this docstring, same reasoning as
ovos-skill-math-practice's.
"""

import json
import random
from pathlib import Path

from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

NUM_QUIZ_QUESTIONS = 5

SKILL_ROOT = Path(__file__).resolve().parent
DATA_DIR = SKILL_ROOT / "data"
LOCALE_DIR = SKILL_ROOT / "locale"

# Common leading articles that a spoken country name may carry in
# some languages ("la France", "die Türkei", "el Perú") but that
# aren't part of the stored name itself (CLDR/mledoze names are
# bare, e.g. "France"). Stripped before lookup - a pragmatic
# simplification, not full grammatical parsing (see DEVELOPMENT.md).
ARTICLE_PREFIXES = {
    "fr-fr": ["l'", "la ", "le ", "les "],
    "de-de": ["der ", "die ", "das "],
    "es-es": ["el ", "la ", "los ", "las "],
}

def _load_core_data():
    """data/countries.json -> {cca3: {cca3, cca2, capital (raw list),
    region, subregion, borders (list of cca3)}}. See CREDITS.md for
    sourcing (mledoze/countries, ODbL-1.0, trimmed to just these
    fields for the 194 independent UN member states)."""
    path = DATA_DIR / "countries.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        countries = json.load(f)
    return {c["cca3"]: c for c in countries}


CORE_DATA = _load_core_data()
ALL_COUNTRY_CODES = list(CORE_DATA.keys())


def _load_locale_json(filename):
    """locale/<lang>/<filename> -> {lang: {...}}, merged across every
    locale dir found, "_notes" keys dropped - same loader convention
    ovos-skill-math-practice uses for its alias JSON files."""
    merged = {}
    if not LOCALE_DIR.is_dir():
        return merged
    for lang_dir in sorted(LOCALE_DIR.iterdir()):
        if not lang_dir.is_dir():
            continue
        path = lang_dir / filename
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        lang = lang_dir.name.lower()
        merged[lang] = {k: v for k, v in data.items() if not k.startswith("_")}
    return merged


COUNTRY_NAMES = _load_locale_json("country_names.json")      # lang -> {cca3: name}
REGION_NAMES = _load_locale_json("region_names.json")        # lang -> {region: name}
SUBREGION_NAMES = _load_locale_json("subregion_names.json")  # lang -> {subregion: name}
_CAPITAL_NAMES_RAW = _load_locale_json("capital_names.json")
# lang -> {cca3: {"primary": localized name, "all": [every capital,
# unlocalized - only South Africa has more than one]}}
CAPITAL_NAMES = {lang: data.get("capitals", {}) for lang, data in _CAPITAL_NAMES_RAW.items()}


def _reverse_lookup(name_dict):
    """{cca3: name} -> {name.lower(): cca3}, for resolving a spoken
    country name back to its code."""
    return {name.strip().lower(): code for code, name in name_dict.items()}


COUNTRY_NAME_TO_CODE = {lang: _reverse_lookup(names) for lang, names in COUNTRY_NAMES.items()}

def generate_border_question(country_codes=None):
    """Returns (cca3, other_cca3, is_true_border) for a yes/no border
    question. Half true (a real neighbor), half false (a country that
    does NOT border it) - constructed, not guessed: the false case is
    sampled from every country that ISN'T in the true country's own
    borders list, so it can never accidentally produce a false
    negative. A country with zero borders (e.g. an island nation)
    always gets a false-pair question, since it has no true pairs to
    draw from. `country_codes` restricts which country the question
    is ABOUT (for deterministic testing) - the candidate pool for
    'other' always searches the full ALL_COUNTRY_CODES regardless, so
    restricting to a single country never starves that search."""
    codes = country_codes if country_codes is not None else ALL_COUNTRY_CODES
    cca3 = random.choice(codes)
    borders = CORE_DATA[cca3]["borders"]
    ask_true = bool(borders) and random.choice([True, False])
    if ask_true:
        other = random.choice(borders)
        return cca3, other, True
    candidates = [c for c in ALL_COUNTRY_CODES if c != cca3 and c not in borders]
    other = random.choice(candidates)
    return cca3, other, False


class GeographyPractice(OVOSSkill):

    # ------------------------------------------------------------------
    # Name resolution helpers
    # ------------------------------------------------------------------

    def _country_names_for(self, lang):
        lang = lang.lower()
        return COUNTRY_NAMES.get(lang) or COUNTRY_NAMES.get("en-us", {})

    def _strip_article(self, raw, lang):
        lang = lang.lower()
        raw = raw.strip()
        lower = raw.lower()
        for prefix in ARTICLE_PREFIXES.get(lang, []):
            if lower.startswith(prefix):
                return raw[len(prefix):].strip()
        return raw

    def _resolve_country(self, raw, lang):
        """Exact match only (after stripping a leading article, see
        ARTICLE_PREFIXES) - same philosophy as
        ovos-skill-math-practice's operation resolution: a wrong
        country is a more confusing wrong answer than a slightly
        mis-parsed one."""
        if not raw:
            return None
        lang = lang.lower()
        lookup = COUNTRY_NAME_TO_CODE.get(lang) or COUNTRY_NAME_TO_CODE.get("en-us", {})
        return lookup.get(self._strip_article(raw, lang).lower())

    def _country_name_for(self, cca3, lang):
        return self._country_names_for(lang).get(cca3, cca3)

    def _capital_entry_for(self, cca3, lang):
        lang = lang.lower()
        capitals = CAPITAL_NAMES.get(lang) or CAPITAL_NAMES.get("en-us", {})
        return capitals.get(cca3)

    def _region_name_for(self, region, lang):
        lang = lang.lower()
        names = REGION_NAMES.get(lang) or REGION_NAMES.get("en-us", {})
        return names.get(region, region)

    def _subregion_name_for(self, subregion, lang):
        lang = lang.lower()
        names = SUBREGION_NAMES.get(lang) or SUBREGION_NAMES.get("en-us", {})
        return names.get(subregion, subregion)

    # ------------------------------------------------------------------
    # Facts
    # ------------------------------------------------------------------

    @intent_handler("capital_of.intent")
    def handle_capital_of(self, message):
        country_raw = message.data.get("country")
        cca3 = self._resolve_country(country_raw, self.lang)
        if cca3 is None:
            self.speak_dialog("country_not_understood", {"country": country_raw or ""})
            return
        country_name = self._country_name_for(cca3, self.lang)
        entry = self._capital_entry_for(cca3, self.lang)
        if entry and len(entry["all"]) > 1:
            # Only South Africa in this dataset - "all" isn't
            # per-language translated (see CAPITAL_OVERRIDES coverage
            # in data/build_data.py), spoken as-is.
            self.speak_dialog("capital_of_multi", {
                "country": country_name, "capitals": ", ".join(entry["all"])})
        else:
            capital = entry["primary"] if entry else None
            self.speak_dialog("capital_of", {"country": country_name, "capital": capital})

    @intent_handler("continent_of.intent")
    def handle_continent_of(self, message):
        country_raw = message.data.get("country")
        cca3 = self._resolve_country(country_raw, self.lang)
        if cca3 is None:
            self.speak_dialog("country_not_understood", {"country": country_raw or ""})
            return
        country_name = self._country_name_for(cca3, self.lang)
        region_name = self._region_name_for(CORE_DATA[cca3]["region"], self.lang)
        self.speak_dialog("continent_of", {"country": country_name, "continent": region_name})

    @intent_handler("borders_of.intent")
    def handle_borders_of(self, message):
        country_raw = message.data.get("country")
        cca3 = self._resolve_country(country_raw, self.lang)
        if cca3 is None:
            self.speak_dialog("country_not_understood", {"country": country_raw or ""})
            return
        country_name = self._country_name_for(cca3, self.lang)
        borders = CORE_DATA[cca3]["borders"]
        if not borders:
            self.speak_dialog("borders_of_none", {"country": country_name})
            return
        names = [self._country_name_for(b, self.lang) for b in borders]
        self.speak_dialog("borders_of", {"country": country_name, "countries": ", ".join(names)})

    # ------------------------------------------------------------------
    # Quiz
    # ------------------------------------------------------------------

    def _ask_and_grade_capital(self, cca3):
        country_name = self._country_name_for(cca3, self.lang)
        entry = self._capital_entry_for(cca3, self.lang)
        response = self.get_response(dialog="quiz_question_capital", data={"country": country_name})
        if response is None:
            self.speak_dialog("quiz_no_answer")
            return False
        valid_answers = {entry["primary"].strip().lower()} | {c.strip().lower() for c in entry["all"]} if entry else set()
        if response.strip().lower() in valid_answers:
            self.speak_dialog("quiz_correct")
            return True
        self.speak_dialog("quiz_incorrect_capital", {
            "country": country_name, "capital": entry["primary"] if entry else "?"})
        return False

    def _ask_and_grade_continent(self, cca3):
        country_name = self._country_name_for(cca3, self.lang)
        region_name = self._region_name_for(CORE_DATA[cca3]["region"], self.lang)
        response = self.get_response(dialog="quiz_question_continent", data={"country": country_name})
        if response is None:
            self.speak_dialog("quiz_no_answer")
            return False
        if response.strip().lower() == region_name.strip().lower():
            self.speak_dialog("quiz_correct")
            return True
        self.speak_dialog("quiz_incorrect_continent", {"country": country_name, "continent": region_name})
        return False

    def _ask_and_grade_border(self, cca3, other_cca3, is_true):
        country_name = self._country_name_for(cca3, self.lang)
        other_name = self._country_name_for(other_cca3, self.lang)
        response = self.get_response(dialog="quiz_question_border", data={
            "country": country_name, "other": other_name})
        if response is None:
            self.speak_dialog("quiz_no_answer")
            return False
        said_yes = self.voc_match(response, "yes")
        said_no = self.voc_match(response, "no")
        user_answer = True if said_yes else (False if said_no else None)
        if user_answer == is_true:
            self.speak_dialog("quiz_correct")
            return True
        self.speak_dialog(
            "quiz_incorrect_border_yes" if is_true else "quiz_incorrect_border_no",
            {"country": country_name, "other": other_name})
        return False

    def _run_capitals_quiz(self):
        correct_count = 0
        for _ in range(NUM_QUIZ_QUESTIONS):
            cca3 = random.choice(ALL_COUNTRY_CODES)
            if self._ask_and_grade_capital(cca3):
                correct_count += 1
        self.speak_dialog("quiz_finished", {"correct": correct_count, "total": NUM_QUIZ_QUESTIONS})

    def _run_continents_quiz(self):
        correct_count = 0
        for _ in range(NUM_QUIZ_QUESTIONS):
            cca3 = random.choice(ALL_COUNTRY_CODES)
            if self._ask_and_grade_continent(cca3):
                correct_count += 1
        self.speak_dialog("quiz_finished", {"correct": correct_count, "total": NUM_QUIZ_QUESTIONS})

    def _run_borders_quiz(self):
        correct_count = 0
        for _ in range(NUM_QUIZ_QUESTIONS):
            cca3, other_cca3, is_true = generate_border_question()
            if self._ask_and_grade_border(cca3, other_cca3, is_true):
                correct_count += 1
        self.speak_dialog("quiz_finished", {"correct": correct_count, "total": NUM_QUIZ_QUESTIONS})

    @intent_handler("quiz_capitals.intent")
    def handle_quiz_capitals(self, message):
        self._run_capitals_quiz()

    @intent_handler("quiz_continents.intent")
    def handle_quiz_continents(self, message):
        self._run_continents_quiz()

    @intent_handler("quiz_borders.intent")
    def handle_quiz_borders(self, message):
        self._run_borders_quiz()
