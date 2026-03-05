"""Tests unitaires pour disclaimer_registry et injection dans NatalInterpretationResponse.
Story 30-8 T5.
"""

from __future__ import annotations

from app.services.disclaimer_registry import get_disclaimers


class TestGetDisclaimers:
    def test_fr_fr_returns_french_disclaimer(self):
        result = get_disclaimers("fr-FR")
        assert len(result) >= 3
        assert "astrolog" in result[0].lower()
        joined = " ".join(result).lower()
        assert "médical" in joined
        assert "juridique" in joined
        assert "financier" in joined
        assert "libre arbitre" in joined

    def test_en_us_returns_english_disclaimer(self):
        result = get_disclaimers("en-US")
        assert len(result) >= 3
        assert "astrolog" in result[0].lower()
        joined = " ".join(result).lower()
        assert "medical" in joined
        assert "legal" in joined
        assert "financial" in joined
        assert "free will" in joined

    def test_fr_be_returns_french_disclaimer(self):
        result = get_disclaimers("fr-BE")
        assert len(result) >= 3
        assert "astrolog" in result[0].lower()

    def test_fr_ch_returns_french_disclaimer(self):
        result = get_disclaimers("fr-CH")
        assert len(result) >= 3
        assert "astrolog" in result[0].lower()

    def test_en_gb_returns_english_disclaimer(self):
        result = get_disclaimers("en-GB")
        assert len(result) >= 3
        assert "astrolog" in result[0].lower()

    def test_en_au_returns_english_disclaimer(self):
        result = get_disclaimers("en-AU")
        assert len(result) >= 3
        assert "astrolog" in result[0].lower()

    def test_unknown_locale_falls_back_to_default(self):
        result = get_disclaimers("de-DE")
        assert len(result) >= 1
        # default is French
        assert "astrolog" in result[0].lower()

    def test_empty_locale_falls_back_to_default(self):
        result = get_disclaimers("")
        assert len(result) >= 1

    def test_returns_list(self):
        result = get_disclaimers("fr-FR")
        assert isinstance(result, list)
        assert all(isinstance(d, str) for d in result)

    def test_non_empty_strings(self):
        for locale in ["fr-FR", "en-US", "fr-BE", "fr-CH", "en-GB", "en-AU"]:
            result = get_disclaimers(locale)
            assert all(len(d) > 0 for d in result), f"Empty string in {locale}"
