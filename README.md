# <img src='icon.png' card_color='#DB4062' width='50' height='50' style='vertical-align:bottom'/> Geography Practice

Interactive geography quizzes across the 194 independent UN member
states - capitals, continents/regions, and land borders. Fully
offline, available in English, Danish, German, French, and Spanish.

[![Tests](https://github.com/andlo/ovos-skill-geography-practice/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-geography-practice/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-geography-practice.svg)](https://pypi.org/project/ovos-skill-geography-practice/)

- [Quiz only - depends on ovos-skill-geography](#quiz-only---depends-on-ovos-skill-geography)
- [Quiz](#quiz)
- [Usage](#usage)
- [Known simplifications](#known-simplifications)
- [Install](#install)
- [Development](#development)

## Quiz only - depends on ovos-skill-geography

This skill used to bundle its own copy of the country/capital/region
data and answer facts directly ("what is the capital of France").
That's been split out into
[ovos-skill-geography](https://github.com/andlo/ovos-skill-geography),
a utility skill this package now depends on - the same relationship
`ovos-skill-unit-practice` has with `ovos-skill-convert`. Installing
this skill pulls in `ovos-skill-geography` as a dependency, so both
the facts intents AND the quiz intents below end up active. See
`ovos-skill-geography`'s README for why facts have standalone value
independent of any quiz, and its DEVELOPMENT.md for why it's not a
`CommonQuerySkill`.

## Quiz

- `"quiz me on capitals"` - 5 questions, listens for a spoken capital
  name, accepts either the localized name or any of the country's
  actual capital names.
- `"quiz me on continents"` - 5 questions, listens for a spoken
  continent/region name.
- `"quiz me on country borders"` - yes/no format ("does France border
  Germany"), half true and half false, constructed so it can never
  accidentally produce a false negative - see DEVELOPMENT.md for why
  this isn't an open-ended "name a border" question.

## Usage
```
"quiz me on capitals"
"quiz me on continents"
"quiz me on country borders"
"quiz mig i hovedstæder"           (Danish)
"quiz mig i landegrænser"          (Danish)
"quiz mich zu hauptstädten"        (German)
"quiz mich zu landesgrenzen"       (German)
"interroge-moi sur les capitales"  (French)
"interroge-moi sur les frontières" (French)
"pregúntame sobre capitales"       (Spanish)
"pregúntame sobre fronteras"       (Spanish)
```

## Known simplifications

- **No teach-then-practice mode yet** - unlike
  [ovos-skill-math-practice](https://github.com/andlo/ovos-skill-math-practice),
  this is quiz-only for v1.
- Data quality/coverage caveats (capital-name translation coverage,
  scope limited to 194 UN member states, etc) live in
  [ovos-skill-geography](https://github.com/andlo/ovos-skill-geography)'s
  README/CREDITS.md, since that's where the data actually lives now.

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
