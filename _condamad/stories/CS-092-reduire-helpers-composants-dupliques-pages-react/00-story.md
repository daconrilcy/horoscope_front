# Story CS-092 reduire-helpers-composants-dupliques-pages-react: Reduire les helpers et composants dupliques dans les pages React

Status: ready-to-dev

## 1. Objective

Extraire un cluster coherent de helpers et petits composants dupliques hors des pages React.
Le cluster doit converger vers un owner canonique `utils` ou feature-local.
Le comportement reste identique, sans duplication active ni AC en `PASS with limitation`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-003`
- Reason for change: `F-003` identifie des helpers repetes tels que `formatDate`, `formatPrice`, `shouldLogSupportForApiError`, `getErrorMessage` et des builders de chemins.

## 3. Domain Boundary

- Domain: `frontend-react-pages/page-helpers`
- In scope:
  - Classer les duplications de helpers formatage/erreur/path.
  - Migrer un cluster coherent vers un owner canonique.
  - Ajouter des tests unitaires sur l'owner extrait.
- Out of scope:
  - Migration de tous les composants page-local en une seule fois.
  - Refonte UI ou CSS.
  - Changement de contrat API.
- Explicit non-goals:
  - Ne pas creer de utility speculative sans consommateurs reels.
  - Ne pas garder les anciennes copies locales dans les pages migrees.
  - Ne pas accepter de `PASS with limitation`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: service-boundary-refactor
- Archetype reason: la story converge une responsabilite helper vers un owner partage teste, sans deplacement de route ou API.
- Behavior change allowed: no
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le cluster ne peut pas etre borne sans migration massive ou conservation d'une copie legacy.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests unitaires et pages prouvent le comportement runtime frontend. |
| Baseline Snapshot | yes | L'inventaire des duplications before/after borne la story. |
| Ownership Routing | yes | Chaque helper migre doit avoir un owner unique. |
| Allowlist Exception | no | Aucune duplication restante n'est autorisee dans le cluster. |
| Contract Shape | no | Aucun contrat public API/DTO n'est modifie. |
| Batch Migration | no | Un seul cluster est migre. |
| Reintroduction Guard | yes | Les anciens helpers ne doivent pas etre recollés. |
| Persistent Evidence | yes | Les artefacts before/after et evidence finale doivent rester consultables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard or Vitest guard for duplicated page helpers when implemented.
  - `frontend/src/tests/formatDate.test.ts`
  - `frontend/src/tests/BirthProfilePage.test.tsx`
- Secondary evidence:
  - scans cibles des helpers migres.
- Static scans alone are not sufficient because:
  - les pages consommatrices doivent rester couvertes par Vitest.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-092-reduire-helpers-composants-dupliques-pages-react/page-helpers-before.md`.
- Comparison after implementation: `_condamad/stories/CS-092-reduire-helpers-composants-dupliques-pages-react/page-helpers-after.md`.
- Expected invariant: zero copie locale des helpers migres dans les pages du cluster.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Formatage generique | `frontend/src/utils/formatters.ts` ou owner existant | definitions page-locales dupliquees |
| Erreurs API UI reutilisees | helper API/UI canonique apres inspection | `catch` ad hoc duplique |
| Builders de chemins admin | module feature/admin canonique | fonctions locales divergentes |

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: les duplications du cluster doivent etre supprimees, pas allowlistees.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: la story migre un cluster helper unique.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before helper audit | `_condamad/stories/CS-092-reduire-helpers-composants-dupliques-pages-react/page-helpers-before.md` | Capturer duplications du cluster. |
| After helper audit | `page-helpers-after.md` | Prouver owner unique et absence de copies locales migrees. |
| Final validation | `_condamad/stories/CS-092-reduire-helpers-composants-dupliques-pages-react/generated/10-final-evidence.md` | Persister commandes sans limitation. |

## 4i. Reintroduction Guard

- The implementation must add or update an architecture guard that fails if the forbidden surface is reintroduced.
- Architecture guard against reintroduction: tests unitaires de l'owner plus scans des anciennes signatures dans les pages migrees.
- Deterministic source: `frontend/src/tests/formatDate.test.ts` ou tests nouveaux cibles, et `rg`.
- Required forbidden examples: anciennes fonctions locales migrees, copies de formatters, `PASS with limitation`.
- Guard evidence: `npm run test -- formatDate BirthProfilePage NatalChartPage SubscriptionSettings AdminSamplePayloadsAdmin PersonasAdmin`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-003` - helpers et composants page-local dupliquent des responsabilites.
- Evidence 2: `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md#E-006` - scan de duplication helper en echec.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants frontend consultes avant cadrage.

