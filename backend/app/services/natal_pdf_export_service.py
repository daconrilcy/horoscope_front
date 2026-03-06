from __future__ import annotations

import io
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session
from xhtml2pdf import pisa

from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.pdf_template import PdfTemplateModel, PdfTemplateStatus
from app.infra.db.models.user_natal_interpretation import UserNatalInterpretationModel
from app.services.disclaimer_registry import get_disclaimers

logger = logging.getLogger(__name__)


class NatalPdfExportService:
    ESTIMATED_PAGE_LINES = 44
    ESTIMATED_HEADING_CHARS_PER_LINE = 42
    ESTIMATED_CONTENT_CHARS_PER_LINE = 82
    MAX_PARAGRAPH_CHARS = 1000
    STRICT_SECTION_NEW_PAGE = False
    SPLIT_PARAGRAPHS_ENABLED = True
    SECTIONS_START_NEW_PAGE = True
    MIN_LINES_AFTER_HEADING = 3
    SECTION_HEAD_EXTRA_LINES = 1
    PARAGRAPH_SPACING_LINES = 0
    SECTION_TAIL_SPACING_LINES = 1
    SECTIONS_START_NEW_PAGE_MIN_REMAINING_LINES = 10
    PAGINATION_DEBUG = False

    SIGN_LABELS: dict[str, dict[str, str]] = {
        "fr": {
            "aries": "Belier",
            "taurus": "Taureau",
            "gemini": "Gemeaux",
            "cancer": "Cancer",
            "leo": "Lion",
            "virgo": "Vierge",
            "libra": "Balance",
            "scorpio": "Scorpion",
            "sagittarius": "Sagittaire",
            "capricorn": "Capricorne",
            "aquarius": "Verseau",
            "pisces": "Poissons",
        },
        "en": {
            "aries": "Aries",
            "taurus": "Taurus",
            "gemini": "Gemini",
            "cancer": "Cancer",
            "leo": "Leo",
            "virgo": "Virgo",
            "libra": "Libra",
            "scorpio": "Scorpio",
            "sagittarius": "Sagittarius",
            "capricorn": "Capricorn",
            "aquarius": "Aquarius",
            "pisces": "Pisces",
        },
        "es": {
            "aries": "Aries",
            "taurus": "Tauro",
            "gemini": "Geminis",
            "cancer": "Cancer",
            "leo": "Leo",
            "virgo": "Virgo",
            "libra": "Libra",
            "scorpio": "Escorpio",
            "sagittarius": "Sagitario",
            "capricorn": "Capricornio",
            "aquarius": "Acuario",
            "pisces": "Piscis",
        },
    }

    @staticmethod
    def generate_pdf(
        db: Session,
        interpretation: UserNatalInterpretationModel,
        template_key: Optional[str] = None,
        locale: str = "fr",
    ) -> bytes:
        """
        Generates a PDF for a given natal interpretation.
        """
        # 1. Get template
        template_model = None
        if template_key:
            stmt = select(PdfTemplateModel).where(
                PdfTemplateModel.key == template_key,
                PdfTemplateModel.status == PdfTemplateStatus.ACTIVE,
            )
            template_model = db.execute(stmt).scalar_one_or_none()

        if not template_model:
            stmt = select(PdfTemplateModel).where(
                PdfTemplateModel.is_default, PdfTemplateModel.status == PdfTemplateStatus.ACTIVE
            )
            template_model = db.execute(stmt).scalar_one_or_none()
        template_config = (
            template_model.config_json
            if template_model and isinstance(template_model.config_json, dict)
            else {}
        )
        max_paragraph_chars = NatalPdfExportService._read_int_config(
            config=template_config,
            key="max_paragraph_chars",
            default=NatalPdfExportService.MAX_PARAGRAPH_CHARS,
            min_value=200,
            max_value=5000,
        )
        split_paragraphs_enabled = NatalPdfExportService._read_bool_config(
            config=template_config,
            key="split_paragraphs_enabled",
            default=NatalPdfExportService.SPLIT_PARAGRAPHS_ENABLED,
        )
        page_budget_lines = NatalPdfExportService._read_int_config(
            config=template_config,
            key="page_budget_lines",
            default=NatalPdfExportService.ESTIMATED_PAGE_LINES,
            min_value=24,
            max_value=60,
        )
        section_head_extra_lines = NatalPdfExportService._read_int_config(
            config=template_config,
            key="section_head_extra_lines",
            default=NatalPdfExportService.SECTION_HEAD_EXTRA_LINES,
            min_value=0,
            max_value=6,
        )
        paragraph_spacing_lines = NatalPdfExportService._read_int_config(
            config=template_config,
            key="paragraph_spacing_lines",
            default=NatalPdfExportService.PARAGRAPH_SPACING_LINES,
            min_value=0,
            max_value=3,
        )
        section_tail_spacing_lines = NatalPdfExportService._read_int_config(
            config=template_config,
            key="section_tail_spacing_lines",
            default=NatalPdfExportService.SECTION_TAIL_SPACING_LINES,
            min_value=0,
            max_value=4,
        )
        sections_start_new_page = NatalPdfExportService._read_bool_config(
            config=template_config,
            key="sections_start_new_page",
            default=NatalPdfExportService.SECTIONS_START_NEW_PAGE,
        )
        sections_start_new_page_min_remaining_lines = NatalPdfExportService._read_int_config(
            config=template_config,
            key="sections_start_new_page_min_remaining_lines",
            default=NatalPdfExportService.SECTIONS_START_NEW_PAGE_MIN_REMAINING_LINES,
            min_value=0,
            max_value=30,
        )
        pagination_debug = NatalPdfExportService._read_bool_config(
            config=template_config,
            key="pagination_debug",
            default=NatalPdfExportService.PAGINATION_DEBUG,
        )
        config_runtime = {"max_paragraph_chars": max_paragraph_chars}
        config_runtime["split_paragraphs_enabled"] = split_paragraphs_enabled
        config_runtime["page_budget_lines"] = page_budget_lines
        config_runtime["section_head_extra_lines"] = section_head_extra_lines
        config_runtime["paragraph_spacing_lines"] = paragraph_spacing_lines
        config_runtime["section_tail_spacing_lines"] = section_tail_spacing_lines
        config_runtime["sections_start_new_page"] = sections_start_new_page
        config_runtime["sections_start_new_page_min_remaining_lines"] = (
            sections_start_new_page_min_remaining_lines
        )
        config_runtime["pagination_debug"] = pagination_debug

        # 2. Prepare data for template
        payload = interpretation.interpretation_payload
        if not isinstance(payload, dict):
            payload = {}

        chart_result = db.execute(
            select(ChartResultModel).where(ChartResultModel.chart_id == interpretation.chart_id)
        ).scalar_one_or_none()
        chart_payload = (
            chart_result.result_payload
            if chart_result and isinstance(chart_result.result_payload, dict)
            else {}
        )
        sun_sign_code, ascendant_sign_code = NatalPdfExportService._extract_sun_and_ascendant_signs(
            chart_payload
        )

        normalized_locale = (locale or "fr").split("-")[0].lower()
        sun_sign_label = NatalPdfExportService._localize_sign_label(
            sun_sign_code, normalized_locale
        )
        ascendant_sign_label = NatalPdfExportService._localize_sign_label(
            ascendant_sign_code, normalized_locale
        )

        # Data enrichment
        sections = payload.get("sections", [])
        clean_title = NatalPdfExportService._sanitize_inline_text(
            payload.get("title", "Interprétation Natala")
        )
        clean_summary = NatalPdfExportService._sanitize_inline_text(payload.get("summary", ""))
        clean_highlights = NatalPdfExportService._sanitize_text_list(payload.get("highlights", []))
        clean_advice = NatalPdfExportService._sanitize_text_list(payload.get("advice", []))
        clean_evidence = NatalPdfExportService._sanitize_text_list(payload.get("evidence", []))
        meta_line = (
            f"Réf: {interpretation.chart_id} | Niveau: {interpretation.level.value} "
            f"| Persona: {interpretation.persona_name or 'Standard'}"
        )
        intro_lines = NatalPdfExportService._estimate_intro_lines(
            title=clean_title,
            summary=clean_summary,
            highlights=clean_highlights,
            meta_line=meta_line,
        )
        intro_remainder = intro_lines % page_budget_lines
        remaining_after_intro = (
            page_budget_lines - intro_remainder if intro_remainder else page_budget_lines
        )
        sections_start_new_page_effective = (
            sections_start_new_page
            and remaining_after_intro < sections_start_new_page_min_remaining_lines
        )
        config_runtime["sections_start_new_page"] = sections_start_new_page_effective
        render_sections = NatalPdfExportService._prepare_paginated_sections(
            sections=sections,
            title=clean_title,
            summary=clean_summary,
            highlights=clean_highlights,
            meta_line=meta_line,
            max_paragraph_chars=max_paragraph_chars,
            split_paragraphs_enabled=split_paragraphs_enabled,
            page_budget_lines=page_budget_lines,
            section_head_extra_lines=section_head_extra_lines,
            paragraph_spacing_lines=paragraph_spacing_lines,
            section_tail_spacing_lines=section_tail_spacing_lines,
            sections_start_new_page=sections_start_new_page_effective,
            pagination_debug=pagination_debug,
        )

        data = {
            "title": clean_title,
            "summary": clean_summary,
            "sections": render_sections,
            "render_sections": render_sections,
            "highlights": clean_highlights,
            "advice": clean_advice,
            "evidence": clean_evidence,
            "meta": {
                "chart_id": interpretation.chart_id,
                "level": interpretation.level.value,
                "persona_name": interpretation.persona_name,
                "created_at": interpretation.created_at.strftime("%d/%m/%Y %H:%M"),
                "locale": locale,
                "sun_sign_code": sun_sign_code,
                "ascendant_sign_code": ascendant_sign_code,
                "sun_sign_label": sun_sign_label,
                "ascendant_sign_label": ascendant_sign_label,
            },
            "disclaimers": get_disclaimers(locale),
            "generated_at": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"),
            "config": template_config,
            "config_runtime": config_runtime,
        }

        # 3. Render HTML
        template_name = (
            f"natal_{template_model.key}.html" if template_model else "natal_default.html"
        )
        html_content = NatalPdfExportService._render_html(data, locale, template_name)

        # 4. Convert to PDF
        pdf_bytes = NatalPdfExportService._convert_html_to_pdf(html_content)

        return pdf_bytes

    @staticmethod
    def _render_html(
        data: dict[str, Any], locale: str, template_name: str = "natal_default.html"
    ) -> str:
        # Template directory
        template_dir = Path(__file__).parent.parent / "resources" / "templates" / "pdf"
        if not template_dir.exists():
            template_dir.mkdir(parents=True, exist_ok=True)

        # Create default template file if not exists
        default_template_path = template_dir / "natal_default.html"
        if not default_template_path.exists():
            NatalPdfExportService._create_default_template(default_template_path)

        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

        try:
            template = env.get_template(template_name)
        except Exception:
            logger.warning(
                "Template %s not found, falling back to natal_default.html", template_name
            )
            template = env.get_template("natal_default.html")

        return template.render(**data)

    @staticmethod
    def _convert_html_to_pdf(html_content: str) -> bytes:
        result = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.StringIO(html_content), dest=result)
        if pisa_status.err:
            logger.error(f"Error generating PDF: {pisa_status.err}")
            raise RuntimeError("PDF generation failed")

        return result.getvalue()

    @staticmethod
    def _create_default_template(path: Path):
        content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: Helvetica, Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
        }
        h2 {
            color: #2980b9;
            border-bottom: 1px solid #bdc3c7;
            margin: 0 0 8px 0;
        }
        .summary {
            font-style: italic;
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 5px solid #2980b9;
            margin: 20px 0;
        }
        .section-content {
            margin-bottom: 15px;
        }
        .section { margin-bottom: 8px; }
        .section h2 {
            page-break-after: avoid;
        }
        .section-head {
            margin-top: 20px;
            page-break-inside: avoid;
        }
        .para-wrap {
            page-break-inside: avoid;
        }
        p.para {
            margin: 0 0 10px 0;
            page-break-inside: avoid;
        }
        .highlights, .advice {
            background-color: #e8f4f8;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .highlights ul, .advice ul {
            margin: 0;
            padding-left: 20px;
        }
        .footer {
            margin-top: 20px;
            font-size: 9pt;
            color: #7f8c8d;
            border-top: 1px solid #eee;
            padding-top: 10px;
        }
        .metadata {
            font-size: 9pt;
            color: #95a5a6;
            margin-bottom: 30px;
        }
        .generated-at {
            text-align: right;
            font-size: 8pt;
            color: #bdc3c7;
        }
        .pagination-debug {
            color: #95a5a6;
            font-size: 7pt;
            margin-bottom: 2px;
        }
    </style>
