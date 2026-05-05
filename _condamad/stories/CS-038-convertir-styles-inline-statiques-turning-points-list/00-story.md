# Story CS-038 convertir-styles-inline-statiques-turning-points-list: Convertir les styles inline statiques de TurningPointsList vers CSS

Status: done

## 1. Objective

Convertir 100% des styles inline statiques de `TurningPointsList.tsx` vers une feuille CSS appropriee.
Le comportement React et les styles dynamiques reels ne doivent pas changer.
La story doit reduire l'allowlist exacte et prouver qu'aucun `style=` statique ne reste.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1501/03-story-candidates.md#SC-002`
- Reason for change: le finding `F-003` indique 68 attributs `style=` restants dans `frontend/src`.
  `TurningPointsList.tsx` est le composant prioritaire pour convertir les styles statiques vers CSS.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components/prediction`
- In scope:
  - Classer chaque attribut `style=` de `frontend/src/components/prediction/TurningPointsList.tsx` comme `static` ou `dynamic`.
  - Migrer tous les styles `static` de ce fichier vers CSS adjacent.
  - Conserver seulement les styles dynamiques justifies, si un tel cas existe dans ce composant.
  - Reduire `INLINE_STYLE_EXCEPTIONS` et `INLINE_STYLE_DYNAMIC_ALLOWLIST` pour les entrees migrees.
  - Valider `TurningPointsEnriched.test.tsx` et les guards inline-style.
- Out of scope:
  - Migration des styles inline de `AccountSettings.tsx`, `AstrologerProfilePage.tsx` ou `NotFoundPage.tsx`.
  - Modification de la logique de prediction, i18n ou enrichissement.
  - Reduction des fallbacks CSS.
  - Refonte visuelle.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas affaiblir `RG-047` ou `RG-050`.
  - Ne pas deplacer de logique metier vers CSS ou tests.
  - Ne pas garder une entree allowlistee statique sous pretexte de compatibilite.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne d'exceptions inline d'un composant vers CSS.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu structurel et les textes de `TurningPointsList` doivent rester equivalents.
  - Les callbacks, conditions enrichies/legacy et calculs de labels ne doivent pas changer.
  - Seules les classes CSS et imports CSS necessaires peuvent etre ajoutes.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un style semble dynamique et ne peut pas etre classe avec certitude depuis le code.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde doit inspecter les attributs `style=` reels des fichiers TSX. |
| Baseline Snapshot | yes | Le nombre de `style=` de `TurningPointsList.tsx` doit etre compare avant/apres. |
| Ownership Routing | no | Les styles restent dans le composant prediction et sa feuille CSS adjacente. |
| Allowlist Exception | yes | Les exceptions dynamiques restantes doivent etre exactes et justifiees. |
| Contract Shape | no | Aucun contrat API, DTO, payload, type ou schema n'est modifie. |
| Batch Migration | yes | Le scope est le lot complet des inline styles de `TurningPointsList.tsx`. |
| Reintroduction Guard | yes | Aucun style inline statique ne doit revenir dans ce composant. |
| Persistent Evidence | yes | La classification et les scans avant/apres doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard: `frontend/src/tests/inline-style-policy.test.ts`.
  - Executable allowlist guard: `frontend/src/tests/design-system-guards.test.ts`.
- Secondary evidence:
  - `rg -n "style=\\{" src/components/prediction/TurningPointsList.tsx` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - La garde doit verifier que chaque occurrence restante est presente dans l'allowlist exacte.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-038-convertir-styles-inline-statiques-turning-points-list/inline-styles-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-038-convertir-styles-inline-statiques-turning-points-list/inline-styles-after.md`
- Expected invariant:
  - `TurningPointsList.tsx` ne contient plus aucun inline style statique; les exceptions restantes sont dynamiques ou absentes.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `design-system-allowlist.ts` | `INLINE_STYLE_EXCEPTIONS` for `TurningPointsList.tsx` | Dette statique a convertir. | Must leave allowlist after migration. |
