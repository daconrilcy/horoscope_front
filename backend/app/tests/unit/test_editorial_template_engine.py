# backend/app/tests/unit/test_editorial_template_engine.py
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from app.prediction.editorial_builder import BestWindow, CategorySummary, EditorialOutput
from app.prediction.editorial_template_engine import EditorialTemplateEngine


@pytest.fixture
def sample_editorial():
    return EditorialOutput(
        local_date=date(2024, 1, 1),
        top3_categories=[
            CategorySummary(code="love", note_20=15, power=0.8, volatility=0.2),
            CategorySummary(code="work", note_20=12, power=0.5, volatility=0.1),
            CategorySummary(code="energy", note_20=18, power=0.9, volatility=0.3),
        ],
        bottom2_categories=[],
        main_pivot=MagicMock(local_time=datetime(2024, 1, 1, 14, 30), severity=0.6),
        best_window=BestWindow(
            start_local=datetime(2024, 1, 1, 10, 0),
            end_local=datetime(2024, 1, 1, 12, 0),
            dominant_category="love"
        ),
        caution_flags={"health": True, "money": False},
        overall_tone="positive",
        top3_contributors_per_category={}
    )

def test_template_renders_correctly(sample_editorial):
    engine = EditorialTemplateEngine()
    output = engine.render(sample_editorial)
    
    assert "2024-01-01" in output.intro
    assert "très porteuse" in output.intro
    assert "Amour & Relations" in output.intro
    
    assert "love" in output.category_summaries
    assert "15/20" in output.category_summaries["love"]
    assert "porteur" in output.category_summaries["love"]
    
    assert "14:30" in output.pivot_phrase
    # SEVERITY_LABELS: low <= 0.25, medium <= 0.5, high <= 0.75, critical > 0.75
    # 0.6 -> labels["high"] -> "majeur"
    assert "majeur" in output.pivot_phrase
    
    assert "10:00" in output.window_phrase
    assert "12:00" in output.window_phrase
    assert "Amour & Relations" in output.window_phrase
    
    assert output.caution_sante is not None
    assert "vigilance" in output.caution_sante
    assert output.caution_argent is None

def test_variables_from_engine(sample_editorial):
    # [AI-Review] Verifies that injected variables match EditorialOutput
    engine = EditorialTemplateEngine()
    
    # Custom sample to verify specific values
    custom_editorial = EditorialOutput(
        local_date=date(2025, 5, 20),
        top3_categories=[
            CategorySummary(code="love", note_20=20, power=1.0, volatility=0.0),
        ],
        bottom2_categories=[],
        main_pivot=MagicMock(local_time=datetime(2025, 5, 20, 8, 15), severity=0.1),
        best_window=None,
        caution_flags={},
        overall_tone="mixed",
        top3_contributors_per_category={}
    )
    
    output = engine.render(custom_editorial)
    assert "2025-05-20" in output.intro
    assert "contrastée" in output.intro # mixed -> contrastée
    assert "20/20" in output.category_summaries["love"]
    assert "très favorable" in output.category_summaries["love"]
    assert "08:15" in output.pivot_phrase
    assert "mineur" in output.pivot_phrase # 0.1 -> mineur

def test_missing_pivot_none(sample_editorial):
    engine = EditorialTemplateEngine()
    # Mock editorial with no pivot/window
    editorial = MagicMock(spec=EditorialOutput)
    editorial.local_date = date(2024, 1, 1)
    editorial.top3_categories = sample_editorial.top3_categories
    editorial.overall_tone = sample_editorial.overall_tone
    editorial.main_pivot = None
    editorial.best_window = None
    editorial.caution_flags = {}
    
    output = engine.render(editorial)
    assert output.pivot_phrase is None
    assert output.window_phrase is None

def test_no_free_text_generated(sample_editorial):
    engine = EditorialTemplateEngine()
    
    def mock_load(lang, name):
        if name == "intro_du_jour":
            return "MOCK {date_local} {overall_tone_label} {top3_labels}"
        if name == "resume_categorie":
            return "MOCK {category_label} {note_20} {band}"
        if name == "phrase_pivot":
            return "MOCK {pivot_time} {pivot_severity_label}"
        if name == "meilleure_fenetre":
            return "MOCK {window_start} {window_end} {dominant_category_label}"
        return "MOCK"
        
    with patch.object(EditorialTemplateEngine, "_load_template", side_effect=mock_load):
        output = engine.render(sample_editorial)
        expected = (
            "MOCK 2024-01-01 très porteuse "
            "Amour & Relations, Travail, Énergie & Vitalité"
        )
        assert output.intro == expected

def test_load_template_fail_explicitly():
    # [AI-Review] Verifies that missing template raises FileNotFoundError
    engine = EditorialTemplateEngine()
    with pytest.raises(FileNotFoundError):
        engine._load_template("fr", "non_existent_template")

def test_caution_sante_prudent_wording(sample_editorial):
    engine = EditorialTemplateEngine()
    output = engine.render(sample_editorial)
    # AC3: ni "diagnostic" ni "médecin" ni impératif médical
    forbidden = ["diagnostic", "médecin", "docteur", "soigner", "guérir", "maladie"]
    for word in forbidden:
        assert word not in output.caution_sante.lower()

def test_caution_argent_prudent_wording():
    engine = EditorialTemplateEngine()
    editorial = MagicMock(spec=EditorialOutput)
    editorial.local_date = date(2024, 1, 1)
    editorial.top3_categories = []
    editorial.overall_tone = "neutral"
    editorial.main_pivot = None
    editorial.best_window = None
    editorial.caution_flags = {"money": True}
    
    output = engine.render(editorial)
    # AC3: ni "investissez" ni "achetez" ni injonction financière directe
    forbidden = ["investissez", "achetez", "vendez", "bourse", "spéculez"]
    for word in forbidden:
        assert word not in output.caution_argent.lower()


def test_legacy_french_codes_are_normalized_for_labels_and_cautions():
    engine = EditorialTemplateEngine()
    editorial = EditorialOutput(
        local_date=date(2024, 1, 1),
        top3_categories=[CategorySummary(code="amour", note_20=14, power=0.8, volatility=0.2)],
        bottom2_categories=[],
        main_pivot=None,
        best_window=None,
        caution_flags={"argent": True, "sante": True},
        overall_tone="neutral",
        top3_contributors_per_category={},
    )

    output = engine.render(editorial, lang="en")

    assert "Love & Relationships" in output.intro
    assert output.caution_sante is not None
    assert output.caution_argent is not None
