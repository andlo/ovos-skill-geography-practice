"""Tests for the facts intents (capital_of, continent_of,
borders_of), all using the en-us locale fixture."""
from unittest.mock import MagicMock


def _msg(**data):
    m = MagicMock()
    m.data = data
    return m


def test_capital_of_known_country(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_capital_of(_msg(country="France"))
    skill.speak_dialog.assert_called_once_with(
        "capital_of", {"country": "France", "capital": "Paris"})


def test_capital_of_unknown_country_speaks_error(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_capital_of(_msg(country="Narnia"))
    skill.speak_dialog.assert_called_once_with(
        "country_not_understood", {"country": "Narnia"})


def test_capital_of_country_with_multiple_capitals(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_capital_of(_msg(country="South Africa"))
    dialog_name, data = skill.speak_dialog.call_args[0]
    assert dialog_name == "capital_of_multi"
    assert data["country"] == "South Africa"
    assert "Pretoria" in data["capitals"]
    assert "Bloemfontein" in data["capitals"]
    assert "Cape Town" in data["capitals"]


def test_continent_of_known_country(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_continent_of(_msg(country="Kenya"))
    skill.speak_dialog.assert_called_once_with(
        "continent_of", {"country": "Kenya", "continent": "Africa"})


def test_continent_of_unknown_country_speaks_error(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_continent_of(_msg(country="Narnia"))
    skill.speak_dialog.assert_called_once_with(
        "country_not_understood", {"country": "Narnia"})


def test_borders_of_known_country_lists_all_neighbors(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_borders_of(_msg(country="France"))
    dialog_name, data = skill.speak_dialog.call_args[0]
    assert dialog_name == "borders_of"
    assert data["country"] == "France"
    for neighbor in ["Germany", "Spain", "Switzerland", "Belgium", "Italy"]:
        assert neighbor in data["countries"]


def test_borders_of_island_nation_speaks_no_borders_dialog(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_borders_of(_msg(country="Antigua and Barbuda"))
    skill.speak_dialog.assert_called_once_with(
        "borders_of_none", {"country": "Antigua and Barbuda"})


def test_borders_of_unknown_country_speaks_error(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_borders_of(_msg(country="Narnia"))
    skill.speak_dialog.assert_called_once_with(
        "country_not_understood", {"country": "Narnia"})


def test_country_name_lookup_is_case_insensitive(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_capital_of(_msg(country="france"))
    skill.speak_dialog.assert_called_once_with(
        "capital_of", {"country": "France", "capital": "Paris"})
