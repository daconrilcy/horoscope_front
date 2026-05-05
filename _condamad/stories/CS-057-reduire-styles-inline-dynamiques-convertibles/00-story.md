# Story CS-057 reduire-styles-inline-dynamiques-convertibles: Reduire les styles inline dynamiques convertibles

Status: ready-to-dev

## 1. Objective

Convertir les exceptions de styles inline qui peuvent devenir des classes CSS ou des ponts par proprietes CSS custom.
La geometrie runtime et le contrat public `style` de `Skeleton` doivent rester preserves.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-002`
- Reason for change: `F-003` indique 14 attributs `style` restants dans 9 fichiers TSX, exacts mais encore hors ownership CSS.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components`
- In scope:
  - Classer chaque style inline restant comme `runtime-geometry`, `css-custom-property-bridge`, `color-bridge` ou `style-prop-pass-through`.
  - Deplacer les declarations visuelles convertibles vers les fichiers CSS existants.
  - Mettre a jour `frontend/src/tests/inline-style-allowlist.ts` et `frontend/src/tests/design-system-allowlist.ts` apres les changements.
  - Preserver le pass-through `style` de `Skeleton` sauf decision explicite.
- Out of scope:
  - Refonte d'API publique des composants UI.
  - Migration des fallbacks CSS ou selectors legacy.
  - Suppression des styles inline de geometrie runtime non representables en CSS statique.
- Explicit non-goals:
  - Ne pas affaiblir `RG-047` ou `RG-050`.
  - Ne pas transformer un style inline legitime en classe qui perd une valeur runtime.
  - Ne pas supprimer le contrat `Skeleton` `style` sans decision produit/API.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot d'exceptions inline avec baseline, classification et allowlists synchronisees.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les composants doivent conserver leur rendu et leurs valeurs dynamiques.
  - Les declarations purement visuelles converties doivent sortir de TSX vers CSS.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un style inline represente un contrat public de composant, une geometrie runtime, ou un pass-through volontaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards `inline-style` et `design-system` prouvent l'inventaire executable. |
| Baseline Snapshot | yes | Les 14 exceptions doivent etre capturees avant/apres. |
| Ownership Routing | yes | Les styles visuels doivent appartenir aux CSS des composants ou a l'allowlist. |
| Allowlist Exception | yes | Les exceptions restantes doivent rester exactes. |
| Contract Shape | yes | Le contrat frontend `style` de `Skeleton` et les props dynamiques doivent etre explicitement preserves. |
| Batch Migration | yes | Le lot couvre plusieurs composants TSX/CSS. |
| Reintroduction Guard | yes | Les styles inline retires ne doivent pas revenir non classes. |
| Persistent Evidence | yes | Classification et before/after doivent rester auditables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/inline-style-allowlist.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
  - `frontend/src/tests/design-system-guards.test.ts`
  - composants TSX et CSS touches.
- Secondary evidence:
  - `npm run test -- inline-style design-system`
  - `rg -n "style=\\{" src -g "*.tsx"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - Le scan ne distingue pas geometrie runtime, pont CSS custom property et pass-through public.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-057-reduire-styles-inline-dynamiques-convertibles/inline-styles-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-057-reduire-styles-inline-dynamiques-convertibles/inline-styles-after.md`
- Expected invariant:
  - Le nombre d'exceptions diminue pour les styles convertibles; les restants sont classes avec raison.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Style visuel statique | fichier `.css` du composant | objet `style` TSX |
