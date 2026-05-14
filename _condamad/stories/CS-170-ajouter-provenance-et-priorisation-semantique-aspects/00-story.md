# Story CS-170 ajouter-provenance-et-priorisation-semantique-aspects: Ajouter provenance et priorisation semantique des aspects

Status: ready-to-dev

## 1. Objective

Ajouter un contrat canonique de provenance et de candidats semantiques pour les
aspects. La story prepare les divergences entre traditions, autorites,
contextes et niveaux d'interpretation sans transformer le runtime en sortie
unique arbitraire.

## 2. Trigger / Source

- Source type: code-review
- Source reference: revue utilisateur du 2026-05-14 sur provenance,
  primitives symboliques et interpretations concurrentes.
- Reason for change: les axes semantiques doivent rester tracables et
  priorisables quand plusieurs lectures astrologiques coexistent.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/interpretation`
- In scope:
  - definir `SemanticProvenance`;
  - definir `AspectSemanticCandidate`;
  - ajouter `confidence`, `source_system`, `source_tradition`,
    `source_authority` et `origin_reference`;
  - definir une strategie de priorisation contextuelle.
- Out of scope:
  - choisir une doctrine astrologique unique;
  - appeler un LLM;
  - modifier les tables SQL;
  - exposer ces champs au frontend.
- Explicit non-goals:
  - Ne pas ecraser les interpretations concurrentes.
  - Ne pas stocker des auteurs comme strings libres non typees.
  - Ne pas coupler la priorisation au scoring prediction.

## 4. Operation Contract

- Operation type: create
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story ajoute des contrats semantiques internes et des
  guards de priorisation sans changer les APIs.
- Behavior change allowed: constrained
- Behavior change constraints:
  - La provenance accompagne chaque candidat semantique.
  - La priorisation conserve les candidats non retenus.
  - Les poids contextuels restent dans astrology interpretation.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une source d'autorite doit etre declaree canonique.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les candidats semantiques deviennent la source des interpretations concurrentes. |
| Baseline Snapshot | yes | Le passage single-output vers candidats doit etre documente. |
| Ownership Routing | yes | Provenance et priorisation restent dans astrology interpretation. |
| Allowlist Exception | no | Aucune source libre non tracee n'est autorisee. |
| Contract Shape | yes | Provenance et candidats sont des contrats nouveaux. |
| Batch Migration | no | Aucun consommateur public n'est migre. |
| Reintroduction Guard | yes | Les outputs semantiques sans provenance doivent echouer. |
| Persistent Evidence | yes | Exemples before/after requis. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AspectSemanticCandidate`, `SemanticProvenance` et AST guard provenance.
- Secondary evidence:
  - tests `backend/tests/unit/domain/astrology/test_aspect_semantic_provenance.py`.
- Static scans alone are not sufficient for this story because:
  - les tests doivent prouver la conservation des candidats concurrents.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-170-ajouter-provenance-et-priorisation-semantique-aspects/generated/aspect-semantic-provenance-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-170-ajouter-provenance-et-priorisation-semantique-aspects/generated/aspect-semantic-provenance-after.md`
- Expected invariant:
  - aucun axe semantique canonique n'est produit sans provenance.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Provenance semantique | `SemanticProvenance` | renderer editorial |
| Candidats concurrents | `AspectSemanticCandidate` | sortie single-string |
| Priorisation contextuelle | `backend/app/domain/astrology/interpretation` | prediction |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: les sources semantiques doivent toutes etre tracees.

## 4f. Contract Shape

- Contract type:
  - Python semantic contracts.
- Fields:
  - `source_system`, `source_tradition`, `source_authority`,
    `origin_reference`, `confidence`, `context_weight`, `semantic_axes`,
    `priority_rank`, `selected`.
- Required fields:
  - `source_system`, `source_tradition`, `confidence`, `semantic_axes`.
- Optional fields:
  - `source_authority`, `origin_reference`, `context_weight`,
    `priority_rank`, `selected`.
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
- Reason: aucun consommateur public n'est migre dans cette story.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Provenance before | `generated/aspect-semantic-provenance-before.md` | Etat sans provenance canonique. |
| Provenance after | `generated/aspect-semantic-provenance-after.md` | Exemple avec candidats concurrents. |
| Source scan | `generated/aspect-semantic-source-scan.md` | Absence de sources libres non tracees. |

## 4i. Reintroduction Guard

- Guard type: unit tests plus scans.
- Forbidden patterns:
  - axe semantique sans `SemanticProvenance`;
  - `selected=True` qui supprime les candidats concurrents;
  - priorisation dans `domain/prediction`.
- Guard command:
  `pytest -q tests/unit/domain/astrology/test_aspect_semantic_provenance.py`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `_condamad/stories/CS-167-separer-semantique-et-editorial-aspects/00-story.md` - contrat semantique pur.
- Evidence 2: `docs/recherches astro/astral_aspect_interpretation_profiles.json` - profils sources.
- Evidence 3: `backend/app/services/reference_data/aspect_interpretation_seed_service.py` - chargement des profils.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- Chaque candidat semantique porte une provenance.
- Les interpretations concurrentes sont conservees.
- Une priorisation contextuelle peut selectionner un candidat sans supprimer les autres.
- Les renderers editoriaux consomment une selection explicite.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-095` - astrology ne depend pas de prediction.
  - `RG-102` - semantique pure et editorial restent separes.
  - `RG-103` - les poids restent typés par owner.
