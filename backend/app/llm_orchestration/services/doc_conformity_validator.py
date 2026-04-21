from __future__ import annotations

import re
from pathlib import Path

from app.domain.llm.governance.legacy_residual_registry import validate_doc_registry_version
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
from app.llm_orchestration.golden_regression_registry import (
    OBS_SNAPSHOT_CLASSIFICATION_DEFAULT,
)
from app.llm_orchestration.models import FallbackStatus, FallbackType
from app.llm_orchestration.services.fallback_governance import FallbackGovernanceRegistry
from app.llm_orchestration.supported_providers import NOMINAL_SUPPORTED_PROVIDERS


class DocConformityValidator:
    """
    Validator for documentation vs code conformity (Story 66.38 & 66.39).
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
        errors.extend(validate_doc_registry_version(content))
        return errors

    def validate_taxonomy(self, content: str) -> list[str]:
        errors: list[str] = []
        for family in sorted(SUPPORTED_FAMILIES):
            pattern = rf"\|[ \t]*`{family}`[ \t]*\|[^|]*\|[^|]*\|[ \t]*`nominal_canonical`[ \t]*\|"
            if not re.search(pattern, content):
                errors.append(
                    f"Taxonomy error: family '{family}' not found as 'nominal_canonical' in doc. "
                    "Ensure the feature is correctly documented in the taxonomy table."
                )

        alias_expectations = {
            LEGACY_DAILY_FEATURE: "horoscope_daily",
            LEGACY_NATAL_FEATURE: "natal",
        }
        for alias, canonical in alias_expectations.items():
            alias_pattern = rf"`{alias}`.*?`{canonical}`|`{canonical}`.*?`{alias}`"
            if not re.search(alias_pattern, content, flags=re.IGNORECASE | re.DOTALL):
                errors.append(
                    f"Taxonomy error: legacy alias '{alias}' is missing its documented "
                    f"mapping to '{canonical}'. (Requirement: documented for reviewability)."
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

        registry_match = re.search(r"NOMINAL_SUPPORTED_PROVIDERS = \[(.*?)\]", content)
        if registry_match:
            documented_providers.update(re.findall(r'"([^"]+)"', registry_match.group(1)))

        documented_providers = {provider.strip() for provider in documented_providers if provider}
        expected_providers = set(NOMINAL_SUPPORTED_PROVIDERS)

        for provider in sorted(expected_providers - documented_providers):
            errors.append(
                f"Provider error: nominal provider '{provider}' is NOT documented. "
                f"The doc must explicitly mention it as nominal/authorized."
            )

        for provider in sorted(documented_providers - expected_providers):
            errors.append(
                f"Provider error: unexpected nominal provider '{provider}' found in doc "
                "but not in code (NOMINAL_SUPPORTED_PROVIDERS)."
            )

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
                    f"Fallback error: '{fallback_name}' is missing mandatory documentation "
                    "about its status and family perimeter."
                )
                continue

            documented_status = line_match.group(1).strip().lower()
            if documented_status != expected_status.value:
                errors.append(
                    f"Fallback error: '{fallback_name}' status mismatch. "
                    f"Expected: '{expected_status.value}', Found: '{documented_status}'."
                )

            documented_families = set(re.findall(r"`([^`]+)`", line_match.group(2)))
            if documented_families != set(expected_families):
                errors.append(
                    f"Fallback error: '{fallback_name}' forbidden families mismatch. "
                    f"Doc={sorted(documented_families)} vs Code={expected_families}."
                )

        return errors

    def validate_obs_snapshot_classification(self, content: str) -> list[str]:
        errors: list[str] = []

        def get_section(marker: str) -> str:
            match = re.search(rf"-[ \t]*`{marker}`[ \t]*:[ \t]*(.*)", content, flags=re.IGNORECASE)
            return match.group(1) if match else ""

        strict_section = get_section("strict")
        for field in sorted(OBS_SNAPSHOT_CLASSIFICATION_DEFAULT["strict"]):
            is_documented = f"`{field}`" in strict_section
            if not is_documented and field in {
                "requested_provider",
                "resolved_provider",
                "executed_provider",
            }:
                is_documented = "triplet provider" in strict_section
            if not is_documented:
                errors.append(
                    f"ObsSnapshot error: field '{field}' MUST be classified as 'strict' in doc."
                )

        thresholded_section = get_section("thresholded")
        for field in sorted(OBS_SNAPSHOT_CLASSIFICATION_DEFAULT["thresholded"]):
            if f"`{field}`" not in thresholded_section:
                errors.append(
                    "ObsSnapshot error: field "
                    f"'{field}' MUST be classified as 'thresholded' in doc."
                )

        informational_section = get_section("informational")
        for field in sorted(OBS_SNAPSHOT_CLASSIFICATION_DEFAULT["informational"]):
            if f"`{field}`" not in informational_section:
                errors.append(
                    "ObsSnapshot error: field "
                    f"'{field}' MUST be classified as 'informational' in doc."
                )

        return errors

    def is_update_required(self, changed_files: list[str]) -> bool:
        normalized_changed_files = {
            changed_file.replace("\\", "/").removeprefix("./") for changed_file in changed_files
        }
        return any(changed_file in STRUCTURAL_FILES for changed_file in normalized_changed_files)

    def check_verification_reference_updated(self, old_content: str, new_content: str) -> bool:
        """AC4: Verify Date and Stable Ref block update with structured field comparison."""

        def extract_ref_block(content: str) -> dict[str, str | None]:
            if VERIFICATION_MARKER not in content:
                return {}
            block = content.split(VERIFICATION_MARKER, maxsplit=1)[1]
            date_match = re.search(r"- \*\*Date\*\* : `([^`]+)`", block)
            ref_match = re.search(r"- \*\*Référence stable(?: [^*]+)?\*\* : `([^`]+)`", block)
            return {
                "date": date_match.group(1).strip() if date_match else None,
                "ref": ref_match.group(1).strip() if ref_match else None,
            }

        old_data = extract_ref_block(old_content)
        new_data = extract_ref_block(new_content)

        if not new_data.get("date") or not new_data.get("ref"):
            return False

        # Return True if either date or ref has changed
        return new_data["date"] != old_data.get("date") or new_data["ref"] != old_data.get("ref")

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
        """Backward compatibility helper (Story 66.38)."""
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
        changed_files: list[str] | None = None,
    ) -> list[str]:
        """AC5, AC6: Strict PR parser with semantic checks for reasons."""
        if not structural_change:
            return []

        if not pr_content.strip():
            return [
                "PR template error: the documentation governance section must be "
                "filled in for structural changes (PR body empty or missing)."
            ]

        state = self.parse_pr_template_state(pr_content)
        oui_checked = bool(state["oui_checked"])
        checked_reasons = list(state["checked_reasons"])
        errors: list[str] = []

        # AC5: Reject contradictory states
        if oui_checked and checked_reasons:
            errors.append(
                "PR template error: contradictory state. 'OUI' is selected, but "
                f"justification reasons are also checked: {checked_reasons}."
            )
            return errors

        if doc_updated:
            if not oui_checked and checked_reasons != ["DOC_ONLY"]:
                errors.append(
                    "PR template error: doc was updated, so either select 'OUI' "
                    "or ONLY the 'DOC_ONLY' reason."
                )
            return errors

        # Case: structural change BUT doc NOT updated
        if oui_checked:
            errors.append(
                "PR template error: 'OUI' is selected but the documentation "
                "file was NOT updated in this PR."
            )
            return errors

        if len(checked_reasons) != 1:
            errors.append(
                "PR template error: exactly one authorized justification reason must be "
                f"selected since doc is not updated. Found: {checked_reasons or 'none'}."
            )
            return errors

        reason = checked_reasons[0]

        # AC6: Semantic verification of reasons
        if doc_updated:
            # If doc is updated, only OUI or DOC_ONLY are allowed (handled above)
            pass
        else:
            # If doc NOT updated, but structural change detected
            if reason == "DOC_ONLY":
                errors.append(
                    "PR template error: 'DOC_ONLY' reason requires "
                    "the documentation file to be updated."
                )

            if reason == "REF_ONLY":
                errors.append(
                    "PR template error: 'REF_ONLY' reason requires "
                    "a Date/SHA update in the documentation file."
                )

        if changed_files:
            norm_files = {f.replace("\\", "/").lstrip("./") for f in changed_files}
            structural_touched = sorted(norm_files.intersection(STRUCTURAL_FILES))

            if reason == "TEST_ONLY":
                # Only tests, fixtures, or test tooling scripts.
                # Must not touch gateway core logic or manifest.
                invalid_files = [
                    f
                    for f in structural_touched
                    if not any(x in f for x in ("tests/", "test_", "scripts/"))
                ]
                if invalid_files:
                    errors.append(
                        f"PR template error: 'TEST_ONLY' is invalid because core structural files "
                        f"were touched: {invalid_files}."
                    )

            if reason == "FIX_TYPO":
                # Only allowed on doc, template, or markdown files.
                # Strictly forbidden on core .py files (gateway, manifest, registry).
                python_structural = [
                    f
                    for f in structural_touched
                    if f.endswith(".py") and f not in ("backend/scripts/check_doc_conformity.py",)
                ]
                if python_structural:
                    errors.append(
                        f"PR template error: 'FIX_TYPO' is invalid because Python structural "
                        f"files were touched: {python_structural}."
                    )

            if reason == "NON_LLM":
                # Structural files were touched, but justification says it's not an LLM change.
                # This is allowed but must be clear that at least one structural file WAS touched.
                pass

        return errors
