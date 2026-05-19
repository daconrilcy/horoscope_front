"""Valide les migrations des référentiels astrologiques stables."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine.reflection import Inspector

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

EXPECTED_TRADITIONAL_RULERSHIPS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}

EXPECTED_HOUSE_SYSTEMS = {
    "placidus": ("quadrant", False, True, True, 10),
    "whole_sign": ("sign_based", True, False, False, 20),
    "equal": ("ascendant_based", True, False, True, 30),
    "porphyry": ("quadrant", True, True, True, 40),
}
EXPECTED_LANGUAGES = {
    "en": "english",
    "fr": "french",
    "es": "spanish",
    "de": "german",
    "it": "italian",
}

EXPECTED_TRANSLATION_TABLES = {
    "astral_sign_translations": {
        "id",
        "astral_sign_id",
        "language_id",
        "translated_name",
    },
    "astral_house_translations": {
        "id",
        "house_id",
        "language_id",
        "translated_name",
    },
    "astral_planet_translations": {
        "id",
        "planet_id",
        "language_id",
        "translated_name",
    },
    "astral_aspect_translations": {
        "id",
        "aspect_id",
        "language_id",
        "translated_name",
    },
    "astral_house_interpretation_profile_translations": {
        "id",
        "source_profile_id",
        "language_id",
        "title",
        "summary",
        "micro_note",
    },
    "astral_planet_interpretation_profile_translations": {
        "id",
        "source_profile_id",
        "language_id",
        "title",
        "summary",
        "micro_note",
    },
    "astral_aspect_interpretation_profile_translations": {
        "id",
        "source_profile_id",
        "language_id",
        "title",
        "summary",
        "micro_note",
    },
}


def _columns(inspector: Inspector, table_name: str) -> set[str]:
    """Retourne les noms de colonnes declares par la migration pour une table."""
    return {column["name"] for column in inspector.get_columns(table_name)}


def _foreign_key_targets(inspector: Inspector, table_name: str) -> dict[tuple[str, ...], str]:
    """Indexe les tables ciblees par les cles etrangeres d'une table migree."""
    return {
        tuple(foreign_key["constrained_columns"]): foreign_key["referred_table"]
        for foreign_key in inspector.get_foreign_keys(table_name)
    }


