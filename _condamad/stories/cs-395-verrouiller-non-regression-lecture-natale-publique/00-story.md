# Story CS-395 verrouiller-non-regression-lecture-natale-publique: Verrouiller La Lecture Natale Publique
Status: done

## Trigger / Source
- Source type: regression-hardening
- Source reference: `_story_briefs/cs-395-verrouiller-non-regression-lecture-natale-publique.md`
- Reason for change: la convergence publique doit rester vérifiable dans le temps.

## Objective
Ajouter les gardes automatisées et la preuve finale de non-régression pour `/natal`.

## Target State
- Les frontières backend et DOM public sont couvertes.
- La chaîne Alembic conserve l'historique utilisateur.
- La QA responsive est documentée.

## Current State Evidence
- Evidence 1: `backend/tests/architecture/test_narrative_natal_reading_public_boundary.py` - garde backend inspecté.
- Evidence 2: `frontend/src/tests/natalPublicDomGuard.test.tsx` - garde DOM inspecté.
- Evidence 3: `_condamad/reports/cs-395-non-regression-lecture-natale-publique.md` - rapport final inspecté.

## Domain Boundary
- Domain: natal-public-reading-regression
- In scope:
  - Tests d'architecture, test DOM, registre RG et rapport final.
- Out of scope:
  - Nouvelle fonctionnalité publique et nouveau calcul astrologique.
- Explicit non-goals:
  - Aucun changement d'entitlement.

## Operation Contract
- Operation type: update
- Primary archetype: custom
- Archetype reason: la story ajoute plusieurs gardes ciblées sur une même frontière publique.
- Behavior change allowed: no
- Behavior change constraints:
  - Durcir les preuves sans modifier la lecture attendue.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: un garde impose un changement produit.

Additional validation rules:
- Conserver l'historique utilisateur et faire échouer les gardes si une fuite technique revient.

## Required Contracts
| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | La source applicative est déjà couverte par CS-392. |
| Baseline Snapshot | no | Le rapport final porte la QA responsive. |
| Ownership Routing | no | Aucun routage modifié. |
| Allowlist Exception | no | Aucun allowlist requis. |
| Contract Shape | no | Les gardes consomment les contrats existants. |
| Batch Migration | no | Aucune migration destructive autorisée. |
| Reintroduction Guard | yes | Les tests empêchent le retour des fuites. |
| Persistent Evidence | yes | Le rapport final et le registre restent versionnés. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La frontière backend publique est testée. | `pytest -q tests/architecture/test_narrative_natal_reading_public_boundary.py`. |
| AC2 | Le DOM public interdit les détails techniques. | `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC3 | La révision Alembic ne détruit pas l'historique utilisateur. | `pytest -q tests/architecture/test_narrative_natal_reading_public_boundary.py`. |
| AC4 | Les invariants RG-152 à RG-154 sont inscrits. | `rg -n "RG-152|RG-153|RG-154" _condamad/stories/regression-guardrails.md`. |
| AC5 | La QA responsive est documentée. | Manual check: ouvrir `/natal` et confirm le fil narratif dans les deux tailles prévues. |

## Implementation Tasks
- [x] Task 1: Ajouter les gardes backend. (AC: AC1, AC3)
- [x] Task 2: Ajouter le garde DOM public. (AC: AC2)
- [x] Task 3: Inscrire RG-152 à RG-154. (AC: AC4)
- [x] Task 4: Documenter la QA responsive. (AC: AC5)

## Mandatory Reuse / DRY Constraints
- Réutiliser les suites Pytest et Vitest existantes.
- Conserver un registre RG canonique unique.

## No Legacy / Forbidden Paths
- Aucun wrapper legacy.
- Aucun chemin compatibility.
- Aucun fallback public technique.

## Regression Guardrails
- Applicable invariants: `RG-152`, `RG-153`, `RG-154`.
- Required regression evidence: `pytest -q tests/architecture/test_narrative_natal_reading_public_boundary.py`.
- Allowed differences: ajout de preuves de non-régression.

## Files to Inspect First
- `backend/tests/architecture/test_narrative_natal_reading_public_boundary.py`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `_condamad/stories/regression-guardrails.md`

## Expected Files to Modify
Likely files:
- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/cs-395-non-regression-lecture-natale-publique.md`
- `backend/migrations/versions/20260530_0141_purge_legacy_user_natal_interpretations.py`

Likely tests:
- `backend/tests/architecture/test_narrative_natal_reading_public_boundary.py`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`

Files not expected to change:
- `frontend/src/pages/**`

## Dependency Policy
- New dependencies: none.
- Justification: les outils de test existants suffisent.

## Validation Plan
- VC1: `pytest -q tests/architecture/test_narrative_natal_reading_public_boundary.py`
- VC2: `pnpm --dir frontend test -- natalPublicDomGuard`
- VC3: `ruff check .`
- VC4: `pnpm --dir frontend lint`

## Regression Risks
- Une purge Alembic pourrait effacer l'historique ; le garde architecture interdit `DELETE FROM`.
- Une fuite DOM pourrait revenir ; RG-154 et le test dédié bornent ce risque.

## Reintroduction Guard
- Forbidden symbol: `raw_payload`.
- Forbidden symbol: `provider`.
- Evidence profile: `reintroduction_guard`; `pytest -q tests/architecture/test_narrative_natal_reading_public_boundary.py`.
- Architecture guard: le test DOM échoue si un détail technique est reintroduced dans `/natal`.

## Baseline / Before-After Rule
- Baseline artifact before implementation: `_condamad/reports/cs-390-audit-architecture-lecture-natale.md`.
- Comparison after implementation: `pnpm --dir frontend test -- natalPublicDomGuard`.
- Expected invariant: le DOM public expose seulement la lecture narrative et ses sources humaines.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Rapport final | `_condamad/reports/cs-395-non-regression-lecture-natale-publique.md` | Archiver la QA et les validations. |
| Registre RG | `_condamad/stories/regression-guardrails.md` | Conserver les invariants durables. |

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.

## References
- `_story_briefs/cs-395-verrouiller-non-regression-lecture-natale-publique.md`
- `_condamad/stories/regression-guardrails.md`
