"""Validators for the prompt catalog."""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models import LlmUseCaseConfigModel
from app.prompts.catalog import PROMPT_CATALOG
from app.prompts.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

def validate_catalog_vs_db(db: Session) -> None:
    """
    Validate that all active use cases in the database are present in the catalog.
    
    Raises:
        ConfigurationError: If a database use case is missing from the catalog.
    """
    stmt = select(LlmUseCaseConfigModel)
    db_use_cases = db.execute(stmt).scalars().all()
    
    catalog_keys = set(PROMPT_CATALOG.keys())
    missing_from_catalog = []
    
    for uc in db_use_cases:
        if uc.key not in catalog_keys:
            missing_from_catalog.append(uc.key)
            
    if missing_from_catalog:
        error_msg = (
            f"Database use cases missing from Python catalog: {', '.join(missing_from_catalog)}"
        )
        logger.error(error_msg)
        raise ConfigurationError(error_msg)
        
    logger.info("Prompt catalog OK — %d use cases validated", len(db_use_cases))