def _unique_column_sets(inspector: Inspector, table_name: str) -> set[tuple[str, ...]]:
    """Retourne les contraintes uniques sous forme de tuples de colonnes."""
    return {
        tuple(constraint["column_names"])
        for constraint in inspector.get_unique_constraints(table_name)
    }


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def test_translation_tables_migration_creates_expected_schema(
    monkeypatch: object, tmp_path: Path
) -> None:
    """La migration dédiée crée uniquement les tables de traduction attendues."""
    db_path = tmp_path / "migration-translation-test.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.downgrade(config, "base")
    command.upgrade(config, "20260516_0117")

    engine = create_engine(database_url, future=True)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    for table_name, expected_columns in EXPECTED_TRANSLATION_TABLES.items():
        assert table_name in tables
        columns = {column["name"] for column in inspector.get_columns(table_name)}
        assert columns == expected_columns
        foreign_key_targets = {
            foreign_key["referred_table"] for foreign_key in inspector.get_foreign_keys(table_name)
        }
        assert "languages" in foreign_key_targets
    engine.dispose()


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
    assert "reference_versions" not in head_tables
    assert "astral_reference_versions" in head_tables
    assert "astro_characteristics" not in head_tables
    assert "planets" not in head_tables
    assert "astral_planets" in head_tables
    assert "signs" not in head_tables
    assert "houses" not in head_tables
    assert "astral_houses" in head_tables
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
        "astral_house_systems",
        "astral_house_interpretation_profiles",
        "astral_aspect_interpretation_profiles",
        "astral_aspect_families",
        "astral_default_valence",
        "astral_interpretive_valence",
        "astral_aspect_definitions",
        "astral_aspect_orb_rules",
        "languages",
        "astral_house_axis_definitions",
        "astral_house_axis_members",
        "astral_angle_points",
        "astral_astrological_roles",
        "astral_calculation_types",
        "astral_house_modalities",
        "astral_object_types",
        "astral_constellations",
        "astral_hemispheres",
        "astral_zodiacal_reference_system_categories",
        "astral_zodiacal_reference_systems",
        "astral_reference_epochs",
        "astral_reference_sources",
        "astral_fixed_stars",
        "astral_fixed_star_keywords",
        "astral_fixed_star_keyword_translations",
        "astral_fixed_star_definitions",
        "astral_sources",
        "astral_dignity_functional_effects",
        "astral_dignity_intensity_effects",
        "astral_essential_dignity_types",
        "astral_accidental_dignity_types",
        "astral_diginity_score_profiles",
        "astral_term_bounds",
        "astral_face_decans",
        "astral_essential_dignity_rules",
        "astral_accidental_dignity_rules",
        "astral_chart_planet_dignity_results",
        "astral_planet_condition_signal_profiles",
        "astral_dominance_factor_types",
        "astral_dominance_score_profiles",
        "astral_dominance_score_weights",
        "astral_advanced_condition_types",
        "astral_advanced_condition_score_profiles",
        "astral_advanced_condition_weights",
    ):
        assert table_name in head_tables
    assert _columns(head_inspector, "astral_diginity_score_profiles") == {
        "id",
        "code",
        "label",
        "astral_system_id",
        "profile_family_source_id",
        "description",
        "is_default",
    }
    assert _foreign_key_targets(head_inspector, "astral_diginity_score_profiles") == {
        ("astral_system_id",): "astral_systems",
        ("profile_family_source_id",): "astral_sources",
    }
    assert ("code",) in _unique_column_sets(head_inspector, "astral_diginity_score_profiles")
    assert _columns(head_inspector, "astral_essential_dignity_rules") == {
        "id",
        "planet_id",
        "sign_id",
        "essential_dignity_types_id",
        "degree_start",
        "degree_end",
        "astral_system_id",
        "reference_version_id",
        "source_id",
        "micro_note",
    }
    assert _foreign_key_targets(head_inspector, "astral_essential_dignity_rules") == {
        ("planet_id",): "astral_planets",
        ("sign_id",): "astral_signs",
        ("essential_dignity_types_id",): "astral_essential_dignity_types",
        ("astral_system_id",): "astral_systems",
        ("reference_version_id",): "astral_reference_versions",
        ("source_id",): "astral_sources",
    }
    assert (
        "reference_version_id",
        "astral_system_id",
        "planet_id",
        "sign_id",
        "essential_dignity_types_id",
    ) in _unique_column_sets(head_inspector, "astral_essential_dignity_rules")
    assert _columns(head_inspector, "astral_accidental_dignity_rules") == {
        "id",
        "accidental_dignity_type_id",
        "planet_id",
        "condition_schema_id",
        "condition_json",
        "astral_system_id",
        "reference_version_id",
        "micro_note",
    }
    assert _foreign_key_targets(head_inspector, "astral_accidental_dignity_rules") == {
        ("accidental_dignity_type_id",): "astral_accidental_dignity_types",
        ("planet_id",): "astral_planets",
        ("condition_schema_id",): "astral_accidental_dignity_condition_schemas",
        ("astral_system_id",): "astral_systems",
        ("reference_version_id",): "astral_reference_versions",
    }
    expected_score_weight_columns = {
        "id",
        "score_profile_id",
        "score_value",
        "functional_weight",
        "expression_weight",
        "intensity_weight",
        "visibility_weight",
        "stability_weight",
        "coherence_weight",
        "support_weight",
        "constraint_weight",
        "notes",
    }
    assert _columns(head_inspector, "astral_essential_dignity_score_weights") == {
        *expected_score_weight_columns,
        "essential_dignity_types_id",
    }
    assert _columns(head_inspector, "astral_accidental_dignity_score_weights") == {
        *expected_score_weight_columns,
        "accidental_dignity_type_id",
    }
    assert _columns(head_inspector, "astral_chart_planet_dignity_results") == {
        "id",
        "chart_result_id",
        "planet_id",
        "score_profile_id",
        "astral_system_id",
        "reference_version_id",
        "essential_score",
        "accidental_score",
        "total_score",
        "functional_strength_score",
        "expression_quality_score",
        "intensity_score",
        "essential_breakdown_json",
        "accidental_breakdown_json",
        "condition_summary_json",
        "calculation_context_json",
        "created_at",
    }
    assert _foreign_key_targets(head_inspector, "astral_chart_planet_dignity_results") == {
        ("chart_result_id",): "chart_results",
        ("planet_id",): "astral_planets",
        ("score_profile_id",): "astral_diginity_score_profiles",
        ("astral_system_id",): "astral_systems",
        ("reference_version_id",): "astral_reference_versions",
    }
    assert (
        "chart_result_id",
        "planet_id",
        "score_profile_id",
        "reference_version_id",
    ) in _unique_column_sets(head_inspector, "astral_chart_planet_dignity_results")
    assert _columns(head_inspector, "astral_planet_condition_signal_profiles") == {
        "id",
        "condition_axis",
        "level_min",
        "level_max",
        "signal_code",
        "signal_label",
        "signal_level",
        "interpretation_use",
        "priority_weight",
        "prompt_hint",
        "reference_version_id",
    }
    assert _foreign_key_targets(head_inspector, "astral_planet_condition_signal_profiles") == {
        ("reference_version_id",): "astral_reference_versions",
    }
    assert (
        "reference_version_id",
        "condition_axis",
        "signal_code",
        "signal_level",
    ) in _unique_column_sets(head_inspector, "astral_planet_condition_signal_profiles")
    assert _columns(head_inspector, "astral_dominance_factor_types") == {
        "id",
        "code",
        "label",
        "category",
        "default_weight",
        "sort_order",
        "is_active",
        "description",
        "reference_version_id",
    }
    assert _foreign_key_targets(head_inspector, "astral_dominance_factor_types") == {
        ("reference_version_id",): "astral_reference_versions",
    }
    assert (
        "reference_version_id",
        "code",
    ) in _unique_column_sets(head_inspector, "astral_dominance_factor_types")
    assert _columns(head_inspector, "astral_dominance_score_profiles") == {
        "id",
        "code",
        "label",
        "tradition_code",
        "description",
        "reference_version_code",
        "is_active",
        "reference_version_id",
    }
    assert _foreign_key_targets(head_inspector, "astral_dominance_score_profiles") == {
        ("reference_version_id",): "astral_reference_versions",
    }
    assert (
        "reference_version_id",
        "code",
    ) in _unique_column_sets(head_inspector, "astral_dominance_score_profiles")
    assert _columns(head_inspector, "astral_dominance_score_weights") == {
        "id",
        "score_profile_id",
        "factor_type_id",
        "weight",
        "min_value",
        "max_value",
        "normalization_method",
        "notes",
    }
    assert _foreign_key_targets(head_inspector, "astral_dominance_score_weights") == {
        ("score_profile_id",): "astral_dominance_score_profiles",
        ("factor_type_id",): "astral_dominance_factor_types",
    }
    assert (
        "score_profile_id",
        "factor_type_id",
    ) in _unique_column_sets(head_inspector, "astral_dominance_score_weights")
    assert _columns(head_inspector, "astral_advanced_condition_types") == {
        "id",
        "code",
        "label",
        "category",
        "description",
        "functional_effect",
        "expression_effect",
        "intensity_effect",
        "visibility_effect",
        "default_weight",
        "sort_order",
        "is_active",
        "reference_version_id",
    }
    assert _foreign_key_targets(head_inspector, "astral_advanced_condition_types") == {
        ("reference_version_id",): "astral_reference_versions",
    }
    assert (
        "reference_version_id",
        "code",
    ) in _unique_column_sets(head_inspector, "astral_advanced_condition_types")
    assert "house_interpretation_profiles" not in head_tables
    assert "astral_sign_rulerships" not in head_tables
    for table_name in (
        "astral_planets",
        "astral_signs",
        "astral_houses",
        "astral_aspects",
        "astro_points",
        "astral_house_axis_definitions",
    ):
        columns = {column["name"] for column in head_inspector.get_columns(table_name)}
        assert "reference_version_id" not in columns
    planet_columns = {column["name"] for column in head_inspector.get_columns("astral_planets")}
    assert planet_columns == {"id", "code", "name", "swe_id"}
    constellation_columns = {
        column["name"] for column in head_inspector.get_columns("astral_constellations")
    }
    assert constellation_columns == {
        "id",
        "key",
        "display_name",
        "latin_name",
        "abbreviation",
        "zodiacal",
        "hemisphere_id",
        "notes",
    }
    constellation_foreign_key_targets = {
        foreign_key["referred_table"]
        for foreign_key in head_inspector.get_foreign_keys("astral_constellations")
        if "hemisphere_id" in foreign_key["constrained_columns"]
    }
    assert constellation_foreign_key_targets == {"astral_hemispheres"}
    hemisphere_columns = {
        column["name"] for column in head_inspector.get_columns("astral_hemispheres")
    }
    assert hemisphere_columns == {"id", "key", "display_name", "description", "usage_note"}
    zodiacal_category_columns = {
        column["name"]
        for column in head_inspector.get_columns("astral_zodiacal_reference_system_categories")
    }
    assert zodiacal_category_columns == {
        "id",
        "key",
        "display_name",
        "description",
        "usage_note",
    }
    zodiacal_system_columns = {
        column["name"] for column in head_inspector.get_columns("astral_zodiacal_reference_systems")
    }
    assert zodiacal_system_columns == {
        "id",
        "key",
        "display_name",
        "category_id",
        "description",
        "requires_ayanamsha",
        "usage_note",
    }
    zodiacal_system_foreign_key_targets = {
        foreign_key["referred_table"]
        for foreign_key in head_inspector.get_foreign_keys("astral_zodiacal_reference_systems")
        if "category_id" in foreign_key["constrained_columns"]
    }
    assert zodiacal_system_foreign_key_targets == {"astral_zodiacal_reference_system_categories"}
    reference_epoch_columns = {
        column["name"] for column in head_inspector.get_columns("astral_reference_epochs")
    }
    assert reference_epoch_columns == {
        "id",
        "key",
        "display_name",
        "description",
        "epoch_type",
        "julian_year",
        "iso_datetime",
        "is_standard",
        "usage_note",
    }
    reference_source_columns = {
        column["name"] for column in head_inspector.get_columns("astral_reference_sources")
    }
    assert reference_source_columns == {
        "id",
        "key",
        "display_name",
        "category",
        "publisher",
        "website",
        "is_canonical",
        "usage_note",
    }
    fixed_star_columns = {
        column["name"] for column in head_inspector.get_columns("astral_fixed_stars")
    }
    assert fixed_star_columns == {"id", "key", "display_name"}
    fixed_star_keyword_columns = {
        column["name"] for column in head_inspector.get_columns("astral_fixed_star_keywords")
    }
    assert fixed_star_keyword_columns == {"id", "keywords_json"}
    fixed_star_keyword_translation_columns = {
        column["name"]
        for column in head_inspector.get_columns("astral_fixed_star_keyword_translations")
    }
    assert fixed_star_keyword_translation_columns == {
        "id",
        "astral_fixed_star_keywords_id",
        "language_id",
        "keywords_json",
    }
    fixed_star_definition_columns = {
        column["name"] for column in head_inspector.get_columns("astral_fixed_star_definitions")
    }
    assert fixed_star_definition_columns == {
        "id",
        "fixed_star_id",
        "constellation_id",
        "zodiacal_reference_system_id",
        "reference_epoch_id",
        "ecliptic_longitude_deg",
        "zodiac_sign_id",
        "zodiac_degree",
        "declination_deg",
        "right_ascension_deg",
        "visual_magnitude",
        "astral_fixed_star_keywords_id",
        "is_active",
        "source_id",
        "notes",
    }
    fixed_star_definition_foreign_key_targets = {
        foreign_key["referred_table"]
        for foreign_key in head_inspector.get_foreign_keys("astral_fixed_star_definitions")
    }
    assert fixed_star_definition_foreign_key_targets == {
        "astral_fixed_stars",
        "astral_constellations",
        "astral_zodiacal_reference_systems",
        "astral_reference_epochs",
        "astral_signs",
        "astral_fixed_star_keywords",
        "astral_reference_sources",
    }
    axis_definition_columns = {
        column["name"] for column in head_inspector.get_columns("astral_house_axis_definitions")
    }
    assert axis_definition_columns == {
        "id",
        "astral_system_id",
        "key",
        "title",
        "summary",
        "language_id",
        "micro_note",
    }
    aspect_definition_check_constraints = {
        constraint["name"]
        for constraint in head_inspector.get_check_constraints("astral_aspect_definitions")
    }
    assert "ck_astral_aspect_definitions_enabled_default_orb" in (
        aspect_definition_check_constraints
    )
    planet_foreign_key_targets = {
        foreign_key["referred_table"]
        for table_name in (
            "astral_prediction_daily_planet_profiles",
            "astral_planet_category_weights",
            "astral_planet_sign_dignities",
        )
        for foreign_key in head_inspector.get_foreign_keys(table_name)
        if (
            "planet_id" in foreign_key["constrained_columns"]
            or "astral_planet_id" in foreign_key["constrained_columns"]
        )
    }
    assert planet_foreign_key_targets == {"astral_planets"}
    house_foreign_key_targets = {
        foreign_key["referred_table"]
        for table_name in (
            "astral_prediction_daily_house_profiles",
            "astral_house_category_weights",
        )
        for foreign_key in head_inspector.get_foreign_keys(table_name)
        if "house_id" in foreign_key["constrained_columns"]
    }
    assert house_foreign_key_targets == {"astral_houses"}
    aspect_family_foreign_key_targets = {
        foreign_key["referred_table"]
        for foreign_key in head_inspector.get_foreign_keys("astral_aspects")
        if foreign_key["constrained_columns"] == ["family"]
    }
    assert aspect_family_foreign_key_targets == {"astral_aspect_families"}
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
    system_columns = {column["name"] for column in head_inspector.get_columns("astral_systems")}
    assert system_columns == {"id", "name", "inherits_from_system_id"}
    system_foreign_keys = {
        tuple(foreign_key["constrained_columns"]): foreign_key["referred_table"]
        for foreign_key in head_inspector.get_foreign_keys("astral_systems")
    }
    assert system_foreign_keys[("inherits_from_system_id",)] == "astral_systems"
    house_system_columns = {
        column["name"] for column in head_inspector.get_columns("astral_house_systems")
    }
    assert house_system_columns == {
        "id",
        "code",
        "name",
        "description",
        "astronomical_family",
        "supports_polar_regions",
        "is_quadrant_based",
        "requires_precise_birth_time",
        "sort_order",
        "is_active",
        "created_at",
        "updated_at",
    }
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
        assert dict(
            connection.execute(
                text(
                    """
                    SELECT child.name, parent.name
                    FROM astral_systems AS child
                    LEFT JOIN astral_systems AS parent
                        ON child.inherits_from_system_id = parent.id
                    """
                )
            ).all()
        ) == {
            "hellenistic": "traditional",
            "medieval": "traditional",
            "modern": None,
            "traditional": None,
        }
        house_system_rows = connection.execute(
            text(
                """
                SELECT
                    code,
                    astronomical_family,
                    supports_polar_regions,
                    is_quadrant_based,
                    requires_precise_birth_time,
                    sort_order
                FROM astral_house_systems
                WHERE is_active IS TRUE
                """
            )
        ).all()
        assert {
            row.code: (
                row.astronomical_family,
                bool(row.supports_polar_regions),
                bool(row.is_quadrant_based),
                bool(row.requires_precise_birth_time),
                row.sort_order,
            )
            for row in house_system_rows
        } == EXPECTED_HOUSE_SYSTEMS
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
            connection.execute(text("SELECT COUNT(*) FROM astral_aspect_families")).scalar_one()
            == 3
        )
        assert "astal_aspect_families" not in head_tables
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_default_valence")).scalar_one()
            == 4
        )
        assert (
            connection.execute(
                text("SELECT COUNT(*) FROM astral_interpretive_valence")
            ).scalar_one()
            == 5
        )
        assert connection.execute(text("SELECT COUNT(*) FROM astral_aspects")).scalar_one() == 20
        assert dict(connection.execute(text("SELECT code, swe_id FROM astral_planets")).all()) == {
            "sun": 0,
            "moon": 1,
            "mercury": 2,
            "venus": 3,
            "mars": 4,
            "jupiter": 5,
            "saturn": 6,
            "uranus": 7,
            "neptune": 8,
            "pluto": 9,
        }
        assert dict(connection.execute(text("SELECT code, name FROM languages")).all()) == (
            EXPECTED_LANGUAGES
        )
        assert (
            connection.execute(
                text("SELECT COUNT(*) FROM astral_house_axis_definitions")
            ).scalar_one()
            == 6
        )
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_house_axis_members")).scalar_one()
            == 12
        )
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_angle_points")).scalar_one() == 4
        )
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_astrological_roles")).scalar_one()
            == 6
        )
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_calculation_types")).scalar_one()
            == 2
        )
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_house_modalities")).scalar_one()
            == 3
        )
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_object_types")).scalar_one() == 3
        )
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_constellations")).scalar_one()
            == 18
        )
        assert dict(
            connection.execute(
                text("SELECT key, abbreviation FROM astral_constellations WHERE zodiacal = 1")
            ).all()
        ) == {
            "aries": "Ari",
            "taurus": "Tau",
            "gemini": "Gem",
            "cancer": "Cnc",
            "leo": "Leo",
            "virgo": "Vir",
            "libra": "Lib",
            "scorpius": "Sco",
            "sagittarius": "Sgr",
            "capricornus": "Cap",
            "aquarius": "Aqr",
            "pisces": "Psc",
        }
        assert (
            connection.execute(
                text("SELECT hemisphere_id FROM astral_constellations WHERE key = 'orion'")
            ).scalar_one()
            == 3
        )
        assert dict(
            connection.execute(text("SELECT key, display_name FROM astral_hemispheres")).all()
        ) == {
            "northern": "Northern",
            "southern": "Southern",
            "equatorial": "Equatorial",
        }
        assert dict(
            connection.execute(
                text("SELECT key, display_name FROM astral_zodiacal_reference_system_categories")
            ).all()
        ) == {
            "zodiac": "Zodiac",
            "observer_frame": "Observer Frame",
            "coordinate_system": "Coordinate System",
        }
        assert (
            connection.execute(
                text("SELECT COUNT(*) FROM astral_zodiacal_reference_systems")
            ).scalar_one()
            == 8
        )
        assert dict(
            connection.execute(
                text("SELECT key, category_id FROM astral_zodiacal_reference_systems")
            ).all()
        ) == {
            "tropical": 1,
            "sidereal": 1,
            "draconic": 1,
            "geocentric": 2,
            "heliocentric": 2,
            "topocentric": 2,
            "equatorial": 3,
            "ecliptic": 3,
        }
        assert dict(
            connection.execute(text("SELECT key, epoch_type FROM astral_reference_epochs")).all()
        ) == {
            "j2000": "julian_epoch",
            "b1950": "besselian_epoch",
            "j2050": "julian_epoch",
            "of_date": "runtime_epoch",
        }
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_reference_sources")).scalar_one()
            == 9
        )
        assert dict(
            connection.execute(
                text(
                    "SELECT key, is_canonical FROM astral_reference_sources WHERE is_canonical = 1"
                )
            ).all()
        ) == {
            "swiss_ephemeris": True,
            "hipparcos": True,
        }
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_fixed_stars")).scalar_one() == 10
        )
        assert (
            connection.execute(text("SELECT COUNT(*) FROM astral_fixed_star_keywords")).scalar_one()
            == 10
        )
        assert (
            connection.execute(
                text("SELECT COUNT(*) FROM astral_fixed_star_keyword_translations")
            ).scalar_one()
            == 40
        )
        assert (
            connection.execute(
                text("SELECT COUNT(*) FROM astral_fixed_star_definitions")
            ).scalar_one()
            == 10
        )
        assert (
            connection.execute(
                text(
                    """
                    SELECT astral_fixed_stars.key
                    FROM astral_fixed_star_definitions
                    JOIN astral_fixed_stars
                        ON astral_fixed_star_definitions.fixed_star_id = astral_fixed_stars.id
                    WHERE astral_fixed_star_definitions.astral_fixed_star_keywords_id = 1
                    """
                )
            ).scalar_one()
            == "regulus"
        )
        assert dict(
            connection.execute(text("SELECT code, associated_house FROM astral_angle_points")).all()
        ) == {"asc": 1, "dsc": 7, "mc": 10, "ic": 4}
        assert {
            row[0]
            for row in connection.execute(text("SELECT code FROM astral_astrological_roles")).all()
        } == {
            "luminary",
            "personal_planet",
            "social_planet",
            "transpersonal_planet",
            "angle",
            "lunar_node",
        }
        assert {
            row[0] for row in connection.execute(text("SELECT name FROM astral_house_modalities"))
        } == {"angular", "succedent", "cadent"}
        axis_member_rows = connection.execute(
            text(
                """
                SELECT house_id, opposite_house_id
                FROM astral_house_axis_members
                ORDER BY house_id
                """
            )
        ).all()
        assert {row.house_id: row.opposite_house_id for row in axis_member_rows} == {
            1: 7,
            2: 8,
            3: 9,
            4: 10,
            5: 11,
            6: 12,
            7: 1,
            8: 2,
            9: 3,
            10: 4,
            11: 5,
            12: 6,
        }
        assert (
            connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM astral_aspects
                    WHERE family IS NULL
                    """
                )
            ).scalar_one()
            == 0
        )
        reference_version_count = connection.execute(
            text("SELECT COUNT(*) FROM astral_reference_versions")
        ).scalar_one()
        modern_definition_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM astral_aspect_definitions
                JOIN astral_systems
                    ON astral_aspect_definitions.astral_system_id = astral_systems.id
                WHERE astral_systems.name = 'modern'
                """
            )
        ).scalar_one()
        orb_rule_count = connection.execute(
            text("SELECT COUNT(*) FROM astral_aspect_orb_rules")
        ).scalar_one()
        if reference_version_count:
            assert modern_definition_count == 20 * reference_version_count
            assert orb_rule_count == 79 * reference_version_count
        else:
            assert modern_definition_count == 0
            assert orb_rule_count == 0
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
        rulership_rows = connection.execute(
            text(
                """
                SELECT astral_signs.code AS sign_code, astral_planets.code AS planet_code
                FROM astral_planet_sign_dignities
                JOIN astral_signs
                    ON astral_planet_sign_dignities.astral_sign_id = astral_signs.id
                JOIN astral_planets
                    ON astral_planet_sign_dignities.astral_planet_id = astral_planets.id
                JOIN astral_dignity_type
                    ON astral_planet_sign_dignities.astral_dignity_type_id =
                        astral_dignity_type.id
                JOIN astral_systems
                    ON astral_planet_sign_dignities.astral_system_id = astral_systems.id
                WHERE astral_dignity_type.code = 'domicile'
                    AND astral_systems.name = 'traditional'
                    AND astral_planet_sign_dignities.is_primary IS TRUE
                """
            )
        ).all()
        assert {row.sign_code: row.planet_code for row in rulership_rows} == (
            EXPECTED_TRADITIONAL_RULERSHIPS
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
        "astral_prediction_daily_house_profiles",
        "astral_house_interpretation_profiles",
        "astral_aspect_interpretation_profiles",
        "astral_aspect_profiles",
        "astral_planet_category_weights",
        "astral_house_category_weights",
        "point_category_weights",
    ):
        columns = {column["name"] for column in head_inspector.get_columns(table_name)}
        assert "reference_version_id" in columns
    daily_planet_columns = {
        column["name"]
        for column in head_inspector.get_columns("astral_prediction_daily_planet_profiles")
    }
    assert daily_planet_columns == {
        "id",
        "reference_version_id",
        "planet_id",
        "weight_intraday",
        "weight_day_climate",
        "daily_visibility_score",
        "daily_emotional_impact_score",
        "daily_conscious_activation_score",
        "is_enabled",
        "micro_note",
    }
    assert (
        not {
            "class_code",
            "speed_rank",
            "speed_class",
            "typical_polarity",
            "orb_active_deg",
            "orb_peak_deg",
            "keywords_json",
        }
        & daily_planet_columns
    )
    house_interpretation_columns = {
        column["name"]
        for column in head_inspector.get_columns("astral_house_interpretation_profiles")
    }
    assert house_interpretation_columns == {
        "id",
        "reference_version_id",
        "house_id",
        "language_id",
        "astral_system_id",
        "title",
        "summary",
        "core_keywords_json",
        "shadow_keywords_json",
        "psychological_keywords_json",
        "material_keywords_json",
        "relationship_keywords_json",
        "career_keywords_json",
        "health_keywords_json",
        "spiritual_keywords_json",
        "body_parts_json",
        "archetypes_json",
        "dos_json",
        "donts_json",
        "prompt_hints_json",
        "micro_note",
    }
    house_interpretation_unique_columns = {
        tuple(constraint["column_names"])
        for constraint in head_inspector.get_unique_constraints(
            "astral_house_interpretation_profiles"
        )
    }
    assert (
        "reference_version_id",
        "house_id",
        "language_id",
        "astral_system_id",
    ) in house_interpretation_unique_columns
    house_interpretation_foreign_keys = {
        tuple(foreign_key["constrained_columns"]): foreign_key["referred_table"]
        for foreign_key in head_inspector.get_foreign_keys("astral_house_interpretation_profiles")
    }
    assert (
        house_interpretation_foreign_keys[("reference_version_id",)] == "astral_reference_versions"
    )
    assert house_interpretation_foreign_keys[("house_id",)] == "astral_houses"
    assert house_interpretation_foreign_keys[("astral_system_id",)] == "astral_systems"
    assert house_interpretation_foreign_keys[("language_id",)] == "languages"
    aspect_interpretation_columns = {
        column["name"]
        for column in head_inspector.get_columns("astral_aspect_interpretation_profiles")
    }
    assert aspect_interpretation_columns == {
        "id",
        "reference_version_id",
        "aspect_id",
        "astral_system_id",
        "language_id",
        "title",
        "summary",
        "core_keywords_json",
        "shadow_keywords_json",
        "psychological_keywords_json",
        "relationship_keywords_json",
        "career_keywords_json",
        "spiritual_keywords_json",
        "energetic_dynamics_json",
        "growth_patterns_json",
        "conflict_patterns_json",
        "archetypes_json",
        "dos_json",
        "donts_json",
        "prompt_hints_json",
        "micro_note",
    }
    aspect_interpretation_unique_columns = {
        tuple(constraint["column_names"])
        for constraint in head_inspector.get_unique_constraints(
            "astral_aspect_interpretation_profiles"
        )
    }
    assert (
        "reference_version_id",
        "aspect_id",
        "astral_system_id",
        "language_id",
    ) in aspect_interpretation_unique_columns
    aspect_interpretation_foreign_keys = {
        tuple(foreign_key["constrained_columns"]): foreign_key["referred_table"]
        for foreign_key in head_inspector.get_foreign_keys("astral_aspect_interpretation_profiles")
    }
    assert (
        aspect_interpretation_foreign_keys[("reference_version_id",)] == "astral_reference_versions"
    )
    assert aspect_interpretation_foreign_keys[("aspect_id",)] == "astral_aspects"
    assert aspect_interpretation_foreign_keys[("astral_system_id",)] == "astral_systems"
    assert aspect_interpretation_foreign_keys[("language_id",)] == "languages"
    user_column_definitions = {
        column["name"]: column for column in head_inspector.get_columns("users")
    }
    user_columns = set(user_column_definitions)
    assert "default_language_id" in user_columns
    assert "detected_locale" in user_columns
    assert "detected_country_code" in user_columns
    assert "detected_timezone" in user_columns
    assert getattr(user_column_definitions["detected_locale"]["type"], "length", None) == 64
    user_foreign_keys = {
        tuple(foreign_key["constrained_columns"]): foreign_key["referred_table"]
        for foreign_key in head_inspector.get_foreign_keys("users")
    }
    assert user_foreign_keys[("default_language_id",)] == "languages"
    for table_name in (
        "prediction_categories",
        "astral_prediction_daily_planet_profiles",
        "astral_prediction_daily_house_profiles",
        "astral_house_interpretation_profiles",
        "astral_aspect_interpretation_profiles",
        "astral_aspect_profiles",
        "astral_planet_category_weights",
        "astral_house_category_weights",
        "point_category_weights",
        "prediction_rulesets",
        "daily_prediction_runs",
        "user_prediction_baselines",
    ):
        foreign_keys = {
            tuple(foreign_key["constrained_columns"]): foreign_key["referred_table"]
            for foreign_key in head_inspector.get_foreign_keys(table_name)
        }
        if ("reference_version_id",) in foreign_keys:
            assert foreign_keys[("reference_version_id",)] == "astral_reference_versions"
    assert "planet_profiles" not in set(head_inspector.get_table_names())
    assert "house_profiles" not in set(head_inspector.get_table_names())
    assert "house_category_weights" not in set(head_inspector.get_table_names())
    runtime_house_system_columns = {
        table_name: {column["name"] for column in head_inspector.get_columns(table_name)}
        for table_name in (
            "prediction_rulesets",
            "daily_prediction_runs",
            "user_prediction_baselines",
        )
    }
    assert "house_system_id" in runtime_house_system_columns["prediction_rulesets"]
    assert "house_system" not in runtime_house_system_columns["prediction_rulesets"]
    assert "house_system_effective_id" in runtime_house_system_columns["daily_prediction_runs"]
    assert "house_system_effective" not in runtime_house_system_columns["daily_prediction_runs"]
    assert "house_system_effective_id" in runtime_house_system_columns["user_prediction_baselines"]
    assert "house_system_effective" not in runtime_house_system_columns["user_prediction_baselines"]
    head_engine.dispose()


