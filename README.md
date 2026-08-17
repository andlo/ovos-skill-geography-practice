# <img src='icon.png' card_color='#DB4062' width='50' height='50' style='vertical-align:bottom'/> Geography Practice

Interactive geography quizzes across the 194 independent UN member
states - capitals, continents/regions, and land borders, plus a
teach-then-practice mode covering all three at once. Fully offline,
available in English, Danish, German, French, and Spanish.

[![Tests](https://github.com/andlo/ovos-skill-geography-practice/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-geography-practice/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-geography-practice.svg)](https://pypi.org/project/ovos-skill-geography-practice/)

- [Quiz only - depends on ovos-skill-geography](#quiz-only---depends-on-ovos-skill-geography)
- [Quiz](#quiz)
- [Teach-then-practice](#teach-then-practice)
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

## Teach-then-practice

The shared pattern from
[ovos-skill-math-practice](https://github.com/andlo/ovos-skill-math-practice)
(see its [issue #1](https://github.com/andlo/ovos-skill-math-practice/issues/1)),
adapted for geography: `"teach me about Europe"` (a continent or
subregion) speaks a combined overview - continent, capital, AND
borders together - for each country in that region, one at a time
("say repeat to hear that again, or say anything else to continue").
Large regions are capped at 10 countries, randomly sampled, rather
than reciting all ~44 European countries in one go.

`"quiz me on what you taught me"` then quizzes ONLY on the countries
that were actually taught - not a fresh random set - asking a
randomly chosen topic (capital, continent, or border) per country,
reusing the exact same grading logic as the regular per-topic
quizzes above.

## Usage
```
"quiz me on capitals"
"quiz me on continents"
"quiz me on country borders"
"teach me about Europe"
"teach me about Northern Europe"
"quiz me on what you taught me"
"quiz mig i hovedstæder"                (Danish)
"quiz mig i landegrænser"               (Danish)
"lær mig om Europa"                     (Danish)
"quiz mig i det du lærte mig"           (Danish)
"quiz mich zu hauptstädten"             (German)
"quiz mich zu landesgrenzen"            (German)
"bring mir etwas über Europa bei"       (German)
"interroge-moi sur les capitales"       (French)
"interroge-moi sur les frontières"      (French)
"apprends-moi l'Europe"                 (French)
"pregúntame sobre capitales"            (Spanish)
"pregúntame sobre fronteras"            (Spanish)
"enséñame sobre Europa"                 (Spanish)
```

## Known simplifications

- **Teach mode caps at 10 countries per region** - a deliberate size
  limit, not a bug, so "teach me about Europe" doesn't turn into a
  44-country monologue.
- **Taught facts are session-only**, same choice as
  `ovos-skill-math-practice`'s `_taught_facts` - resets when the
  skill restarts.
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