| Valeur dynamique projetee en CSS | custom property locale documentee | declaration visuelle inline |
| Pass-through composant public | API du composant et allowlist | suppression silencieuse |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/inline-style-allowlist.ts` | styles inline restants | Inventaire executable exact. | Doit diminuer ou conserver une classification. |
| `frontend/src/tests/design-system-allowlist.ts` | exceptions design-system associees | Guard global anti-drift. | Doit rester synchronise. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract type:
  - frontend component props and inline style allowlist
- Fields:
  - `style` for `Skeleton`
  - dynamic custom property bridges for converted components
- Required fields:
  - preserve existing required component props
- Optional fields:
  - preserve optional `style` pass-through only where currently public
- Status codes:
  - no HTTP status code contract is touched
- Serialization names:
  - CSS custom properties must use existing naming conventions in component CSS
- Frontend type impact:
  - Do not remove `Skeleton` style-prop typing without explicit decision.
- Generated contract impact:
  - no generated API contract changes are expected

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Inline style batch | allowlisted `style` entries | CSS classes or custom properties | touched TSX/CSS pairs | inline-style guard | `rg style={` | runtime geometry |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-057-reduire-styles-inline-dynamiques-convertibles/inline-styles-before.md` | Capturer style attributes and classifications. |
| After inventory | `_condamad/stories/CS-057-reduire-styles-inline-dynamiques-convertibles/inline-styles-after.md` | Prouver migrations, restants et allowlists. |

## 4i. Reintroduction Guard

- Guard target: styles inline retires et allowlists exactes.
- Architecture guard against reintroduction required: `npm run test -- inline-style design-system`.
- Guard evidence: Evidence profile: `reintroduction_guard`; tests plus scan `style={` final.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0016/00-audit-report.md#F-003` - 14 inline style attributes restent dans 9 TSX files.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-002` - demande classification et preservation `Skeleton`.
- Evidence 3: `frontend/src/tests/inline-style-allowlist.ts` - allowlist executable des styles inline.
- Evidence 4: `frontend/src/components/ui/Skeleton/Skeleton.tsx` - surface mentionnee comme pass-through potentiel.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les exceptions convertibles sortent de TSX vers CSS ou custom properties.
- Les exceptions restantes sont classees et exactes.
- Le contrat public `Skeleton` reste preserve ou bloque par decision explicite.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - les styles inline statiques sont interdits hors exceptions exactes.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-048` - les fallbacks CSS ne sont pas le scope.
  - `RG-049` - les selectors legacy ne sont pas le scope.
- Required regression evidence:
  - `npm run test -- inline-style design-system`
  - scan `rg -n "style=\\{" src -g "*.tsx"`
  - artefacts before/after.
- Allowed differences:
  - Diminution des entrees allowlistees et ajout de classes/custom properties dans CSS.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline classe chaque style inline restant. | Evidence profile: `baseline_before_after_diff`; `rg -n "style=\\{" src -g "*.tsx"`. |
| AC2 | Les declarations visuelles convertibles passent en CSS. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- inline-style design-system`. |
| AC3 | Le contrat runtime `Skeleton.style` reste preserve. | Evidence profile: `runtime_openapi_contract`; AST guard `npm run test -- inline-style design-system`. |
| AC4 | Les allowlists design-system restent synchronisees. | Evidence profile: `allowlist_register_validated`; `npm run test -- inline-style design-system`. |
| AC5 | Aucun nouveau style inline non classe n'est introduit. | Evidence profile: `repo_wide_negative_scan`; scan final `rg -n "style=\\{" src -g "*.tsx"`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et classifier chaque style inline (AC: AC1, AC3)
- [ ] Task 2 - Convertir les declarations visuelles en classes ou custom properties CSS (AC: AC2)
- [ ] Task 3 - Preserver ou bloquer les cas `Skeleton` et geometrie runtime (AC: AC3)
- [ ] Task 4 - Synchroniser les allowlists apres modification (AC: AC4)
- [ ] Task 5 - Capturer l'after et executer les validations (AC: AC1, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - fichiers CSS existants des composants touches
  - `frontend/src/tests/inline-style-allowlist.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
- Do not recreate:
  - nouveau registre inline parallele.
  - nouveau composant uniquement pour contourner l'allowlist.
  - API de style alternative.
- Shared abstraction allowed only if:
  - Plusieurs composants touchent la meme responsabilite et une classe utilitaire existante ne suffit pas.

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

- Nouveau `style={{ value }}` non allowliste.
- Suppression silencieuse du prop `style` de `Skeleton`.
- Declarations visuelles statiques encodees en TSX.

## 11. Removal Classification Rules

Classification must be deterministic:

- `dead`: inline style convertible vers CSS sans perte.
- `canonical-active`: runtime geometry or public pass-through still required.
- `needs-user-decision`: component API decision required.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `dead` | `delete` | Must be removed from TSX and allowlists. |
| `canonical-active` | `keep` | Must remain exact and allowlisted. |
| `needs-user-decision` | `needs-user-decision` | Must block that item. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/CS-057-reduire-styles-inline-dynamiques-convertibles/inline-styles-before.md`
- `_condamad/stories/CS-057-reduire-styles-inline-dynamiques-convertibles/inline-styles-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Style visuel composant | fichier CSS du composant | objet `style` TSX |
| Valeur dynamique | custom property locale ou runtime geometry allowlistee | classe generique non parametree |
| Pass-through public | composant proprietaire | suppression silencieuse |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- replacing one inline visual declaration with another inline declaration
- hiding a static style behind a TS object constant
- keeping removed items in allowlists

## 15. External Usage Blocker

If an item is classified as `needs-user-decision`, it must not be deleted. The dev agent must stop for that item or record explicit user decision with evidence and risk.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx`
- `frontend/src/components/ui/Skeleton/Skeleton.css`
- `frontend/src/layouts/TwoColumnLayout.tsx`
- `frontend/src/components/DomainRankingCard.tsx`
- `frontend/src/components/prediction/CategoryGrid.tsx`
- `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/inline-style-allowlist.ts` - synchroniser les exceptions restantes.
- `frontend/src/tests/design-system-allowlist.ts` - synchroniser l'allowlist globale.
- `frontend/src/components/ui/Skeleton/Skeleton.tsx` - inspecter ou conserver le pass-through selon classification.
- `frontend/src/components/ui/Skeleton/Skeleton.css` - CSS cible si migration autorisee.
- `frontend/src/layouts/TwoColumnLayout.tsx` - convertir si l'entree est visuelle.
- `frontend/src/layouts/TwoColumnLayout.css` - porter les styles convertis.
- `_condamad/stories/CS-057-reduire-styles-inline-dynamiques-convertibles/inline-styles-before.md` - baseline.
- `_condamad/stories/CS-057-reduire-styles-inline-dynamiques-convertibles/inline-styles-after.md` - evidence finale.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- tests component/page des surfaces touchees, a selectionner apres classification.

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
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-057-reduire-styles-inline-dynamiques-convertibles/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-057-reduire-styles-inline-dynamiques-convertibles/00-story.md
```

## 22. Regression Risks

- Risk: perte de valeur runtime apres migration CSS.
  - Guardrail: classification obligatoire avant conversion.
- Risk: rupture du contrat public `Skeleton`.
  - Guardrail: AC3 bloque toute suppression sans decision.
- Risk: allowlist masquant une croissance future.
  - Guardrail: AC4 et AC5 exigent guard et scan.

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

- `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-002` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-06-0016/02-finding-register.md#F-003` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-06-0016/00-audit-report.md#F-003` - current count and file list.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
