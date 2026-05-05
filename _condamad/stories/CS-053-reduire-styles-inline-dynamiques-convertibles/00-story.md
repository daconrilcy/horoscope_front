# Story CS-053 reduire-styles-inline-dynamiques-convertibles: Reduire les styles inline dynamiques encore convertibles

Status: ready-to-dev

## 1. Objective

Classifier les 15 styles inline restants et migrer vers CSS uniquement les declarations convertibles.
Les styles de geometrie dynamique, pont CSS variable, couleur runtime ou pass-through public restent exacts et allowlistes.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-002`
- Reason for change: `F-003` indique 15 attributs `style` dans 9 fichiers TSX; certains peuvent encore etre representes par CSS/custom properties.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components`
- In scope:
  - Classer chaque style inline actuel comme `runtime-geometry`, `css-custom-property-bridge`, `color-bridge`, ou `style-prop-pass-through`.
  - Migrer les declarations visuelles statiques convertibles vers les fichiers CSS appropries.
  - Mettre a jour `inline-style-allowlist.ts` et `design-system-allowlist.ts` seulement apres modification du code.
  - Tester les composants touches, notamment `TimelineRail`, `DayTimelineSectionV4`, `TurningPointCard`, `Badge`, et `Skeleton` si modifies.
- Out of scope:
  - Changer les props publiques des composants.
  - Remplacer des valeurs dynamiques par du CSS statique approximatif.
  - Traiter fallbacks CSS, tokens hardcodes larges, ou legacy selectors.
- Explicit non-goals:
  - Ne pas affaiblir `RG-047` ou `RG-050`.
  - Ne pas creer d'exception allowlist non sourcee.
  - Ne pas migrer `Skeleton` ou des progress widths si ce sont des contrats runtime/API.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot multi-composants de styles inline vers CSS ou exceptions exactes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les styles statiques deplaces doivent garder le rendu.
  - Les styles dynamiques doivent conserver leurs valeurs runtime.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une entree semble etre une API publique de style, une largeur/progression runtime, ou un comportement impossible a prouver par tests existants.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards `inline-style` et `design-system` verifient les exceptions executables. |
| Baseline Snapshot | yes | Les 15 styles doivent etre classes before/after. |
| Ownership Routing | yes | Les declarations statiques appartiennent aux CSS composants, pas aux TSX. |
| Allowlist Exception | yes | Les exceptions dynamiques restantes doivent etre exactes. |
| Contract Shape | no | Aucun contrat API/backend ou DTO n'est modifie; les props publiques ne doivent pas changer. |
| Batch Migration | yes | Plusieurs composants TSX peuvent etre touches. |
| Reintroduction Guard | yes | Les styles inline statiques ne doivent pas revenir. |
| Persistent Evidence | yes | La classification before/after doit persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/inline-style-allowlist.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
- Secondary evidence:
  - Scan `rg -n "style=\\{" src -g "*.tsx"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - Un hit inline peut etre legitime s'il porte une valeur runtime exacte.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/inline-styles-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/inline-styles-after.md`
- Expected invariant:
  - Aucun style classe convertible ne reste en TSX; les exceptions restantes sont dynamiques ou pass-through.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Style visuel statique | CSS du composant/page | attribut `style` TSX |
