# Story CS-090 extraire-domaine-feature-admin-prompts: Extraire le domaine feature admin-prompts hors de la page monolithique

Status: ready-to-dev

## 1. Objective

Transformer `AdminPromptsPage` en conteneur de route type qui compose des owners feature `admin-prompts`.
Le comportement utilisateur des routes prompts reste preserve.
Aucun legacy, shim, alias, fallback ou AC limitee ne peut rester apres implementation.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-001`
- Reason for change: `F-001` identifie `AdminPromptsPage.tsx` comme monolithe actif de 3035 lignes avec `// @ts-nocheck`.

## 3. Domain Boundary

- Domain: `frontend-react-pages/admin-prompts`
- In scope:
  - Extraire un premier lot coherent du domaine `admin-prompts` vers `frontend/src/features/admin-prompts/**`.
  - Retirer `// @ts-nocheck` de la slice migree et typer les props/hooks publics.
  - Preserver les sous-routes et tests `AdminPromptsRouting`.
- Out of scope:
  - Refonte visuelle des pages admin.
  - Migration de tous les domaines admin non prompts.
  - Changement backend ou contrat API.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044` a `RG-054`.
  - Ne pas garder l'ancien owner via wrapper, re-export ou duplicate implementation.
  - Ne pas accepter de `PASS with limitation`.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story retire les facades de responsabilites conservees dans la page monolithique apres extraction vers l'owner feature.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les routes et interactions prompts existantes restent fonctionnellement equivalentes.
  - Les changements autorises sont la structure, le typage et la suppression de dette `@ts-nocheck`.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une responsabilite prompts ne peut pas etre extraite sans conserver un chemin legacy ou une AC limitee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests React de routes et flux prompts prouvent le comportement runtime frontend. |
| Baseline Snapshot | yes | Le before/after prouve la reduction du monolithe et de `@ts-nocheck`. |
| Ownership Routing | yes | Les responsabilites doivent avoir un owner feature explicite. |
| Allowlist Exception | yes | Les exceptions temporaires doivent etre exactes, sinon interdites. |
| Contract Shape | no | Aucun contrat API ou DTO n'est modifie. |
| Batch Migration | no | Le lot est unique et coherent, pas une migration batch multi-surface. |
| Reintroduction Guard | yes | Le monolithe et `@ts-nocheck` ne doivent pas revenir. |
| Persistent Evidence | yes | Les artefacts before/after et evidence finale doivent rester consultables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard or Vitest guard for page architecture when implemented.
  - `frontend/src/tests/AdminPromptsPage.test.tsx`
  - `frontend/src/tests/AdminPromptsRouting.test.tsx`
  - `frontend/src/tests/AdminPromptsCatalogFlow.test.tsx`
- Secondary evidence:
  - scans cibles sur `AdminPromptsPage.tsx` et `frontend/src/features/admin-prompts`.
- Static scans alone are not sufficient because:
  - les sous-routes et interactions prompts doivent rester prouvees par Vitest.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/admin-prompts-before.md`.
- Comparison after implementation: `_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/admin-prompts-after.md`.
- Expected invariant: la page route compose des owners feature, et la slice migree ne conserve pas `@ts-nocheck`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Route container admin prompts | `frontend/src/pages/admin/AdminPromptsPage.tsx` | logique feature profonde |
| Composants et hooks prompts | `frontend/src/features/admin-prompts/**` | helpers locaux dupliques dans la page |
| Tests de routage prompts | `frontend/src/tests/AdminPromptsRouting.test.tsx` | tests encodant une facade legacy |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/pages/admin/AdminPromptsPage.tsx` | toute exception `@ts-nocheck` restante | interdite pour la slice migree | doit etre supprimee ou bloquer l'AC |

Rules:
- no wildcard;
- no folder-wide exception;
- no compatibility wrapper;
- no exception can justify `PASS with limitation`.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected beyond local TypeScript props.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: le lot doit rester une extraction coherent admin-prompts, pas une migration batch transverse.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before prompts audit | `_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/admin-prompts-before.md` | Capturer responsabilites et symboles avant extraction. |
| After prompts audit | `_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/admin-prompts-after.md` | Prouver ownership final et absence de duplication active. |
| Final validation | `_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/generated/10-final-evidence.md` | Persister commandes et absence de limitation. |

## 4i. Reintroduction Guard

- The implementation must add or update an architecture guard that fails if the forbidden surface is reintroduced.
- Architecture guard against reintroduction: un test/scan doit echouer si `AdminPromptsPage.tsx` regagne `@ts-nocheck` ou une responsabilite migree.
- Deterministic source: forbidden symbols in prompts tests and targeted `rg` scan.
- Required forbidden examples: `// @ts-nocheck`, re-export legacy depuis la page vers feature, composant migre recopie dans la page.
- Guard evidence: `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow legacy-style design-system`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-001` - `AdminPromptsPage` possede plusieurs responsabilites et `@ts-nocheck`.
- Evidence 2: `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md#E-003` - `AdminPromptsPage.tsx` est le plus grand fichier page audite.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants frontend consultes avant cadrage.

## 6. Target State

- `AdminPromptsPage.tsx` reste le conteneur de route et ne duplique pas la logique feature migree.
- Les composants/hooks extraits ont des types explicites et tests cibles.
- Aucun legacy, fallback, alias ou limitation n'est utilise pour passer l'implementation.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - aucun style inline statique ne doit etre introduit.
  - `RG-049` - aucune surface legacy frontend ne doit etre creee.
  - `RG-050` - les guards design-system existants restent executables.
  - `RG-054` - les redirects admin legacy ne doivent pas revenir pendant le travail admin.
