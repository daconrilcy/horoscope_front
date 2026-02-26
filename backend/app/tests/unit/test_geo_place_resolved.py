"""Tests unitaires pour geo_place_resolved — story 19-4.

Couvre :
- AC1 : création d'une entrée geo_place_resolved
- AC2 : colonnes lat/lon de type DECIMAL stable, country_code ISO2 normalisé
- AC3 : provider borné à 'nominatim'
- AC4 : idempotence/upsert via unique constraint
- AC5 : lecture lat/lon canonique propagée au service natal
- AC6 : tous les champs AC6 persistés et retrouvables
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

# ---------------------------------------------------------------------------
# Task 1 — Structure du modèle SQLAlchemy
# ---------------------------------------------------------------------------


def test_geo_place_resolved_table_name():
    """La table a le bon nom."""
    from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel

    assert GeoPlaceResolvedModel.__tablename__ == "geo_place_resolved"


def test_geo_place_resolved_has_all_required_columns():
    """Tous les champs du schéma minimal sont présents (AC2, AC6)."""
    from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel

    cols = {c.name for c in GeoPlaceResolvedModel.__table__.columns}
    required = {
        # identity provider
        "id",
        "provider",
        "provider_place_id",
        "osm_type",
        "osm_id",
        "display_name",
        "place_type",
        "place_class",
        "importance",
        "place_rank",
        # coordinates
        "latitude",
        "longitude",
        # geo hierarchy
        "country_code",
        "country",
        "state",
        "county",
        "city",
        "postcode",
        # timezone
        "timezone_iana",
        "timezone_source",
        "timezone_confidence",
        # quality/stability
        "normalized_query",
        "query_language",
        "query_country_code",
        "raw_hash",
        # timestamps
        "created_at",
        "updated_at",
    }
    assert required.issubset(cols), f"Colonnes manquantes: {required - cols}"


def test_geo_place_resolved_unique_constraint_on_provider_place_id():
    """Contrainte unique (provider, provider_place_id) pour l'idempotence (AC4)."""
    from sqlalchemy import UniqueConstraint

    from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel

    uc_col_sets = []
    for c in GeoPlaceResolvedModel.__table__.constraints:
        if isinstance(c, UniqueConstraint):
            uc_col_sets.append({col.name for col in c.columns})

    assert any("provider" in s and "provider_place_id" in s for s in uc_col_sets), (
        f"Aucune contrainte unique (provider, provider_place_id) trouvée. UC sets: {uc_col_sets}"
    )


def test_geo_place_resolved_lat_lon_are_numeric_type():
    """lat/lon utilisent Numeric (DECIMAL) pour la stabilité des calculs (AC2)."""
    from sqlalchemy import Numeric

    from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel

    col_map = {c.name: c for c in GeoPlaceResolvedModel.__table__.columns}
    assert isinstance(col_map["latitude"].type, Numeric), (
        "latitude doit être Numeric (DECIMAL), pas Float"
    )
    assert isinstance(col_map["longitude"].type, Numeric), (
        "longitude doit être Numeric (DECIMAL), pas Float"
    )


def test_geo_place_resolved_check_constraints_exist():
    """CheckConstraints lat/lon range et provider existent (AC2, AC3)."""
    from sqlalchemy import CheckConstraint

    from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel

    check_constraints = [
        c for c in GeoPlaceResolvedModel.__table__.constraints if isinstance(c, CheckConstraint)
    ]
    assert len(check_constraints) >= 2, (
        f"Au moins 2 CheckConstraints attendus (lat_range, lon_range). "
        f"Trouvé: {len(check_constraints)}"
    )


def test_geo_place_resolved_has_lat_lon_index():
    """Index sur (latitude, longitude) pour les lookups par coords."""
    from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel

    indexed_col_sets = [
        {col.name for col in idx.columns} for idx in GeoPlaceResolvedModel.__table__.indexes
    ]
    assert any("latitude" in s and "longitude" in s for s in indexed_col_sets), (
        f"Aucun index (latitude, longitude) trouvé. Index sets: {indexed_col_sets}"
    )


def test_geo_place_resolved_has_normalized_query_index():
    """Index sur normalized_query pour les lookups de requête."""
    from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel

    indexed_cols = {
        col.name for idx in GeoPlaceResolvedModel.__table__.indexes for col in idx.columns
    }
    assert "normalized_query" in indexed_cols, "Index sur normalized_query manquant"


