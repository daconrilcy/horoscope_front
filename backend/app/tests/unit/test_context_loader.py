from dataclasses import FrozenInstanceError
from types import MappingProxyType
from unittest.mock import MagicMock, patch

import pytest

from app.infra.db.repositories.prediction_schemas import (
    CalibrationData,
    CategoryData,
    HouseProfileData,
    PlanetProfileData,
    PredictionContext,
    RulesetContext,
    RulesetData,
)
from app.prediction.context_loader import PredictionContextLoader
from app.prediction.exceptions import PredictionContextError


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_rv_model():
    rv = MagicMock()
    rv.id = 1
    rv.version = "V1"
    return rv


def build_prediction_context(*, categories=None, planet_profiles=None, house_profiles=None):
    return PredictionContext(
        categories=categories
        if categories is not None
        else (
            CategoryData(
                id=1,
                code="amour",
                name="Amour",
                display_name="Amour",
                sort_order=1,
                is_enabled=True,
            ),
        ),
        planet_profiles=planet_profiles
        if planet_profiles is not None
        else {
            "sun": PlanetProfileData(
                planet_id=1,
                code="sun",
                name="Sun",
                class_code="luminary",
                speed_rank=1,
                speed_class="fast",
                weight_intraday=1.0,
                weight_day_climate=1.0,
                typical_polarity="yang",
                orb_active_deg=5.0,
                orb_peak_deg=1.5,
                keywords=("vitality",),
            )
        },
        house_profiles=house_profiles
        if house_profiles is not None
        else {
            1: HouseProfileData(
                house_id=1,
                number=1,
                name="House 1",
                house_kind="angular",
                visibility_weight=1.0,
                base_priority=1,
                keywords=("self",),
            )
        },
        planet_category_weights=(),
        house_category_weights=(),
        sign_rulerships={},
        aspect_profiles={},
        astro_points={},
        point_category_weights=(),
    )


def build_ruleset_context(*, reference_version_id=1, parameters=None):
    ruleset = RulesetData(
        id=1,
        version="V1",
        reference_version_id=reference_version_id,
        zodiac_type="tropical",
        coordinate_mode="geocentric",
        house_system="placidus",
        time_step_minutes=60,
        is_locked=True,
    )
    return RulesetContext(
        ruleset=ruleset,
        parameters=parameters if parameters is not None else {"param1": 1.0},
        event_types={},
    )


def build_calibration(*, label: str | None):
    return CalibrationData(
        p05=-1.5,
        p25=-0.5,
        p50=0.0,
        p75=0.5,
        p95=1.5,
        sample_size=10,
        calibration_label=label,
    )


