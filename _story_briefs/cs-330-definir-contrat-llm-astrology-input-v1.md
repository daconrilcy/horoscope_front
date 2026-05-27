# CS-330 - Definir Le Contrat llm_astrology_input_v1

<!-- Commentaire global: ce brief cadre le contrat cible des donnees astrologiques et interpretatives injectees au generateur de prompt LLM natal. -->

## Resume

Definir le contrat interne `llm_astrology_input_v1`, dedie a l'injection LLM, afin que le generateur de prompt recoive une entree riche, structuree et explicite au lieu de dependre de `chart_json`.

Le contrat doit s'appuyer sur `AINarrativeInputContract` comme owner narratif interne et sur `structured_facts_v1` comme source factuelle stable. Il doit separer clairement les faits calcules, les signaux interpretatifs, les limites, les preuves, le shaping editorial et la provenance.

## Contexte

Le rapport de transition indique que le chemin natal audite expose surtout `chart_json` au prompt, alors que des donnees plus riches existent deja:

- `structured_facts_v1`;
- `AINarrativeInputContract`;
- `ChartInterpretationInputRuntimeData`;
- `client_interpretation_projection_v1`;
- `projection_hash`;
- `evidence_refs`;
- `narrative_answer_audit_v1`.

La premiere story de refactor doit donc formaliser le payload cible sans encore brancher tout le runtime.

## Source obligatoire

Lire avant implementation:

- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md`
- `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md`
- `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md`
- `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md`
- `_story_briefs/cs-259-define-narrative-answer-audit-v1.md`

Relire les owners existants:

- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`

## Objectif

Creer un contrat applicatif versionne `llm_astrology_input_v1` qui definit exactement quelles donnees astrologiques et interpretatives peuvent entrer dans la composition du prompt LLM.

## Perimetre inclus

1. Creer un modele ou schema interne versionne `llm_astrology_input_v1`.
2. Definir les blocs obligatoires:
   - `facts`: faits structuraux issus de `structured_facts_v1`;
   - `signals`: signaux pre-narratifs issus de `AINarrativeInputContract`;
   - `limits`: donnees absentes, incertitudes, exclusions de calcul;
   - `evidence`: refs utilisables pour grounding/validation;
   - `shaping`: profondeur et angle editorial par plan/module;
   - `provenance`: versions, hashes et identifiants de contrats;
   - `exclusions`: surfaces interdites dans ce contrat.
3. Documenter la responsabilite de chaque bloc et sa source canonique.
4. Ajouter des tests de forme du contrat.
5. Ajouter des assertions negatives empechant l'exposition brute de `ChartObjectRuntimeData`, `CalculationGraph`, `chart_json` ou `natal_data` comme source canonique du contrat.

## Hors perimetre

- Modifier les prompts redactionnels.
- Modifier le process general de generation de prompt LLM.
- Traiter la securite, le CI ou les profils astrologues.
- Brancher le contrat dans `NatalExecutionInput` ou `ExecutionContext`.
- Supprimer `chart_json` ou `natal_data`.
- Executer un appel LLM reel.

## Questions de conception obligatoires

1. Le contrat vit-il dans `domain/llm`, `domain/astrology/interpretation` ou un module de pont dedie?
2. Quels champs de `AINarrativeInputContract` deviennent prompt-visibles?
3. Quels champs restent runtime-only ou audit-only?
4. Comment representer les limites et donnees manquantes pour reduire l'invention LLM?
5. Quelle granularite de `evidence_refs` est utile au generateur de prompt sans transformer l'evidence en payload verbeux?

## Criteres d'acceptation

1. `llm_astrology_input_v1` existe comme contrat interne versionne.
2. Le contrat separe explicitement facts, signals, limits, evidence, shaping, provenance et exclusions.
3. `structured_facts_v1` est la source canonique du bloc factuel.
4. `AINarrativeInputContract` est l'owner interne des signaux narratifs.
5. Les projections B2C ne deviennent pas source factuelle canonique.
6. Les tests prouvent la forme minimale du contrat et les exclusions.
7. Aucun prompt redactionnel ni provider LLM n'est modifie.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests --tb=short
rg -n "llm_astrology_input_v1|structured_facts_v1|AINarrativeInputContract|ChartObjectRuntimeData|chart_json|natal_data" app tests
```

## Risques

Le risque principal est de creer un contrat trop proche de `chart_json` ou trop proche de la projection B2C. Le contrat doit rester une entree LLM interne, orientee qualite narrative, grounding et lisibilite pour le generateur de prompt.
