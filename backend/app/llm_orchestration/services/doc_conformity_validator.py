from __future__ import annotations

import re
from pathlib import Path

from app.llm_orchestration.doc_conformity_manifest import (
    AUTHORIZED_PR_REASONS,
    DOC_PATH,
    STRUCTURAL_FILES,
    VERIFICATION_MARKER,
)
from app.llm_orchestration.feature_taxonomy import (
    LEGACY_DAILY_FEATURE,
    LEGACY_NATAL_FEATURE,
    SUPPORTED_FAMILIES,
)
from app.llm_orchestration.golden_regression_registry import GOLDEN_THRESHOLDS_DEFAULT
from app.llm_orchestration.models import FallbackStatus, FallbackType
from app.llm_orchestration.services.fallback_governance import FallbackGovernanceRegistry
from app.llm_orchestration.supported_providers import NOMINAL_SUPPORTED_PROVIDERS


class DocConformityValidator:
    """
    Validator for documentation vs code conformity (Story 66.38).
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.doc_path = root_path / DOC_PATH

    def validate_all(self) -> list[str]:
        if not self.doc_path.exists():
            return [f"Documentation file not found at {self.doc_path}"]

        content = self.doc_path.read_text(encoding="utf-8")
        errors: list[str] = []
        errors.extend(self.validate_taxonomy(content))
        errors.extend(self.validate_providers(content))
        errors.extend(self.validate_fallbacks(content))
        errors.extend(self.validate_obs_snapshot_classification(content))
        return errors

    def validate_taxonomy(self, content: str) -> list[str]:
        errors: list[str] = []
        for family in sorted(SUPPORTED_FAMILIES):
            pattern = rf"\|[ \t]*`{family}`[ \t]*\|[^|]*\|[^|]*\|[ \t]*`nominal_canonical`[ \t]*\|"
            if not re.search(pattern, content):
                errors.append(
                    f"Taxonomy error: family '{family}' not found as 'nominal_canonical' in doc."
                )

        alias_expectations = {
            LEGACY_DAILY_FEATURE: "horoscope_daily",
            LEGACY_NATAL_FEATURE: "natal",
        }
        for alias, canonical in alias_expectations.items():
            alias_pattern = rf"`{alias}`.*?`{canonical}`|`{canonical}`.*?`{alias}`"
            if not re.search(alias_pattern, content, flags=re.IGNORECASE | re.DOTALL):
                errors.append(
                    f"Taxonomy error: legacy alias '{alias}' should be documented "
                    f"with its canonical mapping to '{canonical}'."
                )
        return errors

    def validate_providers(self, content: str) -> list[str]:
        errors: list[str] = []
        documented_providers: set[str] = set()

        documented_providers.update(
            re.findall(r"nominalement uniquement par `([^`]+)`", content, flags=re.IGNORECASE)
        )
        documented_providers.update(
            re.findall(
                r"`([^`]+)` seul provider nominalement (?:supporté|autorisé)",
                content,
                flags=re.IGNORECASE,
            )
        )

        registry_match = re.search(r'NOMINAL_SUPPORTED_PROVIDERS = \[(.*?)\]', content)
        if registry_match:
            documented_providers.update(re.findall(r'"([^"]+)"', registry_match.group(1)))

        documented_providers = {provider.strip() for provider in documented_providers if provider}
        expected_providers = set(NOMINAL_SUPPORTED_PROVIDERS)

        for provider in sorted(expected_providers - documented_providers):
            errors.append(f"Provider error: nominal provider '{provider}' not properly documented.")

        for provider in sorted(documented_providers - expected_providers):
            errors.append(f"Provider error: unexpected nominal provider '{provider}' documented.")

        return errors

    def validate_fallbacks(self, content: str) -> list[str]:
        errors: list[str] = []
        critical_fallbacks = ["USE_CASE_FIRST", "RESOLVE_MODEL"]

        for fallback_name in critical_fallbacks:
            fallback_type = FallbackType[fallback_name]
            governance = FallbackGovernanceRegistry.GOVERNANCE_MATRIX.get(fallback_type)
            if not governance:
                continue

            expected_status = governance.get("status")
            expected_families = sorted(governance.get("forbidden_families", set()))
            if expected_status != FallbackStatus.TO_REMOVE:
                continue

            line_match = re.search(
                rf"-\s*`{fallback_name}`\s+est(?:\s+d[ée]sormais)?\s+`([^`]+)`.*?sur\s+([^\n;]+)",
                content,
                flags=re.IGNORECASE,
            )
            if not line_match:
                errors.append(
                    f"Fallback error: '{fallback_name}' should be documented "
                    "with status and family perimeter."
                )
                continue

            documented_status = line_match.group(1).strip().lower()
            if documented_status != expected_status.value:
                errors.append(
                    f"Fallback error: '{fallback_name}' should be documented "
                    f"as '{expected_status.value}'."
                )

            documented_families = set(re.findall(r"`([^`]+)`", line_match.group(2)))
            if documented_families != set(expected_families):
                errors.append(
                    f"Fallback error: '{fallback_name}' families mismatch. "
                    f"Doc={sorted(documented_families)} Code={expected_families}"
                )

        return errors

    def validate_obs_snapshot_classification(self, content: str) -> list[str]:
        errors: list[str] = []

        def get_section(marker: str) -> str:
            match = re.search(rf"-[ \t]*`{marker}`[ \t]*:[ \t]*(.*)", content, flags=re.IGNORECASE)
            return match.group(1) if match else ""

        strict_section = get_section("strict")
        for field in sorted(GOLDEN_THRESHOLDS_DEFAULT.strict_obs_fields):
            is_documented = f"`{field}`" in strict_section
            if not is_documented and field in {
                "requested_provider",
                "resolved_provider",
                "executed_provider",
            }:
                is_documented = "triplet provider" in strict_section
            if not is_documented:
                errors.append(
                    f"ObsSnapshot error: field '{field}' should be classified as 'strict'."
                )

        thresholded_section = get_section("thresholded")
        for field in sorted(GOLDEN_THRESHOLDS_DEFAULT.thresholded_obs_fields):
            if f"`{field}`" not in thresholded_section:
                errors.append(
                    f"ObsSnapshot error: field '{field}' should be classified as 'thresholded'."
                )

        informational_section = get_section("informational")
        for field in sorted(GOLDEN_THRESHOLDS_DEFAULT.informational_obs_fields):
            if f"`{field}`" not in informational_section:
                errors.append(
                    f"ObsSnapshot error: field '{field}' should be classified as 'informational'."
                )

        return errors

    def is_update_required(self, changed_files: list[str]) -> bool:
        normalized_changed_files = {
            changed_file.replace("\\", "/").removeprefix("./") for changed_file in changed_files
        }
        return any(changed_file in STRUCTURAL_FILES for changed_file in normalized_changed_files)

    def check_verification_reference_updated(self, old_content: str, new_content: str) -> bool:
        def extract_ref(content: str) -> tuple[str | None, str | None]:
            if VERIFICATION_MARKER not in content:
                return None, None
            block = content.split(VERIFICATION_MARKER, maxsplit=1)[1]
            date_match = re.search(r"- \*\*Date\*\* : `([^`]+)`", block)
            ref_match = re.search(r"- \*\*Référence stable(?: [^*]+)?\*\* : `([^`]+)`", block)
            return (
                date_match.group(1) if date_match else None,
                ref_match.group(1) if ref_match else None,
            )

        old_date, old_ref = extract_ref(old_content)
        new_date, new_ref = extract_ref(new_content)
        if not new_date or not new_ref:
            return False
        return new_date != old_date or new_ref != old_ref

    def parse_pr_template_state(self, pr_content: str) -> dict[str, object]:
        checked_reasons = [
            reason
            for reason in AUTHORIZED_PR_REASONS
            if re.search(rf"- \[x\] `{reason}`", pr_content, flags=re.IGNORECASE)
        ]
        return {
            "oui_checked": bool(re.search(r"- \[x\] \*\*OUI\*\*", pr_content, flags=re.IGNORECASE)),
            "checked_reasons": checked_reasons,
        }

    def check_pr_template_justification(self, pr_content: str) -> bool:
        state = self.parse_pr_template_state(pr_content)
        if state["oui_checked"]:
            return True
        return len(state["checked_reasons"]) == 1

    def validate_pr_template_state(
        self,
        pr_content: str,
        *,
        structural_change: bool,
        doc_updated: bool,
    ) -> list[str]:
        if not structural_change:
            return []

        if not pr_content.strip():
            return [
                "PR template error: the documentation governance section must be "
                "explicitly filled in for structural changes."
            ]

        state = self.parse_pr_template_state(pr_content)
        oui_checked = bool(state["oui_checked"])
        checked_reasons = list(state["checked_reasons"])
        errors: list[str] = []

        if doc_updated:
            if oui_checked:
                if checked_reasons:
                    errors.append(
                        "PR template error: do not check a justification reason "
                        "when 'OUI' is selected."
                    )
                return errors

            if checked_reasons != ["DOC_ONLY"]:
                errors.append(
                    "PR template error: documentation update requires either "
                    "'OUI' or the sole reason 'DOC_ONLY'."
                )
            return errors

        if oui_checked:
            errors.append(
                "PR template error: 'OUI' cannot be selected when the "
                "documentation file was not updated."
            )
            return errors

        if len(checked_reasons) != 1:
            errors.append(
                "PR template error: exactly one authorized justification "
                "reason must be selected when documentation is not updated."
            )
            return errors

        if checked_reasons[0] == "DOC_ONLY":
            errors.append(
                "PR template error: 'DOC_ONLY' is not valid when the "
                "documentation file was not updated."
            )

        return errors