def test_geo_place_resolved_country_code_is_string_2():
    """country_code est String(2) — convention ISO2 (AC2)."""
    from sqlalchemy import String

    from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel

    col_map = {c.name: c for c in GeoPlaceResolvedModel.__table__.columns}
    assert isinstance(col_map["country_code"].type, String)
    assert col_map["country_code"].type.length == 2


# ---------------------------------------------------------------------------
# Task 2 — Repository: persistance, idempotence, raw_hash, normalisation
# ---------------------------------------------------------------------------


def _make_create_data(
    provider_place_id: int = 12345,
    country_code: str | None = "fr",
    raw_payload: dict | None = None,
):
    """Factory pour GeoPlaceResolvedCreateData."""
    from app.infra.db.repositories.geo_place_resolved_repository import (
        GeoPlaceResolvedCreateData,
    )

    return GeoPlaceResolvedCreateData(
        provider="nominatim",
        provider_place_id=provider_place_id,
        display_name="Paris, Île-de-France, France",
        latitude=48.8566,
        longitude=2.3522,
        osm_type="relation",
        osm_id=7444,
        place_type="administrative",
        place_class="boundary",
        importance=0.9,
        place_rank=12,
        country_code=country_code,
        country="France",
        state="Île-de-France",
        city="Paris",
        raw_payload=raw_payload,
    )


def test_repository_find_or_create_creates_new_entry(in_memory_db):
    """AC1 — find_or_create crée une nouvelle entrée si elle n'existe pas."""
    from app.infra.db.repositories.geo_place_resolved_repository import (
        GeoPlaceResolvedRepository,
    )

    data = _make_create_data()
    repo = GeoPlaceResolvedRepository(in_memory_db)
    model, created = repo.find_or_create(data)

    assert created is True
    assert model.id is not None
    assert model.provider == "nominatim"
    assert model.provider_place_id == 12345
    assert model.display_name == "Paris, Île-de-France, France"


def test_repository_find_or_create_is_idempotent(in_memory_db):
    """AC4 — find_or_create retourne la même entrée pour la même clé provider."""
    from app.infra.db.repositories.geo_place_resolved_repository import (
        GeoPlaceResolvedRepository,
    )

    data = _make_create_data()
    repo = GeoPlaceResolvedRepository(in_memory_db)
    model1, created1 = repo.find_or_create(data)
    model2, created2 = repo.find_or_create(data)

    assert created1 is True
    assert created2 is False
    assert model1.id == model2.id


def test_repository_find_or_create_recovers_after_integrity_error_without_global_rollback():
    """AC4 — collision concurrente: re-lookup après IntegrityError sans rollback global."""
    from contextlib import nullcontext

    from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel
    from app.infra.db.repositories.geo_place_resolved_repository import (
        GeoPlaceResolvedRepository,
    )

    session = MagicMock()
    session.begin_nested.return_value = nullcontext()
    session.rollback = MagicMock()
    session.flush.side_effect = IntegrityError("insert", {}, Exception("unique_violation"))

    existing = GeoPlaceResolvedModel(
        id=7,
        provider="nominatim",
        provider_place_id=12345,
        display_name="Paris, Île-de-France, France",
        latitude=48.8566,
        longitude=2.3522,
    )
    session.scalar.side_effect = [None, existing]

    repo = GeoPlaceResolvedRepository(session)
    model, created = repo.find_or_create(_make_create_data())

    assert created is False
    assert model.id == 7
    session.rollback.assert_not_called()


def test_repository_find_or_create_stores_all_ac6_fields(in_memory_db):
    """AC6 — tous les champs AC6 sont persistés et récupérables."""
    from app.infra.db.repositories.geo_place_resolved_repository import (
        GeoPlaceResolvedCreateData,
        GeoPlaceResolvedRepository,
    )

    data = GeoPlaceResolvedCreateData(
        provider="nominatim",
        provider_place_id=99999,
        display_name="Lyon, Auvergne-Rhône-Alpes, France",
        latitude=45.7578137,
        longitude=4.8320114,
        osm_type="relation",
        osm_id=1234,
        timezone_iana="Europe/Paris",
        timezone_source="geonames",
        timezone_confidence=0.98,
    )
    repo = GeoPlaceResolvedRepository(in_memory_db)
    model, _ = repo.find_or_create(data)

    assert model.provider_place_id == 99999
    assert model.osm_type == "relation"
    assert model.osm_id == 1234
    assert model.display_name == "Lyon, Auvergne-Rhône-Alpes, France"
    assert model.timezone_iana == "Europe/Paris"
    assert model.timezone_source == "geonames"
    assert model.timezone_confidence == pytest.approx(0.98)


