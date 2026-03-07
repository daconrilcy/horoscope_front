from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.models.prediction_ruleset import (
    CategoryCalibrationModel,
    PredictionRulesetModel,
    RulesetEventTypeModel,
    RulesetParameterModel,
)
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.repositories.prediction_ruleset_repository import (
    PredictionRulesetRepository,
)
from app.infra.db.repositories.prediction_schemas import (
    CalibrationData,
    EventTypeData,
    RulesetContext,
    RulesetData,
)

def test_get_ruleset(db_session: Session):
    repo = PredictionRulesetRepository(db_session)
    
    # Seed
    version = ReferenceVersionModel(version="1.0.0")
    db_session.add(version)
    db_session.flush()
    
    ruleset = PredictionRulesetModel(
        version="1.0.0",
        reference_version_id=version.id,
        zodiac_type="tropical",
        coordinate_mode="geocentric",
        house_system="placidus",
        time_step_minutes=30,
        is_locked=False
    )
    db_session.add(ruleset)
    db_session.commit()
    
    result = repo.get_ruleset("1.0.0")
    
    assert isinstance(result, RulesetData)
    assert result.version == "1.0.0"
    assert result.zodiac_type == "tropical"

def test_get_parameters(db_session: Session):
    repo = PredictionRulesetRepository(db_session)
    
    # Seed
    version = ReferenceVersionModel(version="1.0.0")
    db_session.add(version)
    db_session.flush()
    
    ruleset = PredictionRulesetModel(version="1.0.0", reference_version_id=version.id)
    db_session.add(ruleset)
    db_session.flush()
    
    params = [
        RulesetParameterModel(ruleset_id=ruleset.id, param_key="f_val", param_value="1.5", data_type="float"),
        RulesetParameterModel(ruleset_id=ruleset.id, param_key="i_val", param_value="42", data_type="int"),
        RulesetParameterModel(ruleset_id=ruleset.id, param_key="b_val", param_value="true", data_type="bool"),
        RulesetParameterModel(ruleset_id=ruleset.id, param_key="j_val", param_value='{"a": 1}', data_type="json"),
        RulesetParameterModel(ruleset_id=ruleset.id, param_key="s_val", param_value="hello", data_type="string"),
    ]
    db_session.add_all(params)
    db_session.commit()
    
    result = repo.get_parameters(ruleset.id)
    
    assert result["f_val"] == 1.5
    assert result["i_val"] == 42
    assert result["b_val"] is True
    assert result["j_val"] == {"a": 1}
    assert result["s_val"] == "hello"

def test_get_active_ruleset_context(db_session: Session):
    repo = PredictionRulesetRepository(db_session)
    
    # Seed
    version = ReferenceVersionModel(version="1.0.0")
    db_session.add(version)
    db_session.flush()
    
    ruleset = PredictionRulesetModel(version="1.0.0", reference_version_id=version.id)
    db_session.add(ruleset)
    db_session.commit()
    
    result = repo.get_active_ruleset_context("1.0.0")
    
    assert isinstance(result, RulesetContext)
    assert result.ruleset.version == "1.0.0"
    assert isinstance(result.parameters, dict)
    assert isinstance(result.event_types, dict)
