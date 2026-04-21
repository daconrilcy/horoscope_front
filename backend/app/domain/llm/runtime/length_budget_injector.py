from __future__ import annotations

from app.domain.llm.configuration.admin_models import LengthBudget


class LengthBudgetInjector:
    """
    Injects length constraints into the developer prompt (Story 66.12 D3).
    """

    @staticmethod
    def resolve_length_instruction(budget: LengthBudget) -> str:
        """Translates budget into an explicit textual instruction."""
        parts = []
        if budget.target_response_length:
            parts.append(f"Cible : {budget.target_response_length}.")

        for section in budget.section_budgets:
            parts.append(f"Section '{section.section_name}' : {section.target}.")

        if not parts:
            return ""

        return f"\n\n[CONSIGNE DE LONGUEUR] {' '.join(parts)}"

    @staticmethod
    def inject_into_developer_prompt(developer_prompt: str, budget: LengthBudget) -> str:
        """Injects length instruction at the end of the prompt."""
        instruction = LengthBudgetInjector.resolve_length_instruction(budget)
        if not instruction:
            return developer_prompt

        return f"{developer_prompt}{instruction}"