def test_system_inheritance_migration_removes_old_child_orb_rule_copies(
    monkeypatch: object, tmp_path: Path
) -> None:
    """Simule une base deja passee par l'ancien seed 0104 puis nettoyee par 0105."""
    db_path = tmp_path / "migration-orb-copy-cleanup.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.downgrade(config, "base")
    command.upgrade(config, "20260514_0104")

    engine = create_engine(database_url, future=True)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO astral_reference_versions (
                    id,
                    version,
                    description,
                    is_locked,
                    created_at
                )
                VALUES (999, 'legacy-copy-test', '', 0, '2026-05-14 00:00:00')
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO astral_aspect_orb_rules (
                    reference_version_id,
                    astral_system_id,
                    aspect_id,
                    calculation_context,
                    source_body_type,
                    source_planet_id,
                    source_point_code,
                    target_body_type,
                    target_planet_id,
                    target_point_code,
                    orb_deg,
                    priority,
                    is_enabled,
                    micro_note
                )
                SELECT
                    999,
                    astral_systems.id,
                    (SELECT id FROM astral_aspects WHERE code = 'square'),
                    'natal',
                    'luminary',
                    NULL,
                    NULL,
                    'any',
                    NULL,
                    NULL,
                    8.0,
                    800,
                    1,
                    'legacy copied parent rule'
                FROM astral_systems
                WHERE astral_systems.name = 'traditional'
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO astral_aspect_orb_rules (
                    reference_version_id,
                    astral_system_id,
                    aspect_id,
                    calculation_context,
                    source_body_type,
                    source_planet_id,
                    source_point_code,
                    target_body_type,
                    target_planet_id,
                    target_point_code,
                    orb_deg,
                    priority,
                    is_enabled,
                    micro_note
                )
                SELECT
                    parent_rule.reference_version_id,
                    child_system.id,
                    parent_rule.aspect_id,
                    parent_rule.calculation_context,
                    parent_rule.source_body_type,
                    parent_rule.source_planet_id,
                    parent_rule.source_point_code,
                    parent_rule.target_body_type,
                    parent_rule.target_planet_id,
                    parent_rule.target_point_code,
                    parent_rule.orb_deg,
                    parent_rule.priority,
                    parent_rule.is_enabled,
                    parent_rule.micro_note
                FROM astral_aspect_orb_rules AS parent_rule
                JOIN astral_systems AS parent_system
                    ON parent_rule.astral_system_id = parent_system.id
                JOIN astral_systems AS child_system
                    ON child_system.name IN ('hellenistic', 'medieval')
                WHERE parent_system.name = 'traditional'
                    AND parent_rule.reference_version_id = 999
                """
            )
        )
        copied_counts = dict(
            connection.execute(
                text(
                    """
                    SELECT astral_systems.name, COUNT(astral_aspect_orb_rules.id)
                    FROM astral_systems
                    LEFT JOIN astral_aspect_orb_rules
                        ON astral_aspect_orb_rules.astral_system_id = astral_systems.id
                    GROUP BY astral_systems.name
                    """
                )
            ).all()
        )
        assert copied_counts["traditional"] == 1
        assert copied_counts["hellenistic"] == 1
        assert copied_counts["medieval"] == 1
    engine.dispose()

    command.upgrade(config, "head")

    head_engine = create_engine(database_url, future=True)
    with head_engine.connect() as connection:
        final_counts = dict(
            connection.execute(
                text(
                    """
                    SELECT astral_systems.name, COUNT(astral_aspect_orb_rules.id)
                    FROM astral_systems
                    LEFT JOIN astral_aspect_orb_rules
                        ON astral_aspect_orb_rules.astral_system_id = astral_systems.id
                    GROUP BY astral_systems.name
                    """
                )
            ).all()
        )
    head_engine.dispose()

    assert final_counts["traditional"] == 1
    assert final_counts["hellenistic"] == 0
    assert final_counts["medieval"] == 0

    command.downgrade(config, "base")

    downgraded_engine = create_engine(database_url, future=True)
    downgraded_tables = set(inspect(downgraded_engine).get_table_names())
    assert "reference_versions" not in downgraded_tables
    downgraded_engine.dispose()


def test_aspect_interpretation_migration_accepts_matching_precreated_table(
    monkeypatch: object, tmp_path: Path
) -> None:
    """Valide la reprise si la table a été créée avant le stamp Alembic."""
    db_path = tmp_path / "migration-precreated-aspect-interpretation.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.downgrade(config, "base")
    command.upgrade(config, "20260514_0105")

    engine = create_engine(database_url, future=True)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE astral_aspect_interpretation_profiles (
                    id INTEGER NOT NULL,
                    reference_version_id INTEGER NOT NULL,
                    aspect_id INTEGER NOT NULL,
                    astral_system_id INTEGER NOT NULL,
                    language VARCHAR(16) NOT NULL,
                    title VARCHAR(128) NOT NULL,
                    summary TEXT,
                    core_keywords_json TEXT,
                    shadow_keywords_json TEXT,
                    psychological_keywords_json TEXT,
                    relationship_keywords_json TEXT,
                    career_keywords_json TEXT,
                    spiritual_keywords_json TEXT,
                    energetic_dynamics_json TEXT,
                    growth_patterns_json TEXT,
                    conflict_patterns_json TEXT,
                    archetypes_json TEXT,
                    dos_json TEXT,
                    donts_json TEXT,
                    prompt_hints_json TEXT,
                    micro_note TEXT,
                    PRIMARY KEY (id),
                    FOREIGN KEY(reference_version_id) REFERENCES astral_reference_versions (id),
                    FOREIGN KEY(aspect_id) REFERENCES astral_aspects (id),
                    FOREIGN KEY(astral_system_id) REFERENCES astral_systems (id),
                    UNIQUE (reference_version_id, aspect_id, astral_system_id, language)
                )
                """
            )
        )
    engine.dispose()

    command.upgrade(config, "head")

    head_engine = create_engine(database_url, future=True)
    head_inspector = inspect(head_engine)
    indexes = {
        index["name"]
        for index in head_inspector.get_indexes("astral_aspect_interpretation_profiles")
    }
    with head_engine.connect() as connection:
        version = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
        profile_count = connection.execute(
            text("SELECT COUNT(*) FROM astral_aspect_interpretation_profiles")
        ).scalar()
        version_count = connection.execute(
            text("SELECT COUNT(*) FROM astral_reference_versions")
        ).scalar()
    head_engine.dispose()

    assert version == "20260519_0133"
    assert profile_count == version_count * 20
    assert {
        "ix_astral_aspect_interpretation_profiles_reference_version_id",
        "ix_astral_aspect_interpretation_profiles_aspect_id",
        "ix_astral_aspect_interpretation_profiles_astral_system_id",
    } <= indexes


