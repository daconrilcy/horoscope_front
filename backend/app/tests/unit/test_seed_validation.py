# Tests unitaires de validation des contrats de seed LLM canoniques.
"""Verifie que les seeds LLM echouent explicitement sur les personas requises vides."""

from __future__ import annotations

import pytest

from app.domain.llm.configuration.canonical_use_case_registry import CanonicalUseCaseContract
from app.ops.llm.bootstrap.use_cases_seed import (
    CANONICAL_USE_CASE_CONTRACTS,
    SeedValidationError,
    validate_use_case_seed_contracts,
)


def test_seed_validation_rejects_required_persona_without_contract_placeholder() -> None:
    """Une persona requise sans placeholder metier doit bloquer le seed."""
    broken_contract = CanonicalUseCaseContract(
        key="broken_required_persona",
        display_name="Broken required persona",
        description="Contrat de test invalide.",
        persona_strategy="required",
        required_prompt_placeholders=[],
    )

    with pytest.raises(SeedValidationError, match="exige une persona"):
        validate_use_case_seed_contracts([broken_contract])


def test_seed_validation_rejects_required_persona_with_empty_placeholder_values() -> None:
    """Une persona requise ne doit pas accepter des placeholders vides."""
    broken_contract = CanonicalUseCaseContract(
        key="blank_required_persona",
        display_name="Blank required persona",
        description="Contrat de test invalide.",
        persona_strategy="required",
        required_prompt_placeholders=["", "   "],
    )

    with pytest.raises(SeedValidationError, match="placeholder requis non vide"):
        validate_use_case_seed_contracts([broken_contract])


def test_seed_validation_accepts_current_canonical_contracts() -> None:
    """Les contrats canoniques actuels restent executables par le seed."""
    validate_use_case_seed_contracts(CANONICAL_USE_CASE_CONTRACTS)
