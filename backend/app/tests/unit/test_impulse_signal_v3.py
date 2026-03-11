from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.prediction.impulse_signal_builder import ImpulseSignalBuilder
from app.prediction.schemas import AstroEvent, SamplePoint


@pytest.fixture
def mock_context():
    ctx = MagicMock()
    work_cat = MagicMock(code="work", is_enabled=True)
    ctx.prediction_context.categories = [work_cat]
    return ctx

def test_impulse_signal_capping(mock_context):
    builder = ImpulseSignalBuilder()
    
    # Mock contribution calculator to return high value
    builder._contribution_calculator.compute = MagicMock(return_value={"work": 5.0})
    # Mock router
    builder._domain_router.route = MagicMock(return_value=["work"])
    
    samples = [SamplePoint(ut_time=0.0, local_time=datetime(2026, 3, 11, 12, 0, tzinfo=UTC))]
    events = [
        AstroEvent(
            event_type="aspect_exact_to_angle",
            ut_time=0.0,
            local_time=datetime(2026, 3, 11, 12, 0, tzinfo=UTC),
            body="Sun", target="Asc", aspect="conjunction",
            orb_deg=0.0, priority=100, base_weight=1.0
        )
    ]
    
    timeline = builder.build_timeline(events, samples, {"work": 1.0}, mock_context)
    
    score = timeline["work"][samples[0].local_time]
    
    # Individual event capped at 0.5
    # Total impulse capped at 1.0
    assert score == 0.5

def test_impulse_no_faux_relief(mock_context):
    builder = ImpulseSignalBuilder()
    
    # Quiet day: no impulse events
    events = []
    samples = [SamplePoint(ut_time=0.0, local_time=datetime(2026, 3, 11, 12, 0, tzinfo=UTC))]
    
    timeline = builder.build_timeline(events, samples, {"work": 1.0}, mock_context)
    
    assert timeline["work"][samples[0].local_time] == 0.0
