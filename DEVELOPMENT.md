# Development

## Architecture at a glance

Quiz-only skill. All data and name-lookup functions (`CORE_DATA`,
`resolve_country()`, `country_name()`, `capital_entry()`,
`region_name()`, etc) are imported from
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
deterministic scoring. Data-integrity tests (does every country have
a capital, do name files cover every locale, etc) live in
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
