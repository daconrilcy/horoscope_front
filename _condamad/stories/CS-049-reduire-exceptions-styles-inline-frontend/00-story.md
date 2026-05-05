# Story CS-049 reduire-exceptions-styles-inline-frontend: Reduire les exceptions de styles inline frontend

Status: ready-to-dev

## 1. Objective

Classifier 100% des styles inline actifs listes par `F-004`.
Chaque style statique removable doit partir vers CSS/custom properties.
Seuls les ponts dynamiques ou style-prop justifies restent dans les allowlists.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-003`
- Reason for change: 16 exceptions inline restent dans 10 fichiers TSX et peuvent encore cacher des decisions visuelles statiques hors CSS.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components`
- In scope:
  - Inspecter les 10 fichiers TSX F-004.
  - Classer chaque attribut `style` comme `dynamic-bridge`, `removable-static-style`, ou `component-style-prop-pass-through`.
  - Migrer tous les `removable-static-style` vers le fichier CSS approprie.
  - Mettre a jour `inline-style-allowlist.ts` et `design-system-allowlist.ts` uniquement apres les changements.
- Out of scope:
  - Refactor de comportement React ou changement de props publiques.
  - Migration des fallbacks CSS.
  - Migration globale des hardcoded values CSS.
- Explicit non-goals:
  - Ne pas affaiblir `RG-047` ou `RG-050`.
  - Ne pas remplacer un style inline statique par un autre style inline.
  - Ne pas creer d'exception allowlist sans justification exacte.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: plusieurs surfaces TSX sont migrees par lot vers CSS ou exceptions exactes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit rester equivalent pour les styles statiques deplaces.
  - Les styles dynamiques conservent leur comportement runtime.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un style inline semble necessaire a une API publique de composant ou a une integration externe.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards inline-style/design-system verifient les exceptions executables. |
| Baseline Snapshot | yes | Chaque inline actuel doit etre classe avant/apres. |
| Ownership Routing | yes | Les styles statiques doivent appartenir aux CSS correspondants. |
| Allowlist Exception | yes | Les exceptions dynamiques restantes sont allowlistees exactement. |
| Contract Shape | no | Aucun contrat API ou type public ne doit changer. |
| Batch Migration | yes | La story traite un lot multi-composants. |
| Reintroduction Guard | yes | Les styles statiques inline ne doivent pas revenir. |
| Persistent Evidence | yes | La classification before/after doit rester dans le dossier story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/inline-style-allowlist.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
  - `frontend/src/tests/design-system-guards.test.ts`
- Secondary evidence:
  - Scan `rg -n "style=\\{" src -g "*.tsx"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - Chaque hit doit etre classe par intention runtime, pas seulement compte.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-049-reduire-exceptions-styles-inline-frontend/inline-styles-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-049-reduire-exceptions-styles-inline-frontend/inline-styles-after.md`
- Expected invariant:
  - Aucun `removable-static-style` ne reste en inline; toute entree restante est dynamique ou pass-through justifie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Style visuel statique | CSS du composant/layout/page | attribut `style` TSX |
