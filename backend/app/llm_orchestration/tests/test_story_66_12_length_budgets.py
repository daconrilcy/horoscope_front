import pytest
import uuid
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus
from app.infra.db.models import LlmUseCaseConfigModel
from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import LLMExecutionRequest, ExecutionUserInput
from app.llm_orchestration.services.assembly_resolver import build_assembly_preview

@pytest.fixture
def setup_budget_assembly(db):
    fv = LlmPromptVersionModel(
        id=uuid.uuid4(), use_case_key="chat", developer_prompt="BASE PROMPT",
        status=PromptStatus.PUBLISHED, model="gpt-4o", created_by="test"
    )
    db.add(fv)
    
    budget = {
        "target_response_length": "concise",
        "section_budgets": [
            {"section_name": "summary", "target": "2 sentences"},
            {"section_name": "advice", "target": "1 sentence"}
        ],
        "global_max_tokens": 500
    }
    
    assembly = PromptAssemblyConfigModel(
        id=uuid.uuid4(),
        feature="test_budget",
        plan="standard",
        locale="fr-FR",
        feature_template_ref=fv.id,
        length_budget=budget,
        execution_config={"model": "gpt-4o", "max_output_tokens": 2000},
        status=PromptStatus.PUBLISHED,
        created_by="test"
    )
    db.add(assembly)
    db.commit()
    return assembly

@pytest.mark.asyncio
async def test_length_budget_injection(db, setup_budget_assembly):
    """Test Story 66.12: Length budget is injected into developer prompt."""
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat", feature="test_budget", plan="standard"),
        request_id="req-budget", trace_id="tr-budget"
    )
    
    # 2. Resolve plan
    plan, _ = await gateway._resolve_plan(request, db)
    
    # 3. Assertions
    # Textual injection
    assert "[CONSIGNE DE LONGUEUR]" in plan.rendered_developer_prompt
    assert "Cible : concise" in plan.rendered_developer_prompt
    assert "Section 'summary' : 2 sentences" in plan.rendered_developer_prompt
    
    # Global max tokens override
    assert plan.max_output_tokens == 500

@pytest.mark.asyncio
async def test_assembly_preview_includes_budget(db, setup_budget_assembly):
    """Test Story 66.12: Assembly preview includes length budget info."""
    preview = build_assembly_preview(setup_budget_assembly)
    
    assert preview.length_budget is not None
    assert preview.length_budget.target_response_length == "concise"
    assert len(preview.length_budget.section_budgets) == 2
