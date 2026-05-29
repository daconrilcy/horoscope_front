from dataclasses import asdict

import pytest
from pytest import MonkeyPatch
from sqlalchemy import delete, select

from app.domain.astrology.house_ruler_resolver import HouseRulerResult
from app.domain.astrology.natal_calculation import NatalResult
from app.domain.astrology.natal_preparation import BirthInput
from app.infra.db.base import Base
from app.infra.db.models import AstralChartPlanetDignityResultModel, PlanetModel
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.repositories.dignity_reference_repository import DignityReferenceRepository
from app.services.chart.dignity_audit_mapper import build_chart_planet_dignity_audit_input
from app.services.chart.result_service import ChartResultService, ChartResultServiceError
from app.services.natal.calculation_service import NatalCalculationService
from app.services.reference_data_service import ReferenceDataService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session


def _cleanup_chart_results() -> None:
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        db.execute(delete(ChartResultModel))
        db.commit()


def test_compute_input_hash_is_deterministic() -> None:
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    first = ChartResultService.compute_input_hash(payload, "1.0.0", "1.0.0")
    second = ChartResultService.compute_input_hash(payload, "1.0.0", "1.0.0")
    assert first == second


def test_compute_input_hash_changes_with_ruleset_version() -> None:
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    first = ChartResultService.compute_input_hash(payload, "1.0.0", "1.0.0")
    second = ChartResultService.compute_input_hash(payload, "1.0.0", "1.1.0")
    assert first != second


def test_persist_trace_requires_versions() -> None:
    _cleanup_chart_results()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    invalid_result = NatalResult(
        reference_version="",
        ruleset_version="1.0.0",
        house_system="equal",
        prepared_input={
            "birth_datetime_local": "1990-06-15T10:30:00+02:00",
            "birth_datetime_utc": "1990-06-15T08:30:00+00:00",
            "timestamp_utc": 645438600,
            "julian_day": 2448057.8541666665,
            "birth_timezone": "Europe/Paris",
        },
        planet_positions=[],
        houses=[],
        aspects=[],
    )
    with open_app_test_db_session() as db:
        try:
            ChartResultService.persist_trace(db, payload, invalid_result)
        except ChartResultServiceError as error:
            assert error.code == "invalid_chart_result"
        else:
            raise AssertionError("Expected ChartResultServiceError")


def test_natal_result_accepts_pre_cs198_dignity_payload_without_sect_condition() -> None:
    """Les anciens payloads stockes restent lisibles sans alias public."""
    payload = {
        "reference_version": "1.0.0",
        "ruleset_version": "1.0.0",
        "house_system": "equal",
        "prepared_input": {
            "birth_datetime_local": "1990-06-15T10:30:00+02:00",
            "birth_datetime_utc": "1990-06-15T08:30:00+00:00",
            "timestamp_utc": 645438600,
            "julian_day": 2448057.8541666665,
            "birth_timezone": "Europe/Paris",
        },
        "planet_positions": [],
        "houses": [],
        "dignity_sect": {
            "chart_sect": "day",
            "sun_horizon_position": "above_horizon",
            "sun_above_horizon": True,
            "calculation_basis": "sun_house_horizon_rule",
            "reference_system": "traditional",
        },
        "dignities": [
            {
                "planet_code": "sun",
                "score_profile": "traditional_standard",
                "tradition": "traditional",
                "reference_version": "1.0.0",
                "sect": "day",
                "chart_sect": {
                    "chart_sect": "day",
                    "sun_horizon_position": "above_horizon",
                    "sun_above_horizon": True,
                    "calculation_basis": "sun_house_horizon_rule",
                    "reference_system": "traditional",
                },
                "essential_score": 0,
                "accidental_score": 0,
                "total_score": 0,
                "functional_strength_score": 0,
                "expression_quality_score": 0,
                "intensity_score": 0,
                "essential_breakdown": [],
                "accidental_breakdown": [],
            }
        ],
        "aspects": [],
    }

    result = NatalResult.model_validate(payload)

    assert result.dignities[0].sect_condition is None


