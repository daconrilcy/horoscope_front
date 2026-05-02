"""Valide la migration des objectifs catalogue consultation vers guidance."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.core.config import settings
from app.tests.helpers.db_session import build_sqlite_test_engine

_OLD_PROMPTS_BY_KEY = {
    "period": (
        "Analyse le climat astrologique actuel pour l'utilisateur. Concentre-toi sur "
        "les transits planetaires majeurs."
    ),
    "career": (
        "Analyse les opportunites et defis professionnels pour l'utilisateur. "
        "Utilise les maisons liees au travail."
    ),
    "orientation": (
        "Aide l'utilisateur a comprendre sa direction de vie. Analyse les Noeuds Lunaires."
    ),
    "relationship": (
        "Analyse la dynamique entre l'utilisateur et une tierce personne. Compare les Venus."
    ),
    "timing": (
        "Identifie les periodes favorables ou defavorables pour le projet de l'utilisateur."
    ),
}
_EXPECTED_OBJECTIVES_BY_KEY = {
    "period": "Comprendre le climat astrologique de la periode demandee.",
    "career": "Eclairer une interaction ou une decision liee au travail.",
    "orientation": "Clarifier une direction de vie ou une decision structurante.",
    "relationship": "Lire la dynamique relationnelle de maniere prudente et non fataliste.",
    "timing": "Identifier le bon tempo d action avec une lecture astrologique prudente.",
}


def _alembic_config() -> Config:
    """Construit la configuration Alembic backend pour une base temporaire."""
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def test_migration_0084_replaces_existing_consultation_prompt_content(
    monkeypatch: object, tmp_path: Path
) -> None:
    """L upgrade corrige les lignes existantes sans attendre un reseed manuel."""
    db_path = tmp_path / "migration-20260502-0084-consultation-objectives.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.upgrade(config, "20260425_0083")

    engine = build_sqlite_test_engine(database_url)
    with engine.begin() as connection:
        for index, (template_key, old_prompt) in enumerate(_OLD_PROMPTS_BY_KEY.items(), start=1):
            connection.execute(
                text(
                    """
                    INSERT INTO consultation_templates (
                        id,
                        key,
                        icon_ref,
                        title,
                        subtitle,
                        description,
                        prompt_content,
                        metadata_config,
                        is_active,
                        sort_order,
                        created_at,
                        updated_at
                    ) VALUES (
                        :id,
                        :key,
                        :icon_ref,
                        :title,
                        :subtitle,
                        :description,
                        :prompt_content,
                        '{}',
                        1,
                        :sort_order,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                    """
                ),
                {
                    "id": f"00000000-0000-0000-0000-{index:012d}",
                    "key": template_key,
                    "icon_ref": "icon",
                    "title": template_key,
                    "subtitle": template_key,
                    "description": template_key,
                    "prompt_content": old_prompt,
                    "sort_order": index,
                },
            )

    command.upgrade(config, "20260502_0084")

    with engine.connect() as connection:
        rows = (
            connection.execute(
                text(
                    """
                    SELECT key, prompt_content
                    FROM consultation_templates
                    ORDER BY key
                    """
                )
            )
            .mappings()
            .all()
        )

    assert {row["key"]: row["prompt_content"] for row in rows} == _EXPECTED_OBJECTIVES_BY_KEY

    engine.dispose()
