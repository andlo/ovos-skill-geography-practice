"""Tests for the module-level data loading - CORE_DATA and the
per-locale name files. These are data-integrity checks, not skill
logic tests: they catch a broken/incomplete locale file or a stale
cross-reference between the core dataset and a name file."""
import pytest

LOCALES = ["en-us", "da-dk", "de-de", "fr-fr", "es-es"]


def test_core_data_has_194_un_member_states():
    from geographypractice_skill import CORE_DATA
    assert len(CORE_DATA) == 194


def test_every_country_has_a_capital_region_and_subregion():
    from geographypractice_skill import CORE_DATA
    for cca3, c in CORE_DATA.items():
        assert c["capital"], f"{cca3} has no capital"
        assert c["region"], f"{cca3} has no region"
        assert c["subregion"], f"{cca3} has no subregion"


def test_borders_never_reference_a_country_outside_core_data():
    """The data-prep step filters borders to only other UN member
    states in scope - this confirms that held, i.e. no dangling
    reference to a non-sovereign territory (Hong Kong, Gibraltar,
    Western Sahara, etc) slipped through."""
    from geographypractice_skill import CORE_DATA
    for cca3, c in CORE_DATA.items():
        for b in c["borders"]:
            assert b in CORE_DATA, f"{cca3} borders {b}, which isn't in CORE_DATA"


def test_only_south_africa_has_multiple_capitals():
    from geographypractice_skill import CORE_DATA
    multi = [cca3 for cca3, c in CORE_DATA.items() if len(c["capital"]) > 1]
    assert multi == ["ZAF"]


@pytest.mark.parametrize("lang", LOCALES)
def test_country_names_cover_every_country_in_every_locale(lang):
    from geographypractice_skill import CORE_DATA, COUNTRY_NAMES
    names = COUNTRY_NAMES[lang]
    assert set(names.keys()) == set(CORE_DATA.keys())
    assert all(isinstance(v, str) and v for v in names.values())


@pytest.mark.parametrize("lang", LOCALES)
def test_capital_names_cover_every_country_in_every_locale(lang):
    from geographypractice_skill import CORE_DATA, CAPITAL_NAMES
    capitals = CAPITAL_NAMES[lang]
    assert set(capitals.keys()) == set(CORE_DATA.keys())
    for cca3, entry in capitals.items():
        assert entry["primary"], f"{lang}/{cca3} has no primary capital name"
        assert entry["all"], f"{lang}/{cca3} has an empty 'all' capital list"


@pytest.mark.parametrize("lang", LOCALES)
def test_region_and_subregion_names_cover_every_region_in_core_data(lang):
    from geographypractice_skill import CORE_DATA, REGION_NAMES, SUBREGION_NAMES
    regions_used = set(c["region"] for c in CORE_DATA.values())
    subregions_used = set(c["subregion"] for c in CORE_DATA.values())
    assert regions_used <= set(REGION_NAMES[lang].keys())
    assert subregions_used <= set(SUBREGION_NAMES[lang].keys())


def test_country_name_to_code_reverse_lookup_roundtrips():
    from geographypractice_skill import COUNTRY_NAMES, COUNTRY_NAME_TO_CODE
    for lang in LOCALES:
        for cca3, name in COUNTRY_NAMES[lang].items():
            assert COUNTRY_NAME_TO_CODE[lang][name.strip().lower()] == cca3


def test_southern_africa_subregion_is_disambiguated_from_south_africa_country():
    """Danish and German both use nearly the same word for the
    country 'South Africa' and would-be subregion 'Southern Africa'
    if translated naively - confirms the disambiguated wording
    (see data/build_data.py comment) actually landed."""
    from geographypractice_skill import COUNTRY_NAMES, SUBREGION_NAMES
    assert COUNTRY_NAMES["da-dk"]["ZAF"] != SUBREGION_NAMES["da-dk"]["Southern Africa"]
    assert COUNTRY_NAMES["de-de"]["ZAF"] != SUBREGION_NAMES["de-de"]["Southern Africa"]