def test_get_audit_record_preserves_old_payload_gaps_without_backfill() -> None:
    """Les anciens payloads relus ne sont pas modifies pour fabriquer les nouveaux blocs."""
    _cleanup_chart_results()
    chart_id = "old-public-json-gap"
    old_payload = {
        "reference_version": "1.0.0",
        "ruleset_version": "1.0.0",
        "house_system": "equal",
        "prepared_input": {
            "birth_datetime_local": "1990-06-15T10:30:00+02:00",
            "birth_datetime_utc": "1990-06-15T08:30:00+00:00",
            "timestamp_utc": 645438600,
            "julian_day": 2448057.8541666665,
            "birth_timezone": "Europe/Paris",
        },
        "planet_positions": [],
        "houses": [],
        "dignities": [],
        "aspects": [],
    }
    with open_app_test_db_session() as db:
        db.add(
            ChartResultModel(
                chart_id=chart_id,
                reference_version="1.0.0",
                ruleset_version="1.0.0",
                input_hash="old-hash",
                result_payload=old_payload,
            )
        )
        db.commit()
        record = ChartResultService.get_audit_record(db, chart_id)
        stored_payload = db.scalar(
            select(ChartResultModel.result_payload).where(ChartResultModel.chart_id == chart_id)
        )

    assert stored_payload is not None
    assert "condition_signals" not in stored_payload
    assert "dominant_planets" not in stored_payload
    assert "interpretation_adapter" not in stored_payload
    assert "dignity_sect" not in stored_payload
    assert record.result.condition_signals == []
    assert record.result.dominant_planets is None
    assert record.result.interpretation_adapter is None
    assert record.result.dignity_sect is None


def test_persist_and_get_audit_record() -> None:
    _cleanup_chart_results()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        chart_id = ChartResultService.persist_trace(db, payload, result)
        db.commit()

    with open_app_test_db_session() as db:
        record = ChartResultService.get_audit_record(db, chart_id)
        stored_payload = db.scalar(
            select(ChartResultModel).where(ChartResultModel.chart_id == chart_id)
        )
    assert record.chart_id == chart_id
    assert record.reference_version == "1.0.0"
    assert record.result.house_rulers
    assert stored_payload is not None
    assert stored_payload.result_payload["house_rulers"]
    assert stored_payload.result_payload["condition_profiles"]
    assert stored_payload.result_payload["dignity_sect"]["chart_sect"] in {"day", "night"}
    assert stored_payload.result_payload["dignity_sect"]["sun_horizon_position"] in {
        "above_horizon",
        "below_horizon",
    }
    assert isinstance(stored_payload.result_payload["dignity_sect"]["sun_above_horizon"], bool)
    assert (
        stored_payload.result_payload["dignity_sect"]["calculation_basis"]
        == "sun_house_horizon_rule"
    )
    assert stored_payload.result_payload["dignity_sect"]["reference_system"] == "traditional"
    assert (
        stored_payload.result_payload["dignities"][0]["chart_sect"]
        == (stored_payload.result_payload["dignity_sect"])
    )
    assert (
        stored_payload.result_payload["dignities"][0]["sect_condition"]["chart_sect"]
        == stored_payload.result_payload["dignity_sect"]["chart_sect"]
    )
    assert stored_payload.result_payload["dignities"][0]["sect_condition"][
        "planet_sect_condition"
    ] in {
        "in_sect",
        "out_of_sect",
        "neutral_to_sect",
        "variable_by_condition",
        "unknown",
    }
    assert stored_payload.result_payload["condition_signals"]
    assert stored_payload.result_payload["dominant_planets"]
    assert stored_payload.result_payload["dominant_planets"]["planets"]
    first_house = stored_payload.result_payload["houses"][0]
    assert first_house["sign"] == first_house["cusp_sign"]
    assert "contained_signs" in first_house
    assert "intercepted_signs" in first_house
    assert "ruler" in first_house
    assert "occupants" in first_house
    assert "axis" in first_house
    assert "strength" in first_house
    first_aspect = stored_payload.result_payload["aspects"][0]
    assert first_aspect["aspect_interpretive_hints"]["interpretive_valence"]
    assert record.result.aspects[0].aspect_interpretive_hints is not None