| Geometrie runtime | inline allowliste exact | classe CSS approximative |
| Pont custom property | inline exact qui pose une variable CSS | declaration visuelle statique en TSX |
| Style-prop pass-through | API composant documentee | allowlist implicite |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/inline-style-allowlist.ts` | styles inline restants | Runtime or pass-through exact. | Permanent while contract remains true. |
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
| Inline batch | TSX `style` attributes | CSS or exact allowlist | listed TSX | inline/design guards | scans | public prop ambiguity |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before classification | `_condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/inline-styles-before.md` | Classer les 15 styles initiaux. |
| After classification | `_condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/inline-styles-after.md` | Prouver les migrations et exceptions finales. |

## 4i. Reintroduction Guard

- Guard target: styles inline statiques et synchronisation allowlist.
- Architecture guard against reintroduction required: `npm run test -- inline-style design-system`.
- Guard evidence: Evidence profile: `reintroduction_guard`; tests plus scan final `style={`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md#F-003` - 15 styles inline dans 9 fichiers TSX.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-002` - classification et migration des cas convertibles demandees.
- Evidence 3: `frontend/src/tests/inline-style-allowlist.ts` - allowlist executable inline.
- Evidence 4: `frontend/src/tests/design-system-allowlist.ts` - allowlist design-system partagee.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les 15 styles initiaux ont une classification durable.
- Les styles convertibles vivent en CSS ou en custom properties correctement bornees.
- Les allowlists restantes ne couvrent que des exceptions dynamiques exactes.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - les styles inline statiques sont interdits hors exceptions exactes.
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
| AC1 | Les 15 styles inline initiaux sont classes dans `inline-styles-before.md`. | Evidence profile: `baseline_snapshot`; scan `rg -n "style=\\{" src -g "*.tsx"`. |
| AC2 | Chaque style convertible est retire du TSX. | Evidence profile: `negative_scan`; `rg -n "style=\\{" src -g "*.tsx"`. |
| AC3 | Les styles conserves ont une justification exacte. | Evidence profile: `allowlist_guard`; AST guard runtime `npm run test -- inline-style design-system`. |
| AC4 | La synchronisation des allowlists inline passe le guard. | Evidence profile: `allowlist_guard`; `npm run test -- inline-style design-system`. |
| AC5 | Les composants touches gardent leur comportement public. | Evidence profile: `frontend_test`; tests cibles existants et `npm run test -- inline-style design-system`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer et classifier tous les styles inline actuels (AC: AC1)
- [ ] Task 2 - Migrer les styles convertibles vers CSS ou pont custom property borne (AC: AC2)
- [ ] Task 3 - Documenter les exceptions runtime/pass-through restantes (AC: AC3)
- [ ] Task 4 - Synchroniser les allowlists apres les changements (AC: AC4)
- [ ] Task 5 - Capturer l'after et executer les tests cibles (AC: AC1, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - CSS deja associe aux composants touches.
  - `frontend/src/tests/inline-style-allowlist.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
  - Variables CSS existantes avant toute creation.
- Do not recreate:
  - Prop de style parallele.
  - Classe globale speculative pour un cas unique.
  - Objet de style statique deplace dans un autre fichier TS.
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
- Migration vers inline custom property sans justification dynamique.

## 11. Removal Classification Rules

Classification must be deterministic:

- `runtime-geometry`: value depends on measurement, position, width, progress, or animation runtime.
- `css-custom-property-bridge`: inline only sets a CSS variable consumed by CSS.
- `color-bridge`: runtime color value cannot be represented statically.
- `style-prop-pass-through`: public component API forwards style.
- `removable-static-style`: constant visual style expressible in CSS.
- `needs-user-decision`: ambiguity blocks implementation for that item.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `runtime-geometry` | `keep` | Must remain exact and allowlisted. |
| `css-custom-property-bridge` | `keep`, `narrow` | Must expose only runtime variable values. |
| `color-bridge` | `keep`, `migrate` | Keep only if color is runtime. |
| `style-prop-pass-through` | `keep` | Must be documented as component API. |
| `removable-static-style` | `delete` | Must move to CSS. |
| `needs-user-decision` | `needs-user-decision` | Must block that item. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/inline-styles-before.md`
- `_condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/inline-styles-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Styles statiques | CSS du composant/page | attribut `style` TSX |
| Exceptions dynamiques | `inline-style-allowlist.ts` | inline non reference |
| Exceptions design-system | `design-system-allowlist.ts` | divergence allowlist |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- moving a static inline style to another inline object
- preserving static style through a renamed prop
- broad allowlist retention

## 15. External Usage Blocker

If an item is `style-prop-pass-through` or `needs-user-decision`, public API risk must be documented before keeping it.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/components/prediction/TimelineRail.tsx`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/TurningPointCard.tsx`
- `frontend/src/components/ui/Badge/Badge.tsx`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx`
- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `unknown until repo inspection` plus assumption risk: exact TSX/CSS files depend on which entries are classified convertible.
- `frontend/src/tests/inline-style-allowlist.ts` - exceptions finales.
- `frontend/src/tests/design-system-allowlist.ts` - synchronisation.
- `_condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/inline-styles-before.md` - baseline.
- `_condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/inline-styles-after.md` - evidence finale.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- Existing tests for `Badge`, `Skeleton`, `TurningPointCard`, `TimelineRail`, or `DayTimelineSectionV4` when present.

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
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/00-story.md
```

## 22. Regression Risks

- Risk: une valeur runtime est figee en CSS.
  - Guardrail: classification `runtime-geometry` ou `color-bridge` bloque la migration.
- Risk: `Skeleton` perd son API `style`.
  - Guardrail: classification `style-prop-pass-through` exige documentation.
- Risk: allowlist trop large.
  - Guardrail: AC4 exige guards et synchronisation exacte.

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

- `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-002` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-2053/02-finding-register.md#F-003` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md#F-003` - current count and file list.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