- Non-applicable invariants:
  - `RG-044` - aucun namespace token global n'est attendu.
  - `RG-053` - la story ne touche pas les contrats runtime consultation/prediction.
- Required regression evidence:
  - `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow legacy-style design-system`
  - `npm run lint`
- Allowed differences:
  - structure interne et ownership feature uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Baseline initial. | Evidence profile: `baseline_before_after_diff`; artifact `admin-prompts-before.md`; command `rg -n "@ts-nocheck" AdminPromptsPage.tsx`. |
| AC2 | La slice migree vit sous un owner `features/admin-prompts` sans duplication active dans la page. | Evidence profile: `ownership_routing`; diff + `rg` des symboles migres. |
| AC3 | `// @ts-nocheck` est retire sans nouveau `@ts-ignore`. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "@ts-nocheck|@ts-ignore" src/pages/admin`. |
| AC4 | Le flux prompts reste couvert. | Evidence profile: `runtime_behavior`; Runtime evidence: `npm run test -- frontend/src/tests/AdminPromptsPage.test.tsx`. |
| AC5 | Aucun legacy ne reste. | Evidence profile: `persistent_evidence`; `rg -n "PASS with limitation|legacy|fallback" generated/10-final-evidence.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline before du monolithe prompts. (AC: AC1)
- [ ] Task 2 - Choisir une slice coherent et creer son owner feature. (AC: AC2, AC3)
- [ ] Task 3 - Remplacer les definitions locales par la composition feature sans wrapper legacy. (AC: AC2, AC4)
- [ ] Task 4 - Ajouter ou adapter les tests de la slice et du routage prompts. (AC: AC3, AC4)
- [ ] Task 5 - Capturer l'after et les scans No Legacy sans limitation. (AC: AC1, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/pages/admin/AdminPromptEditorPanel.tsx`, `AdminPromptsLogicGraph.tsx`, `AdminPromptCatalogNodeModal.tsx` et projections existantes si elles sont canoniques.
- Do not recreate hooks, DTOs, formatters or projections already present for prompts.
- Shared abstraction allowed only if elle remplace une duplication constatee dans la slice.

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
- `// @ts-nocheck` dans la slice migree.
- re-export depuis `AdminPromptsPage.tsx` pour preserver un ancien import.
- nouveau wrapper de compatibilite sous `frontend/src/pages/admin`.

## 11. Removal Classification Rules

- `canonical-active`: item est l'owner feature ou route container canonique encore requis.
- `external-active`: item prouve consomme hors repo ou par contrat public; bloque la suppression silencieuse.
- `historical-facade`: responsabilite conservee dans `AdminPromptsPage.tsx` uniquement pour l'ancien owner monolithique.
- `dead`: copie locale ou helper sans consommateur apres extraction.
- `needs-user-decision`: ambiguite apres scans et tests.

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete` | Must be deleted under the no-legacy decision. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:
- `_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/admin-prompts-after.md`

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Route prompts admin | `frontend/src/pages/admin/AdminPromptsPage.tsx` | composants feature locaux dans la page |
| Feature prompts | `frontend/src/features/admin-prompts/**` | duplications page-locales |
| Evidence prompts | story before/after | preuves manuelles non persistantes |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.
Forbidden: wrapper component, compatibility alias, duplicate local helper, soft-disable behavior, re-export.

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted without a user decision.
Implementation must stop and record exact external evidence, required decision, and risk.
Without such proof, the no-legacy decision requires deletion of historical facades in the migrated slice.

## 17. Generated Contract Check

- OpenAPI path absence: no backend OpenAPI path may change for this frontend-only removal.
- Generated artifact absence: if a route manifest, schema, public contract or generated client exists, prove removed facades are absent.
- Required evidence: `npm run lint` and targeted scans for removed exported symbols/import paths.

## 18. Files to Inspect First

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `frontend/src/tests/AdminPromptsRouting.test.tsx`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/pages/admin/AdminPromptsPage.tsx` - reduire au role de conteneur.
- `frontend/src/features/admin-prompts/**` - owner feature extrait.
- `frontend/src/pages/admin/AdminPromptsPage.css` - uniquement si une classe suit la slice extraite, sans style inline.

Likely tests:
- `frontend/src/tests/AdminPromptsPage.test.tsx` - comportement conteneur.
- `frontend/src/tests/AdminPromptsRouting.test.tsx` - routes prompts.
- `frontend/src/tests/AdminPromptsCatalogFlow.test.tsx` - flux catalogue.

Files not expected to change:
- `frontend/package.json` - aucune dependance.
- `backend/app/main.py` - aucun backend.
- `frontend/src/app/routes.tsx` - pas de changement de contrat de route attendu.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow legacy-style design-system
npm run lint
rg -n "@ts-nocheck|@ts-ignore|PASS with limitation" src/pages/admin src/features/admin-prompts
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: extraction change les sous-routes prompts.
  - Guardrail: tests `AdminPromptsRouting` et baseline after.
- Risk: duplication temporaire conserve un second owner actif.
  - Guardrail: AC2 et scans des symboles migres.
- Risk: `@ts-nocheck` est conserve pour passer vite.
  - Guardrail: AC3 bloque l'implementation.

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

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md#SC-001`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md#F-001`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`
