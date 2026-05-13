"""Valide les migrations des référentiels astrologiques stables."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.core.config import settings

EXPECTED_SIGN_PROFILE_MAPPING = {
    "aries": ("fire", "cardinal", "yang"),
    "taurus": ("earth", "fixed", "yin"),
    "gemini": ("air", "mutable", "yang"),
    "cancer": ("water", "cardinal", "yin"),
    "leo": ("fire", "fixed", "yang"),
    "virgo": ("earth", "mutable", "yin"),
    "libra": ("air", "cardinal", "yang"),
    "scorpio": ("water", "fixed", "yin"),
    "sagittarius": ("fire", "mutable", "yang"),
    "capricorn": ("earth", "cardinal", "yin"),
    "aquarius": ("air", "fixed", "yang"),
    "pisces": ("water", "mutable", "yin"),
}


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def test_reference_migrations_upgrade_and_downgrade(monkeypatch: object, tmp_path: Path) -> None:
    db_path = tmp_path / "migration-reference-test.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.downgrade(config, "base")
    command.upgrade(config, "20260218_0001")

    engine = create_engine(database_url, future=True)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    assert "reference_versions" in tables
    assert "planets" in tables
    assert "astral_planets" not in tables
    assert "signs" in tables
    assert "houses" in tables
    assert "aspects" in tables
    assert "astro_characteristics" in tables
    engine.dispose()

    command.upgrade(config, "head")

    head_engine = create_engine(database_url, future=True)
    head_inspector = inspect(head_engine)
    head_tables = set(head_inspector.get_table_names())
    assert "reference_versions" in head_tables
    assert "astro_characteristics" not in head_tables
    assert "planets" not in head_tables
    assert "astral_planets" in head_tables
    assert "signs" not in head_tables
    assert "sign_rulerships" not in head_tables
    for table_name in (
        "astral_signs",
        "astral_systems",
        "astral_elements",
        "astral_modalities",
        "astral_polarities",
        "astral_dignity_type",
        "astral_planet_sign_dignities",
        "astral_sign_profiles",
        "astral_sign_rulerships",
    ):
        assert table_name in head_tables
    for table_name in ("astral_planets", "astral_signs", "houses", "aspects", "astro_points"):
        columns = {column["name"] for column in head_inspector.get_columns(table_name)}
        assert "reference_version_id" not in columns
    planet_foreign_key_targets = {
        foreign_key["referred_table"]
        for table_name in (
            "astral_prediction_daily_planet_profiles",
            "planet_category_weights",
            "astral_sign_rulerships",
            "astral_planet_sign_dignities",
        )
        for foreign_key in head_inspector.get_foreign_keys(table_name)
        if (
            "planet_id" in foreign_key["constrained_columns"]
            or "astral_planet_id" in foreign_key["constrained_columns"]
        )
    }
    assert planet_foreign_key_targets == {"astral_planets"}
    profile_columns = {
        column["name"] for column in head_inspector.get_columns("astral_sign_profiles")
    }
    assert profile_columns >= {
        "astral_sign_id",
        "astral_element_id",
        "astral_modality_id",
        "astral_polarity_id",
        "keywords_json",
        "shadow_keywords_json",
    }
    unique_constraints = head_inspector.get_unique_constraints("astral_sign_profiles")
    unique_columns = {tuple(constraint["column_names"]) for constraint in unique_constraints}
    assert ("astral_sign_id",) in unique_columns
    assert ("astral_element_id",) not in unique_columns
    assert ("astral_modality_id",) not in unique_columns
    assert ("astral_polarity_id",) not in unique_columns
    rulership_columns = {
        column["name"] for column in head_inspector.get_columns("astral_sign_rulerships")
    }
    assert "reference_version_id" not in rulership_columns
    assert "astral_sign_id" in rulership_columns
    assert "system" in rulership_columns
    system_columns = {column["name"] for column in head_inspector.get_columns("astral_systems")}
    assert system_columns == {"id", "name"}
    dignity_columns = {
        column["name"] for column in head_inspector.get_columns("astral_planet_sign_dignities")
    }
    assert dignity_columns == {
        "id",
        "astral_sign_id",
        "astral_planet_id",
        "astral_dignity_type_id",
        "astral_system_id",
        "weight",
        "is_primary",
    }
    with head_engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM astral_elements")).scalar_one() == 4
        assert connection.execute(text("SELECT COUNT(*) FROM astral_systems")).scalar_one() == 4
        assert connection.execute(text("SELECT COUNT(*) FROM astral_modalities")).scalar_one() == 3
        assert connection.execute(text("SELECT COUNT(*) FROM astral_polarities")).scalar_one() == 2
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_dignity_type")).scalar_one() == 4
        )
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_sign_profiles")).scalar_one() == 12
        )
        assert {
            row[0] for row in connection.execute(text("SELECT code FROM astral_elements")).all()
        } == {"fire", "earth", "air", "water"}
        assert {
            row[0] for row in connection.execute(text("SELECT name FROM astral_systems")).all()
        } == {"traditional", "modern", "hellenistic", "medieval"}
        assert {
            row[0] for row in connection.execute(text("SELECT code FROM astral_modalities")).all()
        } == {"cardinal", "fixed", "mutable"}
        assert {
            row[0] for row in connection.execute(text("SELECT code FROM astral_polarities")).all()
        } == {"yang", "yin"}
        assert {
            row[0] for row in connection.execute(text("SELECT code FROM astral_dignity_type")).all()
        } == {"domicile", "detriment", "exaltation", "fall"}
        assert (
            connection.execute(
                text("SELECT COUNT(*) FROM astral_planet_sign_dignities")
            ).scalar_one()
            == 50
        )
        assert (
            connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM astral_planet_sign_dignities
                    JOIN astral_dignity_type
                        ON astral_planet_sign_dignities.astral_dignity_type_id =
                            astral_dignity_type.id
                    JOIN astral_systems
                        ON astral_planet_sign_dignities.astral_system_id = astral_systems.id
                    WHERE astral_dignity_type.code = 'domicile'
                        AND astral_systems.name = 'traditional'
                    """
                )
            ).scalar_one()
            == 12
        )
        assert (
            connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM astral_planet_sign_dignities
                    WHERE astral_dignity_type_id IS NULL
                        OR astral_system_id IS NULL
                    """
                )
            ).scalar_one()
            == 0
        )
        profile_rows = connection.execute(
            text(
                """
                SELECT
                    astral_signs.code AS sign_code,
                    astral_elements.code AS element_code,
                    astral_modalities.code AS modality_code,
                    astral_polarities.code AS polarity_code,
                    astral_sign_profiles.keywords_json AS keywords_json,
                    astral_sign_profiles.shadow_keywords_json AS shadow_keywords_json
                FROM astral_sign_profiles
                JOIN astral_signs
                    ON astral_sign_profiles.astral_sign_id = astral_signs.id
                JOIN astral_elements
                    ON astral_sign_profiles.astral_element_id = astral_elements.id
                JOIN astral_modalities
                    ON astral_sign_profiles.astral_modality_id = astral_modalities.id
                JOIN astral_polarities
                    ON astral_sign_profiles.astral_polarity_id = astral_polarities.id
                """
            )
        ).all()
        assert {
            row.sign_code: (row.element_code, row.modality_code, row.polarity_code)
            for row in profile_rows
        } == EXPECTED_SIGN_PROFILE_MAPPING
        assert all(row.keywords_json and row.shadow_keywords_json for row in profile_rows)
        assert any(
            row.sign_code == "aries" and "initiative" in row.keywords_json for row in profile_rows
        )
    for table_name in (
        "astral_prediction_daily_planet_profiles",
        "house_profiles",
        "aspect_profiles",
        "planet_category_weights",
        "house_category_weights",
        "point_category_weights",
    ):
        columns = {column["name"] for column in head_inspector.get_columns(table_name)}
        assert "reference_version_id" in columns
    assert "planet_profiles" not in set(head_inspector.get_table_names())
    head_engine.dispose()

    command.downgrade(config, "base")

    downgraded_engine = create_engine(database_url, future=True)
    downgraded_tables = set(inspect(downgraded_engine).get_table_names())
    assert "reference_versions" not in downgraded_tables
    downgraded_engine.dispose()
