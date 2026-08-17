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

Interactive geography quizzes (capitals, continents, country
borders) across the 194 independent UN member states.

This skill is QUIZ ONLY - facts ("what is the capital of France") are
ovos-skill-geography's job, which this package depends on directly
for its data and name-lookup functions (CORE_DATA, resolve_country(),
country_name(), etc) rather than duplicating them, the same
relationship ovos-skill-unit-practice has with ovos-skill-convert.
See that package's README/DEVELOPMENT.md for the data sourcing and
the "why fixed intents, not Common Query" reasoning.

See README.md for the full feature list and DEVELOPMENT.md for the
architecture (including why the border quiz is yes/no, not
open-ended).
"""

import random

from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

from ovos_skill_geography import (
    CORE_DATA,
    ALL_COUNTRY_CODES,
    resolve_country,
    country_name,
    capital_entry,
    region_name,
    resolve_area,
    countries_in_area,
    render_country_overview,
)

NUM_QUIZ_QUESTIONS = 5
# Cap on how many countries a single "teach me about {region}" round
# recites - Europe alone has ~44 countries, and reciting all of them
# in one go would be a very long, low-value monologue. 10 mirrors
# ovos-skill-math-practice's table size (a times table is 10 rows).
TEACH_MAX_COUNTRIES = 10


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

    def initialize(self):
        # Session-only, not persisted across restarts - same
        # deliberate v1 scoping choice as ovos-skill-math-practice's
        # _taught_facts (see its README "Shared pattern: teach-then-
        # practice").
        self._taught_countries = []

    def _ask_and_grade_capital(self, cca3):
        name = country_name(cca3, self.lang)
        entry = capital_entry(cca3, self.lang)
        response = self.get_response(dialog="quiz_question_capital", data={"country": name})
        if response is None:
            self.speak_dialog("quiz_no_answer")
            return False
        valid_answers = {entry["primary"].strip().lower()} | {c.strip().lower() for c in entry["all"]} if entry else set()
        if response.strip().lower() in valid_answers:
            self.speak_dialog("quiz_correct")
            return True
        self.speak_dialog("quiz_incorrect_capital", {
            "country": name, "capital": entry["primary"] if entry else "?"})
        return False

    def _ask_and_grade_continent(self, cca3):
        name = country_name(cca3, self.lang)
        continent = region_name(CORE_DATA[cca3]["region"], self.lang)
        response = self.get_response(dialog="quiz_question_continent", data={"country": name})
        if response is None:
            self.speak_dialog("quiz_no_answer")
            return False
        if response.strip().lower() == continent.strip().lower():
            self.speak_dialog("quiz_correct")
            return True
        self.speak_dialog("quiz_incorrect_continent", {"country": name, "continent": continent})
        return False

    def _ask_and_grade_border(self, cca3, other_cca3, is_true):
        name = country_name(cca3, self.lang)
        other_name = country_name(other_cca3, self.lang)
        response = self.get_response(dialog="quiz_question_border", data={
            "country": name, "other": other_name})
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
            {"country": name, "other": other_name})
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

    # ------------------------------------------------------------------
    # Teach-then-practice (see README "Teach-then-practice" and
    # ovos-skill-math-practice issue #1 for the shared pattern this
    # follows)
    # ------------------------------------------------------------------

    def _teach_countries(self, cca3_list):
        """Speaks each country's combined continent+capital+borders
        overview in turn (render_country_overview(), shared with
        ovos-skill-geography's own 'tell me about X' fact intent -
        this repo carries its own copy of the about_country*.dialog
        WORDING for self.resources.load_dialog_file() to find, but
        the LOGIC of what data goes into it lives in one place).
        Offers 'repeat' before moving to the next country, and
        records exactly which countries were presented so the
        follow-up quiz asks about them - and only them."""
        self._taught_countries = []
        for idx, cca3 in enumerate(cca3_list):
            dialog_name, data = render_country_overview(cca3, self.lang)
            rendered = self.resources.load_dialog_file(dialog_name, data)[0]
            self.speak(rendered, wait=True)
            self._taught_countries.append(cca3)

            if idx == len(cca3_list) - 1:
                break
            response = self.get_response(dialog="continue_teaching_prompt")
            if response and self.voc_match(response, "repeat"):
                self.speak(rendered, wait=True)

        self.speak_dialog("teaching_finished", {"count": len(self._taught_countries)})

    @intent_handler("teach_me.intent")
    def handle_teach_me(self, message):
        region_raw = message.data.get("region")
        resolved = resolve_area(region_raw, self.lang)
        if resolved is None:
            self.speak_dialog("region_not_understood", {"region": region_raw or ""})
            return
        kind, key = resolved
        codes = list(countries_in_area(kind, key))
        if len(codes) > TEACH_MAX_COUNTRIES:
            codes = random.sample(codes, TEACH_MAX_COUNTRIES)
        else:
            random.shuffle(codes)
        self._teach_countries(codes)

    @intent_handler("quiz_taught.intent")
    def handle_quiz_taught(self, message):
        """Quizzes ONLY on the recorded taught countries (not
        NUM_QUIZ_QUESTIONS=5) - for each one, a RANDOMLY chosen topic
        (capital/continent/border), reusing the exact same grading
        methods the regular per-topic quizzes use. For the border
        topic, generate_border_question(country_codes=[cca3]) forces
        the question to be ABOUT that taught country while still
        drawing the yes/no comparison country from the full universe,
        same true/false-pair construction as the regular border quiz."""
        if not self._taught_countries:
            self.speak_dialog("nothing_taught_yet")
            return
        correct_count = 0
        total = len(self._taught_countries)
        for cca3 in self._taught_countries:
            topic = random.choice(["capital", "continent", "border"])
            if topic == "capital":
                ok = self._ask_and_grade_capital(cca3)
            elif topic == "continent":
                ok = self._ask_and_grade_continent(cca3)
            else:
                _, other_cca3, is_true = generate_border_question(country_codes=[cca3])
                ok = self._ask_and_grade_border(cca3, other_cca3, is_true)
            if ok:
                correct_count += 1
        self.speak_dialog("quiz_finished", {"correct": correct_count, "total": total})