</head>
<body>
    <div class="metadata">
        Réf: {{ meta.chart_id | e }} | Niveau: {{ meta.level | e }} |
        Persona: {{ (meta.persona_name or "Standard") | e }} | Date: {{ meta.created_at | e }}
        {% if meta.sun_sign_label %}| Signe: {{ meta.sun_sign_label | e }}{% endif %}
        {% if meta.ascendant_sign_label %}
        | Ascendant: {{ meta.ascendant_sign_label | e }}
        {% endif %}
    </div>

    <h1>{{ title | e }}</h1>

    <div class="summary">
        {{ summary | e }}
    </div>

    <div class="highlights">
        <h3>Points clés</h3>
        <ul>
            {% for h in highlights %}
            <li>{{ h | e }}</li>
            {% endfor %}
        </ul>
    </div>

    {% if config_runtime and config_runtime.sections_start_new_page
       and render_sections and render_sections|length > 0 %}
    <pdf:nextpage />
    {% endif %}

    {% for section in (render_sections if render_sections else sections) %}
    <div class="section">
        {% if section.blocks and section.blocks|length > 0 %}
            {% set head_block = section.blocks[0] %}
            {% if head_block.force_page_break %}<pdf:nextpage />{% endif %}
            <div class="section-head">
                <h2>{{ section.heading | e }}</h2>
                {% if head_block.text %}
                {% if section.show_pagination_debug %}
                <div class="pagination-debug">
                    [rem={{ head_block.debug_remaining_before }},
                    cost={{ head_block.debug_cost }},
                    pb={{ head_block.force_page_break }}]
                </div>
                {% endif %}
                <div class="para-wrap">
                    <p class="para">{{ head_block.text | e }}</p>
                </div>
                {% endif %}
            </div>
            {% if section.blocks|length > 1 %}
            <div class="section-content">
                {% for block in section.blocks[1:] %}
                    {% if block.force_page_break %}<pdf:nextpage />{% endif %}
                    {% if section.show_pagination_debug %}
                    <div class="pagination-debug">
                        [rem={{ block.debug_remaining_before }},
                        cost={{ block.debug_cost }},
                        pb={{ block.force_page_break }}]
                    </div>
                    {% endif %}
                    <div class="para-wrap">
                        <p class="para">{{ block.text | e }}</p>
                    </div>
                {% endfor %}
            </div>
            {% endif %}
        {% elif section.paragraphs and section.paragraphs|length > 0 %}
        <div class="section-head">
            <h2>{{ section.heading | e }}</h2>
            <div class="para-wrap">
                <p class="para">{{ section.paragraphs[0] | e }}</p>
            </div>
        </div>
        <div class="section-content">
            {% for p in section.paragraphs[1:] %}
            <div class="para-wrap">
                <p class="para">{{ p | e }}</p>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <h2>{{ section.heading | e }}</h2>
        {% endif %}
    </div>
    {% endfor %}

    <div class="advice">
        <h3>Conseils</h3>
        <ul>
            {% for a in advice %}
            <li>{{ a | e }}</li>
            {% endfor %}
        </ul>
    </div>

    <div class="footer">
        {% for d in disclaimers %}
        <p>{{ d | e }}</p>
        {% endfor %}
    </div>
    
    <div class="generated-at">
        Généré le {{ generated_at | e }} UTC
    </div>
