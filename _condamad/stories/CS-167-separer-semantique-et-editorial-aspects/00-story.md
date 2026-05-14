# Story CS-167 separer-semantique-et-editorial-aspects: Separer semantique et editorial des aspects

Status: ready-to-dev

## 1. Objective

Introduire `AspectInterpretationFacts` comme couche purement semantique entre
`AspectRuntimeData` et les renderers editoriaux. La story empeche
`AspectInterpretationBuilder` de devenir un moteur narratif implicite.

## 2. Trigger / Source

- Source type: code-review
- Source reference: revue utilisateur du 2026-05-14 sur CS-163 a CS-166.
- Reason for change: les faits astrologiques, la semantique et la narration
  editoriale doivent rester separes avant l'implementation massive des aspects.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/interpretation`
- In scope:
  - definir `AspectInterpretationFacts`;
  - exposer primitives symboliques, axes semantiques et references editoriales;
  - garder la place pour des provenances et interpretations concurrentes;
  - brancher les profils d'interpretation aspect vers ce contrat semantique;
  - adapter CS-165 pour consommer ce contrat.
- Out of scope:
  - generation LLM;
  - personas, langues et styles editoriaux;
  - projection publique frontend;
  - scoring prediction.
- Explicit non-goals:
  - Ne pas mettre de phrases narratives dans la couche semantique.
  - Ne pas dupliquer les profils editoriaux existants.
  - Ne pas importer prediction depuis astrology.

## 4. Operation Contract

- Operation type: create
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story fixe un contrat runtime semantique consomme par
  les builders d'interpretation.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les primitives symboliques, axes semantiques et themes editoriaux restent distincts.
  - Les champs semantiques sont des listes/taxonomies, pas des paragraphes.
  - Les renderers editoriaux restent consommateurs.
  - Les profils existants restent la source des axes semantiques.
  - La provenance detaillee est cadree par CS-170.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un champ semantique ne peut pas etre derive des
  profils existants.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `AspectInterpretationFacts` devient la source semantique. |
| Baseline Snapshot | yes | La separation before/after doit etre documentee. |
| Ownership Routing | yes | Semantique, editorial et LLM ont des owners distincts. |
| Allowlist Exception | no | Aucun fallback narratif n'est autorise. |
| Contract Shape | yes | Le contrat semantique est nouveau. |
| Batch Migration | no | Les renderers sont adaptes dans CS-165. |
| Reintroduction Guard | yes | Le retour de narration dans la semantique doit echouer. |
| Persistent Evidence | yes | Un exemple semantique doit etre conserve. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AspectInterpretationFacts` et AST guard du contrat semantique.
- Secondary evidence:
  - tests `backend/tests/unit/domain/astrology/test_aspect_interpretation_facts.py`.
- Static scans alone are not sufficient for this story because:
  - les fixtures doivent prouver que le contrat semantique est produit.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-167-separer-semantique-et-editorial-aspects/generated/aspect-semantics-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-167-separer-semantique-et-editorial-aspects/generated/aspect-semantics-after.md`
- Expected invariant:
  - la couche semantique ne contient pas de paragraphes editoriaux.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Faits runtime aspect | `backend/app/domain/astrology/runtime` | renderer editorial |
| Primitives symboliques | `AspectInterpretationFacts` | renderer editorial |
| Axes semantiques | `AspectInterpretationFacts` | renderer editorial |
| Themes editoriaux | `AspectInterpretationBuilder` | contrat semantique |
| Narration editoriale | `AspectInterpretationBuilder` | contrat semantique |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucune exception narrative n'est autorisee dans la semantique.

## 4f. Contract Shape

- Contract type:
  - Python runtime semantic contract.
- Fields:
  - `symbolic_primitives`, `semantic_axes`, `editorial_theme_refs`,
    `relationship_axes`, `growth_axes`, `shadow_axes`, `source_profile_code`.
- Required fields:
  - `symbolic_primitives`, `semantic_axes`, `growth_axes`.
- Optional fields:
  - `editorial_theme_refs`, `relationship_axes`, `shadow_axes`,
    `source_profile_code`, `semantic_candidates`.
- Status codes:
  - none.
- Serialization names:
  - snake_case.
- Frontend type impact:
  - none direct.
- Generated contract impact:
  - none.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: la migration des renderers est couverte par CS-165.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Semantics before | `generated/aspect-semantics-before.md` | Etat avant separation. |
| Semantics after | `generated/aspect-semantics-after.md` | Exemple semantique pur. |
| Narrative scan | `generated/aspect-semantics-narrative-scan.md` | Absence de paragraphes narratifs. |

## 4i. Reintroduction Guard

- Guard type: unit test plus scans.
- Forbidden patterns:
  - paragraphes editoriaux dans `AspectInterpretationFacts`;
  - appels LLM dans `domain/astrology`;
  - import prediction depuis astrology.
