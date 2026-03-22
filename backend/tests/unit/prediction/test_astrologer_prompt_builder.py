from app.prediction.astrologer_prompt_builder import AstrologerPromptBuilder
from app.prompts.common_context import PromptCommonContext


def test_prompt_builder_contains_style():
    builder = AstrologerPromptBuilder()
    ctx = PromptCommonContext(
        precision_level="précision complète",
        astrologer_profile={"tonality": "bienveillant"},
        period_covered="journée",
        today_date="2026-03-20",
        use_case_name="Test",
        use_case_key="test",
        natal_interpretation="Vous êtes un Lion fier.",
    )

    prompt = builder.build(
        ctx,
        [],
        "vedique",
        "fr",
        day_climate={"label": "Journée contrastée", "tone": "mixed"},
        best_window={"time_range": "10:00–12:00", "label": "Pic du jour", "why": "élan net"},
        turning_point={"time": "15:30", "title": "Bascule", "what_changes": "Le rythme change"},
    )
    assert "nakshatra" in prompt
    assert "Lion fier" in prompt
    assert "daily_advice" in prompt
    assert "main_turning_point_narrative" in prompt
    assert "5 à 7 phrases" in prompt
    assert "3 ou 4 phrases" in prompt


def test_prompt_builder_formats_windows():
    builder = AstrologerPromptBuilder()
    ctx = PromptCommonContext(
        precision_level="H1",
        astrologer_profile={"tonality": "fun"},
        period_covered="day",
        today_date="today",
        use_case_name="U",
        use_case_key="K",
        natal_interpretation="X",
    )
    windows = [
        {
            "period_key": "matin",
            "time_range": "06:00-12:00",
            "regime": "progression",
            "top_domains": ["pro"],
        }
    ]

    prompt = builder.build(ctx, windows, "standard", "fr")
    assert "[matin]" in prompt
    assert "06:00-12:00" in prompt
    assert "progression" in prompt
    assert "Orientation pratique" in prompt


def test_prompt_builder_empty_natal_data_shows_unavailable():
    builder = AstrologerPromptBuilder()
    ctx = PromptCommonContext(
        precision_level="précision complète",
        astrologer_profile={"tonality": "bienveillant"},
        period_covered="journée",
        today_date="2026-03-20",
        use_case_name="Test",
        use_case_key="test",
        natal_interpretation=None,
        natal_data={},  # present but empty → falsy → triggers "non disponible" branch
    )

    prompt = builder.build(ctx, [], "standard", "fr")
    assert "non disponible" in prompt


def test_prompt_builder_includes_structural_day_context():
    builder = AstrologerPromptBuilder()
    ctx = PromptCommonContext(
        precision_level="précision complète",
        astrologer_profile={"tonality": "bienveillant"},
        period_covered="journée",
        today_date="2026-03-20",
        use_case_name="Test",
        use_case_key="test",
        natal_interpretation="Vous avez besoin d'un cap clair.",
    )

    prompt = builder.build(
        common_context=ctx,
        time_windows=[],
        astrologer_profile_key="standard",
        lang="fr",
        day_climate={
            "label": "Journée contrastée",
            "tone": "mixed",
            "intensity": 7.5,
            "stability": 5.0,
            "summary": "Le climat alterne entre élan et réajustement.",
            "top_domains": ["relations_echanges"],
            "watchout": "energie_bienetre",
        },
        best_window={
            "time_range": "10:00–12:00",
            "label": "Votre meilleur créneau",
            "why": "La dynamique se fluidifie.",
            "recommended_actions": ["prendre un rendez-vous"],
        },
        turning_point={
            "time": "15:30",
            "title": "Bascule relationnelle",
            "change_type": "recomposition",
            "what_changes": "Le focus se déplace vers l'échange.",
            "affected_domains": ["relations_echanges"],
            "do": "clarifier",
            "avoid": "surcharger",
        },
        domain_ranking=[{"key": "relations_echanges", "label": "Relations et échanges"}],
    )

    assert "Climat général" in prompt
    assert "Relations et échanges" in prompt
    assert "10:00–12:00" in prompt
    assert "Bascule relationnelle" in prompt
