# Development

## Architecture at a glance

Two modes: **facts** (`capital_of`, `continent_of`, `borders_of` -
one-shot, no interaction) and **quiz** (`quiz_capitals`,
`quiz_continents`, `quiz_borders` - `OVOSSkill.get_response()`-based,
same sequential-blocking-conversation pattern as
`ovos-skill-math-practice`, not a background thread).

**Data is bundled, not fetched at runtime.** `data/countries.json`
(language-agnostic: cca3 code, capital(s), region, subregion,
borders) plus one JSON file per locale per name type
(`country_names.json`, `region_names.json`, `subregion_names.json`,
`capital_names.json`). All loaded once at import time into
module-level dicts (`CORE_DATA`, `COUNTRY_NAMES`, etc) - see
`_load_core_data()` / `_load_locale_json()`.

**The border quiz is yes/no, not open-ended.** "Name a country that
borders France" has many valid answers and is hard to grade reliably
by voice; some countries have 10+ neighbors, making a truly
open-ended question unwieldy either way. Instead,
`generate_border_question()` asks "does X border Y" - constructed
(not guessed) to be true exactly half the time: the false case is
sampled from every country NOT in X's actual borders list, so it can
never accidentally produce a false negative. A country with zero
borders (an island nation) always gets a false-pair question, since
it has no true pairs to draw from.

## The data pipeline (data/build_data.py)

A one-off script, NOT part of the shipped skill or its runtime
dependencies (needs `pip install babel` separately - not in
`requirements.txt`). Run it again to regenerate `data/countries.json`
and every `locale/*/{country,region,subregion,capital}_names.json`
file from scratch, e.g. after mledoze/countries updates upstream.

Steps, in order:
1. Fetch `mledoze/countries`' `countries.json`, filter to
   `independent and unMember` (194 states - dependent territories,
   disputed regions, and non-sovereign entities excluded).
2. Write the trimmed core dataset, filtering each country's
   `borders` list to only reference OTHER countries within that same
   194-country scope (drops references to e.g. Hong Kong, Gibraltar,
   Western Sahara - never dangling).
3. Write `country_names.json` per locale: en-us from mledoze's own
   `name.common`; da-dk/de-de/fr-fr/es-es from Unicode CLDR via
   `babel.Locale(...).territories` - confirmed 100% coverage across
   all 194 countries before relying on it, not assumed.
4. Write `region_names.json` / `subregion_names.json` per locale:
   hand-translated (only 5 regions + 23 subregions - small enough to
   do directly and confidently, unlike 194 capitals). Danish/German
   deliberately avoid translating the "Southern Africa" SUBREGION as
   "Sydafrika"/"Südafrika", since that's identical to the country
   name South Africa in both languages - used "det sydlige
   Afrika"/"Südliches Afrika" instead.
5. Write `capital_names.json` per locale: defaults to mledoze's own
   spelling, overridden only for well-known cases curated by hand -
   see "Capital names" below.

## Capital names: the weak link, and how to improve it

No CLDR-equivalent authoritative source exists for city names at
this scale. `CAPITAL_OVERRIDES` in `data/build_data.py` is a
hand-curated, per-language dict of well-known cases (Moscow ->
Moskva/Moskau/Moscou/Moscú, etc), NOT verified per-entry against a
dictionary and NOT exhaustive - everything not in the override dict
falls back to mledoze's own (Latin-script/international) spelling.

**To add or correct an entry:** edit the relevant language's dict in
`CAPITAL_OVERRIDES` (keyed by cca3 code), then re-run
`data/build_data.py` to regenerate the locale JSON files - don't hand
-edit `locale/*/capital_names.json` directly, since a re-run would
overwrite it. This is exactly the kind of contribution OVOS Translate
is well suited for.

## Adding a new locale

1. Add the language code to the loop lists in `data/build_data.py`
   (`country_names`, `SUBREGION_NAMES` dict, `CAPITAL_OVERRIDES`) and
   confirm CLDR has full coverage for it (`babel.Locale(code)
   .territories`) before relying on it, same as da/de/fr/es.
2. Hand-translate `REGION_NAMES`/`SUBREGION_NAMES` for the new
   language (only 28 terms total).
3. Re-run `data/build_data.py`.
4. Add the intent/dialog/vocab files under `locale/<new-lang>/`,
   mirroring an existing locale's structure exactly (6 intents, 16
   dialogs, `yes.voc`/`no.voc`, `skill.json`).
5. Add the new language to `LOCALES` in `tests/test_data_loading.py`.

## Setup
```bash
git clone https://github.com/andlo/ovos-skill-geography-practice.git
cd ovos-skill-geography-practice
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r requirements-test.txt
```

## Running tests
```bash
pytest tests/ -v
```
`tests/test_data_loading.py` checks data INTEGRITY, not skill logic:
every country has a capital/region/subregion, borders never dangle
outside the 194-country scope, every locale's name files cover every
country, and the Southern-Africa/South-Africa disambiguation actually
landed. `tests/test_border_generation.py` and `tests/test_quiz.py`
mirror `ovos-skill-math-practice`'s testing style: pure-logic
generator tests run many iterations to catch randomization edge
cases, `get_response()` is mocked for deterministic flow/scoring
tests. `tests/test_country_resolution.py` covers the
`ARTICLE_PREFIXES` stripping specifically.

## Versioning

`version.py` follows `VERSION_MAJOR.VERSION_MINOR.VERSION_BUILD[aVERSION_ALPHA]`,
same convention as `ovos-skill-math-practice`.

## Releasing

Releases are tag-triggered (`v*`):
```bash
git add version.py
git commit -m "chore: bump version to 0.0.X"
git tag vX.Y.Z
git push && git push --tags
```
Triggers `.github/workflows/test.yml` then `.github/workflows/publish.yml`
(PyPI via trusted publishing - see `ovos-skill-convert`'s
DEVELOPMENT.md for the one-time PyPI setup needed before the first
tagged release).

## Style / conventions

- License: GPL-3.0-or-later for the skill's own code (matches the
  other `andlo` skill repos). The bundled dataset in
  `data/countries.json` is itself ODbL-1.0 - see CREDITS.md, this is
  a different license than the code around it.
- `locale/<lang-code>/` layout, `skill.json` inside each locale
  folder.
- Present design changes for review before implementing.
