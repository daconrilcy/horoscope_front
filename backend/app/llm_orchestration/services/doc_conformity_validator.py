from __future__ import annotations

import re
from pathlib import Path
from typing import List

from app.llm_orchestration.feature_taxonomy import SUPPORTED_FAMILIES
from app.llm_orchestration.golden_regression_registry import GOLDEN_THRESHOLDS_DEFAULT
from app.llm_orchestration.services.fallback_governance import FallbackGovernanceRegistry
from app.llm_orchestration.supported_providers import NOMINAL_SUPPORTED_PROVIDERS


class DocConformityValidator:
    """
    Validator for documentation vs code conformity (Story 66.38).
    AC1 to AC5, AC6, AC7, AC11, AC12, AC17.
    """

    STRUCTURAL_FILES = {
        "docs/llm-prompt-generation-by-feature.md",
        ".github/pull_request_template.md",
        "backend/app/llm_orchestration/gateway.py",
        "backend/app/llm_orchestration/feature_taxonomy.py",
        "backend/app/llm_orchestration/services/fallback_governance.py",
        "backend/app/llm_orchestration/services/provider_parameter_mapper.py",
        "backend/app/llm_orchestration/services/config_coherence_validator.py",
        "backend/app/llm_orchestration/golden_regression_registry.py",
        "backend/app/llm_orchestration/supported_providers.py",
        "backend/app/llm_orchestration/models.py",
    }

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.doc_path = root_path / "docs" / "llm-prompt-generation-by-feature.md"

    def validate_all(self) -> List[str]:
        """Runs all checks and returns a list of error messages."""
        if not self.doc_path.exists():
            return [f"Documentation file not found at {self.doc_path}"]

        content = self.doc_path.read_text(encoding="utf-8")
        errors = []

        errors.extend(self.validate_taxonomy(content))
        errors.extend(self.validate_providers(content))
        errors.extend(self.validate_fallbacks(content))
        errors.extend(self.validate_obs_snapshot_classification(content))

        return errors

    def validate_taxonomy(self, content: str) -> List[str]:
        """AC2: Check if supported families match code."""
        errors = []
        # Look for the table under 'Familles et points d'entrée réels'
        # Or look for where families are mentioned.
        # Simple check: each supported family must be mentioned as a canonical family.
        for family in SUPPORTED_FAMILIES:
            pattern = rf"\| `{family}` \|.*\|.*\| `nominal_canonical` \|"
            if not re.search(pattern, content):
                errors.append(
                    f"Taxonomy error: family '{family}' not found as 'nominal_canonical' in doc."
                )
        return errors

    def validate_providers(self, content: str) -> List[str]:
        """AC3: Check if nominal providers match code."""
        errors = []
        for provider in NOMINAL_SUPPORTED_PROVIDERS:
            # Check if mentioned as only nominal provider
            pattern = rf"nominalement uniquement par `{provider}`"
            if (
                not re.search(pattern, content)
                and f"`{provider}` seul provider nominalement supporté" not in content
            ):
                # Fallback check for another phrasing
                if not re.search(rf"NOMINAL_SUPPORTED_PROVIDERS = \[\"{provider}\"\]", content):
                    errors.append(
                        f"Provider error: nominal provider '{provider}' not properly documented."
                    )
        return errors

    def validate_fallbacks(self, content: str) -> List[str]:
        """AC4: Check if critical fallbacks match code (TO_REMOVE on supported perimeter)."""
        errors = []
        matrix = FallbackGovernanceRegistry.GOVERNANCE_MATRIX

        # We check specific ones mentioned in the story and doc
        critical_fallbacks = ["USE_CASE_FIRST", "RESOLVE_MODEL"]
        for fb_name in critical_fallbacks:
            # Find in matrix (mapping string name to Enum is easier via value)
            # Actually FallbackType is an Enum, we can search by name if we have it
            from app.llm_orchestration.models import FallbackStatus, FallbackType

            try:
                fb_type = FallbackType[fb_name]
                gov = matrix.get(fb_type)
                if gov and gov.get("status") == FallbackStatus.TO_REMOVE:
                    # Check if name and 'à retirer' are in the same vicinity
                    if not re.search(rf"`{fb_name}`.*`à retirer`", content, re.IGNORECASE):
                        errors.append(
                            f"Fallback error: '{fb_name}' should be documented as 'à retirer'."
                        )

            except KeyError:
                continue

        return errors

    def validate_obs_snapshot_classification(self, content: str) -> List[str]:
        """AC5: Check obs_snapshot field classification."""
        errors = []
        # Check 'strict' fields
        for field in GOLDEN_THRESHOLDS_DEFAULT.strict_obs_fields:
            pattern = rf"- `strict` :.*`{field}`"
            if not re.search(pattern, content):
                # Try with comma or other separators
                if f"`{field}`" not in content or "classification `strict`" not in content:
                    errors.append(
                        f"ObsSnapshot error: field '{field}' should be classified as 'strict'."
                    )

        # Check 'informational' fields
        for field in GOLDEN_THRESHOLDS_DEFAULT.informational_obs_fields:
            pattern = rf"- `informational` :.*`{field}`"
            if not re.search(pattern, content):
                if f"`{field}`" not in content or "classification `informational`" not in content:
                    errors.append(
                        f"ObsSnapshot error: field '{field}' should be classified as 'informational'."
                    )

        return errors

    def is_update_required(self, changed_files: List[str]) -> bool:
        """AC6, AC8: Returns True if any structural file was changed."""
        for cf in changed_files:
            # Normalize path (remove leading ./ if any)
            normalized_cf = cf.replace("\\", "/").lstrip("./")
            if normalized_cf in self.STRUCTURAL_FILES:
                return True
        return False

    def check_verification_reference_updated(self, old_content: str, new_content: str) -> bool:
        """AC7: Check if Date or Reference stable changed."""

        def extract_ref(content: str):
            marker = "Dernière vérification manuelle contre le pipeline réel du gateway"
            if marker not in content:
                return None, None
            block = content.split(marker, maxsplit=1)[1]
            date_match = re.search(r"- \*\*Date\*\* : `([^`]+)`", block)
            ref_match = re.search(r"- \*\*Référence stable(?: [^*]+)?\*\* : `([^`]+)`", block)
            return (
                date_match.group(1) if date_match else None,
                ref_match.group(1) if ref_match else None,
            )

        old_date, old_ref = extract_ref(old_content)
        new_date, new_ref = extract_ref(new_content)

        if not new_date or not new_ref:
            return False  # Invalid format in new content

        return new_date != old_date or new_ref != old_ref
