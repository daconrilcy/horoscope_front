# Story CS-165 construire-builder-interpretation-aspects: Construire le builder d'interpretation des aspects

Status: ready-to-dev

## 1. Objective

Creer `AspectInterpretationBuilder` comme renderer editorial deterministic. Il
consomme les faits semantiques d'aspect et les profils editoriaux sans devenir
la source des axes psychologiques ou relationnels.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-14, priorite 5 `Runtime Explanation Builder`.
- Reason for change: les profils editoriaux existent, mais aucun service canonique ne les assemble avec les faits runtime.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/interpretation`
- In scope:
  - creer `AspectInterpretationBuilder`;
  - consommer `AspectInterpretationFacts` quand CS-167 est disponible;
  - definir le contrat de sortie `summary`, `psychological_meaning`, `relationship_expression`, `shadow_expression`, `growth_path`;
  - consommer les profils d'interpretation aspect existants;
  - tester les cas profil present, profil absent controle et participants.
- Out of scope:
  - definir les themes semantiques purs;
  - appeler un LLM;
  - modifier les prompts existants;
  - exposer un nouvel endpoint;
  - construire les dominants aspects.
- Explicit non-goals:
  - Ne pas deplacer l'editorial dans prediction.
  - Ne pas creer de fallback texte generique silencieux.
  - Ne pas dupliquer `AspectInterpretationFacts`.
  - Ne pas modifier les seeds SQL hors tests si les donnees existent deja.

## 4. Operation Contract

- Operation type: create
- Primary archetype: service-boundary-refactor
- Archetype reason: la story cree un service de domaine qui fixe la frontiere entre faits astrologiques et interpretation editoriale.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le builder doit produire une sortie deterministe sans LLM.
  - Les themes semantiques viennent d'`AspectInterpretationFacts`.
  - Une absence de profil doit etre explicite et testee.
  - Les textes viennent des profils, pas de constantes dispersees.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un champ editorial requis n'existe pas dans le referentiel actuel.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le builder consomme `AspectRuntimeData`. |
| Baseline Snapshot | yes | La forme d'interpretation avant/apres doit etre documentee. |
| Ownership Routing | yes | Le domaine interpretation possede l'assemblage editorial. |
| Allowlist Exception | no | Aucun fallback texte silencieux n'est autorise. |
| Contract Shape | yes | La sortie interpretation est un nouveau contrat. |
| Batch Migration | no | Aucun lot de consommateurs n'est migre ici. |
| Reintroduction Guard | yes | Les fallbacks editoriaux disperses doivent etre bloques. |
| Persistent Evidence | yes | Exemples d'interpretation persistants requis. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AspectRuntimeData`, `AspectInterpretationFacts`,
    `astral_aspect_interpretation_profiles` et AST guard du renderer.
- Secondary evidence:
  - tests unitaires du builder.
- Static scans alone are not sufficient for this story because:
  - les sorties doivent etre produites a partir de profils reels ou fixtures representatives.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-165-construire-builder-interpretation-aspects/generated/aspect-interpretation-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-165-construire-builder-interpretation-aspects/generated/aspect-interpretation-after.md`
- Expected invariant:
  - aucune narration LLM n'est appelee; l'interpretation est deterministe.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Faits runtime aspect | `backend/app/domain/astrology/runtime` | builder editorial |
| Assemblage editorial aspect | `backend/app/domain/astrology/interpretation` | `domain/prediction`, API, frontend |
| Faits semantiques aspect | `AspectInterpretationFacts` | renderer editorial |
| Appel LLM | story/service LLM ulterieur | builder domain |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucun texte fallback generique n'est autorise.

## 4f. Contract Shape

- Contract type:
  - Python interpretation data contract.
- Fields:
  - `summary`, `psychological_meaning`, `relationship_expression`, `shadow_expression`, `growth_path`, `source_profile_code`.
- Required fields:
  - `summary`, `psychological_meaning`, `shadow_expression`, `growth_path`.
- Optional fields:
  - `relationship_expression`, `source_profile_code`.
- Status codes:
  - none.
- Serialization names:
  - snake_case.
- Frontend type impact:
  - none direct.
- Generated contract impact:
  - none unless exposed later.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: aucun consommateur public n'est migre dans cette story.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Interpretation before | `_condamad/stories/CS-165-construire-builder-interpretation-aspects/generated/aspect-interpretation-before.md` | Etat sans builder canonique. |
| Interpretation after | `_condamad/stories/CS-165-construire-builder-interpretation-aspects/generated/aspect-interpretation-after.md` | Exemple structure. |
| Fallback scan | `_condamad/stories/CS-165-construire-builder-interpretation-aspects/generated/aspect-interpretation-fallback-scan.md` | Absence de textes fallback disperses. |

## 4i. Reintroduction Guard

- Guard type: unit tests + scan.
- Forbidden patterns:
  - texte generique hardcode pour aspects dans services LLM/API;
  - fallback silencieux quand un profil manque;
  - import prediction depuis astrology.
- Guard command:
  `pytest -q tests/unit/domain/astrology/test_aspect_interpretation_builder.py`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/services/reference_data/aspect_interpretation_seed_service.py` - seed des profils editoriaux aspect.
