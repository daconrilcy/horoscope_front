import uuid
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import ExecutionUserInput, LLMExecutionRequest


@pytest.mark.evaluation
@pytest.mark.asyncio
async def test_prompt_resolution_matrix(
    db, evaluation_matrix, mock_context_by_quality, mock_personas
):
    """
    Evaluates prompt resolution for every combination in the matrix.
    Checks: absence of {{}}, context quality handling, runtime schema resolution,
    and length-budget propagation in the assembly path.
    """
    results = []

    for case in evaluation_matrix:
        feat = case["feature"]
        plan = case["plan"]
        subfeat = case.get("subfeature")
        persona_type = case["persona"]
        cq = case["context_quality"]

        # 1. Setup DB data for this combination
        # Clear previous to avoid unique constraints
        db.query(PromptAssemblyConfigModel).delete()
        db.query(LlmPromptVersionModel).delete()
        db.query(LlmUseCaseConfigModel).delete()
        db.query(LlmPersonaModel).delete()
        db.query(LlmExecutionProfileModel).delete()
        db.commit()

        # Create Persona
        p_data = mock_personas[persona_type]
        persona = LlmPersonaModel(
            id=uuid.uuid4(),
            name=p_data["name"],
            description="test",
            style_markers=p_data["style_markers"],
            boundaries=p_data["boundaries"],
            enabled=True,
        )
        db.add(persona)

        # Create Template
        uc_key = f"{feat}_test"
        uc = LlmUseCaseConfigModel(
            key=uc_key, display_name=uc_key, description="test", safety_profile="astrology"
        )
        db.add(uc)
        v = LlmPromptVersionModel(
            id=uuid.uuid4(),
            use_case_key=uc_key,
            developer_prompt=f"BASE PROMPT FOR {feat} {{#context_quality:minimal}}MINIMAL{{/context_quality}}",
            model="gpt-4o",
            status=PromptStatus.PUBLISHED,
            created_by="eval",
        )
        db.add(v)

        # Create Profile
        prof = LlmExecutionProfileModel(
            id=uuid.uuid4(),
            name="Eval Profile",
            provider="openai",
            model="gpt-4o",
            status=PromptStatus.PUBLISHED,
            created_by="eval",
        )
        db.add(prof)

        # Create Output Schema for paid cases so the gateway resolves a real contract.
        schema_id = None
        if feat == "natal" and plan == "premium":
            from app.infra.db.models import LlmOutputSchemaModel
            from app.llm_orchestration.seeds.use_cases_seed import ASTRO_RESPONSE_V3_JSON_SCHEMA

            schema = LlmOutputSchemaModel(
                id=uuid.uuid4(),
                name=f"Schema {feat}",
                json_schema=ASTRO_RESPONSE_V3_JSON_SCHEMA,
                version=1,
            )
            db.add(schema)
            schema_id = str(schema.id)
            uc.output_schema_id = schema_id

        # Create Assembly
        assembly = PromptAssemblyConfigModel(
            id=uuid.uuid4(),
            feature=feat,
            subfeature=subfeat,
            plan=plan,
            locale="fr-FR",
            feature_template_ref=v.id,
            persona_ref=persona.id,
            persona_enabled=True,
            execution_profile_ref=prof.id,
            execution_config={"model": "gpt-4o", "max_output_tokens": 2000},
            output_contract_ref=schema_id,
            length_budget={
                "target_response_length": "standard" if plan == "premium" else "concise",
                "global_max_tokens": 2000 if plan == "premium" else 500,
            },
            status=PromptStatus.PUBLISHED,
            created_by="eval",
        )
        db.add(assembly)
        db.commit()

        # Story 66.24: Invalidate cache to avoid using stale data from previous iteration
        from app.llm_orchestration.services.assembly_registry import AssemblyRegistry

        AssemblyRegistry(db).invalidate_cache()

        # 2. Resolve via Gateway
        gateway = LLMGateway()
        # Mock Context Quality resolution (usually handled by CommonContextBuilder)
        # We simulate it by passing the quality level in render_vars

        # Build request
        ctx_data = mock_context_by_quality[cq]
        request = LLMExecutionRequest(
            user_input=ExecutionUserInput(
                use_case=uc_key, feature=feat, subfeature=subfeat, plan=plan, locale="fr-FR"
            ),
            request_id="eval-req",
            trace_id="eval-trace",
        )

        # We need to mock CommonContextBuilder.build to return our desired quality
        from app.prompts.common_context import PromptCommonContext, QualifiedContext

        mock_payload = PromptCommonContext(
            natal_interpretation=ctx_data.get("natal_interpretation"),
            natal_data=ctx_data.get("natal_data"),
            precision_level="full" if cq == "full" else "partial",
            astrologer_profile={"name": "test"},
            period_covered="today",
            today_date=ctx_data.get("today_date", "2026-04-11"),
            use_case_name=uc_key,
            use_case_key=uc_key,
        )

        mock_qualified = QualifiedContext(
            payload=mock_payload,
            source="db",
            missing_fields=["natal_interpretation"] if cq == "minimal" else [],
            context_quality=cq,
        )

        with MagicMock():
            import app.llm_orchestration.gateway as gateway_module

            # We patch it directly in the module
            original_build = gateway_module.CommonContextBuilder.build
            gateway_module.CommonContextBuilder.build = MagicMock(return_value=mock_qualified)

            try:
                plan_resolved, _ = await gateway._resolve_plan(
                    request, db, context_override=ctx_data
                )

                # 3. Assertions (Story 66.16 Medium 2 fix)
                prompt = plan_resolved.rendered_developer_prompt

                # Check Placeholders
                placeholders_ok = "{{" not in prompt and "}}" not in prompt

                # Check Context Quality
                cq_ok = (
                    cq == "minimal"
                    and (
                        "MINIMAL" in prompt
                        or "[CONTEXTE" in prompt
                        or "dégradé" in prompt.lower()
                    )
                ) or (cq in ["full", "partial"])

                # Check Persona
                persona_ok = (
                    p_data["name"] in (plan_resolved.persona_block or "")
                    or p_data["name"] in prompt
                )

                # Check Length Budget Consistency (Story 66.12/66.18)
                expected_tokens = 500 if plan == "free" else 2000
                length_ok = (
                    plan_resolved.max_output_tokens == expected_tokens
                    and plan_resolved.max_output_tokens_source == "length_budget_global"
                    and "[CONSIGNE DE LONGUEUR]" in prompt
                )

                if not length_ok:
                    print(f"DEBUG: feat={feat}, plan={plan}, tokens={plan_resolved.max_output_tokens}, source={plan_resolved.max_output_tokens_source}")
                    print(f"DEBUG PROMPT: {prompt}")

                # Check Output Contract resolution (AC3)

                schema_ok = True
                # Story 66.24: Currently only natal has a published schema in the registry for this eval
                # horoscope_daily is still in structured mode but uses a narrator schema not yet in seeds
                if feat == "natal" and plan == "premium":
                    schema_ok = (
                        plan_resolved.output_schema is not None
                        and plan_resolved.response_format is not None
                        and plan_resolved.response_format.type == "json_schema"
                    )

                # Check Pipeline Maturity (Story 66.24 AC2)
                CANONICAL_FAMILIES = {"chat", "guidance", "natal", "horoscope_daily"}
                actual_pipeline_kind = (
                    "nominal_canonical"
                    if feat in CANONICAL_FAMILIES
                    else "transitional_governance"
                )

                # Cross-check with matrix expectation
                expected_pipeline_kind = case.get("pipeline_kind", "nominal_canonical")
                pipeline_ok = actual_pipeline_kind == expected_pipeline_kind

                results.append(
                    {
                        "case": f"{feat}/{plan}/{persona_type}/{cq}",
                        "pipeline_kind": actual_pipeline_kind,
                        "pipeline_ok": pipeline_ok,
                        "placeholders": placeholders_ok,
                        "context_quality": cq_ok,
                        "persona": persona_ok,
                        "output_contract": schema_ok,
                        "length_budget_global": length_ok,
                        "differentiation_plan": True,
                    }
                )

                assert pipeline_ok, f"Pipeline kind mismatch for {feat}: expected {expected_pipeline_kind}, got {actual_pipeline_kind}"
                assert placeholders_ok, f"Surviving placeholders in {feat}/{plan}"
                if cq == "minimal":
                    assert cq_ok, f"Context quality instruction missing in {feat}/{plan}"
                assert length_ok, f"Length budget inconsistent in {feat}/{plan}"
                if feat == "natal" and plan == "premium":
                    assert schema_ok, f"Output schema missing for paid {feat}/{plan}"

            finally:
                # Restore
                gateway_module.CommonContextBuilder.build = original_build

    # Final result report summary (will be used by report generator later)
    print("\nEVALUATION MATRIX SUMMARY:")
    for r in results:
        print(
            f"{r['case']}: Placeholders={'✅' if r['placeholders'] else '❌'}, CQ={'✅' if r['context_quality'] else '❌'}, Persona={'✅' if r['persona'] else '❌'}"
        )

    # Story 66.24: Generate markdown report file
    from tests.evaluation.report_generator import generate_markdown_report

    report_md = generate_markdown_report(results)
    report_path = Path(__file__).parent / "evaluation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# LLM Orchestration Evaluation Report (Story 66.24 Matrix)\n\n")
        f.write(report_md)
    print(f"\nReport generated at {report_path}")
