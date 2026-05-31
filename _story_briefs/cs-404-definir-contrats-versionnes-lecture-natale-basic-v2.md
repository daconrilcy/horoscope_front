# CS-404 - Definir Les Contrats Versionnes De Lecture Natale Basic V2

<!-- Commentaire global: ce brief cadre le socle contractuel versionne du futur moteur de lecture natale Basic. -->

## Resume

Definir les contrats internes et publics du pipeline Basic avant toute nouvelle generation
LLM. La refonte ne doit pas commencer par un meilleur prompt: elle doit d'abord fixer les
objets versionnes qui relient le calcul natal, les faits selectionnes, le plan de lecture,
la validation narrative et la projection publique.

## Contexte

Le plan source `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
demande un pipeline controle:

```text
NatalResult -> EligibilityContext -> FactGraph -> SalienceModel -> ThemeModel
-> SynthesisResolver -> ReadingPlan -> NarrativeDraft -> NarrativeValidator
-> BasicNatalInterpretation
```

Les stories CS-391 a CS-403 ont deja verrouille le contrat narratif V3, la route Basic
complete, le refus des schemas courts et la non-exposition des donnees techniques. Cette
story pose le vocabulaire et les versions du nouveau moteur Basic afin d'eviter une
implementation opportuniste par ajouts disperses.

## Objectif

Creer le contrat minimal versionne pour:

- `EligibilityContext`;
- `NatalFactGraph`;
- `NatalSalienceModel`;
- `NatalNarrativeThemeModel`;
- `NatalSynthesis`;
- `BasicNatalReadingPlan`;
- `BasicNatalInterpretationV2`.

Chaque contrat doit distinguer les donnees internes, editoriales et publiques.

## Perimetre Inclus

1. Creer les modeles de contrat dans un owner canonique backend, sans dupliquer les schemas
   publics existants.
2. Definir les constantes de version: taxonomie de faits, modele de salience, taxonomie de
   themes, builder de plan, prompt cible, validateur, schema public.
3. Ajouter une section de documentation technique courte qui explique le flux cible et les
   responsabilites de chaque contrat.
4. Definir explicitement les niveaux de preuve `internal_evidence`, `editorial_evidence` et
   `public_evidence`.
5. Interdire dans les contrats publics les champs `ranking_score`, `condition_axis`,
   `score_profile`, `weighted_score`, `prompt_hint`, `audit_input` et identifiants internes.
6. Prevoir `locale`, `level=basic`, `engine_version=basic-natal-reading-v1` et
   `schema_version=basic_natal_interpretation_v2`.
7. Ajouter des tests de serialisation et de refus des champs inconnus.
8. Ajouter une garde d'architecture prouvant que les contrats purs n'importent ni API, ni DB,
   ni runtime LLM provider.

## Hors Perimetre

- Extraire les faits astrologiques.
- Scorer les faits.
- Construire une lecture narrative complete.
- Modifier le frontend.
- Ajouter une migration de donnees.
- Appeler un provider LLM.

## Sources Obligatoires

- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/llm/prompting/narrative_natal_reading_v1.py`
- `backend/app/domain/llm/prompting/schemas.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
- `backend/app/services/api_contracts/public/natal_interpretation.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-149` - le flux natal moderne reste gouverne et explicite, sans retour aux payloads
    legacy prompt-visibles.
  - `RG-150` - les payloads rejetes ne deviennent pas des interpretations publiques.
  - `RG-152` - les lectures completes acceptees ne doivent pas exposer les donnees techniques.
  - `RG-154` - la denylist publique reste applicable au nouveau contrat.
  - `RG-155` - le contrat interdit le padding semantique et les sources vides.
  - `RG-156` - la couverture editoriale Basic doit rester diversifiee dans les budgets.
- Required regression evidence:
  - `pytest -q backend/tests/unit/test_basic_natal_reading_contracts.py`
  - `pytest -q backend/tests/architecture/test_basic_natal_reading_contract_boundaries.py`
  - `rg -n "ranking_score|condition_axis|score_profile|weighted_score|prompt_hint|audit_input" backend/app/domain/astrology backend/app/services/llm_generation/natal`
- Registry enrichment expected:
  - Ajouter un nouveau `RG-XXX` quand la story concrete cree l'invariant durable du contrat
    `basic_natal_interpretation_v2`.
- Allowed differences:
  - De nouveaux objets de domaine versionnes apparaissent, sans changement de comportement
    runtime tant qu'ils ne sont pas branches.

## Criteres D'acceptation

1. Les versions du moteur Basic sont centralisees et testees.
2. Les modeles internes, editoriaux et publics sont separes.
3. Les modeles publics refusent les champs inconnus et les marqueurs techniques interdits.
4. Le contrat est localisable via `locale` sans phrases francaises hardcodees dans le scoring.
5. Aucun schema public existant V1/V3 n'est affaibli pour accepter les nouveaux champs.
6. Les objets de contrat n'importent pas FastAPI, SQLAlchemy, repositories ou provider LLM.
7. La documentation indique que le LLM est redacteur controle, pas source d'intelligence
   astrologique.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/test_basic_natal_reading_contracts.py --tb=short
python -B -m pytest -q tests/architecture/test_basic_natal_reading_contract_boundaries.py --tb=short
```

## Dependances

- CS-391 a CS-403 pour le contrat narratif et le routage Basic complete.

## Risques

Le risque principal est de creer un second contrat public concurrent de
`narrative_natal_reading_v1`. Cette story doit poser un contrat de pipeline Basic qui alimente
le narratif public, pas une facade incompatible.