- Non-applicable invariants:
  - `RG-104` - patterns et graphe hors scope.
- Required regression evidence:
  - tests provenance;
  - scan anti-priorisation prediction;
  - artefact before/after des candidats.
- Allowed differences:
  - ajout de provenance et candidats concurrents.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `SemanticProvenance` expose `source_system`. | `pytest -q tests/unit/domain/astrology/test_aspect_semantic_provenance.py`. |
| AC2 | `AspectSemanticCandidate` conserve `confidence`. | `pytest -q tests/unit/domain/astrology/test_aspect_semantic_provenance.py`. |
| AC3 | La priorisation conserve les candidats non selectionnes. | `pytest -q tests/unit/domain/astrology/test_aspect_semantic_provenance.py`. |
| AC4 | `domain/prediction` ne priorise pas les candidats semantiques. | `rg -n "semantic_candidate" app/domain/prediction -g "*.py"` attendu zero hit. |

## 8. Implementation Tasks

- [ ] Task 1 - Definir la provenance (AC: AC1)
  - [ ] Ajouter `SemanticProvenance`.
  - [ ] Typer les champs de source et confiance.

- [ ] Task 2 - Definir les candidats concurrents (AC: AC2, AC3)
  - [ ] Ajouter `AspectSemanticCandidate`.
  - [ ] Conserver les candidats non selectionnes.

- [ ] Task 3 - Ajouter guards et preuves (AC: AC1, AC2, AC3, AC4)
  - [ ] Ajouter tests.
  - [ ] Capturer les artefacts generated.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AspectInterpretationFacts`.
  - `astral_aspect_interpretation_profiles`.
  - `AspectModifierRuntimeData` pour les contextes disponibles.
- Do not recreate:
  - strings de source non tracees;
  - output semantique unique obligatoire;
  - scoring prediction dans astrology.
- Shared abstraction allowed only if:
  - elle sert aussi les futures provenances maisons ou patterns.

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

- `semantic_axes` sans provenance
- `AspectSemanticCandidate` dans `backend/app/domain/prediction`
- `source_authority = "unknown"`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Provenance | `SemanticProvenance` | renderer editorial |
| Candidats semantiques | `AspectSemanticCandidate` | payload public direct |
| Priorisation | `domain/astrology/interpretation` | prediction |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py`
- `backend/app/services/reference_data/aspect_interpretation_seed_service.py`
- `docs/recherches astro/astral_aspect_interpretation_profiles.json`
- `backend/app/domain/prediction/natal_sensitivity.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/aspect_semantic_provenance.py` - provenance et candidats.
- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py` - rattacher les candidats.
- `backend/app/domain/astrology/interpretation/__init__.py` - export.

Likely tests:

- `backend/tests/unit/domain/astrology/test_aspect_semantic_provenance.py` - provenance et priorisation.
- `backend/tests/unit/domain/astrology/test_aspect_interpretation_facts.py` - integration.

Files not expected to change:

- `backend/migrations/**` - aucun changement SQL.
- `frontend/**` - aucune UI.
- `backend/app/api/**` - aucun endpoint.

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
pytest -q tests/unit/domain/astrology/test_aspect_semantic_provenance.py
pytest -q tests/unit/domain/astrology/test_aspect_interpretation_facts.py
rg -n "AspectSemanticCandidate|SemanticProvenance|semantic_candidate" app/domain/prediction -g "*.py"
rg -n "source_authority\\s*=\\s*[\"']unknown|semantic_axes.*without" app/domain/astrology -g "*.py"
```

## 22. Regression Risks

- Risk: la provenance devient une string libre inutile.
  - Guardrail: contrat typé et tests.
- Risk: la priorisation supprime les lectures concurrentes.
  - Guardrail: test conservation des candidats.
- Risk: prediction choisit la semantique.
  - Guardrail: scan `domain/prediction`.

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

- Revue utilisateur du 2026-05-14 - provenance et interpretations concurrentes.
- `_condamad/stories/CS-167-separer-semantique-et-editorial-aspects/00-story.md`.
- `docs/recherches astro/astral_aspect_interpretation_profiles.json`.
