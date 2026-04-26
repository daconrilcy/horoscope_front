"""Valide les helpers partages de texte entre guidance et consultation."""

from app.api.v1.schemas.routers.public.consultation import ConsultationBlockKind
from app.services.llm_generation.consultation_generation_service import (
    ConsultationGenerationService,
)
from app.services.llm_generation.shared.contextual_text import (
    StructuredTextBlock,
    compose_structured_guidance_full_text,
    normalize_structured_string_list,
    parse_structured_guidance_blocks,
)


def test_compose_structured_guidance_full_text_keeps_canonical_sections() -> None:
    """Le texte guidance canonique doit conserver synthese, points et conseils."""
    full_text = compose_structured_guidance_full_text(
        "Synthese utile.",
        ["Point A", "Point B"],
        ["Conseil A"],
    )

    assert "Synthese utile." in full_text
    assert "Points cles :" in full_text
    assert "- Point A" in full_text
    assert "Conseils :" in full_text
    assert "- Conseil A" in full_text


def test_normalize_structured_string_list_accepts_string_and_list() -> None:
    """Le normaliseur partage doit supporter les sorties LLM les plus courantes."""
    assert normalize_structured_string_list("  Point unique  ") == ["Point unique"]
    assert normalize_structured_string_list([" A ", "", "B"]) == ["A", "B"]


def test_parse_structured_guidance_blocks_extracts_titles_paragraphs_and_bullets() -> None:
    """Le parser partage doit produire des blocs structurels stables."""
    blocks = parse_structured_guidance_blocks(
        "## Vision\n\nUn paragraphe **important**.\n\n- Premier point\n- Second point\n"
    )

    assert blocks == [
        StructuredTextBlock(kind="title", text="Vision"),
        StructuredTextBlock(kind="paragraph", text="Un paragraphe important"),
        StructuredTextBlock(kind="bullet_list", items=["Premier point", "Second point"]),
    ]


def test_consultation_service_maps_shared_blocks_to_consultation_schema() -> None:
    """La consultation doit reutiliser les blocs partages sans redefinir le parsing."""
    blocks = ConsultationGenerationService._parse_section_blocks(
        "## Vision\n\nUne lecture.\n\n- Point 1\n- Point 2\n"
    )

    assert [block.kind for block in blocks] == [
        ConsultationBlockKind.title,
        ConsultationBlockKind.paragraph,
        ConsultationBlockKind.bullet_list,
    ]
    assert blocks[0].text == "Vision"
    assert blocks[1].text == "Une lecture"
    assert blocks[2].items == ["Point 1", "Point 2"]
