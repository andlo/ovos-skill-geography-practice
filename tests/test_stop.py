"""Stop support: a quiz ends when stop is requested for its session,
instead of asking the next question until ovos-core times it out."""
from unittest.mock import MagicMock, patch

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session


def _msg(session_id, **data):
    return Message("test", data, {"session": Session(session_id).serialize()})


def test_stop_ends_the_quiz_in_that_session(skill):
    skill.speak_dialog = MagicMock()
    asked = []

    def answer(*args, **kwargs):
        asked.append(args)
        if len(asked) == 2:
            assert skill.can_stop(_msg("s1"))
            assert not skill.can_stop(_msg("other"))
            assert skill.stop_session(Session("s1")) is True
            return None
        return "Paris"

    skill.get_response = MagicMock(side_effect=answer)
    with patch("geographypractice_skill.random.choice", return_value="FRA"):
        skill.handle_quiz_capitals(_msg("s1"))
    assert len(asked) == 2
    said = [c[0][0] for c in skill.speak_dialog.call_args_list]
    assert "quiz_finished" not in said and "quiz_no_answer" not in said
    assert not skill.can_stop(_msg("s1"))


def test_nothing_to_stop_when_idle(skill):
    assert not skill.can_stop(_msg("s1"))
    assert skill.stop_session(Session("s1")) is False
