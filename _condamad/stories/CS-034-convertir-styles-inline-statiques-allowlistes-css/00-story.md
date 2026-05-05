# Story CS-034 convertir-styles-inline-statiques-allowlistes-css: Convertir les styles inline statiques allowlistes vers CSS

Status: ready-to-dev

## 1. Objective

Convertir un lot de styles inline statiques encore allowlistes vers des fichiers CSS appropries.
Seuls les styles dynamiques justifies par des valeurs runtime restent inline.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1411/03-story-candidates.md#SC-002`
- Reason for change: le finding `F-003` indique que 85 attributs `style=` restent dans `frontend/src/**/*.tsx`, dont des entrees statiques conservees par allowlist exacte.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components`
- In scope:
  - Classer chaque inline style touche comme `static` ou `dynamic`.
  - Migrer les styles statiques du lot vers CSS.
  - Reduire `INLINE_STYLE_EXCEPTIONS` dans `design-system-allowlist.ts`.
  - Ajouter ou ajuster les tests composant des surfaces touchees.
- Out of scope:
  - Migration de tous les inline styles restants.
  - Modification des fallbacks CSS.
  - Refonte visuelle ou changement de contenu.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas affaiblir `RG-047` ou `RG-050`.
  - Ne pas convertir les styles dynamiques runtime en classes trompeuses.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne d'exceptions inline vers CSS, avec preuve avant/apres.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu des surfaces touchees doit rester equivalent.
  - Les styles dynamiques peuvent rester inline seulement s'ils sont explicitement classes.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un style semble statique mais depend en fait d'une donnee runtime ou d'un choix UX non documente.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde doit inspecter les attributs `style=` reels des fichiers TSX. |
| Baseline Snapshot | yes | Le nombre de `style=` doit etre compare avant/apres. |
| Ownership Routing | no | Les styles restent dans la surface frontend existante. |
| Allowlist Exception | yes | Les styles dynamiques restants doivent rester allowlistes exactement. |
| Contract Shape | no | Aucun contrat API ou type public n'est touche. |
| Batch Migration | yes | Le scope est un lot de styles inline allowlistes. |
| Reintroduction Guard | yes | Aucun style inline statique non classe ne doit revenir. |
| Persistent Evidence | yes | La classification et les scans avant/apres doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard / inventaire TSX des attributs `style=` sous `frontend/src`.
  - Commande cible: `npm run test -- inline-style`.
- Secondary evidence:
  - `rg -n "style=" src -g "*.tsx"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - La garde Vitest doit comparer chaque occurrence a `INLINE_STYLE_EXCEPTIONS`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-034-convertir-styles-inline-statiques-allowlistes-css/inline-styles-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-034-convertir-styles-inline-statiques-allowlistes-css/inline-styles-after.md`
- Expected invariant:
  - Le nombre d'exceptions inline statiques diminue et aucun nouveau `style=` non classe n'apparait.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | `INLINE_STYLE_EXCEPTIONS` dynamiques | Valeur runtime. | Permanent while required. |
| `frontend/src/tests/design-system-allowlist.ts` | `INLINE_STYLE_EXCEPTIONS` statiques | Dette a convertir. | Leave allowlist after migration. |

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
| 1 | Inline styles statiques du lot | CSS adjacent | Liste dans `inline-styles-after.md` | Tests touches et `inline-style` | Scan `rg -n "style="` | Ambiguite static/dynamic |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-034-convertir-styles-inline-statiques-allowlistes-css/inline-styles-before.md` | Classer les styles touches avant migration. |
| After inventory | `_condamad/stories/CS-034-convertir-styles-inline-statiques-allowlistes-css/inline-styles-after.md` | Prouver la reduction et les exceptions restantes. |

## 4i. Reintroduction Guard

- Guard target: attribut `style=` statique absent de `INLINE_STYLE_EXCEPTIONS`.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- inline-style design-system`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md#E-011` - 85 inline style attributes restent dans `frontend/src/**/*.tsx`.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md#E-015` -
  trois fichiers deja audites ont zero inline style.
- Evidence 3: `frontend/src/tests/design-system-allowlist.ts` -
  `INLINE_STYLE_EXCEPTIONS` contient des entrees statiques candidates.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les styles statiques du lot vivent dans CSS.
