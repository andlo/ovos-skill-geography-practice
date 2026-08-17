# Data credits and licensing

## Country/capital/region data

Source: [mledoze/countries](https://github.com/mledoze/countries),
licensed under the **Open Database License (ODbL-1.0)**.

This skill bundles a **trimmed subset** of that dataset (`data/countries.json`):
country code, capital name(s), region, subregion, and land borders for
the 194 independent UN member states - not the full dataset (currencies,
languages, calling codes, flags, native names, etc. are not included,
since this skill doesn't use them).

Per the ODbL, this derivative:
- **Attributes** the source: mledoze/countries, itself compiled from
  Wikipedia (general country facts) and thematicmapping.org's World
  Borders Dataset (border/geographic data).
- Is itself made available under **ODbL-1.0** for the trimmed
  subset in `data/countries.json`, consistent with the ODbL's
  share-alike requirement for derivative databases. This does NOT
  extend to the skill's own code (`__init__.py`, tests, etc.), which
  remains GPL-3.0-or-later per `LICENSE`.

## Country names (localized)

Country names in `locale/*/country_names.json` (da-dk, de-de, fr-fr,
es-es) are sourced from **Unicode CLDR** (Common Locale Data
Repository), via the [Babel](https://babel.pocoo.org/) Python library
(BSD-3-Clause), used only as a one-off data-generation tool (see
`data/build_data.py`) - not a runtime dependency of the shipped skill.
en-us uses mledoze/countries' own `name.common` field.

## Region/subregion names (localized)

Hand-translated for this skill (only 5 regions and 23 subregions -
a small enough set to translate directly and confidently). Not
sourced from CLDR or any external database.

## Capital names (localized)

**Partial, best-effort.** No CLDR-equivalent authoritative source
exists for city names at this scale. `locale/*/capital_names.json`
defaults to mledoze/countries' own spelling, overridden only for
well-known cases curated by hand for this release - not verified
per-entry against a dictionary or exhaustively covering all 194
capitals in each language. See each file's own `_notes` field.
**Corrections and additions here are a good fit for OVOS Translate.**

## Population data

Not included in this release - population figures go stale quickly
and this skill doesn't currently disclose "as of" dates for bundled
data. See the design-doc README history for the reasoning; may be
added in a future version with an explicit staleness disclaimer.