## 6. Target State

- Le cluster choisi a un owner canonique teste.
- Les pages consomment l'owner au lieu de conserver des copies.
- Les validations passent sans legacy ni limitation.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - pas de style inline introduit en extrayant un composant.
  - `RG-049` - pas de surface legacy frontend.
  - `RG-050` - les guards frontend restent executables.
- Non-applicable invariants:
  - `RG-044` - pas de token CSS.
  - `RG-054` - pas de route admin.
- Required regression evidence:
  - `npm run test -- formatDate BirthProfilePage NatalChartPage SubscriptionSettings AdminSamplePayloadsAdmin PersonasAdmin`
  - `npm run lint`
- Allowed differences:
  - changement d'import uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le cluster est documente. | Evidence profile: `baseline_before_after_diff`; artifact `page-helpers-before.md`; command `rg -n "formatDate|formatPrice" src/pages`. |
| AC2 | Un owner canonique remplace les copies locales. | Evidence profile: `ownership_routing`; test `npm run test -- frontend/src/tests/formatDate.test.ts`. |
| AC3 | Les anciennes copies locales migrees sont absentes. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg` sur fonctions migrees. |
| AC4 | Le comportement page reste couvert. | Evidence profile: `runtime_behavior`; test `npm run test -- frontend/src/tests/BirthProfilePage.test.tsx`. |
| AC5 | Aucun legacy ne reste. | Evidence profile: `persistent_evidence`; `rg -n "PASS with limitation|legacy|fallback" generated/10-final-evidence.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline des helpers/composants du cluster. (AC: AC1)
- [ ] Task 2 - Choisir l'owner canonique existant ou minimal. (AC: AC2)
- [ ] Task 3 - Migrer les consommateurs et supprimer les copies locales. (AC: AC2, AC3)
- [ ] Task 4 - Ajouter ou adapter les tests unitaires et pages. (AC: AC4)
- [ ] Task 5 - Capturer l'after no-legacy sans limitation. (AC: AC3, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/utils/formatters.ts` si le role correspond.
- Reuse les helpers API existants avant de creer un nouveau module.
- Shared abstraction allowed only if au moins deux consommateurs reels l'utilisent dans le cluster.

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
- anciennes copies locales des helpers migres.
- `PASS with limitation` dans les preuves.
- module `legacy*`, `compat*` ou `fallback*` pour ce cluster.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Helpers formatage | `frontend/src/utils/formatters.ts` ou owner choisi | pages individuelles |
| Helpers erreur/path feature | module feature/API canonique | functions locales dupliquees |
| Tests helpers | `frontend/src/tests/*.test.ts` | verification manuelle |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md`
- `frontend/src/utils/formatters.ts`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx`
- `frontend/src/pages/admin/PersonasAdmin.tsx`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/utils/formatters.ts` - owner formatage si le cluster choisi est formatage.
- `frontend/src/pages/**/*.tsx` - remplacer copies locales du cluster par imports canoniques.
- `frontend/src/features/admin/**` - owner feature si le cluster est admin-only.

Likely tests:
- `frontend/src/tests/formatDate.test.ts`
- `frontend/src/tests/BirthProfilePage.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/SubscriptionSettings.test.tsx`
- `frontend/src/tests/AdminSamplePayloadsAdmin.test.tsx`
- `frontend/src/tests/PersonasAdmin.test.tsx`

Files not expected to change:
- `frontend/package.json` - aucune dependance.
- `backend/app/main.py` - aucun backend.
- `frontend/src/app/routes.tsx` - aucune route.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- formatDate BirthProfilePage NatalChartPage SubscriptionSettings AdminSamplePayloadsAdmin PersonasAdmin
npm run lint
rg -n "PASS with limitation|legacy|compatibility|fallback" src/utils src/pages
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-092-reduire-helpers-composants-dupliques-pages-react/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: helper partage change un format visible.
  - Guardrail: tests unitaires + tests pages cibles.
- Risk: abstraction speculative augmente la complexite.
  - Guardrail: obligation de consommateurs reels.
- Risk: copies locales restent.
  - Guardrail: scans AC3.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not create compatibility shims, aliases, fallbacks, wrappers or re-exports.
- No legacy may remain in the implemented cluster.
- No AC may be accepted as `PASS with limitation`.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-003`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-003`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`
