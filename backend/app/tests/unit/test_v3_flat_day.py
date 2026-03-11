from datetime import date, datetime, UTC
from unittest.mock import MagicMock
import pytest
from app.prediction.public_projection import _is_flat_day
from app.prediction.persisted_snapshot import PersistedPredictionSnapshot

def create_mock_cat_dict(note_20, intensity_20, stability_day):
    return {
        "note_20": note_20,
        "intensity_20": intensity_20,
        "stability_day": stability_day
    }

def test_is_flat_day_true_flat():
    # AC1: All categories low intensity, high stability (>= 14.0)
    snapshot = MagicMock(spec=PersistedPredictionSnapshot)
    snapshot.time_blocks = [MagicMock()]
    
    categories = [
        create_mock_cat_dict(10.0, 1.0, 14.0),
        create_mock_cat_dict(10.0, 0.5, 19.0)
    ]
    
    assert _is_flat_day(snapshot, [], categories) is True

def test_is_flat_day_unstable():
    # AC1: If one category is unstable (< 14.0), it's NOT a flat day (it's volatile/uncertain)
    snapshot = MagicMock(spec=PersistedPredictionSnapshot)
    snapshot.time_blocks = [MagicMock()]
    
    categories = [
        create_mock_cat_dict(10.0, 1.0, 10.0), # unstable
        create_mock_cat_dict(10.0, 0.5, 18.0)
    ]
    
    assert _is_flat_day(snapshot, [], categories) is False

def test_is_flat_day_intense_neutral():
    # AC3: Intense but neutral score should NOT be flat
    snapshot = MagicMock(spec=PersistedPredictionSnapshot)
    snapshot.time_blocks = [MagicMock()]
    
    categories = [
        create_mock_cat_dict(10.0, 8.0, 5.0), 
        create_mock_cat_dict(10.0, 1.0, 18.0)
    ]
    
    assert _is_flat_day(snapshot, [], categories) is False

def test_is_flat_day_weak_not_flat():
    snapshot = MagicMock(spec=PersistedPredictionSnapshot)
    snapshot.time_blocks = [MagicMock()]
    
    categories = [
        create_mock_cat_dict(10.0, 4.0, 15.0), 
        create_mock_cat_dict(10.0, 1.0, 18.0)
    ]
    
    assert _is_flat_day(snapshot, [], categories) is False

def test_is_flat_day_fallback_v2():
    snapshot = MagicMock(spec=PersistedPredictionSnapshot)
    snapshot.time_blocks = [MagicMock()]
    
    categories = [
        create_mock_cat_dict(10.0, None, None),
        create_mock_cat_dict(10.0, None, None)
    ]
    
    assert _is_flat_day(snapshot, [], categories) is True
    
    # If one note is high
    categories[0]["note_20"] = 15.0
    assert _is_flat_day(snapshot, [], categories) is False
