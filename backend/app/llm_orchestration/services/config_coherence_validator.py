from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.llm_orchestration.prompt_governance_registry import (
    format_placeholder_violation_report,
    get_prompt_governance_registry,
)
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.feature_taxonomy import (
    NATAL_CANONICAL_FEATURE,
    is_natal_subfeature_canonical,
    is_nominal_feature_allowed,
    is_supported_feature,
)
from app.llm_orchestration.services.assembly_resolver import PLAN_RULES_REGISTRY
from app.llm_orchestration.services.execution_profile_registry import (
    ExecutionProfileRegistry,
)
from app.llm_orchestration.supported_providers import is_provider_supported
from app.prompts.validators import validate_plan_rules_content

logger = logging.getLogger(__name__)
gov_logger = logging.getLogger("app.llm_orchestration.governance")


class ValidationError(BaseModel):
    error_code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[ValidationError] = Field(default_factory=list)

    def add_error(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.errors.append(ValidationError(error_code=error_code, message=message, details=details))
        self.is_valid = False
        gov_logger.error(
            f"coherence_validation_error: code={error_code} message={message} details={details}"
        )


class CoherenceError(Exception):
    """Exception raised when a coherence validation fails."""

    def __init__(self, result: ValidationResult):
        self.result = result
        super().__init__(f"Coherence validation failed with {len(result.errors)} errors.")


def validate_execution_profile(profile: LlmExecutionProfileModel) -> ValidationResult:
    """
    Validate a single execution profile.
    Synchronous and independent of DB session.
    (Story 66.31 AC4)
    """
    result = ValidationResult(is_valid=True)

    # AC4: Provider support
    if not is_provider_supported(profile.provider):
        # We check if it's a supported feature perimeter if feature is set
        feature = profile.feature
        if feature and is_supported_feature(feature):
            result.add_error(
                "unsupported_execution_provider",
                f"Provider '{profile.provider}' is not nominally supported "
                f"for feature '{feature}'.",
                {"provider": profile.provider, "feature": feature},
            )
        elif not feature:
            # Generic profiles also need to use supported providers for nominal familias
            result.add_error(
                "unsupported_execution_provider",
                f"Provider '{profile.provider}' is not in the supported providers list.",
                {"provider": profile.provider},
            )

    # AC8: No legacy dependency on nominal families
    if profile.feature:
        if not is_nominal_feature_allowed(profile.feature):
            result.add_error(
                "legacy_dependency_forbidden",
                f"Feature identifier '{profile.feature}' is forbidden for nominal use.",
                {"feature": profile.feature},
            )

        # AC6: Ensure subfeature is canonical if feature is natal
        if profile.feature == NATAL_CANONICAL_FEATURE and profile.subfeature:
            if not is_natal_subfeature_canonical(profile.subfeature):
                result.add_error(
                    "legacy_dependency_forbidden",
                    f"Subfeature '{profile.subfeature}' is not canonical for '{profile.feature}'.",
                    {"feature": profile.feature, "subfeature": profile.subfeature},
                )

    return result


class ConfigCoherenceValidator:
    """
    Central validator for LLM configuration coherence.
    Used at publish-time and boot-time.
    (Story 66.31)
    """

    def __init__(self, session: Union[AsyncSession, Session]):
        self.session = session

    async def _execute(self, stmt):
        """Unified executor for sync/async sessions."""
        from sqlalchemy.ext.asyncio import AsyncSession

        if isinstance(self.session, AsyncSession):
            return await self.session.execute(stmt)
        return self.session.execute(stmt)

    async def validate_assembly(
        self, config: PromptAssemblyConfigModel, bundle: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate a single assembly configuration.
        Story 66.32: Support optional snapshot bundle for self-sufficient validation (Finding 5).
        """
        result = ValidationResult(is_valid=True)
        feature = config.feature
        is_supported = is_supported_feature(feature)

        # AC8: No legacy dependency on nominal families
        if not is_nominal_feature_allowed(feature):
            result.add_error(
                "legacy_dependency_forbidden",
                f"Feature identifier '{feature}' is forbidden for nominal use.",
                {"feature": feature},
            )

        # 1. Execution Profile Validation (AC2)
        profile, profile_error_code = await self._resolve_and_validate_profile(
            config, is_supported, bundle
        )
        if profile_error_code:
            result.add_error(
                profile_error_code,
                self._get_error_message(profile_error_code),
                {"feature": feature, "subfeature": config.subfeature, "plan": config.plan},
            )

        # 2. Provider Support (AC4)
        if profile:
            if not is_provider_supported(profile.provider):
                if is_supported:
                    result.add_error(
                        "unsupported_execution_provider",
                        f"Provider '{profile.provider}' is not supported for feature '{feature}'.",
                        {"provider": profile.provider, "feature": feature},
                    )

        # 3. Output Contract Validation (AC3)
        if config.output_contract_ref:
            res_contract = await self._validate_output_contract(config, profile, bundle)
            contract_valid, contract_error_code = res_contract
            if not contract_valid:
                result.add_error(
                    contract_error_code,
                    self._get_error_message(contract_error_code),
                    {"output_contract_ref": config.output_contract_ref},
                )

        # 4. Placeholders Validation (AC5)
        await self._validate_templates_placeholders(config, result)

        # 5. Persona Validation (AC6)
        if config.persona_enabled and config.persona_ref:
            await self._validate_persona(config, result, bundle)

        # 6. Plan Rules & Length Budget (AC7)
        if config.plan_rules_enabled and config.plan_rules_ref:
            self._validate_plan_rules(config, result)

        if config.length_budget:
            self._validate_length_budget(config, result)

        return result

    async def _resolve_and_validate_profile(
        self,
        config: PromptAssemblyConfigModel,
        is_supported: bool,
        bundle: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[LlmExecutionProfileModel], Optional[str]]:
        """
        AC2: execution_profile_ref vs waterfall.
        Returns (Profile, error_code)
        """
        # Story 66.32: Try from bundle first (Finding 5)
        if bundle and "profile" in bundle:
            profile_data = bundle["profile"]
            # Check if this profile matches the explicit ref or is the one for this target
            if config.execution_profile_ref:
                if profile_data.get("id") == str(config.execution_profile_ref):
                    from app.infra.db.utils import reconstruct_orm

                    profile = reconstruct_orm(LlmExecutionProfileModel, profile_data)
                    if profile.status == PromptStatus.PUBLISHED:
                        return profile, None
            else:
                # Waterfall case - the bundle already contains the correctly resolved profile
                from app.infra.db.utils import reconstruct_orm

                profile = reconstruct_orm(LlmExecutionProfileModel, profile_data)
                if profile.status == PromptStatus.PUBLISHED:
                    return profile, None

        # Finding 5 hardening: if bundle is provided, NEVER fall back to live DB
        if bundle:
            return None, "missing_execution_profile"

        # Case 1: Explicit reference (Live DB)
        if config.execution_profile_ref:
            stmt = select(LlmExecutionProfileModel).where(
                LlmExecutionProfileModel.id == config.execution_profile_ref
            )
            res = await self._execute(stmt)
            profile = res.scalar_one_or_none()

            if not profile or profile.status != PromptStatus.PUBLISHED:
                return None, "invalid_execution_profile_ref"

            return profile, None

        # Case 2: Waterfall resolution (Live DB)
        profile = await self._resolve_profile_via_waterfall(
            feature=config.feature,
            subfeature=config.subfeature,
            plan=config.plan,
        )

        if not profile and is_supported:
            return None, "missing_execution_profile"

        return profile, None

    async def _resolve_profile_via_waterfall(
        self,
        *,
        feature: str,
        subfeature: Optional[str],
        plan: Optional[str],
    ) -> Optional[LlmExecutionProfileModel]:
        if isinstance(self.session, Session):
            return ExecutionProfileRegistry.get_active_profile(
                self.session,
                feature=feature,
                subfeature=subfeature,
                plan=plan,
            )

        candidates = [
            (feature, subfeature, plan),
            (feature, subfeature, None) if subfeature else None,
            (feature, None, None),
        ]

        for candidate in candidates:
            if candidate is None:
                continue

            cand_feature, cand_subfeature, cand_plan = candidate
            stmt = select(LlmExecutionProfileModel).where(
                LlmExecutionProfileModel.feature == cand_feature,
                LlmExecutionProfileModel.subfeature == cand_subfeature,
                LlmExecutionProfileModel.plan == cand_plan,
                LlmExecutionProfileModel.status == PromptStatus.PUBLISHED,
            )
            res = await self._execute(stmt)
            profile = res.scalar_one_or_none()
            if profile:
                return profile

        return None

    async def _validate_output_contract(
        self,
        config: PromptAssemblyConfigModel,
        profile: Optional[LlmExecutionProfileModel],
        bundle: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        AC3: Output contract validity and compatibility.
        """
        contract_ref = config.output_contract_ref

        # Story 66.32: Try from bundle first (Finding 5)
        if bundle and "schema" in bundle:
            schema_data = bundle["schema"]
            if schema_data.get("id") == contract_ref or schema_data.get("name") == contract_ref:
                return True, None

        # Finding 5 hardening: if bundle is provided, NEVER fall back to live DB
        if bundle:
            return False, "invalid_output_contract_ref"

        contract = None

        try:
            contract_id = uuid.UUID(contract_ref)
        except (TypeError, ValueError):
            contract_id = None

        if contract_id is not None:
            stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.id == contract_id)
            res = await self._execute(stmt)
            contract = res.scalar_one_or_none()

        if contract is None:
            stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == contract_ref)
            res = await self._execute(stmt)
            contract = res.scalar_one_or_none()

        if not contract:
            return False, "invalid_output_contract_ref"

        return True, None

    async def _validate_templates_placeholders(
        self, config: PromptAssemblyConfigModel, result: ValidationResult
    ):
        """
        AC5: Static validation of placeholders (registre central 66.42, AC7).
        """
        reg = get_prompt_governance_registry()

        # Feature Template
        if config.feature_template:
            _invalid, violations = reg.validate_placeholders_in_template(
                config.feature_template.developer_prompt,
                config.feature,
                source="assembly.feature_template",
            )
            if violations:
                result.add_error(
                    "placeholder_policy_violation",
                    f"Placeholders non gouvernés (feature template): {', '.join(_invalid)}. "
                    f"Détail:\n{format_placeholder_violation_report(violations)}",
                    {
                        "placeholders": _invalid,
                        "template": "feature",
                        "governance_report": format_placeholder_violation_report(violations),
                        "violations": [v.__dict__ for v in violations],
                    },
                )

        # Subfeature Template
        if config.subfeature_template_ref and config.subfeature_template:
            _inv_sub, viol_sub = reg.validate_placeholders_in_template(
                config.subfeature_template.developer_prompt,
                config.feature,
                source="assembly.subfeature_template",
            )
            if viol_sub:
                result.add_error(
                    "placeholder_policy_violation",
                    f"Placeholders non gouvernés (subfeature template): {', '.join(_inv_sub)}. "
                    f"Détail:\n{format_placeholder_violation_report(viol_sub)}",
                    {
                        "placeholders": _inv_sub,
                        "template": "subfeature",
                        "governance_report": format_placeholder_violation_report(viol_sub),
                        "violations": [v.__dict__ for v in viol_sub],
                    },
                )

    async def _validate_persona(
        self,
        config: PromptAssemblyConfigModel,
        result: ValidationResult,
        bundle: Optional[Dict[str, Any]] = None,
    ):
        """
        AC6: Persona existence and authorization.
        """
        # Story 66.32: Try from bundle first (Finding 5)
        # Reconstructed assembly config already has the persona object if it was in the bundle
        if config.persona:
            if not config.persona.enabled:
                result.add_error(
                    "persona_not_allowed",
                    f"Persona '{config.persona.name}' is disabled.",
                    {"persona_id": str(config.persona_ref)},
                )
            return

        # Finding 5 hardening: if bundle is provided, NEVER fall back to live DB
        if bundle:
            result.add_error(
                "persona_not_allowed",
                "Persona referenced missing from bundle.",
                {"persona_id": str(config.persona_ref)},
            )
            return

        stmt = select(LlmPersonaModel).where(LlmPersonaModel.id == config.persona_ref)
        res = await self._execute(stmt)
        persona = res.scalar_one_or_none()

        if not persona:
            result.add_error(
                "persona_not_allowed",
                "Persona referenced does not exist.",
                {"persona_id": str(config.persona_ref)},
            )
            return

        if not persona.enabled:
            result.add_error(
                "persona_not_allowed",
                f"Persona '{persona.name}' is disabled.",
                {"persona_id": str(config.persona_ref)},
            )

    def _validate_plan_rules(self, config: PromptAssemblyConfigModel, result: ValidationResult):
        """
        AC7: plan_rules invariants.
        """
        rule = PLAN_RULES_REGISTRY.get(config.plan_rules_ref)
        if not rule:
            return

        if rule.instruction:
            violations = validate_plan_rules_content(rule.instruction)
            is_feat_violation = any(
                v.violation_type == "plan_rules_violation:feature_selection" for v in violations
            )
            if is_feat_violation:
                result.add_error(
                    "plan_rules_scope_violation",
                    "Plan rules attempt to modify forbidden taxonomic scope (feature selection).",
                    {"plan_rules_ref": config.plan_rules_ref},
                )

    def _validate_length_budget(self, config: PromptAssemblyConfigModel, result: ValidationResult):
        """
        AC7: LengthBudget invariants.
        """
        budget = config.length_budget
        if not budget:
            return

        global_max = budget.get("global_max_tokens")
        if global_max and global_max > 128000:
            result.add_error(
                "length_budget_scope_violation",
                f"LengthBudget global_max_tokens ({global_max}) exceeds technical ceiling.",
                {"global_max_tokens": global_max},
            )

    def _get_error_message(self, error_code: str) -> str:
        messages = {
            "missing_execution_profile": (
                "L'assembly active ne pointe vers aucun profil d'exécution valide."
            ),
            "invalid_execution_profile_ref": (
                "La référence au profil d'exécution est invalide ou pointe vers "
                "un profil non publié."
            ),
            "unsupported_execution_provider": (
                "Le provider LLM n'est pas nominalement supporté sur ce périmètre."
            ),
            "missing_output_contract": (
                "Le contrat de sortie requis est manquant pour cette configuration."
            ),
            "invalid_output_contract_ref": (
                "La référence au contrat de sortie est invalide ou pointe vers "
                "un contrat non publié."
            ),
            "placeholder_policy_violation": (
                "Les placeholders utilisés violent la politique de la famille canonique."
            ),
            "persona_not_allowed": ("La persona référencée n'est pas autorisée ou est désactivée."),
            "plan_rules_scope_violation": (
                "Les plan_rules tentent de modifier le périmètre taxonomique interdit."
            ),
            "length_budget_scope_violation": (
                "Le LengthBudget contient des instructions hors de sa responsabilité."
            ),
            "legacy_dependency_forbidden": (
                "Une dépendance legacy interdite a été détectée sur une famille nominale fermée."
            ),
        }
        return messages.get(error_code, "Unknown coherence error.")

    async def scan_active_configurations(
        self,
    ) -> List[Tuple[PromptAssemblyConfigModel, ValidationResult]]:
        """
        AC10: Scan only active published configurations for boot runtime validation.
        Story 66.32: Prioritize active release snapshot if available (Finding 6).
        """
        from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
        from app.llm_orchestration.services.release_service import ReleaseService

        active_snapshot_id = await ReleaseService.get_active_release_id(self.session)

        if active_snapshot_id:
            # Validate the snapshot manifest instead of live tables
            from app.infra.db.models.llm_release import LlmReleaseSnapshotModel

            if isinstance(self.session, AsyncSession):
                snapshot = await self.session.get(LlmReleaseSnapshotModel, active_snapshot_id)
            else:
                snapshot = self.session.get(LlmReleaseSnapshotModel, active_snapshot_id)

            if snapshot:
                logger.info(
                    "scan_active_configurations: validating active snapshot %s", snapshot.version
                )
                results = []
                manifest = snapshot.manifest
                targets = manifest.get("targets", {})
                registry = AssemblyRegistry(self.session)

                for target_key, bundle in targets.items():
                    assembly_data = bundle.get("assembly")
                    if not assembly_data:
                        continue

                    assembly = registry._reconstruct_config(assembly_data)
                    # Important: Pass the bundle for transitive validation (Finding 5)
                    val_result = await self.validate_assembly(assembly, bundle=bundle)
                    if not val_result.is_valid:
                        results.append((assembly, val_result))
                return results

        # Fallback to legacy live table scanning if no snapshot is active
        stmt = (
            select(PromptAssemblyConfigModel)
            .where(PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED)
            .options(
                selectinload(PromptAssemblyConfigModel.feature_template),
                selectinload(PromptAssemblyConfigModel.subfeature_template),
                selectinload(PromptAssemblyConfigModel.persona),
            )
        )

        res = await self._execute(stmt)
        configs = res.scalars().all()

        latest_by_target: Dict[
            Tuple[str, Optional[str], Optional[str], str],
            PromptAssemblyConfigModel,
        ] = {}
        for config in configs:
            target = (config.feature, config.subfeature, config.plan, config.locale)
            previous = latest_by_target.get(target)
            if previous is None:
                latest_by_target[target] = config
                continue

            previous_published = previous.published_at or previous.created_at
            current_published = config.published_at or config.created_at
            if current_published >= previous_published:
                latest_by_target[target] = config

        results = []
        for config in latest_by_target.values():
            val_result = await self.validate_assembly(config)
            if not val_result.is_valid:
                results.append((config, val_result))

        return results
