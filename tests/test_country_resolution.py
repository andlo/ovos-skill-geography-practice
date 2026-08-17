"""Tests for article-stripping in country name resolution (French,
German, Spanish spoken country names often carry a leading article
that isn't part of the stored CLDR name itself, e.g. 'la France')."""
from unittest.mock import MagicMock


def _msg(**data):
    m = MagicMock()
    m.data = data
    return m


def test_strip_article_french(skill):
    assert skill._strip_article("la France", "fr-fr") == "France"
    assert skill._strip_article("le Japon", "fr-fr") == "Japon"
    assert skill._strip_article("les États-Unis", "fr-fr") == "États-Unis"
    assert skill._strip_article("l'Allemagne", "fr-fr") == "Allemagne"


def test_strip_article_german(skill):
    assert skill._strip_article("die Türkei", "de-de") == "Türkei"
    assert skill._strip_article("der Iran", "de-de") == "Iran"


def test_strip_article_spanish(skill):
    assert skill._strip_article("la India", "es-es") == "India"
    assert skill._strip_article("el Perú", "es-es") == "Perú"


def test_strip_article_leaves_english_untouched(skill):
    assert skill._strip_article("France", "en-us") == "France"


def test_resolve_country_with_french_article(skill, monkeypatch):
    from geographypractice_skill import GeographyPractice
    monkeypatch.setattr(GeographyPractice, "lang", "fr-fr", raising=False)
    assert skill._resolve_country("la France", "fr-fr") == "FRA"
