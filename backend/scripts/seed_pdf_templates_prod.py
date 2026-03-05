"""Upsert production PDF templates for natal exports.

Creates/updates two templates:
- prod_premium (ACTIVE, default)
- prod_compact (ACTIVE)

Run:
    python -m scripts.seed_pdf_templates_prod
"""

from __future__ import annotations

from sqlalchemy import select, update

from app.infra.db.models.pdf_template import PdfTemplateModel, PdfTemplateStatus
from app.infra.db.session import SessionLocal

PROD_TEMPLATES: dict[str, dict[str, object]] = {
    "prod_premium": {
        "name": "Natal PDF - Prod Premium",
        "description": "Rendu lisible et aere, priorite confort de lecture",
        "locale": "fr",
        "status": PdfTemplateStatus.ACTIVE,
        "is_default": True,
        "version": "1.0.0",
        "config_json": {
            "split_paragraphs_enabled": True,
            "max_paragraph_chars": 900,
            "page_budget_lines": 44,
            "section_head_extra_lines": 1,
            "paragraph_spacing_lines": 0,
            "section_tail_spacing_lines": 1,
            "sections_start_new_page": True,
            "sections_start_new_page_min_remaining_lines": 12,
            "pagination_debug": False,
        },
    },
    "prod_compact": {
        "name": "Natal PDF - Prod Compact",
        "description": "Rendu dense, moins de pages, sans couper les paragraphes",
        "locale": "fr",
        "status": PdfTemplateStatus.ACTIVE,
        "is_default": False,
        "version": "1.0.0",
        "config_json": {
            "split_paragraphs_enabled": True,
            "max_paragraph_chars": 900,
            "page_budget_lines": 44,
            "section_head_extra_lines": 1,
            "paragraph_spacing_lines": 0,
            "section_tail_spacing_lines": 0,
            "sections_start_new_page": True,
            "sections_start_new_page_min_remaining_lines": 7,
            "pagination_debug": False,
        },
    },
}


def _upsert_template(db, key: str, payload: dict[str, object]) -> None:
    item = db.execute(
        select(PdfTemplateModel).where(PdfTemplateModel.key == key)
    ).scalar_one_or_none()
    if item is None:
        item = PdfTemplateModel(
            key=key,
            name=str(payload["name"]),
            description=str(payload["description"]),
            locale=str(payload["locale"]),
            status=payload["status"],
            version=str(payload["version"]),
            config_json=payload["config_json"],
            is_default=bool(payload["is_default"]),
            created_by=None,
        )
        db.add(item)
        print(f"Created template: {key}")
        return

    item.name = str(payload["name"])
    item.description = str(payload["description"])
    item.locale = str(payload["locale"])
    item.status = payload["status"]
    item.version = str(payload["version"])
    item.config_json = payload["config_json"]
    item.is_default = bool(payload["is_default"])
    print(f"Updated template: {key}")


def seed() -> None:
    db = SessionLocal()
    try:
        # Ensure only prod_premium remains default after upsert.
        db.execute(
            update(PdfTemplateModel)
            .where(PdfTemplateModel.key.in_(list(PROD_TEMPLATES.keys())))
            .values(is_default=False)
        )

        for key, payload in PROD_TEMPLATES.items():
            _upsert_template(db, key, payload)

        db.commit()
        print("Done. Templates upserted: prod_premium, prod_compact")
    except Exception as exc:
        db.rollback()
        print(f"Failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
