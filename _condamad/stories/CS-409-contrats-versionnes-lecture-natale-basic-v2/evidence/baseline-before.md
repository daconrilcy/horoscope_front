# Baseline avant implementation CS-409

<!-- Commentaire global: preuve initiale des surfaces avant ajout des contrats Basic V2. -->

- Story: `CS-409-contrats-versionnes-lecture-natale-basic-v2`
- Date: `2026-05-31`
- Statut initial tracker: `ready-to-dev`
- Capsule generated: prepare + validate `PASS`
- Owner canonique absent avant implementation: aucun symbole `BasicNatalInterpretationV2`,
  `EligibilityContext`, `NatalFactGraph`, `NatalSalienceModel`,
  `NatalNarrativeThemeModel`, `NatalSynthesis` ou `BasicNatalReadingPlan` trouve dans
  `backend/app` et `backend/tests`.
- Surface publique existante inspectee:
  `backend/app/services/api_contracts/public/natal_interpretation.py` expose
  `narrative_natal_reading_v1` sans champ Basic V2.
- Guardrails applicables resolus: `RG-149`, `RG-150`, `RG-152`, `RG-154`, `RG-155`,
  `RG-156`.
- Changements preexistants non lies observes dans `git status`: `_condamad/run-state.json`,
  `_condamad/stories/regression-guardrails.md`, `backend/app/main.py`,
  `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`,
  `backend/tests/unit/test_canonical_llm_bootstrap.py`,
  `backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py`.