def test_repository_normalizes_country_code_to_uppercase(in_memory_db):
    """AC2 — country_code est normalisé en uppercase (convention ISO2 uppercase)."""
    from app.infra.db.repositories.geo_place_resolved_repository import (
        GeoPlaceResolvedRepository,
    )

    data = _make_create_data(provider_place_id=11111, country_code="fr")
    repo = GeoPlaceResolvedRepository(in_memory_db)
    model, _ = repo.find_or_create(data)

    assert model.country_code == "FR", (
        f"country_code doit être uppercase 'FR', reçu: '{model.country_code}'"
    )


def test_repository_computes_raw_hash(in_memory_db):
    """Task 2 — raw_hash est calculé depuis raw_payload (SHA256)."""
    import hashlib
    import json

    from app.infra.db.repositories.geo_place_resolved_repository import (
        GeoPlaceResolvedRepository,
    )

    raw_payload = {"place_id": 12345, "lat": "48.8566", "lon": "2.3522"}
    data = _make_create_data(provider_place_id=22222, raw_payload=raw_payload)
    repo = GeoPlaceResolvedRepository(in_memory_db)
    model, _ = repo.find_or_create(data)

    expected_hash = hashlib.sha256(
        json.dumps(raw_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
    assert model.raw_hash == expected_hash


def test_repository_raw_hash_is_none_without_payload(in_memory_db):
    """Task 2 — raw_hash est None si raw_payload non fourni."""
    from app.infra.db.repositories.geo_place_resolved_repository import (
        GeoPlaceResolvedRepository,
    )

    data = _make_create_data(provider_place_id=33333, raw_payload=None)
    repo = GeoPlaceResolvedRepository(in_memory_db)
    model, _ = repo.find_or_create(data)

    assert model.raw_hash is None


def test_repository_find_by_provider_key_returns_none_if_missing(in_memory_db):
    """find_by_provider_key retourne None si entrée inexistante."""
    from app.infra.db.repositories.geo_place_resolved_repository import (
        GeoPlaceResolvedRepository,
    )

    repo = GeoPlaceResolvedRepository(in_memory_db)
    result = repo.find_by_provider_key("nominatim", 999999999)
    assert result is None


def test_repository_lat_lon_are_stable_across_sessions(in_memory_db):
    """AC5 — lat/lon lus depuis geo_place_resolved sont stables (valeurs identiques)."""
    from app.infra.db.repositories.geo_place_resolved_repository import (
        GeoPlaceResolvedRepository,
    )

    data = _make_create_data(provider_place_id=44444)
    repo = GeoPlaceResolvedRepository(in_memory_db)
    model, _ = repo.find_or_create(data)

    # Re-fetch to simulate a second session read
    found = repo.find_by_provider_key("nominatim", 44444)
    assert found is not None
    assert float(found.latitude) == pytest.approx(48.8566)
    assert float(found.longitude) == pytest.approx(2.3522)


# ---------------------------------------------------------------------------
# Task 3 — Pipeline natal : propagation lat/lon canonique
# ---------------------------------------------------------------------------


def test_natal_service_propagates_birth_lat_lon_to_birth_input():
    """AC5 — generate_for_user passe birth_lat/birth_lon au BirthInput depuis le profil."""
    from datetime import date

    from app.services.user_natal_chart_service import UserNatalChartService

    # Mock du profil avec lat/lon renseignés
    mock_profile = MagicMock()
    mock_profile.birth_date = date(1990, 1, 1)
    mock_profile.birth_time = "12:00"
    mock_profile.birth_place = "Paris, France"
    mock_profile.birth_timezone = "Europe/Paris"
    mock_profile.birth_lat = 48.8566
    mock_profile.birth_lon = 2.3522

    captured_birth_input = {}

    def mock_calculate(
        db,
        birth_input,
        reference_version=None,
        timeout_check=None,
        accurate=False,
        **kwargs,
    ):
        captured_birth_input["birth_lat"] = birth_input.birth_lat
        captured_birth_input["birth_lon"] = birth_input.birth_lon
        raise Exception("stop-here")

    with (
        patch(
            "app.services.user_natal_chart_service.UserBirthProfileService.get_for_user",
            return_value=mock_profile,
        ),
        patch(
            "app.services.user_natal_chart_service.NatalCalculationService.calculate",
            side_effect=mock_calculate,
        ),
    ):
        with pytest.raises(Exception, match="stop-here"):
            UserNatalChartService.generate_for_user(db=MagicMock(), user_id=1)

    assert captured_birth_input.get("birth_lat") == pytest.approx(48.8566), (
        "birth_lat non propagé depuis le profil vers BirthInput"
    )
    assert captured_birth_input.get("birth_lon") == pytest.approx(2.3522), (
        "birth_lon non propagé depuis le profil vers BirthInput"
    )


def test_natal_service_propagates_none_lat_lon_when_absent():
    """AC5 (transitoire) — birth_lat/lon passés None si absents du profil."""
    from datetime import date

    from app.services.user_natal_chart_service import UserNatalChartService

    mock_profile = MagicMock()
    mock_profile.birth_date = date(1990, 1, 1)
    mock_profile.birth_time = "12:00"
    mock_profile.birth_place = "Paris, France"
    mock_profile.birth_timezone = "Europe/Paris"
    mock_profile.birth_lat = None
    mock_profile.birth_lon = None

    captured = {}

    def mock_calculate(
        db,
        birth_input,
        reference_version=None,
        timeout_check=None,
        accurate=False,
        **kwargs,
    ):
        captured["birth_lat"] = birth_input.birth_lat
        captured["birth_lon"] = birth_input.birth_lon
        raise Exception("stop-here")

    with (
        patch(
            "app.services.user_natal_chart_service.UserBirthProfileService.get_for_user",
            return_value=mock_profile,
        ),
        patch(
            "app.services.user_natal_chart_service.NatalCalculationService.calculate",
            side_effect=mock_calculate,
        ),
    ):
        with pytest.raises(Exception, match="stop-here"):
            UserNatalChartService.generate_for_user(db=MagicMock(), user_id=1)

    assert captured.get("birth_lat") is None
    assert captured.get("birth_lon") is None


def test_natal_service_prioritizes_resolved_coordinates_over_legacy_conflict():
    """Conflit source: coords résolues doivent gagner sur les coords legacy."""
    from datetime import date

    from app.services.user_natal_chart_service import UserNatalChartService

    mock_profile = MagicMock()
    mock_profile.birth_date = date(1990, 1, 1)
    mock_profile.birth_time = "12:00"
    mock_profile.birth_place = "Paris, France"
    mock_profile.birth_timezone = "Europe/Paris"
    mock_profile.birth_lat = 40.7128
    mock_profile.birth_lon = -74.0060
    mock_profile.birth_place_resolved_id = 777

    class _ResolvedCoordinates:
        birth_lat = 48.8566
        birth_lon = 2.3522
        birth_place_resolved_id = 777
        resolved_from_place = True

    captured = {}

    def mock_calculate(
        db,
        birth_input,
        reference_version=None,
        timeout_check=None,
        accurate=False,
        **kwargs,
    ):
        captured["place_resolved_id"] = birth_input.place_resolved_id
        captured["birth_lat"] = birth_input.birth_lat
        captured["birth_lon"] = birth_input.birth_lon
        raise Exception("stop-here")

    with (
        patch(
            "app.services.user_natal_chart_service.UserBirthProfileService.get_for_user",
            return_value=mock_profile,
        ),
        patch(
            "app.services.user_natal_chart_service.UserBirthProfileService.resolve_coordinates",
            return_value=_ResolvedCoordinates(),
        ),
        patch(
            "app.services.user_natal_chart_service.NatalCalculationService.calculate",
            side_effect=mock_calculate,
        ),
    ):
        with pytest.raises(Exception, match="stop-here"):
            UserNatalChartService.generate_for_user(db=MagicMock(), user_id=1)

    assert captured.get("place_resolved_id") == 777
    assert captured.get("birth_lat") == pytest.approx(48.8566)
    assert captured.get("birth_lon") == pytest.approx(2.3522)


# ---------------------------------------------------------------------------
# Helpers: in-memory SQLite DB fixture (isolation des tests Task 2)
# ---------------------------------------------------------------------------


@pytest.fixture
def in_memory_db():
    """Session SQLite en mémoire avec création des tables nécessaires."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.infra.db.base import Base
    from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel  # noqa: F401

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