| Pont dynamique runtime | inline allowliste exact | classe CSS speculative |
| Style-prop pass-through | API composant documentee/allowlistee | exception implicite |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/inline-style-allowlist.ts` | inline styles restants | Dynamic bridge or style-prop pass-through. | Permanent only while dynamic/pass-through remains true. |
| `frontend/src/tests/design-system-allowlist.ts` | exceptions design-system liees | Synchronisation executable. | Must match final scan. |

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
| F-004 inline batch | static style entries | component CSS or dynamic allowlist | listed TSX components | inline-style guards | before/after scan | API ambiguity |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before classification | `_condamad/stories/CS-049-reduire-exceptions-styles-inline-frontend/inline-styles-before.md` | Classer 100% des hits initiaux. |
| After classification | `_condamad/stories/CS-049-reduire-exceptions-styles-inline-frontend/inline-styles-after.md` | Prouver que seuls les cas dynamiques/pass-through restent. |

## 4i. Reintroduction Guard

- Guard target: static inline styles and exact allowlist synchronization.
- Architecture guard against reintroduction required: `npm run test -- inline-style design-system`.
- Guard evidence: Evidence profile: `reintroduction_guard`; tests plus scan `style={` final.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md#F-004` - 16 inline style exceptions across 10 TSX files.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-003` - classification and migration required.
- Evidence 3: `frontend/src/tests/inline-style-allowlist.ts` - executable inline allowlist.
- Evidence 4: `frontend/src/tests/design-system-allowlist.ts` - shared design-system allowlist.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consulted before cadrage.

## 6. Target State

- 100% des inline styles initiaux ont une classification durable.
- Les styles statiques removable vivent dans CSS, pas en TSX.
- Les allowlists ne contiennent que des exceptions dynamiques/pass-through exactes.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - les styles inline statiques sont interdits.
  - `RG-050` - les allowlists design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-048` - fallbacks CSS hors scope.
  - `RG-049` - legacy selectors hors scope.
- Required regression evidence:
  - `npm run test -- inline-style design-system`, scan `style={` final, artefacts before/after.
- Allowed differences:
  - Diminution des entrees allowlistees; ajout de classes CSS locales pour styles statiques.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Chaque inline style initial est classe dans `inline-styles-before.md`. | Evidence profile: `baseline_snapshot`; `rg -n "style=\\{" src -g "*.tsx"`. |
| AC2 | Aucun style classe `removable-static-style` ne reste en TSX. | Evidence profile: `negative_scan`; `rg -n "style=\\{" src -g "*.tsx"`. |
| AC3 | Les styles statiques migres vivent dans des fichiers CSS appropries. | Evidence profile: `code_review_guard`; `npm run test -- inline-style design-system`. |
| AC4 | Les allowlists inline/design-system correspondent aux exceptions restantes. | Evidence profile: `allowlist_guard`; `npm run test -- inline-style design-system`. |
| AC5 | Aucun comportement composant public n'est change. | Evidence profile: `frontend_test`; `npm run test -- inline-style design-system`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer et classifier tous les inline styles F-004 (AC: AC1)
- [ ] Task 2 - Migrer chaque style statique removable vers CSS existant ou nouveau CSS local approprie (AC: AC2, AC3)
- [ ] Task 3 - Conserver uniquement les ponts dynamiques/pass-through justifies (AC: AC2)
- [ ] Task 4 - Synchroniser les allowlists apres modification du code (AC: AC4)
- [ ] Task 5 - Capturer l'etat after et executer les validations (AC: AC1, AC2, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - CSS deja associe aux composants modifies.
  - `inline-style-allowlist.ts` et `design-system-allowlist.ts`.
  - Variables CSS existantes avant toute creation.
- Do not recreate:
  - Une prop de style parallele pour contourner CSS.
  - Une classe utilitaire globale pour un cas unique.
- Shared abstraction allowed only if:
  - Au moins deux composants du lot partagent le meme besoin et l'owner CSS est clair.

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

- Nouveau attribut `style` statique.
- Allowlist wildcard ou entree dossier.
- Migration vers inline CSS custom property sans justification dynamique.

## 11. Removal Classification Rules

Classification must be deterministic:

- `dynamic-bridge`: depends on runtime geometry, runtime color, measurement, or CSS custom property value.
- `removable-static-style`: constant visual style expressible in CSS.
- `component-style-prop-pass-through`: intentional component API forwarding style props.
- `needs-user-decision`: ambiguity remains and must block the item.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `dynamic-bridge` | `keep` | Must remain exact and allowlisted. |
| `removable-static-style` | `delete` | Must move to CSS. |
| `component-style-prop-pass-through` | `keep` | Must be documented as API bridge. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation for that item. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/CS-049-reduire-exceptions-styles-inline-frontend/inline-styles-before.md`
- `_condamad/stories/CS-049-reduire-exceptions-styles-inline-frontend/inline-styles-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Styles statiques composants | CSS du composant | attribut `style` TSX |
| Exceptions inline dynamiques | `inline-style-allowlist.ts` | inline non reference |
| Exceptions design-system | `design-system-allowlist.ts` | divergence allowlist |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving static inline style under a renamed prop
- moving static style to another inline object
- broad allowlist retention

## 15. External Usage Blocker

If an item is classified as `component-style-prop-pass-through` or `needs-user-decision`, public API risk must be documented before keeping it.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/layouts/TwoColumnLayout.tsx`
- `frontend/src/components/DomainRankingCard.tsx`
- `frontend/src/components/TurningPointCard.tsx`
- `frontend/src/components/ui/Badge/Badge.tsx`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx`
- `frontend/src/components/prediction/CategoryGrid.tsx`
- `frontend/src/components/prediction/DayPredictionCard.tsx`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/prediction/TimelineRail.tsx`
- `frontend/src/features/chat/components/AstrologerPickerModal.tsx`
- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/inline-style-allowlist.ts` - exceptions finales.
- `frontend/src/tests/design-system-allowlist.ts` - synchronisation.
- TSX files listed in Files to Inspect First - remove static inline entries when classified removable.
- CSS files adjacent to modified TSX files - receive migrated static styles.
- `_condamad/stories/CS-049-reduire-exceptions-styles-inline-frontend/inline-styles-before.md` - baseline.
- `_condamad/stories/CS-049-reduire-exceptions-styles-inline-frontend/inline-styles-after.md` - final evidence.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/inline-style-allowlist.ts`

Files not expected to change:

- `backend/` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/styles/css-fallback-allowlist.md` - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- inline-style design-system
npm run lint
rg -n "style=\{" src -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-049-reduire-exceptions-styles-inline-frontend/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-049-reduire-exceptions-styles-inline-frontend/00-story.md
```

## 22. Regression Risks

- Risk: un style dynamique est deplace en CSS et perd sa valeur runtime.
  - Guardrail: classification `dynamic-bridge` bloque la migration.
- Risk: une allowlist cache un style statique restant.
  - Guardrail: AC2 et AC4 exigent zero static keep et tests.
- Risk: migration visuelle partielle.
  - Guardrail: AC1 couvre 100% des hits initiaux.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-003` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1942/02-finding-register.md#F-004` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md#F-004` - file list and current count.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