- Evidence 2: `docs/recherches astro/astral_aspect_interpretation_profiles.json` - source documentaire des profils.
- Evidence 3: `backend/app/domain/astrology/runtime/house_runtime_data.py` - precedent de runtime astrologique consomme par interpretation.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- `AspectInterpretationBuilder` produit une interpretation editoriale structuree.
- Les axes semantiques proviennent d'`AspectInterpretationFacts`.
- Les champs editoriaux viennent des profils de reference.
- Les absences de profils sont explicites et testees.
- Aucun appel LLM n'est effectue dans le domaine astrology.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-095` - astrology ne depend pas de prediction.
  - `RG-098` - le runtime aspect canonique reste la source des faits.
  - `RG-102` - la couche semantique pure reste separee du renderer editorial.
  - `RG-099` - la projection publique ne doit pas redevenir proprietaire de l'interpretation.
- Non-applicable invariants:
  - `RG-097` - l'heritage des orbes n'est pas modifie.
- Required regression evidence:
  - tests builder;
  - scan fallback texte;
  - scan imports prediction.
- Allowed differences:
  - creation d'un contrat d'interpretation interne.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le builder produit les cinq champs editoriaux attendus depuis un profil. | `pytest -q tests/unit/domain/astrology/test_aspect_interpretation_builder.py`. |
| AC2 | Une absence de profil produit une erreur ou un etat explicite. | `pytest -q tests/unit/domain/astrology/test_aspect_interpretation_builder.py`. |
| AC3 | Le builder consomme `AspectInterpretationFacts`. | `pytest -q tests/unit/domain/astrology/test_aspect_interpretation_builder.py`. |
| AC4 | Aucun appel LLM n'est introduit dans `domain/astrology`. | `rg -n "OpenAI|AIEngineAdapter|chat\\.completions|llm" app/domain/astrology -g "*.py"`. |

## 8. Implementation Tasks

- [ ] Task 1 - Definir le contrat d'interpretation (AC: AC1)
  - [ ] Ajouter les dataclasses/modeles de sortie.

- [ ] Task 2 - Implementer `AspectInterpretationBuilder` (AC: AC1, AC2, AC3)
  - [ ] Mapper runtime + profil editorial.
  - [ ] Gerer explicitement les profils absents.

- [ ] Task 3 - Ajouter tests et preuves (AC: AC1, AC2, AC3, AC4)
  - [ ] Couvrir profil present et absent.
  - [ ] Capturer les artefacts generated.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AspectRuntimeData`.
  - `AspectInterpretationFacts`.
  - `astral_aspect_interpretation_profiles`.
  - seed service existant pour comprendre la shape des donnees.
- Do not recreate:
  - axes semantiques dans le renderer editorial;
  - textes editoriaux hardcodes hors profils;
  - client LLM;
  - mapping produit prediction.
- Shared abstraction allowed only if:
  - elle sert plusieurs builders d'interpretation astrologique sans coupler au produit.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `backend/app/domain/astrology/** -> app.domain.prediction`
- `OpenAI` ou `AIEngineAdapter` dans `backend/app/domain/astrology`
- texte fallback aspect hardcode hors fixtures de tests

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Interpretation aspect deterministic | `backend/app/domain/astrology/interpretation` | API, frontend, prediction |
| Generation LLM | service LLM futur | domain astrology |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/services/reference_data/aspect_interpretation_seed_service.py`
- `docs/recherches astro/astral_aspect_interpretation_profiles.json`
- `backend/app/domain/astrology/runtime/aspect_runtime_data.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py`
- `backend/app/domain/astrology/interpretation/__init__.py`
- `backend/app/tests/unit/test_aspect_interpretation_seed_service.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py` - nouveau builder.
- `backend/app/domain/astrology/interpretation/aspect_interpretation_contracts.py` - contrat de sortie.
- `backend/app/domain/astrology/interpretation/__init__.py` - export.

Likely tests:

- `backend/tests/unit/domain/astrology/test_aspect_interpretation_builder.py` - builder.
- `backend/app/tests/unit/test_aspect_interpretation_seed_service.py` - compatibilite shape des profils.

Files not expected to change:

- `backend/migrations/**` - pas de changement SQL.
- `frontend/**` - exposition UI hors scope.
- `backend/app/domain/prediction/**` - pas de mapping produit.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/domain/astrology/test_aspect_interpretation_builder.py
pytest -q app/tests/unit/test_aspect_interpretation_seed_service.py
rg -n "themes|psychological_axes|relationship_patterns|growth_patterns" app/domain/astrology/interpretation -g "*.py"
rg -n "OpenAI|AIEngineAdapter|chat\\.completions|llm" app/domain/astrology -g "*.py"
rg -n "app\\.domain\\.prediction|app\\.services\\.prediction" app/domain/astrology -g "*.py"
```

## 22. Regression Risks

- Risk: texte fallback silencieux qui masque un profil manquant.
  - Guardrail: test absence explicite.
- Risk: couplage LLM dans le domaine pur.
  - Guardrail: scan anti-LLM.
- Risk: duplication des profils editoriaux.
  - Guardrail: reuse seed/profils existants.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respecter l'AGENTS.md: toute commande Python doit etre executee apres `.\.venv\Scripts\Activate.ps1`.

## 24. References

- Demande utilisateur du 2026-05-14 - priorite `Runtime Explanation Builder`.
- `docs/recherches astro/astral_aspect_interpretation_profiles.json` - profils editoriaux.
- `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/00-story.md` - prerequis runtime.