def test_load_complete_ok(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    valid_pred_ctx = build_prediction_context()
    valid_ruleset_ctx = build_ruleset_context()

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo = mock_ref_repo_cls.return_value
        mock_ref_repo.load_prediction_context.return_value = valid_pred_ctx
        mock_ref_repo.get_categories.return_value = valid_pred_ctx.categories

        mock_ruleset_repo = mock_ruleset_repo_cls.return_value
        mock_ruleset_repo.get_active_ruleset_context.return_value = valid_ruleset_ctx
        mock_ruleset_repo.get_calibrations.return_value = build_calibration(label="v1")

        ctx = PredictionContextLoader().load(mock_db, "V1", "V1")

    assert ctx.is_provisional_calibration is False
    assert ctx.calibration_label == "v1"
    assert "amour" in ctx.calibrations
    assert isinstance(ctx.calibrations, MappingProxyType)
    assert isinstance(ctx.prediction_context.categories, tuple)
    assert isinstance(ctx.ruleset_context.parameters, MappingProxyType)


def test_loaded_context_is_functionally_immutable(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    valid_pred_ctx = build_prediction_context()
    valid_ruleset_ctx = build_ruleset_context()

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo = mock_ref_repo_cls.return_value
        mock_ref_repo.load_prediction_context.return_value = valid_pred_ctx
        mock_ref_repo.get_categories.return_value = valid_pred_ctx.categories

        mock_ruleset_repo = mock_ruleset_repo_cls.return_value
        mock_ruleset_repo.get_active_ruleset_context.return_value = valid_ruleset_ctx
        mock_ruleset_repo.get_calibrations.return_value = None

        ctx = PredictionContextLoader().load(mock_db, "V1", "V1")

    with pytest.raises(TypeError):
        ctx.calibrations["amour"] = "broken"
    with pytest.raises(AttributeError):
        ctx.prediction_context.categories.append("broken")
    with pytest.raises(FrozenInstanceError):
        ctx.prediction_context.categories[0].code = "amitie"


def test_missing_reference_version_raises(mock_db):
    mock_db.scalar.return_value = None

    with pytest.raises(PredictionContextError, match="Reference version 'V_INVALID' not found"):
        PredictionContextLoader().load(mock_db, "V_INVALID", "V1")


def test_missing_categories_raises(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    invalid_pred_ctx = build_prediction_context(categories=())
    valid_ruleset_ctx = build_ruleset_context()

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo_cls.return_value.load_prediction_context.return_value = invalid_pred_ctx
        mock_ref_repo_cls.return_value.get_categories.return_value = ()
        mock_ruleset_repo_cls.return_value.get_active_ruleset_context.return_value = (
            valid_ruleset_ctx
        )

        with pytest.raises(
            PredictionContextError, match="Prediction context has no enabled categories"
        ):
            PredictionContextLoader().load(mock_db, "V1", "V1")


def test_missing_planet_profiles_raises(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    invalid_pred_ctx = build_prediction_context(planet_profiles={})
    valid_ruleset_ctx = build_ruleset_context()

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo_cls.return_value.load_prediction_context.return_value = invalid_pred_ctx
        mock_ref_repo_cls.return_value.get_categories.return_value = invalid_pred_ctx.categories
        mock_ruleset_repo_cls.return_value.get_active_ruleset_context.return_value = (
            valid_ruleset_ctx
        )

        with pytest.raises(
            PredictionContextError, match="Prediction context has no planet profiles"
        ):
            PredictionContextLoader().load(mock_db, "V1", "V1")


def test_missing_house_profiles_raises(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    invalid_pred_ctx = build_prediction_context(house_profiles={})
    valid_ruleset_ctx = build_ruleset_context()

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo_cls.return_value.load_prediction_context.return_value = invalid_pred_ctx
        mock_ref_repo_cls.return_value.get_categories.return_value = invalid_pred_ctx.categories
        mock_ruleset_repo_cls.return_value.get_active_ruleset_context.return_value = (
            valid_ruleset_ctx
        )

        with pytest.raises(
            PredictionContextError, match="Prediction context has no house profiles"
        ):
            PredictionContextLoader().load(mock_db, "V1", "V1")


def test_missing_ruleset_raises(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    valid_pred_ctx = build_prediction_context()

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo_cls.return_value.load_prediction_context.return_value = valid_pred_ctx
        mock_ruleset_repo_cls.return_value.get_active_ruleset_context.return_value = None

        with pytest.raises(PredictionContextError, match="Ruleset version 'V_INVALID' not found"):
            PredictionContextLoader().load(mock_db, "V1", "V_INVALID")


def test_missing_params_raises(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    valid_pred_ctx = build_prediction_context()
    invalid_ruleset_ctx = build_ruleset_context(parameters={})

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo_cls.return_value.load_prediction_context.return_value = valid_pred_ctx
        mock_ref_repo_cls.return_value.get_categories.return_value = valid_pred_ctx.categories
        mock_ruleset_repo_cls.return_value.get_active_ruleset_context.return_value = (
            invalid_ruleset_ctx
        )

        with pytest.raises(PredictionContextError, match="Ruleset context has no parameters"):
            PredictionContextLoader().load(mock_db, "V1", "V1")


def test_version_mismatch_raises(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    valid_pred_ctx = build_prediction_context()
    invalid_ruleset_ctx = build_ruleset_context(reference_version_id=2)

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo_cls.return_value.load_prediction_context.return_value = valid_pred_ctx
        mock_ruleset_repo_cls.return_value.get_active_ruleset_context.return_value = (
            invalid_ruleset_ctx
        )

        with pytest.raises(PredictionContextError, match="mismatch"):
            PredictionContextLoader().load(mock_db, "V1", "V1")


def test_categories_belong_to_correct_version(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    loaded_pred_ctx = build_prediction_context(
        categories=(
            CategoryData(
                id=999,
                code="etranger",
                name="Etranger",
                display_name="Etranger",
                sort_order=1,
                is_enabled=True,
            ),
        )
    )
    expected_categories = (
        CategoryData(
            id=1,
            code="amour",
            name="Amour",
            display_name="Amour",
            sort_order=1,
            is_enabled=True,
        ),
    )
    valid_ruleset_ctx = build_ruleset_context()

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo = mock_ref_repo_cls.return_value
        mock_ref_repo.load_prediction_context.return_value = loaded_pred_ctx
        mock_ref_repo.get_categories.return_value = expected_categories
        mock_ruleset_repo_cls.return_value.get_active_ruleset_context.return_value = (
            valid_ruleset_ctx
        )

        with pytest.raises(
            PredictionContextError,
            match="categories do not match the requested reference version",
        ):
            PredictionContextLoader().load(mock_db, "V1", "V1")


def test_missing_calibration_provisional(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    valid_pred_ctx = build_prediction_context()
    valid_ruleset_ctx = build_ruleset_context()

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo_cls.return_value.load_prediction_context.return_value = valid_pred_ctx
        mock_ref_repo_cls.return_value.get_categories.return_value = valid_pred_ctx.categories
        mock_ruleset_repo_cls.return_value.get_active_ruleset_context.return_value = (
            valid_ruleset_ctx
        )
        mock_ruleset_repo_cls.return_value.get_calibrations.return_value = None

        ctx = PredictionContextLoader().load(mock_db, "V1", "V1")

    assert ctx.is_provisional_calibration is True
    assert ctx.calibration_label == "provisional"
    assert ctx.calibrations["amour"] is None


def test_provisional_label_keeps_provisional_flag(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    valid_pred_ctx = build_prediction_context()
    valid_ruleset_ctx = build_ruleset_context()

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo_cls.return_value.load_prediction_context.return_value = valid_pred_ctx
        mock_ref_repo_cls.return_value.get_categories.return_value = valid_pred_ctx.categories
        mock_ruleset_repo_cls.return_value.get_active_ruleset_context.return_value = (
            valid_ruleset_ctx
        )
        mock_ruleset_repo_cls.return_value.get_calibrations.return_value = build_calibration(
            label="provisional"
        )

        ctx = PredictionContextLoader().load(mock_db, "V1", "V1")

    assert ctx.is_provisional_calibration is True
    assert ctx.calibration_label == "provisional"


def test_mixed_stable_labels_are_reported_explicitly(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    valid_pred_ctx = build_prediction_context(
        categories=(
            CategoryData(
                id=1,
                code="amour",
                name="Amour",
                display_name="Amour",
                sort_order=1,
                is_enabled=True,
            ),
            CategoryData(
                id=2,
                code="travail",
                name="Travail",
                display_name="Travail",
                sort_order=2,
                is_enabled=True,
            ),
        )
    )
    valid_ruleset_ctx = build_ruleset_context()

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo_cls.return_value.load_prediction_context.return_value = valid_pred_ctx
        mock_ref_repo_cls.return_value.get_categories.return_value = valid_pred_ctx.categories
        mock_ruleset_repo_cls.return_value.get_active_ruleset_context.return_value = (
            valid_ruleset_ctx
        )
        mock_ruleset_repo_cls.return_value.get_calibrations.side_effect = [
            build_calibration(label="v1"),
            build_calibration(label="v2"),
        ]

        ctx = PredictionContextLoader().load(mock_db, "V1", "V1")

    assert ctx.is_provisional_calibration is False
    assert ctx.calibration_label == "mixed"


def test_repository_value_error_is_normalized(mock_db, mock_rv_model):
    mock_db.scalar.return_value = mock_rv_model
    valid_pred_ctx = build_prediction_context()

    with (
        patch("app.prediction.context_loader.PredictionReferenceRepository") as mock_ref_repo_cls,
        patch("app.prediction.context_loader.PredictionRulesetRepository") as mock_ruleset_repo_cls,
    ):
        mock_ref_repo_cls.return_value.load_prediction_context.return_value = valid_pred_ctx
        mock_ruleset_repo_cls.return_value.get_active_ruleset_context.side_effect = ValueError(
            "Invalid float ruleset parameter value: 'oops'"
        )

        with pytest.raises(
            PredictionContextError,
            match="Failed to load prediction context: Invalid float ruleset parameter value",
        ):
            PredictionContextLoader().load(mock_db, "V1", "V1")
