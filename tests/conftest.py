"""Shared pytest fixtures for the geography-practice skill test suite."""
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_INIT_PATH = Path(__file__).resolve().parents[1] / "__init__.py"
_spec = importlib.util.spec_from_file_location("geographypractice_skill", _INIT_PATH)
_module = importlib.util.module_from_spec(_spec)
sys.modules["geographypractice_skill"] = _module
_spec.loader.exec_module(_module)

GeographyPractice = _module.GeographyPractice


@pytest.fixture
def skill(monkeypatch):
    s = GeographyPractice.__new__(GeographyPractice)
    s.log = MagicMock()
    s.skill_id = "ovos-skill-geography-practice.test"
    s.status = MagicMock()
    s._bus = MagicMock()
    monkeypatch.setattr(GeographyPractice, "lang", "en-us", raising=False)
    s.res_dir = str(Path(__file__).resolve().parents[1])
    s._lang_resources = {}
    s._voc_cache = {}  # needed by voc_match()/voc_list(), bypassed by __new__()
    s._taught_countries = []  # normally set by initialize(), which __new__() bypasses
    return s