| `frontend/src/tests/inline-style-allowlist.ts` | `INLINE_STYLE_DYNAMIC_ALLOWLIST` | Valeurs runtime exactes seulement. | Permanent only for true dynamic entries. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| TurningPointsList | `style=` static attributes | CSS adjacent | `TurningPointsList.tsx` | targeted Vitest | zero static `style=` | dynamic ambiguity |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `inline-styles-before.md` | Classer chaque `style=` du composant avant migration. |
| After inventory | `inline-styles-after.md` | Prouver la conversion des styles statiques et les exceptions finales. |

## 4i. Reintroduction Guard

- Guard target: `style=` statique dans `frontend/src/components/prediction/TurningPointsList.tsx`.
- Architecture guard required: `frontend/src/tests/inline-style-policy.test.ts` must fail when a static inline style is not in the exact executable policy.
- Guard evidence: Evidence profile: `reintroduction_guard`;
  `npm run test -- inline-style design-system TurningPointsEnriched`
  and `rg -n "style=\\{" src/components/prediction/TurningPointsList.tsx`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md#E-009` - 68 attributs `style=` restent dans `frontend/src`.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md#E-010` - `TurningPointsList.tsx` contient encore de la dette inline statique.
- Evidence 3: `frontend/src/tests/design-system-allowlist.ts` - plusieurs entrees exactes ciblent `components/prediction/TurningPointsList.tsx`.
- Evidence 4: `frontend/src/components/prediction/TurningPointsList.tsx` -
  les styles inline visibles sont des declarations de layout, couleur et typographie statiques,
  sauf preuve contraire a documenter.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `TurningPointsList.tsx` utilise des classes CSS pour les styles statiques.
- Une feuille CSS adjacente porte les declarations statiques, avec variables existantes et sans style inline.
- Les allowlists ne conservent aucune entree statique pour `TurningPointsList.tsx`.
- Les tests prouvent que les branches enrichies et legacy continuent de rendre correctement.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - les styles inline statiques sont interdits hors allowlist exacte.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-044`, `RG-045`, `RG-046` - les tokens et roles peuvent etre reutilises mais ne sont pas le domaine principal.
  - `RG-048` - les fallbacks CSS sont traites par `CS-039`.
  - `RG-049` - aucun selecteur legacy n'est cree par cette story.
- Required regression evidence:
  - `npm run test -- inline-style design-system TurningPointsEnriched`, scan cible `rg -n "style=\\{" src/components/prediction/TurningPointsList.tsx`, `npm run lint`.
- Allowed differences:
  - Conversion d'attributs `style=` statiques en classes CSS equivalentes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Chaque `style=` initial est classe `static` ou `dynamic`. | Evidence profile: `baseline_before_after_diff`; `rg -n "static|dynamic" inline-styles-before.md`. |
| AC2 | Tous les styles `static` du composant sont portes par CSS. | Evidence profile: `targeted_forbidden_symbol_scan`; targeted `rg` on `TurningPointsList.tsx`. |
| AC3 | Le CSS reutilise les variables existantes. | Evidence profile: `reintroduction_guard`; command: `npm run test -- design-system inline-style`. |
| AC4 | Les entrees `INLINE_STYLE_EXCEPTIONS` du composant sont reduites. | Evidence profile: `allowlist_register_validated`; `npm run test -- inline-style`. |
| AC5 | Les tests `TurningPointsEnriched` passent. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- TurningPointsEnriched`. |
| AC6 | Le frontend reste lintable. | Evidence profile: `frontend_typecheck_no_orphan`; command: `npm run lint`. |

## 8. Implementation Tasks

