from datetime import date, datetime, UTC
from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy.orm import Session

from app.services.user_prediction_baseline_service import UserPredictionBaselineService
from app.infra.db.repositories.user_prediction_baseline_repository import UserPredictionBaselineRepository
from app.prediction.persisted_baseline import V3Granularity
from app.prediction.schemas import PersistablePredictionBundle, CoreEngineOutput, EffectiveContext, V3EngineOutput, TimeBlock
from app.tests.helpers.db_utils import (
    create_user, create_user_birth_profile, create_chart_result,
    create_reference_version, create_prediction_ruleset, create_prediction_category
)

@pytest.fixture
def mock_context_loader():
    loader = MagicMock()
    ctx = MagicMock()
    ctx.ruleset_context.parameters = {}
    loader.load.return_value = ctx
    return loader

def test_generate_baseline_granularities(db_session: Session, mock_context_loader):
    user = create_user(db_session)
    create_user_birth_profile(db_session, user.id)
    create_chart_result(db_session, user.id)
    ref = create_reference_version(db_session, version="2.0.0")
    ruleset = create_prediction_ruleset(db_session, ref.id, version="2.0.0")
    cat = create_prediction_category(db_session, ref.id, code="work")
    
    ctx = mock_context_loader.load.return_value
    ctx.prediction_context.categories = [cat]
    
    # Mock EngineOrchestrator.run to avoid complex dependency issues
    mock_bundle = PersistablePredictionBundle(
        core=CoreEngineOutput(
            effective_context=EffectiveContext(
                house_system_requested="placidus",
                house_system_effective="placidus",
                timezone="UTC",
                input_hash="hash",
                local_date=date(2026, 3, 11)
            ),
            run_metadata={},
            category_scores={"work": {"raw_score": 1.5, "note_20": 15}},
            time_blocks=[],
            turning_points=[],
            decision_windows=[],
            detected_events=[]
        ),
        v3_core=V3EngineOutput(
            time_blocks=[
                TimeBlock(
                    start_local=datetime(2026, 3, 11, 10, 0),
                    end_local=datetime(2026, 3, 11, 12, 0),
                    intensity=0.8,
                    dominant_themes=["work"],
                    sub_themes=[]
                )
            ]
        )
    )

    with patch("app.services.user_prediction_baseline_service.EngineOrchestrator") as mock_orch_cls:
        mock_orch = mock_orch_cls.return_value
        mock_orch.with_context_loader.return_value = mock_orch
        mock_orch.run.return_value = mock_bundle

        service = UserPredictionBaselineService(mock_context_loader)
        window = 1
        end_date = date(2026, 3, 11)
        
        service.generate_baseline(
            db_session, user.id, window_days=window, end_date=end_date,
            reference_version="2.0.0", ruleset_version="2.0.0"
        )
    
    repo = UserPredictionBaselineRepository(db_session)
    
    # Check DAY level
    baselines_day = repo.get_baselines_for_user(
        user.id, ref.id, ruleset.id, "placidus", window, 
        end_date, end_date, granularity_type=V3Granularity.DAY
    )
    assert len(baselines_day) > 0
    assert baselines_day[0].mean_note_20 == 15.0
    assert baselines_day[0].granularity_value == "all"
    
    # Check SEASON level
    baselines_season = repo.get_baselines_for_user(
        user.id, ref.id, ruleset.id, "placidus", window, 
        end_date, end_date, granularity_type=V3Granularity.SEASON
    )
    assert len(baselines_season) > 0
    assert baselines_season[0].granularity_value == "spring"

    # Check SLOT level
    baselines_slot = repo.get_baselines_for_user(
        user.id, ref.id, ruleset.id, "placidus", window, 
        end_date, end_date, granularity_type=V3Granularity.SLOT
    )
    assert len(baselines_slot) > 0
    assert baselines_slot[0].granularity_value == "morning"

    # Check MONTH level
    baselines_month = repo.get_baselines_for_user(
        user.id, ref.id, ruleset.id, "placidus", window, 
        end_date, end_date, granularity_type=V3Granularity.MONTH
    )
    assert len(baselines_month) > 0
    assert baselines_month[0].granularity_value == "month_3"