- Guard command:
  `pytest -q tests/unit/domain/astrology/test_aspect_interpretation_facts.py`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/services/reference_data/aspect_interpretation_seed_service.py` - charge les profils d'interpretation.
- Evidence 2: `docs/recherches astro/astral_aspect_interpretation_profiles.json` - contient la matiere semantique/editoriale.
- Evidence 3: `_condamad/stories/CS-165-construire-builder-interpretation-aspects/00-story.md` - builder editorial a cadrer.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- `AspectInterpretationFacts` existe comme contrat semantique pur.
- Le contrat distingue primitives symboliques, axes semantiques et references
  de themes editoriaux.
- Les builders editoriaux consomment ce contrat.
- Les champs semantiques restent des listes ou taxonomies.
- Les LLM/personas/langues restent hors domaine astrology.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-095` - astrology ne depend pas de prediction.
  - `RG-098` - le runtime aspect canonique reste la source des faits.
  - `RG-100` - l'interpretation editoriale reste separee du LLM/API.
  - `RG-105` - la provenance et les interpretations concurrentes restent typées.
- Non-applicable invariants:
  - `RG-097` - les regles d'orbes ne sont pas modifiees.
- Required regression evidence:
  - tests du contrat semantique;
  - scan anti-LLM;
  - artefact semantique before/after.
- Allowed differences:
  - ajout de `AspectInterpretationFacts`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `AspectInterpretationFacts` expose `symbolic_primitives`. | `pytest -q tests/unit/domain/astrology/test_aspect_interpretation_facts.py`. |
| AC2 | Les champs semantiques ne contiennent pas de paragraphes narratifs. | `pytest -q tests/unit/domain/astrology/test_aspect_interpretation_facts.py`. |
| AC3 | Le contrat est produit depuis un profil aspect. | `pytest -q tests/unit/domain/astrology/test_aspect_interpretation_facts.py`. |
| AC4 | `domain/astrology` ne contient pas d'appel LLM. | `rg -n "OpenAI|AIEngineAdapter|chat\\.completions|llm" app/domain/astrology -g "*.py"`. |
| AC5 | Les themes editoriaux ne sont pas stockes comme axes semantiques. | `pytest -q tests/unit/domain/astrology/test_aspect_interpretation_facts.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Definir le contrat semantique (AC: AC1, AC2)
  - [ ] Ajouter `AspectInterpretationFacts`.
  - [ ] Documenter `symbolic_primitives`, `semantic_axes` et `editorial_theme_refs`.

- [ ] Task 2 - Brancher les profils aspect (AC: AC1, AC3, AC5)
  - [ ] Mapper les profils vers les axes semantiques.
  - [ ] Lever une erreur explicite si le profil ne couvre pas un champ requis.

- [ ] Task 3 - Ajouter preuves et guards (AC: AC2, AC4)
  - [ ] Ajouter tests.
  - [ ] Capturer les artefacts generated.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AspectRuntimeData`.
  - `astral_aspect_interpretation_profiles`.
  - seed service existant comme reference de shape.
- Do not recreate:
  - profils editoriaux dupliques;
  - renderer narratif dans le contrat semantique;
  - themes editoriaux comme axes semantiques;
  - mapping produit prediction.
- Shared abstraction allowed only if:
  - elle sert aussi les futures semantiques maisons ou patterns.

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

- paragraphes narratifs dans `AspectInterpretationFacts`
- `editorial_themes` comme champ semantique canonique
- `OpenAI` ou `AIEngineAdapter` dans `backend/app/domain/astrology`
- `backend/app/domain/astrology/** -> app.domain.prediction`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Faits astrologiques | `AspectRuntimeData` | interpretation |
| Primitives symboliques | `AspectInterpretationFacts` | renderer editorial |
| Axes semantiques | `AspectInterpretationFacts` | renderer editorial |
| Narration | builder/editorial/LLM futur | contrat semantique |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/aspect_runtime_data.py`
- `backend/app/services/reference_data/aspect_interpretation_seed_service.py`
- `docs/recherches astro/astral_aspect_interpretation_profiles.json`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py`
- `backend/app/domain/astrology/interpretation/__init__.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py` - contrat semantique.
- `backend/app/domain/astrology/interpretation/__init__.py` - export.
- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py` - consommation du contrat.

Likely tests:

- `backend/tests/unit/domain/astrology/test_aspect_interpretation_facts.py` - contrat semantique.
- `backend/tests/unit/domain/astrology/test_aspect_interpretation_builder.py` - consommation par renderer.

Files not expected to change:

- `backend/migrations/**` - aucun changement SQL.
- `frontend/**` - aucune UI.
- `backend/app/domain/prediction/**` - aucune logique produit.

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
pytest -q tests/unit/domain/astrology/test_aspect_interpretation_facts.py
pytest -q tests/unit/domain/astrology/test_aspect_interpretation_builder.py
rg -n "OpenAI|AIEngineAdapter|chat\\.completions|llm" app/domain/astrology -g "*.py"
rg -n "app\\.domain\\.prediction|app\\.services\\.prediction" app/domain/astrology -g "*.py"
rg -n "editorial_themes|themes\\s*=" app/domain/astrology/interpretation -g "*.py"
```

## 22. Regression Risks

- Risk: le builder editorial redevient source semantique.
  - Guardrail: ownership routing et tests.
- Risk: le contrat semantique contient de la narration.
  - Guardrail: test de forme et scan narratif.
- Risk: couplage prediction.
  - Guardrail: scan `RG-095`.

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

- Revue utilisateur du 2026-05-14 - separation faits / semantique / editorial.
- `_condamad/stories/CS-165-construire-builder-interpretation-aspects/00-story.md` - renderer editorial a cadrer.
- `docs/recherches astro/astral_aspect_interpretation_profiles.json` - source des profils.
