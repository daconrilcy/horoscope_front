"""Tests unitaires pour le service d'export PDF."""

from __future__ import annotations

from unittest.mock import MagicMock

from app.infra.db.models.user_natal_interpretation import (
    InterpretationLevel,
    UserNatalInterpretationModel,
)
from app.services.natal_pdf_export_service import NatalPdfExportService


class TestNatalPdfExportService:
    def test_render_html_basic(self):
        data = {
            "title": "Test Title",
            "summary": "Test Summary",
            "sections": [],
            "render_sections": [
                {
                    "heading": "S1",
                    "paragraphs": ["C1"],
                    "blocks": [
                        {"kind": "head", "text": "C1", "force_page_break": False},
                    ],
                    "force_page_break": False,
                }
            ],
            "highlights": ["H1"],
            "advice": ["A1"],
            "evidence": [],
            "meta": {
                "chart_id": "c1",
                "level": "short",
                "persona_name": "Standard",
                "created_at": "04/03/2026 20:00",
                "locale": "fr",
                "sun_sign_label": "Lion",
                "ascendant_sign_label": "Scorpion",
            },
            "disclaimers": ["D1"],
            "generated_at": "04/03/2026 21:00",
            "config": {},
            "config_runtime": {},
        }
        html = NatalPdfExportService._render_html(data, "fr")
        assert "Test Title" in html
        assert "Test Summary" in html
        assert "S1" in html
        assert "C1" in html
        assert "H1" in html
        assert "A1" in html
        assert "Lion" in html
        assert "Scorpion" in html

    def test_convert_html_to_pdf(self):
        html = "<html><body><h1>Test</h1></body></html>"
        pdf_bytes = NatalPdfExportService._convert_html_to_pdf(html)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # Check PDF header
        assert pdf_bytes.startswith(b"%PDF-")

    def test_generate_pdf_integration(self):
        # Mock DB session
        mock_db = MagicMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None # No custom template
        
        interpretation = UserNatalInterpretationModel(
            chart_id="test-chart",
            level=InterpretationLevel.SHORT,
            persona_name="Test Persona",
            interpretation_payload={
                "title": "Title",
                "summary": "Summary",
                "sections": [{"heading": "H", "content": "C"}],
                "highlights": ["Hi"],
                "advice": ["Ad"],
            },
            created_at=MagicMock()
        )
        interpretation.created_at.strftime.return_value = "01/01/2026"
        
        pdf_bytes = NatalPdfExportService.generate_pdf(mock_db, interpretation)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF-")

    def test_generate_pdf_disables_sections_start_new_page_when_intro_overflows(self):
        mock_db = MagicMock()

        template_model = MagicMock()
        template_model.key = "default_natal"
        template_model.config_json = {
            "sections_start_new_page": True,
            "page_budget_lines": 24,
            "paragraph_spacing_lines": 0,
            "section_tail_spacing_lines": 0,
        }
        chart_result = MagicMock()
        chart_result.result_payload = {}

        r1 = MagicMock()
        r1.scalar_one_or_none.return_value = template_model
        r2 = MagicMock()
        r2.scalar_one_or_none.return_value = chart_result
        mock_db.execute.side_effect = [r1, r2]

        interpretation = UserNatalInterpretationModel(
            chart_id="test-chart",
            level=InterpretationLevel.SHORT,
            persona_name="Test Persona",
            interpretation_payload={
                "title": "Title",
                "summary": "Summary " * 120,
                "sections": [{"heading": "H", "content": "C"}],
                "highlights": ["Hi"] * 20,
                "advice": ["Ad"],
            },
            created_at=MagicMock(),
        )
        interpretation.created_at.strftime.return_value = "01/01/2026"

        html = NatalPdfExportService._render_html(
            {
                **{
                    "title": "T",
                    "summary": "S",
                    "sections": [],
                    "render_sections": [],
                    "highlights": [],
                    "advice": [],
                    "evidence": [],
                    "meta": {
                        "chart_id": "x",
                        "level": "short",
                        "persona_name": "Standard",
                        "created_at": "01/01/2026",
                        "locale": "fr",
                        "sun_sign_label": None,
                        "ascendant_sign_label": None,
                    },
                    "disclaimers": [],
                    "generated_at": "01/01/2026",
                    "config": {},
                    "config_runtime": {"sections_start_new_page": False},
                }
            },
            "fr",
        )
        assert "<pdf:nextpage />" not in html

        pdf_bytes = NatalPdfExportService.generate_pdf(
            mock_db,
            interpretation,
            template_key="default_natal",
        )
        assert len(pdf_bytes) > 0

    def test_generate_pdf_with_template_key_found_does_not_raise(self):
        mock_db = MagicMock()

        template_model = MagicMock()
        template_model.key = "default_natal"
        template_model.config_json = {}
        chart_result = MagicMock()
        chart_result.result_payload = {}

        r1 = MagicMock()
        r1.scalar_one_or_none.return_value = template_model
        r2 = MagicMock()
        r2.scalar_one_or_none.return_value = chart_result
        mock_db.execute.side_effect = [r1, r2]

        interpretation = UserNatalInterpretationModel(
            chart_id="test-chart",
            level=InterpretationLevel.SHORT,
            persona_name="Test Persona",
            interpretation_payload={
                "title": "Title",
                "summary": "Summary",
                "sections": [{"heading": "H", "content": "C"}],
                "highlights": ["Hi"],
                "advice": ["Ad"],
            },
            created_at=MagicMock(),
        )
        interpretation.created_at.strftime.return_value = "01/01/2026"

        pdf_bytes = NatalPdfExportService.generate_pdf(
            mock_db,
            interpretation,
            template_key="default_natal",
        )
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF-")

    def test_extract_sun_and_ascendant_signs_from_natal_result_payload(self):
        payload = {
            "planet_positions": [
                {"planet_code": "sun", "sign_code": "leo"},
                {"planet_code": "moon", "sign_code": "aries"},
            ],
            "houses": [
                {"number": 1, "cusp_longitude": 220.0},
                {"number": 2, "cusp_longitude": 250.0},
            ],
        }

        sun, ascendant = NatalPdfExportService._extract_sun_and_ascendant_signs(payload)

        assert sun == "leo"
        assert ascendant == "scorpio"

    def test_prepare_paginated_sections_chunks_very_long_section_content(self):
        long_content = "x" * 8000
        sections = [
            {"heading": "S1", "content": "court"},
            {"heading": "Tres longue section", "content": long_content},
        ]

        prepared = NatalPdfExportService._prepare_paginated_sections(
            sections=sections,
            title="Titre",
            summary="Resume",
            highlights=["h1", "h2"],
            meta_line="meta",
            max_paragraph_chars=NatalPdfExportService.MAX_PARAGRAPH_CHARS,
            split_paragraphs_enabled=True,
        )

        assert prepared[0]["force_page_break"] is False
        assert len(prepared[1]["paragraphs"]) > 1

    def test_prepare_paginated_sections_starts_new_page_when_less_than_half_fits(self):
        old_page_lines = NatalPdfExportService.ESTIMATED_PAGE_LINES
        old_intro_estimator = NatalPdfExportService._estimate_intro_lines
        NatalPdfExportService.ESTIMATED_PAGE_LINES = 20
        NatalPdfExportService._estimate_intro_lines = staticmethod(lambda *_args, **_kwargs: 0)
        try:
            sections = [
                {"heading": "Bloc 1", "content": "x" * 820},
                {"heading": "Bloc 2", "content": "x" * 820},
            ]

            prepared = NatalPdfExportService._prepare_paginated_sections(
                sections=sections,
                title="",
                summary="",
                highlights=[],
                meta_line="",
                max_paragraph_chars=NatalPdfExportService.MAX_PARAGRAPH_CHARS,
                split_paragraphs_enabled=True,
            )
        finally:
            NatalPdfExportService.ESTIMATED_PAGE_LINES = old_page_lines
            NatalPdfExportService._estimate_intro_lines = old_intro_estimator

        assert prepared[0]["force_page_break"] is False
        assert prepared[1]["force_page_break"] is True

    def test_sanitize_inline_text_removes_json_artifacts(self):
        raw = "Texte initial ”},{ suite  bullet"
        clean = NatalPdfExportService._sanitize_inline_text(raw)
        assert "”},{" not in clean
        assert "" not in clean
        assert "Texte initial" in clean

    def test_sanitize_inline_text_strips_trailing_json_suffix(self):
        raw = 'Texte de fin utile "}],'
        clean = NatalPdfExportService._sanitize_inline_text(raw)
        assert clean == "Texte de fin utile"

    def test_split_paragraphs_preserves_paragraph_boundaries(self):
        raw = "Premier paragraphe.\n\nDeuxieme paragraphe.\r\n\r\nTroisieme ligne."
        paragraphs = NatalPdfExportService._split_paragraphs(
            raw,
            max_chars=NatalPdfExportService.MAX_PARAGRAPH_CHARS,
            split_enabled=True,
        )
        assert paragraphs == [
            "Premier paragraphe.",
            "Deuxieme paragraphe.",
            "Troisieme ligne.",
        ]

    def test_split_paragraphs_chunks_very_long_paragraph(self):
        long_sentence = "Phrase longue. " * 300
        paragraphs = NatalPdfExportService._split_paragraphs(
            long_sentence,
            max_chars=NatalPdfExportService.MAX_PARAGRAPH_CHARS,
            split_enabled=True,
        )
        assert len(paragraphs) > 1
        assert all(len(p) <= NatalPdfExportService.MAX_PARAGRAPH_CHARS for p in paragraphs)

    def test_prepare_paginated_sections_uses_max_paragraph_chars_override(self):
        content = "Phrase longue. " * 180
        sections = [{"heading": "Section", "content": content}]
        prepared = NatalPdfExportService._prepare_paginated_sections(
            sections=sections,
            title="Titre",
            summary="Resume",
            highlights=[],
            meta_line="meta",
            max_paragraph_chars=300,
            split_paragraphs_enabled=True,
        )
        assert len(prepared[0]["paragraphs"]) > 1
        assert all(len(p) <= 300 for p in prepared[0]["paragraphs"])

    def test_prepare_paginated_sections_inserts_page_break_before_paragraph_block(self):
        old_page_lines = NatalPdfExportService.ESTIMATED_PAGE_LINES
        old_intro_estimator = NatalPdfExportService._estimate_intro_lines
        NatalPdfExportService.ESTIMATED_PAGE_LINES = 20
        NatalPdfExportService._estimate_intro_lines = staticmethod(lambda *_args, **_kwargs: 0)
        try:
            sections = [
                {"heading": "Bloc 1", "content": "x" * 500},
                {"heading": "Bloc 2", "content": "Premier.\n\n" + ("x" * 700)},
            ]
            prepared = NatalPdfExportService._prepare_paginated_sections(
                sections=sections,
                title="",
                summary="",
                highlights=[],
                meta_line="",
                max_paragraph_chars=5000,
                split_paragraphs_enabled=True,
            )
        finally:
            NatalPdfExportService.ESTIMATED_PAGE_LINES = old_page_lines
            NatalPdfExportService._estimate_intro_lines = old_intro_estimator

        second_blocks = prepared[1]["blocks"]
        assert second_blocks[0]["kind"] == "head"
        assert second_blocks[0]["force_page_break"] is False
        assert second_blocks[1]["kind"] == "paragraph"
        assert second_blocks[1]["force_page_break"] is True

    def test_prepare_paginated_sections_respects_runtime_page_budget_and_head_extra(self):
        old_intro_estimator = NatalPdfExportService._estimate_intro_lines
        NatalPdfExportService._estimate_intro_lines = staticmethod(lambda *_args, **_kwargs: 0)
        try:
            sections = [
                {"heading": "A", "content": "x" * 1100},
                {"heading": "B", "content": "Premier paragraphe."},
            ]
            prepared = NatalPdfExportService._prepare_paginated_sections(
                sections=sections,
                title="",
                summary="",
                highlights=[],
                meta_line="",
                max_paragraph_chars=5000,
                split_paragraphs_enabled=True,
                page_budget_lines=20,
                section_head_extra_lines=2,
            )
        finally:
            NatalPdfExportService._estimate_intro_lines = old_intro_estimator

        second_head = prepared[1]["blocks"][0]
        assert second_head["kind"] == "head"
        assert second_head["force_page_break"] is True

    def test_split_paragraphs_disabled_returns_single_flattened_paragraph(self):
        raw = "A.\n\nB.\n\nC."
        paragraphs = NatalPdfExportService._split_paragraphs(
            raw,
            max_chars=10,
            split_enabled=False,
        )
        assert paragraphs == ["A. B. C."]

    def test_prepare_paginated_sections_sections_start_new_page_ignores_intro_remainder(self):
        old_intro_estimator = NatalPdfExportService._estimate_intro_lines
        NatalPdfExportService._estimate_intro_lines = staticmethod(lambda *_args, **_kwargs: 19)
        try:
            sections = [{"heading": "Bloc", "content": "Premier paragraphe."}]
            without_reset = NatalPdfExportService._prepare_paginated_sections(
                sections=sections,
                title="",
                summary="",
                highlights=[],
                meta_line="",
                max_paragraph_chars=5000,
                split_paragraphs_enabled=True,
                page_budget_lines=20,
                section_head_extra_lines=1,
                sections_start_new_page=False,
            )
            with_reset = NatalPdfExportService._prepare_paginated_sections(
                sections=sections,
                title="",
                summary="",
                highlights=[],
                meta_line="",
                max_paragraph_chars=5000,
                split_paragraphs_enabled=True,
                page_budget_lines=20,
                section_head_extra_lines=1,
                sections_start_new_page=True,
            )
        finally:
            NatalPdfExportService._estimate_intro_lines = old_intro_estimator

        assert without_reset[0]["blocks"][0]["force_page_break"] is True
        assert with_reset[0]["blocks"][0]["force_page_break"] is False

    def test_generate_pdf_sections_start_new_page_effective_uses_min_remaining_threshold(self):
        mock_db = MagicMock()

        template_model = MagicMock()
        template_model.key = "default_natal"
        template_model.config_json = {
            "sections_start_new_page": True,
            "sections_start_new_page_min_remaining_lines": 10,
            "page_budget_lines": 24,
        }
        chart_result = MagicMock()
        chart_result.result_payload = {}
        r1 = MagicMock()
        r1.scalar_one_or_none.return_value = template_model
        r2 = MagicMock()
        r2.scalar_one_or_none.return_value = chart_result
        mock_db.execute.side_effect = [r1, r2]

        interpretation = UserNatalInterpretationModel(
            chart_id="test-chart",
            level=InterpretationLevel.SHORT,
            persona_name="Test Persona",
            interpretation_payload={
                "title": "Title",
                "summary": "Summary",
                "sections": [{"heading": "H", "content": "C"}],
                "highlights": ["Hi"],
                "advice": ["Ad"],
            },
            created_at=MagicMock(),
        )
        interpretation.created_at.strftime.return_value = "01/01/2026"

        captured_data: dict[str, object] = {}
        old_render = NatalPdfExportService._render_html
        old_convert = NatalPdfExportService._convert_html_to_pdf
        old_intro_estimate = NatalPdfExportService._estimate_intro_lines
        NatalPdfExportService._estimate_intro_lines = staticmethod(lambda *_args, **_kwargs: 16)
        NatalPdfExportService._render_html = staticmethod(
            lambda data, _locale, _template: captured_data.update(data) or "<html></html>"
        )
        NatalPdfExportService._convert_html_to_pdf = staticmethod(lambda _html: b"%PDF-test")
        try:
            _pdf_bytes = NatalPdfExportService.generate_pdf(
                mock_db,
                interpretation,
                template_key="default_natal",
            )
        finally:
            NatalPdfExportService._render_html = old_render
            NatalPdfExportService._convert_html_to_pdf = old_convert
            NatalPdfExportService._estimate_intro_lines = old_intro_estimate

        config_runtime = captured_data["config_runtime"]
        assert isinstance(config_runtime, dict)
        assert config_runtime["sections_start_new_page"] is True
