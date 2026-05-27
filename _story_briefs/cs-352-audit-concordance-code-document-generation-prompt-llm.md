# CS-352 - Audit Concordance Code Document Generation Prompt LLM

<!-- Commentaire global: ce brief cadre l'audit de concordance entre le document final et le code executable de generation des prompts LLM. -->

## Resume

Verifier que la cartographie documentaire de `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` correspond au code executable actuel.

Cette story se concentre sur la concordance source-document: elle prouve ou invalide les chemins, owners, symboles et frontieres cites par le document final.

## Contexte

CS-351 challenge le document comme artefact editorial et factuel. CS-352 descend au niveau code pour verifier que les descriptions du flux nominal, des fallbacks et des exclusions prompt-visible sont encore exactes dans `backend/app/**` et `backend/tests/**`.

## Objectif

Produire une preuve source-alignee que le document final decrit correctement:

- la selection de use case et de contrat canonique;
- la resolution d'assembly;
- le rendu des placeholders;
- la construction de `llm_astrology_input_v1`;
- le filtrage prompt-visible;
- la composition `structured` et `chat`;
- le handoff provider;
- la validation, le repair, le fallback, la persistence et l'observability.

## Perimetre inclus

1. Tracer le flux nominal depuis les services applicatifs jusqu'au provider handoff.
2. Verifier les fonctions et classes citees dans le document.
3. Verifier les exclusions `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, `chart_json` et `natal_data`.
4. Verifier les tests qui protegent la frontiere prompt-visible/backend-only.
5. Relever tout symbole cite par le document mais absent, renomme ou non responsable.
6. Relever tout symbole important present dans le code mais absent du document.

## Hors perimetre

- Modifier le code.
- Modifier le document.
- Auditer les prompts metier ligne par ligne.
- Faire un appel LLM reel.
- Decider l'owner final des output schemas.

## Sources obligatoires

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`
- `backend/tests/integration/test_llm_legacy_extinction.py`

## Livrable attendu

Creer:

```text
_condamad/audits/prompt-generation-document-review/<YYYY-MM-DD-HHMM>/02-code-document-concordance-audit.md
```

Le document doit contenir:

1. Resume executif.
2. Trace code du flux nominal.
3. Matrice document section -> code source -> statut.
4. Matrice symbole cite -> presence -> responsabilite reelle.
5. Matrice des exclusions prompt-visible/backend-only.
6. Tests et guardrails confirmes ou insuffisants.
7. Gaps de concordance.
8. Corrections documentaires candidates.

## Criteres d'acceptation

1. Les chemins de code cites existent et sont lies a une responsabilite precise.
2. Les fonctions majeures du gateway et du renderer sont verifiees.
3. Les exclusions legacy et audit-only sont controlees par scan ou test existant.
4. Les surfaces non-natales decouvertes sont notees sans etre forcees dans le flux natal moderne.
5. Le rapport distingue absence documentaire, erreur documentaire et risque de test coverage.

## Validation attendue

```powershell
rg -n "def execute_request|def _resolve_plan|def _build_messages|def _call_provider|def compose_chat_messages|def compose_structured_messages" backend/app/domain/llm/runtime/gateway.py
rg -n "llm_astrology_input_v1|chart_json|natal_data|evidence|provenance|prompt_visible" backend/app backend/tests
rg -n "code-document-concordance-audit|section -> code|symbole cite" _condamad/audits/prompt-generation-document-review
```

## Risques

Le risque principal est de confondre presence d'un symbole avec responsabilite effective. L'audit doit lire le contexte autour des fonctions et ne pas conclure sur un simple `rg`.
