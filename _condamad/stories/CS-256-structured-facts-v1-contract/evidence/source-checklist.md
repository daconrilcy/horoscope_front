<!-- Commentaire global: cette checklist prouve les sources consultees avant de figer le contrat structured_facts_v1. -->

# Source checklist CS-256

## Sources obligatoires consultees

- PASS: `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md` aligne l'objectif stable, hashable, non narratif.
- PASS: `_condamad/stories/story-status.md` contient la ligne `CS-256` avec le chemin story et le brief source attendus.
- PASS: `docs/architecture/official-product-primitives-public-projections.md` contient deja le primitif produit `structured_facts`.
- PASS: `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/00-story.md` definit l'amont/aval IA et interdit que prompt ou LLM output deviennent source de verite.
- PASS: `_condamad/stories/CS-255-product-architecture-current-state/00-story.md` preserve la direction `calcul -> faits -> signaux -> narration/projection`.
- PASS: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` possede `AINarrativeInputContract`.
- PASS: `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` adapte l'input interpretatif existant vers `AINarrativeInputContract`.
- PASS: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` possede `ChartObjectRuntimeData`.
- PASS: `backend/app/domain/astrology/natal_calculation.py` contient `chart_objects` comme surface runtime interne exclue du contrat public.

## Conclusion

Le contrat ajoute par CS-256 est documentation-only. Les proprietaires runtime, AI input, API, frontend, DB et migrations restent inchanges.
