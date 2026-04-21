"""Validators for the prompt catalog."""

import logging
import re
from typing import Any, Literal, Optional

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.llm.prompting.catalog import PROMPT_CATALOG
from app.domain.llm.prompting.exceptions import ConfigurationError
from app.infra.db.models import LlmUseCaseConfigModel

logger = logging.getLogger(__name__)


class ArchitectureViolation(BaseModel):
    entity: str
    violation_type: str
    severity: Literal["WARNING", "ERROR"]
    excerpt: str


def validate_template_content(template_text: str) -> list[ArchitectureViolation]:
    violations = []
    text_lower = template_text.lower()
    patterns = {
        "model_reference": [r"use model", r"utilise le modèle", r"gpt-", r"claude-", r"o1-"],
        "provider_reference": [r"provider", r"openai", r"anthropic"],
    }
    for v_type, p_list in patterns.items():
        for p in p_list:
            match = re.search(p, text_lower)
            if match:
                start = max(0, match.start() - 20)
                end = min(len(template_text), match.end() + 20)
                violations.append(
                    ArchitectureViolation(
                        entity="LlmPromptVersion",
                        violation_type=f"template_content_violation:{v_type}",
                        severity="WARNING",
                        excerpt=f"...{template_text[start:end]}...",
                    )
                )
                break
    return violations


def validate_plan_rules_content(plan_rules_text: str) -> list[ArchitectureViolation]:
    violations = []
    text_lower = plan_rules_text.lower()
    patterns = {
        "feature_selection": [r"si premium", r"if premium", r"utilise la feature", r"use case"],
    }
    for v_type, p_list in patterns.items():
        for p in p_list:
            match = re.search(p, text_lower)
            if match:
                start = max(0, match.start() - 20)
                end = min(len(plan_rules_text), match.end() + 20)
                violations.append(
                    ArchitectureViolation(
                        entity="PlanRule",
                        violation_type=f"plan_rules_violation:{v_type}",
                        severity="WARNING",
                        excerpt=f"...{plan_rules_text[start:end]}...",
                    )
                )
                break
    return violations


def validate_use_case_naming(
    use_case: str, output_schema: Optional[dict[str, Any]] = None
) -> list[str]:
    warnings = []
    if use_case.endswith(("_free", "_full")):
        if output_schema and len(output_schema.get("properties", {})) > 0:
            return []
        warnings.append(
            f"use_case suffix '_free'/'_full' detected for '{use_case}' "
            "without distinct output schema — prefer plan_rules in PromptAssemblyConfig"
        )
    return warnings


def validate_catalog_vs_db(db: Session) -> None:
    stmt = select(LlmUseCaseConfigModel)
    db_use_cases = db.execute(stmt).scalars().all()
    catalog_keys = set(PROMPT_CATALOG.keys())
    missing_from_catalog = [uc.key for uc in db_use_cases if uc.key not in catalog_keys]
    if missing_from_catalog:
        error_msg = (
            f"Database use cases missing from Python catalog: {', '.join(missing_from_catalog)}"
        )
        logger.error(error_msg)
        raise ConfigurationError(error_msg)
    logger.info("Prompt catalog OK — %d use cases validated", len(db_use_cases))


__all__ = [
    "ArchitectureViolation",
    "validate_catalog_vs_db",
    "validate_plan_rules_content",
    "validate_template_content",
    "validate_use_case_naming",
]
