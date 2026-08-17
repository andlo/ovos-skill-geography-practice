"""Tests for the three quiz modes - get_response() and (where used)
the generator functions are mocked/patched so scoring/flow logic is
tested deterministically."""
from unittest.mock import MagicMock, patch


def _msg(**data):
    m = MagicMock()
    m.data = data
    return m


def test_quiz_capitals_all_correct(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="Paris")
    with patch("geographypractice_skill.random.choice", return_value="FRA"):
        skill.handle_quiz_capitals(_msg())
    correct_calls = [c for c in skill.speak_dialog.call_args_list if c[0][0] == "quiz_correct"]
    assert len(correct_calls) == 5
    final_call = skill.speak_dialog.call_args_list[-1]
    assert final_call == (("quiz_finished", {"correct": 5, "total": 5}), {})


def test_quiz_capitals_all_wrong(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="Nowhere")
    with patch("geographypractice_skill.random.choice", return_value="FRA"):
        skill.handle_quiz_capitals(_msg())
    final_call = skill.speak_dialog.call_args_list[-1]
    assert final_call == (("quiz_finished", {"correct": 0, "total": 5}), {})
    incorrect_calls = [c for c in skill.speak_dialog.call_args_list if c[0][0] == "quiz_incorrect_capital"]
    assert incorrect_calls[0] == (("quiz_incorrect_capital", {"country": "France", "capital": "Paris"}), {})


def test_quiz_capitals_no_response_counts_as_wrong_but_does_not_crash(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value=None)
    with patch("geographypractice_skill.random.choice", return_value="FRA"):
        skill.handle_quiz_capitals(_msg())
    no_answer_calls = [c for c in skill.speak_dialog.call_args_list if c[0][0] == "quiz_no_answer"]
    assert len(no_answer_calls) == 5


def test_quiz_continents_all_correct(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="Africa")
    with patch("geographypractice_skill.random.choice", return_value="KEN"):
        skill.handle_quiz_continents(_msg())
    final_call = skill.speak_dialog.call_args_list[-1]
    assert final_call == (("quiz_finished", {"correct": 5, "total": 5}), {})


def test_quiz_continents_wrong_answer_names_the_right_one(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="Europe")
    with patch("geographypractice_skill.random.choice", return_value="KEN"):
        skill.handle_quiz_continents(_msg())
    incorrect_calls = [c for c in skill.speak_dialog.call_args_list if c[0][0] == "quiz_incorrect_continent"]
    assert incorrect_calls[0] == (("quiz_incorrect_continent", {"country": "Kenya", "continent": "Africa"}), {})


def test_quiz_borders_true_question_correct_yes_answer(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="yes")
    with patch("geographypractice_skill.generate_border_question", return_value=("FRA", "DEU", True)):
        skill.handle_quiz_borders(_msg())
    correct_calls = [c for c in skill.speak_dialog.call_args_list if c[0][0] == "quiz_correct"]
    assert len(correct_calls) == 5


def test_quiz_borders_false_question_correct_no_answer(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="no")
    with patch("geographypractice_skill.generate_border_question", return_value=("FRA", "JPN", False)):
        skill.handle_quiz_borders(_msg())
    correct_calls = [c for c in skill.speak_dialog.call_args_list if c[0][0] == "quiz_correct"]
    assert len(correct_calls) == 5


def test_quiz_borders_wrong_yes_when_answer_is_no(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="yes")
    with patch("geographypractice_skill.generate_border_question", return_value=("FRA", "JPN", False)):
        skill.handle_quiz_borders(_msg())
    incorrect_calls = [c for c in skill.speak_dialog.call_args_list if c[0][0] == "quiz_incorrect_border_no"]
    assert incorrect_calls[0] == (("quiz_incorrect_border_no", {"country": "France", "other": "Japan"}), {})


def test_quiz_borders_wrong_no_when_answer_is_yes(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="no")
    with patch("geographypractice_skill.generate_border_question", return_value=("FRA", "DEU", True)):
        skill.handle_quiz_borders(_msg())
    incorrect_calls = [c for c in skill.speak_dialog.call_args_list if c[0][0] == "quiz_incorrect_border_yes"]
    assert incorrect_calls[0] == (("quiz_incorrect_border_yes", {"country": "France", "other": "Germany"}), {})


def test_quiz_borders_question_dialog_receives_both_country_names(skill):
    skill.speak_dialog = MagicMock()
    skill.get_response = MagicMock(return_value="yes")
    with patch("geographypractice_skill.generate_border_question", return_value=("FRA", "DEU", True)):
        skill.handle_quiz_borders(_msg())
    dialog_name = skill.get_response.call_args_list[0][1]["dialog"]
    data = skill.get_response.call_args_list[0][1]["data"]
    assert dialog_name == "quiz_question_border"
    assert data == {"country": "France", "other": "Germany"}
