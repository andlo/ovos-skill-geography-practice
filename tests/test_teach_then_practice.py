"""Tests for the teach-then-practice pattern (README "Teach-then-
practice", ovos-skill-math-practice issue #1's shared pattern).
get_response()/voc_match()/resources are mocked so the teaching
loop's flow and state tracking are tested deterministically."""
from unittest.mock import MagicMock, patch

import pytest


def _msg(**data):
    m = MagicMock()
    m.data = data
    return m


def _fake_resources():
    """load_dialog_file() stand-in that just renders '{dialog_name}: k=v, k=v'
    so tests can assert on both which dialog was requested and what
    data it got, without needing real .dialog files."""
    m = MagicMock()
    m.load_dialog_file = MagicMock(
        side_effect=lambda name, data: [f"{name}:" + ",".join(f"{k}={v}" for k, v in data.items())])
    return m


def test_teach_me_speaks_every_country_and_records_taught_countries(skill):
    skill.speak = MagicMock()
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="ok")  # anything but "repeat"
    skill.voc_match = MagicMock(return_value=False)
    with patch.object(type(skill), "resources", property(lambda self: _fake_resources())):
        with patch("geographypractice_skill.resolve_area", return_value=("subregion", "Northern Europe")):
            with patch("geographypractice_skill.countries_in_area", return_value=["DNK", "SWE", "NOR"]):
                skill.handle_teach_me(_msg(region="Northern Europe"))

    assert set(skill._taught_countries) == {"DNK", "SWE", "NOR"}
    assert skill.speak.call_count == 3  # one per country, no repeats requested
    skill.speak_dialog.assert_called_once_with("teaching_finished", {"count": 3})


def test_teach_me_repeats_a_country_when_asked(skill):
    skill.speak = MagicMock()
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(side_effect=["repeat"] + ["ok"] * 10)
    skill.voc_match = MagicMock(side_effect=lambda utt, voc: utt == "repeat")
    with patch.object(type(skill), "resources", property(lambda self: _fake_resources())):
        with patch("geographypractice_skill.resolve_area", return_value=("region", "Europe")):
            with patch("geographypractice_skill.countries_in_area", return_value=["DNK", "SWE"]):
                skill.handle_teach_me(_msg(region="Europe"))

    # 2 countries + 1 extra repeat of the first = 3 speak() calls
    assert skill.speak.call_count == 3
    assert len(skill._taught_countries) == 2


def test_teach_me_no_prompt_after_last_country(skill):
    skill.speak = MagicMock()
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="ok")
    skill.voc_match = MagicMock(return_value=False)
    with patch.object(type(skill), "resources", property(lambda self: _fake_resources())):
        with patch("geographypractice_skill.resolve_area", return_value=("region", "Europe")):
            with patch("geographypractice_skill.countries_in_area", return_value=["DNK", "SWE", "NOR"]):
                skill.handle_teach_me(_msg(region="Europe"))
    # 3 countries -> only 2 continue-prompts (never after the last one)
    assert skill.get_response.call_count == 2


def test_teach_me_caps_at_ten_countries_for_a_large_region(skill):
    skill.speak = MagicMock()
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="ok")
    skill.voc_match = MagicMock(return_value=False)
    big_region = [f"C{i:02d}" for i in range(44)]  # e.g. all of Europe
    with patch.object(type(skill), "resources", property(lambda self: _fake_resources())):
        with patch("geographypractice_skill.resolve_area", return_value=("region", "Europe")):
            with patch("geographypractice_skill.countries_in_area", return_value=big_region):
                with patch("geographypractice_skill.render_country_overview",
                           return_value=("about_country", {"country": "x"})):
                    skill.handle_teach_me(_msg(region="Europe"))
    assert len(skill._taught_countries) == 10


def test_teach_me_unrecognized_region(skill):
    skill.speak = MagicMock()
    skill.speak_dialog = MagicMock()
    with patch("geographypractice_skill.resolve_area", return_value=None):
        skill.handle_teach_me(_msg(region="Narnia"))
    skill.speak_dialog.assert_called_once_with("region_not_understood", {"region": "Narnia"})
    skill.speak.assert_not_called()


def test_quiz_taught_with_nothing_taught_yet(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_quiz_taught(_msg())
    skill.speak_dialog.assert_called_once_with("nothing_taught_yet")


def test_quiz_taught_only_asks_about_taught_countries(skill):
    """Forces the topic choice to always be 'capital' (mocking
    random.choice) so this test can assert deterministically that
    every question is about a taught country, without depending on
    real capital data."""
    skill._taught_countries = ["FRA", "DEU"]
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="Paris")
    with patch("geographypractice_skill.random.choice", return_value="capital"), \
            patch("geographypractice_skill.capital_entry",
                  return_value={"primary": "Paris", "all": ["Paris"]}), \
            patch("geographypractice_skill.country_name", side_effect=lambda cca3, lang: cca3):
        skill.handle_quiz_taught(_msg())
    # 2 taught countries -> exactly 2 questions, not NUM_QUIZ_QUESTIONS(5)
    assert skill.get_response.call_count == 2
    final_call = skill.speak_dialog.call_args_list[-1]
    assert final_call == (("quiz_finished", {"correct": 2, "total": 2}), {})


def test_quiz_taught_uses_border_topic_with_generate_border_question(skill):
    skill._taught_countries = ["FRA"]
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="yes")
    skill.voc_match = MagicMock(side_effect=lambda utt, voc: voc == "yes" and utt == "yes")
    with patch("geographypractice_skill.random.choice", return_value="border"), \
            patch("geographypractice_skill.generate_border_question",
                  return_value=("FRA", "DEU", True)) as gen_border, \
            patch("geographypractice_skill.country_name", side_effect=lambda cca3, lang: cca3):
        skill.handle_quiz_taught(_msg())
    gen_border.assert_called_once_with(country_codes=["FRA"])
    final_call = skill.speak_dialog.call_args_list[-1]
    assert final_call == (("quiz_finished", {"correct": 1, "total": 1}), {})