def test_daily_planet_profile_simplification_preserves_existing_versions(
    monkeypatch: object,
    tmp_path: Path,
) -> None:
    """Vérifie que la simplification daily ne supprime pas les versions existantes."""
    db_path = tmp_path / "daily-planet-profile-simplification.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.downgrade(config, "base")
    command.upgrade(config, "20260515_0114")

    engine = create_engine(database_url, future=True)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO astral_reference_versions
                    (id, version, description, is_locked, created_at)
                VALUES
                    (101, 'test-101', 'Test 101', 0, '2026-05-15 00:00:00'),
                    (202, 'test-202', 'Test 202', 0, '2026-05-15 00:00:00')
                """
            )
        )
    engine.dispose()

    command.upgrade(config, "head")

    head_engine = create_engine(database_url, future=True)
    with head_engine.connect() as connection:
        counts = dict(
            connection.execute(
                text(
                    """
                    SELECT reference_version_id, COUNT(*)
                    FROM astral_prediction_daily_planet_profiles
                    WHERE reference_version_id IN (101, 202)
                    GROUP BY reference_version_id
                    """
                )
            ).all()
        )
        planet_codes = {
            row[0]
            for row in connection.execute(
                text(
                    """
                    SELECT planet.code
                    FROM astral_prediction_daily_planet_profiles AS profile
                    JOIN astral_planets AS planet ON planet.id = profile.planet_id
                    WHERE profile.reference_version_id = 101
                    """
                )
            ).all()
        }
    head_engine.dispose()

    assert counts == {101: 10, 202: 10}
    assert planet_codes == {
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    }
