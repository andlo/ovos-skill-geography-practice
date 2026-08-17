# Development

## Architecture at a glance

Quiz + teach-then-practice skill. All data and name-lookup functions
(`CORE_DATA`, `resolve_country()`, `country_name()`, `capital_entry()`,
`region_name()`, `resolve_area()`, `countries_in_area()`,
`render_country_overview()`, etc) are imported from
[ovos-skill-geography](https://github.com/andlo/ovos-skill-geography)
(a `requirements.txt` dependency), not duplicated here - see that
package's DEVELOPMENT.md for the data pipeline and sourcing.

**The border quiz is yes/no, not open-ended.** "Name a country that
borders France" has many valid answers and is hard to grade reliably
by voice. Instead, `generate_border_question()` asks "does X border
Y" - constructed to be true exactly half the time: the false case is
sampled from every country NOT in X's actual borders list, so it can
never accidentally produce a false negative. A country with zero
borders (an island nation) always gets a false-pair question.

## Teach-then-practice

`handle_teach_me()` resolves a spoken region/subregion via
`resolve_area()`, gets its country list via `countries_in_area()`,
caps it at `TEACH_MAX_COUNTRIES` (10, randomly sampled if the region
is bigger), then `_teach_countries()` recites each one via
`render_country_overview()` - the SAME combined-sentence builder
`ovos-skill-geography`'s own `"tell me about {country}"` fact intent
uses. Only `self._taught_countries` (a list of cca3 codes) is
recorded, not the actual answer VALUES - `handle_quiz_taught()` looks
everything up fresh via the imported functions at quiz time, so there's
no risk of stale duplicated data if the underlying dataset changes
between teaching and quizzing (unlikely within one session, but free
to get right by construction rather than something to remember).

**One real duplication, deliberate, not accidental:** this repo
carries its own copy of `about_country.dialog` /
`about_country_no_borders.dialog` (same WORDING as
`ovos-skill-geography`'s), because `self.resources.load_dialog_file()`
only looks in the calling skill's OWN `locale/` folder -
`render_country_overview()` returns a dialog NAME and DATA, not
rendered text, so each skill instance needs a matching dialog file to
actually speak it. The LOGIC (what data goes into the sentence, which
variant to use) lives in one place; only the wording is duplicated.
If you change the wording in one repo, change it in the other too.

**`handle_quiz_taught()` mixes topics per country**, not per
question: for each taught country, it randomly picks capital,
continent, or border, then calls the SAME `_ask_and_grade_*()` method
the regular per-topic quizzes use - no new grading logic. For the
border topic specifically, `generate_border_question(country_codes=[cca3])`
forces the question to be ABOUT that exact taught country while still
drawing the yes/no comparison country from the full universe.

## Setup
```bash
git clone https://github.com/andlo/ovos-skill-geography-practice.git
cd ovos-skill-geography-practice
python3 -m venv .venv && source .venv/bin/activate
# ovos-skill-geography isn't always on PyPI in lockstep with this
# repo during development - install it in editable mode from a
# sibling checkout first if requirements.txt's pinned version isn't
# published yet:
#   pip install -e ../ovos-skill-geography
pip install -e .
pip install -r requirements-test.txt
```

## Running tests
```bash
pytest tests/ -v
```
`tests/test_border_generation.py` covers `generate_border_question()`
invariants (many iterations, since it's randomized). `tests/test_quiz.py`
covers the three quiz flows with `get_response()` mocked for
deterministic scoring. `tests/test_teach_then_practice.py` covers the
teach loop (row-by-row recitation, "repeat" branch, no prompt after
the last country, the 10-country cap) and `quiz_taught()` (only asks
about taught countries, not `NUM_QUIZ_QUESTIONS`; the border-topic
path calls `generate_border_question()` with a restricted
`country_codes`). Data-integrity tests (does every country have a
capital, do name files cover every locale, etc) live in
`ovos-skill-geography`'s own test suite now, not duplicated here.

## Versioning

`version.py` follows `VERSION_MAJOR.VERSION_MINOR.VERSION_BUILD[aVERSION_ALPHA]`.

## Releasing

Releases are tag-triggered (`v*`):
```bash
git add version.py
git commit -m "chore: bump version to 0.0.X"
git tag vX.Y.Z
git push && git push --tags
```
Triggers `.github/workflows/test.yml` then `.github/workflows/publish.yml`
(PyPI via trusted publishing). If `requirements.txt`'s
`ovos-skill-geography` version bound isn't published yet, CI's
`pip install -e .` step will fail - publish that dependency first.

## Style / conventions

- License: GPL-3.0-or-later.
- `locale/<lang-code>/` layout, `skill.json` inside each locale
  folder.
- Present design changes for review before implementing.
