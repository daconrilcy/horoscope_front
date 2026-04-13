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
        for family in SUPPORTED_FAMILIES:
            # Flexible pattern for table row
            pattern = rf"\|[ \t]*`{family}`[ \t]*\|[^|]*\|[^|]*\|[ \t]*`nominal_canonical`[ \t]*\|"
            if not re.search(pattern, content):
                errors.append(
                    f"Taxonomy error: family '{family}' not found as 'nominal_canonical' in doc."
                )
        return errors

    def validate_providers(self, content: str) -> List[str]:
        """AC3: Check if nominal providers match code."""
        errors = []
        for provider in NOMINAL_SUPPORTED_PROVIDERS:
            # Multiple possible phrasings from the doc
            patterns = [
                rf"nominalement uniquement par `{provider}`",
                rf"`{provider}` seul provider nominalement supporté",
                rf"NOMINAL_SUPPORTED_PROVIDERS = \[\"{provider}\"\]",
            ]
            if not any(re.search(p, content, re.IGNORECASE) for p in patterns):
                errors.append(
                    f"Provider error: nominal provider '{provider}' not properly documented."
                )
        return errors

    def validate_fallbacks(self, content: str) -> List[str]:
        """AC4: Check if critical fallbacks match code (TO_REMOVE on supported perimeter)."""
        errors = []
        matrix = FallbackGovernanceRegistry.GOVERNANCE_MATRIX

        critical_fallbacks = ["USE_CASE_FIRST", "RESOLVE_MODEL"]
        for fb_name in critical_fallbacks:
            from app.llm_orchestration.models import FallbackStatus, FallbackType

            try:
                fb_type = FallbackType[fb_name]
                gov = matrix.get(fb_type)
                if gov and gov.get("status") == FallbackStatus.TO_REMOVE:
                    # More flexible check for 'à retirer'
                    pattern = rf"`{fb_name}`.*`à retirer`"
                    if not re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                        errors.append(
                            f"Fallback error: '{fb_name}' should be documented as 'à retirer'."
                        )

            except KeyError:
                continue

        return errors

    def validate_obs_snapshot_classification(self, content: str) -> List[str]:
        """AC5: Check obs_snapshot field classification."""
        errors = []

        def get_section(marker: str) -> str:
            # Find the line starting with '- `marker` :' and get its content
            # or look for the block after it.
            match = re.search(rf"-[ \t]*`{marker}`[ \t]*:[ \t]*(.*)", content, re.IGNORECASE)
            if match:
                # Return the rest of the line and maybe the next lines if they are indented
                # For now, just the line is often enough if fields are listed there
                return match.group(1)
            return ""

        strict_section = get_section("strict")
        for field in GOLDEN_THRESHOLDS_DEFAULT.strict_obs_fields:
            # Handle triplet provider alias
            is_in_doc = f"`{field}`" in strict_section
            if not is_in_doc and field in [
                "requested_provider",
                "resolved_provider",
                "executed_provider",
            ]:
                is_in_doc = "triplet provider" in strict_section

            if not is_in_doc:
                errors.append(
                    f"ObsSnapshot error: field '{field}' should be classified as 'strict'."
                )

        info_section = get_section("informational")
        for field in GOLDEN_THRESHOLDS_DEFAULT.informational_obs_fields:
            if f"`{field}`" not in info_section:
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

    def check_pr_template_justification(self, pr_content: str) -> bool:
        """AC9, AC13: Check if a valid justification is provided in PR content."""
        # Check if 'OUI' is checked
        if re.search(r"- \[x\] \*\*OUI\*\*", pr_content, re.IGNORECASE):
            return True

        # Check for authorized reasons
        authorized_reasons = ["REF_ONLY", "FIX_TYPO", "TEST_ONLY", "DOC_ONLY", "NON_LLM"]
        checked_reasons = []
        for reason in authorized_reasons:
            if re.search(rf"- \[x\] `{reason}`", pr_content, re.IGNORECASE):
                checked_reasons.append(reason)

        # Must have exactly one reason if 'OUI' is not checked
        return len(checked_reasons) == 1
