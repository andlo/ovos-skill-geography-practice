# <img src='icon.png' card_color='#DB4062' width='50' height='50' style='vertical-align:bottom'/> Geography Practice

Geography facts and interactive quizzes across the 194 independent
UN member states - capitals, continents/regions, and land borders.
Fully offline: all data is bundled as static JSON, no external
lookups at runtime. Available in English, Danish, German, French,
and Spanish.

[![Tests](https://github.com/andlo/ovos-skill-geography-practice/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-geography-practice/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-geography-practice.svg)](https://pypi.org/project/ovos-skill-geography-practice/)

- [Facts](#facts)
- [Quiz](#quiz)
- [Usage](#usage)
- [Data sourcing and licensing](#data-sourcing-and-licensing)
- [Known simplifications](#known-simplifications)
- [Install](#install)
- [Development](#development)

## Facts

- `"what is the capital of France"` - speaks the capital. Handles
  countries with more than one capital (only South Africa in this
  dataset - Pretoria, Bloemfontein, and Cape Town) by naming all of
  them rather than picking one.
- `"what continent is Kenya in"` - speaks the continent/region.
- `"what countries border Germany"` - lists every land border. A
  country with no land borders (an island nation, or one surrounded
  entirely by ocean) gets an explicit "doesn't share a border with
  any other country" response rather than an empty list.

## Quiz

- `"quiz me on capitals"` - 5 questions, listens for a spoken capital
  name, accepts either the localized name or any of the country's
  actual capital names.
- `"quiz me on continents"` - 5 questions, listens for a spoken
  continent/region name.
- `"quiz me on country borders"` - a genuinely different format from
  the other two: yes/no questions ("does France border Germany"),
  half true (an actual neighbor) and half false (a country that
  isn't), rather than an open-ended "name a border" question - see
  DEVELOPMENT.md for why.

## Usage
```
"what is the capital of France"
"what continent is Kenya in"
"what countries border Germany"
"quiz me on capitals"
"quiz me on continents"
"quiz me on country borders"
"hvad er hovedstaden i Frankrig"          (Danish)
"hvilket kontinent er Kenya i"            (Danish)
"quiz mig i hovedstæder"                  (Danish)
"was ist die hauptstadt von Frankreich"   (German)
"quiz mich zu hauptstädten"               (German)
"quelle est la capitale de la France"     (French)
"interroge-moi sur les capitales"         (French)
"cuál es la capital de Francia"           (Spanish)
"pregúntame sobre capitales"              (Spanish)
```

## Data sourcing and licensing

Country/capital/region/border data comes from
[mledoze/countries](https://github.com/mledoze/countries)
(ODbL-1.0), trimmed to just the fields this skill needs, for the 194
independent UN member states. Country names in da/de/fr/es come from
Unicode CLDR (via the [Babel](https://babel.pocoo.org/) library, used
only as a one-off data-generation tool, not a runtime dependency).
Region/subregion names are hand-translated (a small, 28-term set).
**Full attribution and licensing details: [CREDITS.md](CREDITS.md).**

Population data is deliberately NOT included - figures go stale
quickly and this skill doesn't currently disclose "as of" dates for
bundled data. May be added in a future version with an explicit
staleness disclaimer.

## Known simplifications

- **Capital names in da/de/fr/es are partial, best-effort.** No
  CLDR-equivalent authoritative source exists for city names.
  `locale/*/capital_names.json` defaults to the source dataset's own
  spelling, overridden only for well-known cases curated by hand for
  this release - not verified per-entry, not exhaustive. See each
  file's own `_notes` field. **Corrections and additions are a good
  fit for OVOS Translate.**
- **Spoken country names with a leading article** ("la France", "die
  Türkei", "el Perú") are handled with a simple prefix-strip
  (`ARTICLE_PREFIXES` in `__init__.py`), not full grammatical
  parsing - covers the common case, not every gendered-article
  possibility in French/German/Spanish.
- **No teach-then-practice mode yet** - unlike
  [ovos-skill-math-practice](https://github.com/andlo/ovos-skill-math-practice),
  this is facts + quiz only for v1. Worth adopting the shared pattern
  (see math-practice's README and
  [issue #1](https://github.com/andlo/ovos-skill-math-practice/issues/1))
  in a later version.
- **Scope is 194 independent UN member states only** - dependent
  territories, disputed regions, and non-sovereign entities (Hong
  Kong, Gibraltar, Western Sahara, Kosovo, etc) aren't included, and
  border lists are filtered to only reference other countries in this
  same scope.

## Install
```bash
pip install ovos-skill-geography-practice
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md).

## Category
**Education**

## Tags
#geography #education #capitals #countries #quiz #kids
