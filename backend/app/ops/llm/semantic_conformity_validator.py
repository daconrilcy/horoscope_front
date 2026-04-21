"""
Validation sémantique doc ↔ code — Story 66.41.

Vérifie des invariants d'architecture bornés et machine-vérifiables sur le code réel
(sans analyse narrative de toute la doc).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from app.domain.llm.governance.feature_taxonomy import (
    LEGACY_DAILY_FEATURE,
    LEGACY_NATAL_FEATURE,
    NATAL_CANONICAL_FEATURE,
    SUPPORTED_FAMILIES,
)
from app.domain.llm.runtime.contracts import (
    ExecutionObservabilitySnapshot,
    FallbackType,
    ResolvedExecutionPlan,
)
from app.domain.llm.runtime.supported_providers import NOMINAL_SUPPORTED_PROVIDERS
from app.ops.llm.semantic_invariants_registry import (
    ASSEMBLE_DEVELOPER_PROMPT_TRANSFORM_ORDER,
    CRITICAL_EXECUTION_OBS_SNAPSHOT_FIELDS,
    CRITICAL_RESOLVED_EXECUTION_PLAN_FIELDS,
    GATEWAY_PROMPT_TRANSFORM_ORDER,
    GOVERNED_FALLBACK_TYPE_NAMES,
    GOVERNED_LEGACY_FEATURE_ALIASES_TO_CANONICAL,
    GOVERNED_NOMINAL_FAMILIES,
    GOVERNED_NOMINAL_PROVIDERS,
    OBSERVABILITY_LOG_SNAPSHOT_MARKERS,
    SEMANTIC_INVARIANTS_VERSION,
)


@dataclass(frozen=True)
class SemanticInvariantViolation:
    """Erreur structurée pour CI / review (AC7, AC11)."""

    code: str
    invariant_id: str
    component: str
    message: str
    detail: str | None = None

    def as_user_string(self) -> str:
        base = f"[semantic:{self.code}] {self.invariant_id} ({self.component}): {self.message}"
        if self.detail:
            return f"{base} | {self.detail}"
        return base


def _get_class_method_source(src: str, class_name: str, method_name: str) -> str | None:
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name == method_name:
                        seg = ast.get_source_segment(src, item)
                        return seg if seg is not None else None
    return None


def _get_function_source(src: str, func_name: str) -> str | None:
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            seg = ast.get_source_segment(src, node)
            return seg if seg is not None else None
    return None


def _get_class_method_ast(
    module: ast.Module, class_name: str, method_name: str
) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name == method_name:
                        return item
    return None


def _first_index(haystack: str, needle: str) -> int:
    idx = haystack.find(needle)
    if idx < 0:
        raise ValueError(f"marker not found: {needle!r}")
    return idx


def validate_gateway_prompt_transform_order(
    gateway_method_source: str,
) -> list[SemanticInvariantViolation]:
    """AC2 — ordre doctrinal dans la section canonique du gateway."""
    violations: list[SemanticInvariantViolation] = []
    marker = "# STORY 66.14 & 66.18: CANONICAL TRANSFORMATIONS ORDER"
    if marker not in gateway_method_source:
        violations.append(
            SemanticInvariantViolation(
                code="PROMPT_ORDER",
                invariant_id="INV-PROMPT-ORDER-GATEWAY",
                component="gateway.LLMGateway._resolve_plan",
                message="Marqueur canonique des transformations du prompt introuvable.",
                detail=f"Attendu: {marker!r}",
            )
        )
        return violations

    block = gateway_method_source.split(marker, maxsplit=1)[1]
    # Stop avant Stage suivant (messages) — heuristique stable
    for stop in ("\n        interaction_mode =", "\n        if request.overrides"):
        if stop in block:
            block = block.split(stop, maxsplit=1)[0]
            break

    try:
        pos_cq = _first_index(block, "ContextQualityInjector.inject")
        pos_verb = _first_index(block, "[CONSIGNE DE VERBOSITÉ]")
        pos_render = _first_index(block, "self.renderer.render")
    except ValueError as exc:
        violations.append(
            SemanticInvariantViolation(
                code="PROMPT_ORDER",
                invariant_id="INV-PROMPT-ORDER-GATEWAY",
                component="gateway.LLMGateway._resolve_plan",
                message="Impossible de localiser les étapes canoniques du pipeline.",
                detail=str(exc),
            )
        )
        return violations

    expected = list(GATEWAY_PROMPT_TRANSFORM_ORDER)
    actual_pairs = [
        ("context_quality_inject", pos_cq),
        ("verbosity_instruction", pos_verb),
        ("prompt_render", pos_render),
    ]
    actual = [k for k, _ in sorted(actual_pairs, key=lambda x: x[1])]
    if actual != expected:
        violations.append(
            SemanticInvariantViolation(
                code="PROMPT_ORDER",
                invariant_id="INV-PROMPT-ORDER-GATEWAY",
                component="gateway.LLMGateway._resolve_plan",
                message="Ordre effectif des transformations différent du registre sémantique.",
                detail=f"attendu={expected}, obtenu={actual}",
            )
        )
    return violations


def validate_assemble_prompt_transform_order(
    assemble_fn_source: str,
) -> list[SemanticInvariantViolation]:
    """AC2 — LengthBudget puis ContextQuality dans assemble_developer_prompt."""
    violations: list[SemanticInvariantViolation] = []
    if "LengthBudgetInjector" not in assemble_fn_source:
        violations.append(
            SemanticInvariantViolation(
                code="PROMPT_ORDER",
                invariant_id="INV-PROMPT-ORDER-ASSEMBLE",
                component="assembly_resolver.assemble_developer_prompt",
                message="LengthBudgetInjector introuvable dans la fonction.",
            )
        )
        return violations
    if "ContextQualityInjector" not in assemble_fn_source:
        violations.append(
            SemanticInvariantViolation(
                code="PROMPT_ORDER",
                invariant_id="INV-PROMPT-ORDER-ASSEMBLE",
                component="assembly_resolver.assemble_developer_prompt",
                message="ContextQualityInjector introuvable dans la fonction.",
            )
        )
        return violations

    pos_lb = _first_index(assemble_fn_source, "LengthBudgetInjector")
    pos_cq = _first_index(assemble_fn_source, "ContextQualityInjector.inject")
    order = sorted(
        [
            (ASSEMBLE_DEVELOPER_PROMPT_TRANSFORM_ORDER[0], pos_lb),
            (ASSEMBLE_DEVELOPER_PROMPT_TRANSFORM_ORDER[1], pos_cq),
        ],
        key=lambda x: x[1],
    )
    actual = [k for k, _ in order]
    if actual != list(ASSEMBLE_DEVELOPER_PROMPT_TRANSFORM_ORDER):
        violations.append(
            SemanticInvariantViolation(
                code="PROMPT_ORDER",
                invariant_id="INV-PROMPT-ORDER-ASSEMBLE",
                component="assembly_resolver.assemble_developer_prompt",
                message="Ordre length_budget -> context_quality non respecté.",
                detail=(
                    f"attendu={list(ASSEMBLE_DEVELOPER_PROMPT_TRANSFORM_ORDER)}, obtenu={actual}"
                ),
            )
        )
    return violations


def _contains_sqlalchemy_select_on_model(node: ast.AST, live_model_id: str) -> bool:
    """Détecte un appel `select(LiveModel)` (SQLAlchemy)."""
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "select":
            for arg in n.args:
                if isinstance(arg, ast.Name) and arg.id == live_model_id:
                    return True
    return False


def _is_if_snapshot(test: ast.AST) -> bool:
    return isinstance(test, ast.Name) and test.id == "snapshot"


def _find_first_snapshot_if(
    body: list[ast.stmt],
) -> tuple[int, ast.If] | None:
    for i, stmt in enumerate(body):
        if isinstance(stmt, ast.If) and _is_if_snapshot(stmt.test):
            return i, stmt
    return None


def validate_snapshot_runtime_branching(
    func_ast: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    component: str,
    live_model_id: str,
) -> list[SemanticInvariantViolation]:
    """
    AC3 — priorité snapshot : aucune requête table live avant ni dans la branche `if snapshot:`.

    Le fallback ORM ne doit apparaître que sous le `else` associé.
    """
    violations: list[SemanticInvariantViolation] = []
    found = _find_first_snapshot_if(func_ast.body)
    if found is None:
        violations.append(
            SemanticInvariantViolation(
                code="RUNTIME_TRUTH",
                invariant_id="INV-SNAPSHOT-FIRST",
                component=component,
                message="Branche 'if snapshot:' introuvable au niveau racine de la fonction.",
            )
        )
        return violations

    idx_if, if_node = found

    for stmt in func_ast.body[:idx_if]:
        if _contains_sqlalchemy_select_on_model(stmt, live_model_id):
            violations.append(
                SemanticInvariantViolation(
                    code="RUNTIME_TRUTH",
                    invariant_id="INV-SNAPSHOT-LIVE-BEFORE-IF",
                    component=component,
                    message="Requête table live détectée avant la branche `if snapshot:`.",
                    detail=f"model={live_model_id!r}",
                )
            )

    for stmt in if_node.body:
        if _contains_sqlalchemy_select_on_model(stmt, live_model_id):
            violations.append(
                SemanticInvariantViolation(
                    code="RUNTIME_TRUTH",
                    invariant_id="INV-SNAPSHOT-LIVE-IN-SNAPSHOT-BRANCH",
                    component=component,
                    message=(
                        "Requête table live dans la branche `if snapshot:` (ambiguïté / inversion)."
                    ),
                    detail=f"model={live_model_id!r}",
                )
            )

    if not if_node.orelse:
        violations.append(
            SemanticInvariantViolation(
                code="RUNTIME_TRUTH",
                invariant_id="INV-SNAPSHOT-NO-ELSE",
                component=component,
                message="Branche `else` absente : pas de fallback tables live explicite.",
            )
        )
        return violations

    has_else_live = False
    for st in if_node.orelse:
        if _contains_sqlalchemy_select_on_model(st, live_model_id):
            has_else_live = True
            break
    if not has_else_live:
        violations.append(
            SemanticInvariantViolation(
                code="RUNTIME_TRUTH",
                invariant_id="INV-SNAPSHOT-ELSE-MISSING-LIVE",
                component=component,
                message="Le `else` ne contient pas de `select` sur le modèle ORM attendu.",
                detail=f"model={live_model_id!r}",
            )
        )

    return violations


def validate_governed_taxonomy_and_providers() -> list[SemanticInvariantViolation]:
    """AC4 — égalité stricte registre sémantique ↔ modules runtime."""
    violations: list[SemanticInvariantViolation] = []

    if frozenset(SUPPORTED_FAMILIES) != GOVERNED_NOMINAL_FAMILIES:
        violations.append(
            SemanticInvariantViolation(
                code="GOVERNANCE",
                invariant_id="INV-FAMILIES-REGISTRY-MISMATCH",
                component="feature_taxonomy.SUPPORTED_FAMILIES",
                message="SUPPORTED_FAMILIES ne correspond pas à GOVERNED_NOMINAL_FAMILIES.",
                detail=(
                    f"registry={sorted(GOVERNED_NOMINAL_FAMILIES)!r} "
                    f"code={sorted(SUPPORTED_FAMILIES)!r}"
                ),
            )
        )

    code_providers = frozenset(NOMINAL_SUPPORTED_PROVIDERS)
    if code_providers != GOVERNED_NOMINAL_PROVIDERS:
        violations.append(
            SemanticInvariantViolation(
                code="GOVERNANCE",
                invariant_id="INV-PROVIDERS-REGISTRY-MISMATCH",
                component="supported_providers.NOMINAL_SUPPORTED_PROVIDERS",
                message=(
                    "NOMINAL_SUPPORTED_PROVIDERS ne correspond pas à GOVERNED_NOMINAL_PROVIDERS."
                ),
                detail=(
                    f"registry={sorted(GOVERNED_NOMINAL_PROVIDERS)!r} "
                    f"code={sorted(code_providers)!r}"
                ),
            )
        )

    code_aliases = {
        LEGACY_NATAL_FEATURE: NATAL_CANONICAL_FEATURE,
        LEGACY_DAILY_FEATURE: "horoscope_daily",
    }
    if code_aliases != GOVERNED_LEGACY_FEATURE_ALIASES_TO_CANONICAL:
        violations.append(
            SemanticInvariantViolation(
                code="GOVERNANCE",
                invariant_id="INV-LEGACY-ALIASES-MISMATCH",
                component="feature_taxonomy.normalize_feature",
                message="Les aliases legacy→canonique ne correspondent pas au registre sémantique.",
                detail=(
                    f"registry={GOVERNED_LEGACY_FEATURE_ALIASES_TO_CANONICAL!r} "
                    f"code={code_aliases!r}"
                ),
            )
        )

    enum_names = frozenset(FallbackType.__members__.keys())
    if enum_names != GOVERNED_FALLBACK_TYPE_NAMES:
        violations.append(
            SemanticInvariantViolation(
                code="GOVERNANCE",
                invariant_id="INV-FALLBACK-ENUM-MISMATCH",
                component="models.FallbackType",
                message="FallbackType ne correspond pas à GOVERNED_FALLBACK_TYPE_NAMES.",
                detail=(
                    f"registry={sorted(GOVERNED_FALLBACK_TYPE_NAMES)!r} code={sorted(enum_names)!r}"
                ),
            )
        )

    return violations


def validate_critical_model_fields() -> list[SemanticInvariantViolation]:
    """AC5 — discriminants présents sur les modèles pydantic."""
    violations: list[SemanticInvariantViolation] = []
    plan_fields = set(ResolvedExecutionPlan.model_fields.keys())
    missing_plan = sorted(CRITICAL_RESOLVED_EXECUTION_PLAN_FIELDS - plan_fields)
    if missing_plan:
        violations.append(
            SemanticInvariantViolation(
                code="PROPAGATION",
                invariant_id="INV-PLAN-FIELDS",
                component="models.ResolvedExecutionPlan",
                message="Champs critiques absents du modèle.",
                detail=f"missing={missing_plan}",
            )
        )

    obs_fields = set(ExecutionObservabilitySnapshot.model_fields.keys())
    missing_obs = sorted(CRITICAL_EXECUTION_OBS_SNAPSHOT_FIELDS - obs_fields)
    if missing_obs:
        violations.append(
            SemanticInvariantViolation(
                code="PROPAGATION",
                invariant_id="INV-OBS-FIELDS",
                component="models.ExecutionObservabilitySnapshot",
                message="Champs critiques absents du modèle.",
                detail=f"missing={missing_obs}",
            )
        )
    return violations


def validate_observability_log_snapshot_markers(
    observability_source: str,
) -> list[SemanticInvariantViolation]:
    """AC5 — persistance des identifiants snapshot dans log_call."""
    violations: list[SemanticInvariantViolation] = []
    for m in OBSERVABILITY_LOG_SNAPSHOT_MARKERS:
        if m not in observability_source:
            violations.append(
                SemanticInvariantViolation(
                    code="PROPAGATION",
                    invariant_id="INV-LOG-SNAPSHOT",
                    component="observability_service.log_call",
                    message=f"Marqueur de persistance {m!r} introuvable.",
                )
            )
    return violations


class SemanticConformityValidator:
    """Point d'entrée unique pour la suite sémantique (AC8)."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self._domain_llm = root_path / "backend" / "app" / "domain" / "llm"

    def validate_all(self) -> list[SemanticInvariantViolation]:
        violations: list[SemanticInvariantViolation] = []

        gw_path = self._domain_llm / "runtime" / "gateway.py"
        ar_path = self._domain_llm / "configuration" / "assembly_resolver.py"
        asm_reg_path = self._domain_llm / "configuration" / "assembly_registry.py"
        ex_reg_path = self._domain_llm / "configuration" / "execution_profile_registry.py"
        obs_path = self._domain_llm / "runtime" / "observability_service.py"

        gw_src = gw_path.read_text(encoding="utf-8")
        ar_src = ar_path.read_text(encoding="utf-8")
        asm_reg_src = asm_reg_path.read_text(encoding="utf-8")
        ex_reg_src = ex_reg_path.read_text(encoding="utf-8")
        obs_src = obs_path.read_text(encoding="utf-8")

        resolve_plan = _get_class_method_source(gw_src, "LLMGateway", "_resolve_plan")
        if not resolve_plan:
            violations.append(
                SemanticInvariantViolation(
                    code="INTERNAL",
                    invariant_id="INV-PARSE",
                    component="gateway.LLMGateway._resolve_plan",
                    message="Méthode introuvable pour analyse AST.",
                )
            )
        else:
            violations.extend(validate_gateway_prompt_transform_order(resolve_plan))

        assemble_fn = _get_function_source(ar_src, "assemble_developer_prompt")
        if not assemble_fn:
            violations.append(
                SemanticInvariantViolation(
                    code="INTERNAL",
                    invariant_id="INV-PARSE",
                    component="assembly_resolver.assemble_developer_prompt",
                    message="Fonction introuvable pour analyse AST.",
                )
            )
        else:
            violations.extend(validate_assemble_prompt_transform_order(assemble_fn))

        asm_mod = ast.parse(asm_reg_src)
        asm_async_ast = _get_class_method_ast(asm_mod, "AssemblyRegistry", "get_active_config")
        if asm_async_ast:
            violations.extend(
                validate_snapshot_runtime_branching(
                    asm_async_ast,
                    component="AssemblyRegistry.get_active_config",
                    live_model_id="PromptAssemblyConfigModel",
                )
            )

        asm_sync_ast = _get_class_method_ast(asm_mod, "AssemblyRegistry", "get_active_config_sync")
        if asm_sync_ast:
            violations.extend(
                validate_snapshot_runtime_branching(
                    asm_sync_ast,
                    component="AssemblyRegistry.get_active_config_sync",
                    live_model_id="PromptAssemblyConfigModel",
                )
            )

        ex_mod = ast.parse(ex_reg_src)
        ex_prof_ast = _get_class_method_ast(
            ex_mod, "ExecutionProfileRegistry", "get_active_profile"
        )
        if ex_prof_ast:
            violations.extend(
                validate_snapshot_runtime_branching(
                    ex_prof_ast,
                    component="ExecutionProfileRegistry.get_active_profile",
                    live_model_id="LlmExecutionProfileModel",
                )
            )

        log_fn = _get_function_source(obs_src, "log_call")
        if log_fn:
            violations.extend(validate_observability_log_snapshot_markers(log_fn))
        else:
            violations.append(
                SemanticInvariantViolation(
                    code="INTERNAL",
                    invariant_id="INV-PARSE",
                    component="observability_service.log_call",
                    message="Fonction log_call introuvable.",
                )
            )

        violations.extend(validate_governed_taxonomy_and_providers())
        violations.extend(validate_critical_model_fields())
        return violations


def semantic_violations_version() -> str:
    return SEMANTIC_INVARIANTS_VERSION