- L'allowlist inline ne conserve que les exceptions dynamiques du lot.
- Les tests et scans prouvent que le nombre de `style=` baisse sans nouveau contournement.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - les styles inline statiques sont interdits hors allowlist exacte.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-044`, `RG-045`, `RG-046` - les tokens CSS peuvent etre reutilises mais ne sont pas le domaine principal.
  - `RG-048` - les fallbacks CSS sont traites par `CS-035`.
- Required regression evidence:
  - `npm run test -- inline-style design-system`, scan `rg -n "style=" src -g "*.tsx"` depuis `frontend`, `npm run lint`.
- Allowed differences:
  - Retrait d'attributs `style=` statiques et ajout de classes CSS equivalentes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les inline styles touches sont classes `static` ou `dynamic`. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "static|dynamic" inline-styles-before.md`. |
| AC2 | Les styles `static` du lot migrent hors des composants TSX. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `rg -n "style=" src -g "*.tsx"`. |
| AC3 | Les styles migres vivent dans des fichiers CSS appropries. | Evidence profile: `component_behavior_test`; command: `npm run test -- inline-style`. |
| AC4 | `INLINE_STYLE_EXCEPTIONS` est reduite pour les entrees migrees. | Evidence profile: `allowlist_register_validated`; `npm run test -- inline-style`. |
| AC5 | Aucun nouveau inline style non classe n'est ajoute. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system inline-style`. |
| AC6 | Le frontend reste lintable. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inventorier et classer les inline styles du lot (AC: AC1)
- [ ] Task 2 - Creer ou reutiliser les classes CSS adjacentes pour les styles statiques (AC: AC2, AC3)
- [ ] Task 3 - Mettre a jour l'allowlist apres migration des entrees statiques (AC: AC4)
- [ ] Task 4 - Adapter les tests des surfaces touchees si le rendu structurel change (AC: AC3)
- [ ] Task 5 - Executer scans, guards et lint (AC: AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Fichiers CSS adjacents existants quand ils existent.
  - `frontend/src/tests/inline-style-policy.test.ts` pour la garde.
  - Variables CSS existantes de `design-tokens.css`, `theme.css` ou `premium-theme.css`.
- Do not recreate:
  - Un fichier CSS global pour une surface locale.
  - Des classes dupliquees si une classe composant existe deja.
- Shared abstraction allowed only if:
  - Deux surfaces du meme composant reutilisent exactement le meme pattern.

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

- `style=` statique dans les fichiers touches
- entree `INLINE_STYLE_EXCEPTIONS` conservee sans classification dynamique
- style inline ajoute pour remplacer une classe CSS

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Styles statiques composants/pages | CSS adjacent ou feuille de style existante | attribut `style=` |
| Exceptions inline dynamiques | `frontend/src/tests/design-system-allowlist.ts` | exception implicite dans TSX |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/settings/AccountSettings.tsx`
- `frontend/src/pages/AstrologerProfilePage.tsx`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/components/prediction/TurningPointsList.tsx` - retrait d'un lot statique si selectionne.
- `frontend/src/components/prediction/TurningPointsList.css` - CSS adjacent si le composant n'a pas encore de feuille dediee.
- `frontend/src/pages/PrivacyPolicyPage.tsx` - retrait d'un lot statique si selectionne.
- `frontend/src/pages/PrivacyPolicyPage.css` - CSS adjacent si selectionne.
- `frontend/src/pages/settings/AccountSettings.tsx` - retrait d'un lot statique si selectionne.
- `frontend/src/tests/design-system-allowlist.ts` - reduction des exceptions.
- `_condamad/stories/CS-034-convertir-styles-inline-statiques-allowlistes-css/inline-styles-before.md` - baseline.
- `_condamad/stories/CS-034-convertir-styles-inline-statiques-allowlistes-css/inline-styles-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/inline-style-policy.test.ts` - garde principale.
- Tests existants des pages/composants touches quand disponibles.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/styles/css-fallback-allowlist.md` - hors story.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- inline-style design-system
rg -n "style=" src -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-034-convertir-styles-inline-statiques-allowlistes-css/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-034-convertir-styles-inline-statiques-allowlistes-css/00-story.md
```

## 22. Regression Risks

- Risk: un style dynamique est migre en CSS et perd sa valeur runtime.
  - Guardrail: classification obligatoire static/dynamic avant edition.
- Risk: un fichier TSX conserve une exception statique par oubli.
  - Guardrail: `RG-047` et reduction explicite de `INLINE_STYLE_EXCEPTIONS`.

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

- `_condamad/audits/frontend-design-system/2026-05-05-1411/03-story-candidates.md#SC-002` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1411/02-finding-register.md#F-003` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1411/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