</body>
</html>
"""
        path.write_text(content, encoding="utf-8")

    @staticmethod
    def _read_int_config(
        config: Any,
        key: str,
        default: int,
        min_value: int,
        max_value: int,
    ) -> int:
        if not isinstance(config, dict):
            return default
        raw = config.get(key, default)
        try:
            value = int(raw)
        except (TypeError, ValueError):
            return default
        if value < min_value:
            return min_value
        if value > max_value:
            return max_value
        return value

    @staticmethod
    def _read_bool_config(config: Any, key: str, default: bool) -> bool:
        if not isinstance(config, dict):
            return default
        raw = config.get(key, default)
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, str):
            return raw.strip().lower() in {"1", "true", "yes", "on"}
        if isinstance(raw, (int, float)):
            return bool(raw)
        return default

    @staticmethod
    def _estimate_heading_lines(heading: str) -> int:
        return max(
            1,
            (len(heading) + NatalPdfExportService.ESTIMATED_HEADING_CHARS_PER_LINE - 1)
            // NatalPdfExportService.ESTIMATED_HEADING_CHARS_PER_LINE,
        )

    @staticmethod
    def _estimate_paragraph_lines(text: str, spacing_lines: int) -> int:
        return (
            max(
                1,
                (len(text) + NatalPdfExportService.ESTIMATED_CONTENT_CHARS_PER_LINE - 1)
                // NatalPdfExportService.ESTIMATED_CONTENT_CHARS_PER_LINE,
            )
            + spacing_lines
        )

    @staticmethod
    def _consume_page_budget(
        remaining_budget_lines: int,
        page_budget_lines: int,
        consumed_lines: int,
    ) -> int:
        if consumed_lines >= remaining_budget_lines:
            overflow = consumed_lines - remaining_budget_lines
            if overflow <= 0:
                return page_budget_lines
            used_last_page = overflow % page_budget_lines
            return page_budget_lines if used_last_page == 0 else page_budget_lines - used_last_page
        return remaining_budget_lines - consumed_lines

    @staticmethod
    def _sanitize_inline_text(content: Any) -> str:
        text = str(content or "")
        # Artifacts sometimes returned by model JSON glue and then persisted as text.
        replacements = {
            "”},{": " ",
            '"},{': " ",
            "}, {": " ",
            "": "- ",
        }
        for source, target in replacements.items():
            text = text.replace(source, target)
        text = " ".join(text.split())
        return NatalPdfExportService._strip_trailing_json_artifacts(text)

    @staticmethod
    def _strip_trailing_json_artifacts(text: str) -> str:
        cleaned = text
        trailing_patterns = (
            r'\s*["”]\}\]\s*,?\s*$',
            r"\s*\}\]\s*,?\s*$",
            r"\s*\]\s*,?\s*$",
        )
        for pattern in trailing_patterns:
            cleaned = re.sub(pattern, "", cleaned)
        return cleaned.strip()

    @staticmethod
    def _split_paragraphs(content: Any, max_chars: int, split_enabled: bool) -> list[str]:
        raw = str(content or "")
        raw = raw.replace("\r\n", "\n").replace("\r", "\n")

        replacements = {
            "”},{": "\n\n",
            '"},{': "\n\n",
            "}, {": "\n\n",
            "": "- ",
        }
        for source, target in replacements.items():
            raw = raw.replace(source, target)

        if not split_enabled:
            flattened = NatalPdfExportService._sanitize_inline_text(raw)
            return [flattened] if flattened else []

        chunks = re.split(r"\n\s*\n+", raw)
        paragraphs: list[str] = []
        for chunk in chunks:
            chunk = re.sub(r"[ \t]+", " ", chunk)
            chunk = re.sub(r"\n+", " ", chunk)
            chunk = chunk.strip()
            if chunk:
                chunk = NatalPdfExportService._strip_trailing_json_artifacts(chunk)
            if chunk:
                paragraphs.extend(
                    NatalPdfExportService._chunk_long_paragraph(chunk, max_chars=max_chars)
                )
        return [
            NatalPdfExportService._strip_trailing_json_artifacts(paragraph)
            for paragraph in paragraphs
            if paragraph
        ]

    @staticmethod
    def _chunk_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
        if len(paragraph) <= max_chars:
            return [paragraph]

        sentences = re.split(r"(?<=[.!?;:])\s+", paragraph)
        if len(sentences) <= 1:
            words = paragraph.split()
            chunks: list[str] = []
            current: list[str] = []
            current_len = 0
            for word in words:
                if len(word) > max_chars:
                    if current:
                        chunks.append(" ".join(current))
                        current = []
                        current_len = 0
                    for start in range(0, len(word), max_chars):
                        chunks.append(word[start : start + max_chars])
                    continue
                next_len = current_len + (1 if current else 0) + len(word)
                if current and next_len > max_chars:
                    chunks.append(" ".join(current))
                    current = [word]
                    current_len = len(word)
                else:
                    current.append(word)
                    current_len = next_len
            if current:
                chunks.append(" ".join(current))
            return chunks

        chunks: list[str] = []
        current = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            candidate = sentence if not current else f"{current} {sentence}"
            if current and len(candidate) > max_chars:
                chunks.append(current)
                current = sentence
            else:
                current = candidate
        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def _sanitize_text_list(values: Any) -> list[str]:
        if not isinstance(values, list):
            return []
        return [NatalPdfExportService._sanitize_inline_text(item) for item in values]

    @staticmethod
    def _estimate_intro_lines(
        title: Any,
        summary: Any,
        highlights: Any,
        meta_line: Any,
    ) -> int:
        heading_cpl = NatalPdfExportService.ESTIMATED_HEADING_CHARS_PER_LINE
        body_cpl = NatalPdfExportService.ESTIMATED_CONTENT_CHARS_PER_LINE
        lines = 0

        meta_text = str(meta_line or "")
        lines += max(1, (len(meta_text) + body_cpl - 1) // body_cpl) + 1

        title_text = str(title or "")
        lines += max(1, (len(title_text) + heading_cpl - 1) // heading_cpl) + 2

        summary_text = str(summary or "")
        lines += max(1, (len(summary_text) + body_cpl - 1) // body_cpl) + 3

        lines += 2  # highlights heading + spacing
        if isinstance(highlights, list):
            for item in highlights:
                text = str(item or "")
                lines += max(1, (len(text) + body_cpl - 1) // body_cpl)
        else:
            text = str(highlights or "")
            lines += max(1, (len(text) + body_cpl - 1) // body_cpl)
        lines += 2

        return lines

    @staticmethod
    def _prepare_paginated_sections(
        sections: Any,
        title: Any,
        summary: Any,
        highlights: Any,
        meta_line: Any,
        max_paragraph_chars: int,
        split_paragraphs_enabled: bool,
        page_budget_lines: int | None = None,
        section_head_extra_lines: int | None = None,
        paragraph_spacing_lines: int | None = None,
        section_tail_spacing_lines: int | None = None,
        sections_start_new_page: bool = False,
        pagination_debug: bool = False,
    ) -> list[dict[str, Any]]:
        if not isinstance(sections, list):
            return []

        resolved_page_budget_lines = (
            page_budget_lines
            if isinstance(page_budget_lines, int) and page_budget_lines > 0
            else NatalPdfExportService.ESTIMATED_PAGE_LINES
        )
        resolved_section_head_extra_lines = (
            section_head_extra_lines
            if isinstance(section_head_extra_lines, int) and section_head_extra_lines >= 0
            else NatalPdfExportService.SECTION_HEAD_EXTRA_LINES
        )
        resolved_paragraph_spacing_lines = (
            paragraph_spacing_lines
            if isinstance(paragraph_spacing_lines, int) and paragraph_spacing_lines >= 0
            else NatalPdfExportService.PARAGRAPH_SPACING_LINES
        )
        resolved_section_tail_spacing_lines = (
            section_tail_spacing_lines
            if isinstance(section_tail_spacing_lines, int) and section_tail_spacing_lines >= 0
            else NatalPdfExportService.SECTION_TAIL_SPACING_LINES
        )
        intro_lines = NatalPdfExportService._estimate_intro_lines(
            title=title,
            summary=summary,
            highlights=highlights,
            meta_line=meta_line,
        )
        if sections_start_new_page:
            remaining_budget_lines = resolved_page_budget_lines
        else:
            intro_remainder = intro_lines % resolved_page_budget_lines
            remaining_budget_lines = (
                resolved_page_budget_lines - intro_remainder
                if intro_remainder
                else resolved_page_budget_lines
            )
        prepared: list[dict[str, Any]] = []

        for index, item in enumerate(sections):
            section = item if isinstance(item, dict) else {}
            heading = NatalPdfExportService._sanitize_inline_text(section.get("heading", ""))
            paragraphs = NatalPdfExportService._split_paragraphs(
                section.get("content", ""),
                max_chars=max_paragraph_chars,
                split_enabled=split_paragraphs_enabled,
            )
            section_force_page_break = NatalPdfExportService.STRICT_SECTION_NEW_PAGE and index > 0

            blocks: list[dict[str, Any]] = []
            heading_lines = NatalPdfExportService._estimate_heading_lines(heading)
            first_paragraph = paragraphs[0] if paragraphs else ""
            first_paragraph_lines = (
                NatalPdfExportService._estimate_paragraph_lines(
                    first_paragraph,
                    spacing_lines=resolved_paragraph_spacing_lines,
                )
                if first_paragraph
                else 0
            )
            section_head_lines = (
                heading_lines + first_paragraph_lines + resolved_section_head_extra_lines
            )
            if first_paragraph:
                section_head_lines = max(
                    section_head_lines,
                    heading_lines + NatalPdfExportService.MIN_LINES_AFTER_HEADING,
                )

            head_force_page_break = section_force_page_break
            head_remaining_before = remaining_budget_lines
            if (
                not head_force_page_break
                and section_head_lines > remaining_budget_lines
                and section_head_lines <= resolved_page_budget_lines
            ):
                head_force_page_break = True
            if head_force_page_break:
                remaining_budget_lines = resolved_page_budget_lines

            blocks.append(
                {
                    "kind": "head",
                    "text": first_paragraph,
                    "force_page_break": head_force_page_break,
                    "debug_remaining_before": head_remaining_before,
                    "debug_cost": section_head_lines,
                }
            )

            remaining_budget_lines = NatalPdfExportService._consume_page_budget(
                remaining_budget_lines=remaining_budget_lines,
                page_budget_lines=resolved_page_budget_lines,
                consumed_lines=section_head_lines,
            )

            for paragraph in paragraphs[1:]:
                paragraph_lines = NatalPdfExportService._estimate_paragraph_lines(
                    paragraph,
                    spacing_lines=resolved_paragraph_spacing_lines,
                )
                paragraph_force_page_break = (
                    paragraph_lines > remaining_budget_lines
                    and paragraph_lines <= resolved_page_budget_lines
                )
                paragraph_remaining_before = remaining_budget_lines
                if paragraph_force_page_break:
                    remaining_budget_lines = resolved_page_budget_lines
                blocks.append(
                    {
                        "kind": "paragraph",
                        "text": paragraph,
                        "force_page_break": paragraph_force_page_break,
                        "debug_remaining_before": paragraph_remaining_before,
                        "debug_cost": paragraph_lines,
                    }
                )
                remaining_budget_lines = NatalPdfExportService._consume_page_budget(
                    remaining_budget_lines=remaining_budget_lines,
                    page_budget_lines=resolved_page_budget_lines,
                    consumed_lines=paragraph_lines,
                )

            if resolved_section_tail_spacing_lines > 0:
                remaining_budget_lines = NatalPdfExportService._consume_page_budget(
                    remaining_budget_lines=remaining_budget_lines,
                    page_budget_lines=resolved_page_budget_lines,
                    consumed_lines=resolved_section_tail_spacing_lines,
                )

            prepared.append(
                {
                    **section,
                    "heading": heading,
                    "paragraphs": paragraphs,
                    "blocks": blocks,
                    "force_page_break": head_force_page_break,
                    "show_pagination_debug": pagination_debug,
                }
            )

        return prepared

    @staticmethod
    def _localize_sign_label(sign_code: str | None, locale: str) -> str | None:
        if not sign_code:
            return None
        labels = (
            NatalPdfExportService.SIGN_LABELS.get(locale) or NatalPdfExportService.SIGN_LABELS["fr"]
        )
        return labels.get(sign_code.lower(), sign_code)

    @staticmethod
    def _sign_from_longitude(longitude: Any) -> str | None:
        try:
            normalized = float(longitude) % 360.0
        except (TypeError, ValueError):
            return None
        sign_codes = [
            "aries",
            "taurus",
            "gemini",
            "cancer",
            "leo",
            "virgo",
            "libra",
            "scorpio",
            "sagittarius",
            "capricorn",
            "aquarius",
            "pisces",
        ]
        return sign_codes[int(normalized // 30.0) % 12]

    @staticmethod
    def _extract_sun_and_ascendant_signs(payload: dict[str, Any]) -> tuple[str | None, str | None]:
        sun_sign: str | None = None
        asc_sign: str | None = None

        planet_positions = payload.get("planet_positions")
        if isinstance(planet_positions, list):
            for item in planet_positions:
                if isinstance(item, dict) and str(item.get("planet_code")).lower() == "sun":
                    raw_sign = item.get("sign_code")
                    if isinstance(raw_sign, str) and raw_sign:
                        sun_sign = raw_sign.lower()
                        break

        planets = payload.get("planets")
        if sun_sign is None and isinstance(planets, list):
            for item in planets:
                if isinstance(item, dict) and str(item.get("code")).lower() == "sun":
                    raw_sign = item.get("sign")
                    if isinstance(raw_sign, str) and raw_sign:
                        sun_sign = raw_sign.lower()
                        break

        houses = payload.get("houses")
        if isinstance(houses, list):
            for item in houses:
                if not isinstance(item, dict):
                    continue
                if item.get("number") != 1:
                    continue
                raw_sign = item.get("sign")
                if isinstance(raw_sign, str) and raw_sign:
                    asc_sign = raw_sign.lower()
                    break
                asc_sign = NatalPdfExportService._sign_from_longitude(item.get("cusp_longitude"))
                if asc_sign:
                    break

        angles = payload.get("angles")
        if asc_sign is None and isinstance(angles, dict):
            asc = angles.get("ASC")
            if isinstance(asc, dict):
                raw_sign = asc.get("sign")
                if isinstance(raw_sign, str) and raw_sign:
                    asc_sign = raw_sign.lower()
                if asc_sign is None:
                    asc_sign = NatalPdfExportService._sign_from_longitude(asc.get("longitude"))

        return sun_sign, asc_sign
