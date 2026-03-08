# backend/app/tests/unit/test_editorial_i18n.py
import re
from datetime import date
from pathlib import Path

import pytest

from app.prediction.editorial_builder import CategorySummary, EditorialOutput
from app.prediction.editorial_template_engine import EditorialTemplateEngine

# Fix path to be relative to this file
TEMPLATE_BASE = Path(__file__).parent.parent.parent / "prediction" / "editorial_templates"

def extract_placeholders(text: str) -> set[str]:
    return set(re.findall(r'\{(\w+)\}', text))

def test_fr_en_same_placeholders():
    """AC1, AC2 - Ensure FR and EN templates have exactly the same placeholders."""
    fr_base = TEMPLATE_BASE / "fr"
    en_base = TEMPLATE_BASE / "en"
    
    assert fr_base.exists(), f"FR templates directory missing at {fr_base}"
    assert en_base.exists(), f"EN templates directory missing at {en_base}"
    
    fr_files = list(fr_base.glob("*.txt"))
    for fr_file in fr_files:
        en_file = en_base / fr_file.name
        assert en_file.exists(), f"Missing EN mirror for {fr_file.name}"
        
        fr_text = fr_file.read_text(encoding="utf-8")
        en_text = en_file.read_text(encoding="utf-8")
        
        fr_placeholders = extract_placeholders(fr_text)
        en_placeholders = extract_placeholders(en_text)
        
        assert fr_placeholders == en_placeholders, (
            f"Placeholder mismatch in {fr_file.name}: "
            f"FR {fr_placeholders} != EN {en_placeholders}"
        )

def test_no_calculatory_logic_in_templates():
    """AC2 - Ensure templates only contain text and placeholders, no logic."""
    forbidden_patterns = [
        r'\{% if', r'\{% for', r'\{% set', r'\{\{', # Jinja-like
        r'if ', r'else', r'for ', r'=', r'def ', r'import ' # Python-like
    ]
    
    for lang in ["fr", "en"]:
        base = TEMPLATE_BASE / lang
        for tpl_file in base.glob("*.txt"):
            content = tpl_file.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                if re.search(pattern, content):
                    # Ignore 'if' in words like 'identified'
                    if pattern == 'if ' and 'identified' in content:
                        continue
                    pytest.fail(f"Found forbidden logic pattern '{pattern}' in {tpl_file}")

def test_engine_selects_correct_lang():
    """AC5 - Ensure EditorialTemplateEngine selects the correct language files."""
    engine = EditorialTemplateEngine()
    
    # Mock editorial
    editorial = EditorialOutput(
        local_date=date(2024, 1, 1),
        top3_categories=[
            CategorySummary(code="love", note_20=15, power=0.8, volatility=0.2),
        ],
        bottom2_categories=[],
        main_pivot=None,
        best_window=None,
        caution_flags={},
        overall_tone="positive",
        top3_contributors_per_category={}
    )
    
    # Render in FR
    out_fr = engine.render(editorial, lang="fr")
    assert "Votre journée" in out_fr.intro
    assert "points forts" in out_fr.intro.lower()
    
    # Render in EN
    out_en = engine.render(editorial, lang="en")
    assert "Your day" in out_en.intro
    assert "strong points" in out_en.intro.lower()
    assert "Love & Relationships" in out_en.intro
