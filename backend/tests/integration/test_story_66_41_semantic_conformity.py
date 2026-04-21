"""Story 66.41 — validation sémantique et sabotages ciblés."""

from __future__ import annotations

import ast
from pathlib import Path

from app.ops.llm.semantic_conformity_validator import (
    SemanticConformityValidator,
    validate_assemble_prompt_transform_order,
    validate_gateway_prompt_transform_order,
    validate_governed_taxonomy_and_providers,
    validate_snapshot_runtime_branching,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _async_fn_ast(src: str) -> ast.AsyncFunctionDef:
    mod = ast.parse(src)
    assert len(mod.body) == 1
    fn = mod.body[0]
    assert isinstance(fn, ast.AsyncFunctionDef)
    return fn


def test_semantic_validator_passes_on_repository_tree() -> None:
    v = SemanticConformityValidator(_repo_root())
    violations = v.validate_all()
    assert violations == [], [x.as_user_string() for x in violations]


def test_gateway_order_sabotage_detected() -> None:
    good = """
    # STORY 66.14 & 66.18: CANONICAL TRANSFORMATIONS ORDER
            current_prompt = config.developer_prompt
            if request.user_input.feature:
                (
                    current_prompt,
                    context_quality_injected,
                    context_quality_handled_by_template,
                ) = ContextQualityInjector.inject(
                    current_prompt, request.user_input.feature, cq_level
                )
            if verbosity_instruction:
                current_prompt = (
                    f"{current_prompt}\\n\\n[CONSIGNE DE VERBOSITÉ] {verbosity_instruction}"
                )
            rendered_developer_prompt = self.renderer.render(
                current_prompt,
                render_vars,
                required_variables=config.required_prompt_placeholders,
                feature=request.user_input.feature or "unknown",
            )
        interaction_mode = config.interaction_mode
    """
    bad = (
        good.replace(
            "ContextQualityInjector.inject",
            "ZZZ_INJECT",
        )
        .replace(
            "self.renderer.render",
            "ContextQualityInjector.inject",
        )
        .replace("ZZZ_INJECT", "self.renderer.render")
    )
    assert validate_gateway_prompt_transform_order(good) == []
    assert len(validate_gateway_prompt_transform_order(bad)) >= 1


def test_assemble_order_sabotage_detected() -> None:
    good = """
def assemble_developer_prompt(resolved, config):
    prompt = "x"
    if resolved.length_budget:
        prompt = LengthBudgetInjector.inject_into_developer_prompt(prompt, resolved.length_budget)
    prompt, injected, handled = ContextQualityInjector.inject(
        prompt, config.feature, context_quality
    )
    return prompt
"""
    bad = """
def assemble_developer_prompt(resolved, config):
    prompt = "x"
    prompt, injected, handled = ContextQualityInjector.inject(
        prompt, config.feature, context_quality
    )
    if resolved.length_budget:
        prompt = LengthBudgetInjector.inject_into_developer_prompt(prompt, resolved.length_budget)
    return prompt
"""
    assert validate_assemble_prompt_transform_order(good) == []
    assert len(validate_assemble_prompt_transform_order(bad)) >= 1


def test_snapshot_branching_ok_and_sabotages() -> None:
    ok = """
async def get_active_config(self, feature, subfeature, plan, locale):
    snapshot = await self._get_active_release_snapshot()
    if snapshot:
        manifest = snapshot.manifest
        _ = manifest.get("targets", {})
    else:
        stmt = select(PromptAssemblyConfigModel)
        _ = stmt
"""
    assert (
        validate_snapshot_runtime_branching(
            _async_fn_ast(ok),
            component="test.ok",
            live_model_id="PromptAssemblyConfigModel",
        )
        == []
    )

    live_before_if = """
async def get_active_config(self, feature, subfeature, plan, locale):
    early = select(PromptAssemblyConfigModel)
    _ = early
    snapshot = await self._get_active_release_snapshot()
    if snapshot:
        pass
    else:
        pass
"""
    v_early = validate_snapshot_runtime_branching(
        _async_fn_ast(live_before_if),
        component="test.early",
        live_model_id="PromptAssemblyConfigModel",
    )
    assert any(v.invariant_id == "INV-SNAPSHOT-LIVE-BEFORE-IF" for v in v_early)

    live_in_snapshot_branch = """
async def get_active_config(self, feature, subfeature, plan, locale):
    snapshot = await self._get_active_release_snapshot()
    if snapshot:
        bad = select(PromptAssemblyConfigModel)
        _ = bad
    else:
        pass
"""
    v_in = validate_snapshot_runtime_branching(
        _async_fn_ast(live_in_snapshot_branch),
        component="test.in_branch",
        live_model_id="PromptAssemblyConfigModel",
    )
    assert any(v.invariant_id == "INV-SNAPSHOT-LIVE-IN-SNAPSHOT-BRANCH" for v in v_in)

    else_without_select = """
async def get_active_config(self, feature, subfeature, plan, locale):
    snapshot = await self._get_active_release_snapshot()
    if snapshot:
        x = 1
    else:
        y = 2
"""
    v_else = validate_snapshot_runtime_branching(
        _async_fn_ast(else_without_select),
        component="test.else",
        live_model_id="PromptAssemblyConfigModel",
    )
    assert any(v.invariant_id == "INV-SNAPSHOT-ELSE-MISSING-LIVE" for v in v_else)


def test_governed_registry_matches_runtime() -> None:
    assert validate_governed_taxonomy_and_providers() == []


def test_semantic_invariants_version_format() -> None:
    from app.ops.llm.semantic_invariants_registry import SEMANTIC_INVARIANTS_VERSION

    parts = SEMANTIC_INVARIANTS_VERSION.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)
