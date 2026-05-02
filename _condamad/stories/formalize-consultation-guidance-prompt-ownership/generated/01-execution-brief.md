# Execution Brief - formalize-consultation-guidance-prompt-ownership

## Primary objective

Formaliser les consultations specifiques comme sous-cas canonique de `guidance_contextual` et prouver qu'aucune famille LLM `consultation` concurrente n'est introduite.

## Boundaries

- Toucher uniquement la documentation prompt, les tests backend de guidance/consultation/gouvernance et les artefacts CONDAMAD.
- Ne pas modifier les endpoints consultation, le wizard frontend, les contrats HTTP ou les migrations.
- Ne pas creer de prompt owner dans `consultation_generation_service.py`.

## Done conditions

- AC1: documentation `docs/llm-prompt-generation-by-feature.md` mentionne explicitement l'ownership `guidance_contextual`.
- AC2: test executable du contrat placeholders `situation`, `objective`, `natal_chart_summary`.
- AC3: test executable prouvant qu'un refus precheck n'appelle pas `GuidanceService`.
- AC4: garde de gouvernance bloquant une famille/use case `consultation`.
- Validations ciblees, Ruff, suite backend et preuves finales completees.

## Halt conditions

- Une decision produit impose une famille LLM `consultation`.
- Un test revele un appel LLM apres refus precheck sans correction sure.
- La validation backend complete echoue sur une regression liee a cette story.