- [x] Task 1 - Inventorier et classer tous les `style=` de `TurningPointsList.tsx` (AC: AC1)
- [x] Task 2 - Creer ou reutiliser une feuille CSS adjacente pour les declarations statiques (AC: AC2, AC3)
- [x] Task 3 - Remplacer les styles statiques par des classes explicites dans le TSX (AC: AC2, AC5)
- [x] Task 4 - Reduire `INLINE_STYLE_EXCEPTIONS` et `INLINE_STYLE_DYNAMIC_ALLOWLIST` pour ce composant (AC: AC4)
- [x] Task 5 - Capturer l'inventaire apres et les scans cibles (AC: AC2, AC3, AC4)
- [x] Task 6 - Executer tests et lint (AC: AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/components/prediction/TurningPointsList.tsx` comme unique composant.
  - `frontend/src/tests/TurningPointsEnriched.test.tsx` pour la couverture comportementale existante.
  - `frontend/src/tests/inline-style-policy.test.ts` pour la garde inline.
  - Variables CSS existantes de `design-tokens.css`, `theme.css` et `premium-theme.css`.
- Do not recreate:
  - Un composant parallele pour les turning points.
  - Un fichier CSS global pour ce composant local.
  - Une nouvelle allowlist locale.
- Shared abstraction allowed only if:
  - Deux elements du composant reutilisent exactement le meme style et le nom de classe reste specifique au composant.

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

- `style=` statique dans `frontend/src/components/prediction/TurningPointsList.tsx`
- entree `INLINE_STYLE_EXCEPTIONS` statique pour `components/prediction/TurningPointsList.tsx`
- nouveau composant `TurningPointsListLegacy`
- CSS inline via prop `style` pour remplacer une classe

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Styles statiques TurningPointsList | `frontend/src/components/prediction/TurningPointsList.css` or adjacent existing CSS | attribut `style=` dans TSX |
| Exceptions inline dynamiques | `frontend/src/tests/inline-style-allowlist.ts` | exception implicite dans le composant |
| Guard executable inline | `frontend/src/tests/inline-style-policy.test.ts` | validation manuelle seulement |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/tests/TurningPointsEnriched.test.tsx`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/components/prediction/TurningPointsList.tsx` - conversion des styles inline statiques.
- `frontend/src/components/prediction/TurningPointsList.css` - ajout ou modification du CSS adjacent.
- `frontend/src/tests/design-system-allowlist.ts` - reduction des exceptions inline exactes.
- `frontend/src/tests/inline-style-allowlist.ts` - conservation uniquement d'eventuelles exceptions dynamiques.
- `_condamad/stories/CS-038-convertir-styles-inline-statiques-turning-points-list/inline-styles-before.md` - baseline.
- `_condamad/stories/CS-038-convertir-styles-inline-statiques-turning-points-list/inline-styles-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/TurningPointsEnriched.test.tsx` - couverture composant.
- `frontend/src/tests/inline-style-policy.test.ts` - garde inline.
- `frontend/src/tests/design-system-guards.test.ts` - garde design-system.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/pages/settings/AccountSettings.tsx` - hors lot.
- `frontend/src/pages/AstrologerProfilePage.tsx` - hors lot.
- `frontend/src/pages/NotFoundPage.tsx` - hors lot.
- `frontend/src/styles/css-fallback-allowlist.md` - hors story.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- TurningPointsEnriched
npm run test -- inline-style design-system
rg -n "style=\\{" src/components/prediction/TurningPointsList.tsx
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-038-convertir-styles-inline-statiques-turning-points-list/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-038-convertir-styles-inline-statiques-turning-points-list/00-story.md
```

## 22. Regression Risks

- Risk: un style dynamique est migre en CSS et perd sa valeur runtime.
  - Guardrail: classification obligatoire `static` ou `dynamic` avant edition.
- Risk: le rendu legacy ou enrichi diverge apres extraction CSS.
  - Guardrail: `npm run test -- TurningPointsEnriched`.
- Risk: l'allowlist conserve une entree statique par oubli.
  - Guardrail: `RG-047` et `npm run test -- inline-style`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Respect the project style rule: no inline style for static styling.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1501/03-story-candidates.md#SC-002` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1501/02-finding-register.md#F-003` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1501/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