def test_persist_trace_writes_dignity_audit_rows_from_precomputed_result() -> None:
    """La persistance du theme ecrit une ligne d'audit par dignite calculee."""
    _cleanup_chart_results()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        chart_id = ChartResultService.persist_trace(db, payload, result)
        chart_result = db.scalar(
            select(ChartResultModel).where(ChartResultModel.chart_id == chart_id)
        )
        assert chart_result is not None
        rows = db.execute(
            select(AstralChartPlanetDignityResultModel, PlanetModel.code)
            .join(PlanetModel, AstralChartPlanetDignityResultModel.planet_id == PlanetModel.id)
            .where(AstralChartPlanetDignityResultModel.chart_result_id == chart_result.id)
        ).all()

    expected_by_planet = {dignity.planet_code: dignity for dignity in result.dignities}
    assert len(rows) == len(expected_by_planet)
    for row, planet_code in rows:
        expected = expected_by_planet[planet_code]
        assert row.essential_score == expected.essential_score
        assert row.accidental_score == expected.accidental_score
        assert row.total_score == expected.total_score
        assert row.functional_strength_score == expected.functional_strength_score
        assert row.expression_quality_score == expected.expression_quality_score
        assert row.intensity_score == expected.intensity_score
        assert row.essential_breakdown_json == [
            asdict(item) for item in expected.essential_breakdown
        ]
        assert row.accidental_breakdown_json == [
            asdict(item) for item in expected.accidental_breakdown
        ]
        assert row.condition_summary_json["chart_sect"] == asdict(expected.chart_sect)
        assert row.condition_summary_json["sect_condition"] == asdict(expected.sect_condition)
        assert row.calculation_context_json["source_field"] == "NatalResult.dignities"
        assert "birth_date" not in row.calculation_context_json
        assert "birth_time" not in row.calculation_context_json
        assert "birth_place" not in row.calculation_context_json


def test_persist_trace_does_not_fabricate_dignity_audit_rows_without_dignities() -> None:
    """Un resultat sans dignites ne cree aucune ligne d'audit inventee."""
    _cleanup_chart_results()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    result = NatalResult(
        reference_version="1.0.0",
        ruleset_version="1.0.0",
        house_system="equal",
        prepared_input={
            "birth_datetime_local": "1990-06-15T10:30:00+02:00",
            "birth_datetime_utc": "1990-06-15T08:30:00+00:00",
            "timestamp_utc": 645438600,
            "julian_day": 2448057.8541666665,
            "birth_timezone": "Europe/Paris",
        },
        planet_positions=[],
        houses=[],
        aspects=[],
    )

    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        chart_id = ChartResultService.persist_trace(db, payload, result)
        chart_result = db.scalar(
            select(ChartResultModel).where(ChartResultModel.chart_id == chart_id)
        )
        assert chart_result is not None
        rows = db.scalars(
            select(AstralChartPlanetDignityResultModel).where(
                AstralChartPlanetDignityResultModel.chart_result_id == chart_result.id
            )
        ).all()

    assert rows == []


def test_persist_trace_propagates_dignity_audit_write_errors(
    monkeypatch: MonkeyPatch,
) -> None:
    """Une erreur d'ecriture audit remonte sans fallback silencieux."""
    _cleanup_chart_results()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )

    def _raise_audit_error(
        _repository: DignityReferenceRepository,
        _payload: object,
    ) -> None:
        raise ValueError("audit write failed")

    monkeypatch.setattr(
        DignityReferenceRepository,
        "upsert_chart_planet_dignity_result",
        _raise_audit_error,
    )
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        with pytest.raises(ChartResultServiceError) as error_info:
            ChartResultService.persist_trace(db, payload, result)
        assert error_info.value.code == "dignity_audit_persistence_failed"
        assert error_info.value.__cause__ is not None


