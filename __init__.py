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
)

NUM_QUIZ_QUESTIONS = 5


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
