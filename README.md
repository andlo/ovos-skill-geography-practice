# Geography Practice — a design document, not a working skill yet

**Status: idea and data-sourcing investigation stage.** Same pattern
as [ovos-skill-math-practice](https://github.com/andlo/ovos-skill-math-practice)
and [ovos-skill-science-practice](https://github.com/andlo/ovos-skill-science-practice):
facts/recitation mode plus an interactive quiz mode.

## The idea

- **Facts/recitation** - "what is the capital of France", "what
  continent is Kenya in", "what countries border Germany".
- **Quiz** - "quiz me on capitals", "quiz me on country borders" -
  same `get_response()`-based interactive scoring loop already built
  and tested in `ovos-skill-math-practice`.

Candidate topics: capitals, population (exact figures go stale fast -
see caveat below), continent/region membership, and land borders
between neighboring countries.

## Where the data comes from - investigated, not guessed at

**[mledoze/countries](https://github.com/mledoze/countries)** - a
comprehensive, actively maintained, static JSON dataset covering
every country: capital(s), population, region/subregion (continent-
level grouping), land borders (as ISO country codes), area, and more.
Confirmed by checking the actual repo, not assumed:

- **License: ODbL-1.0** (Open Database License) - this is a real,
  specific obligation, not "do whatever": it requires attribution and,
  if a modified/derivative version of the database itself is
  redistributed, that derivative must also be shared under ODbL. This
  needs a clear `CREDITS.md`-style attribution when actually bundling
  the data, same diligence `ovos-skill-sound-like` applied to its CC0
  audio sources - ODbL is a different, stricter kind of license than
  the CC0 sources used elsewhere in this project, worth being precise
  about rather than treating all "open" licenses as interchangeable.
- Sourced from Wikipedia (general country facts) and
  thematicmapping.org's World Borders dataset (the border/geographic
  data specifically) - both cited directly in the repo's own README.

## A real, honest caveat: population numbers go stale

Unlike capitals, continents, or land borders (all essentially
static), population figures change continuously and any bundled
snapshot is a **fixed point in time from whenever this skill's data
was last updated**, not a live figure. Worth disclosing this in the
skill itself if population questions are included ("as of when this
skill's data was compiled") rather than presenting a bundled number
as current fact - the same kind of honesty this project applied to
`ovos-skill-tuning-fork`'s Danish spelling caveat and
`ovos-skill-network-scanner`'s "only what announces itself" caveat.

## A realistic v1 scope

1. Capitals, continents/regions, and land borders - the genuinely
   stable facts. Population deferred to a later version specifically
   *because* of the staleness problem above, not forgotten.
2. Facts mode + quiz mode reusing `ovos-skill-math-practice`'s
   existing `_run_quiz()` architecture, same as
   `ovos-skill-science-practice`.
3. **Before bundling**: pull the actual `countries.json` from
   mledoze/countries, trim to just the fields this skill needs
   (name, capital, region/subregion, borders) rather than shipping
   the entire dataset (currencies, languages, calling codes, flags,
   etc aren't needed here), and write the ODbL attribution notice
   properly before shipping - not an afterthought.

## Category
**Education**

## Tags
#geography #education #trivia #quiz #idea #design-doc

## Shared pattern: teach-then-practice

Once proven, this skill should adopt the "teach, then quiz on what was
taught" pattern being designed on `ovos-skill-math-practice`
(see [issue #1](https://github.com/andlo/ovos-skill-math-practice/issues/1))
rather than only quizzing on arbitrary generated facts the user was
never actually taught. Not re-designed here to avoid the same
architecture being derived slightly differently in every `*-practice`
README - the shared design lives in one place and every sibling skill
points back to it.