def test_dignity_audit_upsert_is_idempotent_for_same_chart_result() -> None:
    """L'upsert d'audit conserve une ligne par cle fonctionnelle."""
    _cleanup_chart_results()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        chart_id = ChartResultService.persist_trace(db, payload, result)
        chart_result = db.scalar(
            select(ChartResultModel).where(ChartResultModel.chart_id == chart_id)
        )
        assert chart_result is not None
        repository = DignityReferenceRepository(db)
        first = result.dignities[0]
        existing = repository.get_chart_planet_dignity_result(
            chart_result.id,
            first.planet_code,
            first.score_profile,
            first.reference_version,
        )
        assert existing is not None
        existing_id = existing.id
        repository.upsert_chart_planet_dignity_result(
            build_chart_planet_dignity_audit_input(
                chart_result_id=chart_result.id,
                chart_id=chart_id,
                input_hash=chart_result.input_hash,
                ruleset_version=chart_result.ruleset_version,
                dignity=first,
            )
        )
        rows = db.scalars(
            select(AstralChartPlanetDignityResultModel).where(
                AstralChartPlanetDignityResultModel.chart_result_id == chart_result.id,
                AstralChartPlanetDignityResultModel.id == existing_id,
            )
        ).all()
        all_rows = db.scalars(
            select(AstralChartPlanetDignityResultModel).where(
                AstralChartPlanetDignityResultModel.chart_result_id == chart_result.id
            )
        ).all()
        same_planet = repository.get_chart_planet_dignity_result(
            chart_result.id,
            first.planet_code,
            first.score_profile,
            first.reference_version,
        )

    assert len(rows) == 1
    assert len(all_rows) == len(result.dignities)
    assert same_planet is not None
    assert same_planet.id == existing_id


def test_persist_trace_projects_legacy_house_rulers_from_runtime_houses() -> None:
    _cleanup_chart_results()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        result.house_rulers[0] = HouseRulerResult(
            house_number=result.house_rulers[0].house_number,
            cusp_sign=result.house_rulers[0].cusp_sign,
            ruler_planet="stale_planet",
            ruler_planet_sign="stale_sign",
            ruler_planet_house=12,
        )
        chart_id = ChartResultService.persist_trace(db, payload, result)
        db.commit()

    with open_app_test_db_session() as db:
        stored_payload = db.scalar(
            select(ChartResultModel.result_payload).where(ChartResultModel.chart_id == chart_id)
        )

    assert stored_payload is not None
    houses_by_number = {house["number"]: house for house in stored_payload["houses"]}
    for legacy_ruler in stored_payload["house_rulers"]:
        house = houses_by_number[legacy_ruler["house_number"]]
        assert legacy_ruler["cusp_sign"] == house["cusp_sign"]
        assert legacy_ruler["ruler_planet"] == house["ruler"]["planet"]
        assert legacy_ruler["ruler_planet_sign"] == house["ruler"]["sign"]
        assert legacy_ruler["ruler_planet_house"] == house["ruler"]["house"]
    assert all(
        legacy_ruler["ruler_planet"] != "stale_planet"
        for legacy_ruler in stored_payload["house_rulers"]
    )


def test_persist_trace_generates_unique_chart_ids_for_identical_inputs() -> None:
    _cleanup_chart_results()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        first_chart_id = ChartResultService.persist_trace(
            db,
            payload,
            result,
        )
        second_chart_id = ChartResultService.persist_trace(
            db,
            payload,
            result,
        )
        db.commit()

    assert first_chart_id != second_chart_id
