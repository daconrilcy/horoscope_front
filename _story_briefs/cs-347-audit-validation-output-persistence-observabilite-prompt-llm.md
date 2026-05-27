# CS-347 - Audit Validation Output Persistence Observabilite Prompt LLM

<!-- Commentaire global: ce brief cadre l'audit des controles apres generation et des traces persistantes liees aux prompts LLM. -->

## Resume

Auditer ce qui se passe apres le handoff provider: validation de sortie, rejet narratif, persistence d'audit, usage tokens, observability et replay.

## Contexte

Une cartographie de prompt est incomplete si elle s'arrete au message provider. Le systeme conserve aussi prompt version, input hash, projection hash, evidence refs, validation status et traces d'execution.

## Objectif

Documenter comment la reponse LLM est:

- validee contre un schema;
- normalisee ou reparee;
- rejetee si non groundee;
- persistee avec les ancres prompt/input/audit;
- tracee dans l'observability;
- exploitable pour replay ou audit admin.

## Perimetre inclus

1. Auditer output validation runtime.
2. Auditer rejected narrative answer workflow.
3. Auditer persistence natal interpretation.
4. Auditer `llm_call_logs`, replay snapshots et metadata gateway si applicables.
5. Auditer les services admin audit/replay/observability.
6. Auditer tests integration audit et workflows de rejet.
7. Produire une matrice prompt -> output -> audit.

## Hors perimetre

- Modifier les schemas de sortie.
- Ajouter replay ou admin UI.
- Faire des appels provider reels.
- Corriger les gaps de validation identifies.

## Sources a lire

- `_story_briefs/cs-288-implement-narrative-answer-audit-v1-persistence.md`
- `_story_briefs/cs-289-implement-evidence-refs-validation.md`
- `_story_briefs/cs-290-implement-rejected-narrative-answer-workflow.md`
- `_story_briefs/cs-298-implement-replay-snapshot-v1-execution-audit.md`
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`
- `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md`

## Fichiers a inspecter en priorite

- `backend/app/domain/llm/runtime/output_validator.py`
- `backend/app/domain/llm/runtime/repair.py`
- `backend/app/domain/llm/runtime/observability.py`
- `backend/app/domain/llm/runtime/observability_service.py`
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/infra/db/models/user_natal_interpretation.py`
- `backend/app/infra/db/models/llm/**`
- `backend/app/services/api_contracts/admin/audit.py`
- `backend/tests/unit/test_rejected_narrative_answer_workflow.py`
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`

## Livrable attendu

Creer:

```text
_condamad/audits/prompt-generation-cartography/<YYYY-MM-DD-HHMM>/05-output-validation-persistence-audit.md
```

Le document doit contenir:

1. Pipeline post-provider.
2. Schemas de sortie par use case.
3. Statuts validation/recovery/rejection.
4. Champs persistants prompt/input/audit.
5. Relations avec evidence refs.
6. Observability et replay.
7. Tests et gaps.

## Criteres d'acceptation

1. Les statuts de validation et rejet sont expliques.
2. Les champs `prompt_version`, `prompt_ref`, `projection_hash`, `llm_input_hash`, `evidence_refs`, `grounding_status` sont traces.
3. Les chemins de persistence ne sont pas confondus avec le prompt provider.
4. Les limites de validation semantique sont explicites.
5. Les risques residuels alimentent CS-348 et CS-350.

## Validation attendue

```powershell
rg -n "validate_output|RejectedNarrativeAnswer|grounding_status|evidence_refs|prompt_version|llm_input_hash|projection_hash|llm_call_logs|replay" backend/app backend/tests
rg -n "output-validation-persistence-audit" _condamad
```

## Risques

Le risque principal est de decrire l'audit persistant comme une preuve que le prompt etait correct. Le livrable doit separer validation runtime, audit apres coup et preuve de handoff.

