# Story CS-029 encadrer-styles-inline-statiques-frontend: Encadrer les styles inline statiques frontend

Status: ready-to-dev

## 1. Objective

Formaliser une politique CSS-only pour les styles inline TSX.
Les declarations statiques doivent vivre dans les fichiers `.css`; les styles dynamiques exigent une allowlist exacte.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-004`
- Reason for change: le finding `F-004` montre 90 attributs `style` TSX, avec un melange de cas dynamiques legitimes et de styling statique.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src`
- In scope:
  - Classer les attributs `style` TSX existants.
  - Migrer les exemples statiques audites vers CSS.
  - Creer une allowlist exacte pour largeurs, progressions, positions, transforms calculees et custom properties dynamiques.
  - Ajouter une garde qui bloque les nouveaux styles inline statiques.
- Out of scope:
  - Refaire les composants UI.
  - Modifier les routes ou appels API.
  - Convertir les SVG ou animations dynamiques qui exigent une valeur calculee.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas autoriser une exception globale par dossier.
  - Ne pas utiliser de style inline pour contourner un fichier CSS manquant.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: test-guard-hardening
- Archetype reason: la story ajoute une politique et une garde statique avec allowlist exacte pour empecher la derive.
- Behavior change allowed: no
- Behavior change constraints:
  - Les classes CSS doivent reproduire les styles statiques existants.
  - Les cas dynamiques deja legitimes restent fonctionnels.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un style inline existant encode une valeur produit qui ne peut pas etre deplacee en CSS ni exprimee comme variable dynamique.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde doit parser les fichiers TSX reels. |
| Baseline Snapshot | yes | L'inventaire des styles inline doit etre capture avant/apres classification. |
| Ownership Routing | no | La politique a un seul owner frontend. |
| Allowlist Exception | yes | Les styles dynamiques autorises exigent une allowlist exacte. |
| Contract Shape | no | Aucun contrat API ou type frontend public n'est touche. |
| Batch Migration | no | Le scope est une politique de garde, pas une migration multi-lot. |
| Reintroduction Guard | yes | La garde doit echouer sur un nouveau style inline statique. |
| Persistent Evidence | yes | L'allowlist et les inventaires avant/apres doivent persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard TypeScript des fichiers TSX frontend.
  - Commande cible: `npm run test -- inline-style`.
- Secondary evidence:
  - `rg -n "style=" frontend/src -g "*.tsx"`
- Static scans alone are not sufficient for this story because:
  - La garde doit distinguer objet statique, variable dynamique et custom property.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-029-encadrer-styles-inline-statiques-frontend/inline-styles-before.md`
- Comparison after implementation: `_condamad/stories/CS-029-encadrer-styles-inline-statiques-frontend/inline-styles-after.md`
- Expected invariant: les styles inline statiques non allowlistes disparaissent de l'inventaire final.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: les styles inline frontend sont gouvernes par une seule politique sous `frontend/src/tests` et son registre.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/components/prediction/DayTimeline.tsx` | dynamic width | Valeur calculee par donnees runtime. | Permanent avec test dynamique. |
| `frontend/src/components/astro/AstroMoodBackground.tsx` | CSS custom property object | Pont controle vers CSS variables. | Permanent si la propriete est declaree dans CSS. |
| `frontend/src/components/StarfieldBackground.tsx` | transform or position computed from geometry | Etat visuel calcule. | Permanent avec test exact du fichier et du prop. |

Rules:

- no wildcard folder-only exception;
- no static object exception;
- every exception must reference a file and a style key;
- every exception must be validated by the guard.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: la story migre seulement les exemples statiques audites et installe une garde.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Inline style allowlist | `frontend/src/tests/inline-style-allowlist.ts` | Classer les exceptions dynamiques autorisees. |
| Before inventory | `inline-styles-before.md` | Capturer les styles inline initiaux. |
| After inventory | `inline-styles-after.md` | Prouver que les statiques non allowlistes sont partis. |

## 4i. Reintroduction Guard

- Guard target: attribut `style` TSX statique non allowliste.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- inline-style`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md#E-006` - 90 attributs `style` detectes dans `frontend/src`.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-004` - plusieurs composants TSX contiennent des exemples statiques.
- Evidence 3: règle projet `AGENTS.md` - aucun style inline; tout style doit vivre dans le CSS approprie.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les styles inline statiques audites sont convertis en classes CSS.
- Les styles dynamiques restants sont classifies avec fichier, cle et raison.
- Un test Vitest echoue sur tout nouvel objet statique non allowliste.
- Aucun nouveau style inline n'est ajoute pour de la presentation statique.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - les styles inline statiques frontend doivent rester interdits.
- Non-applicable invariants:
  - `RG-001` a `RG-043` - hors surface frontend TSX/CSS.
- Required regression evidence:
  - Test inline-style, scan cible `style=`, `npm run lint`.
- Allowed differences:
  - Remplacement de styles inline statiques par classes CSS equivalentes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les styles inline existants sont classes. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- inline-style`. |
| AC2 | Les exemples statiques audites sont deplaces vers CSS. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `npm run test -- inline-style`. |
| AC3 | Les exceptions dynamiques ont une cle style exacte. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- inline-style`. |
| AC4 | Un nouveau style inline statique fait echouer la garde. | Evidence profile: `reintroduction_guard`; `npm run test -- inline-style`. |
| AC5 | Le lint frontend reste passant. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inventorier les attributs `style` TSX existants (AC: AC1)
- [ ] Task 2 - Creer l'allowlist dynamique exacte (AC: AC1, AC3)
- [ ] Task 3 - Migrer les exemples statiques vers CSS (AC: AC2)
- [ ] Task 4 - Ajouter la garde Vitest inline-style (AC: AC3, AC4)
- [ ] Task 5 - Executer lint et tests cibles (AC: AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Les fichiers `.css` adjacents aux composants audites.
  - Les helpers de test Vitest existants sous `frontend/src/tests`.
- Do not recreate:
  - Un systeme de style runtime.
  - Des classes dupliquees entre composants quand une classe utilitaire existe.
- Shared abstraction allowed only if:
  - Elle evite la duplication du parser de garde dans plusieurs tests.

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

- objet `style` statique non allowliste
- exception par dossier sans fichier exact
- classe CSS dupliquee pour contourner un token existant

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Politique inline style | test inline-style et allowlist associee | revue manuelle |
| Styling statique | fichiers `.css` appropries | props `style` TSX |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/layouts/SettingsLayout.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/components/settings/DeleteAccountModal.tsx`
- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/settings/AccountSettings.tsx`
- `frontend/src/pages/NotFoundPage.tsx`
- `frontend/src/tests/theme-tokens.test.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/inline-style-policy.test.ts` - garde statique.
- `frontend/src/tests/inline-style-allowlist.ts` - allowlist exacte.
- `frontend/src/layouts/SettingsLayout.tsx` - retrait de styles statiques.
- `frontend/src/features/astrologers/components/AstrologerCard.tsx` - retrait de styles statiques.
- `frontend/src/components/settings/DeleteAccountModal.css` - classes CSS equivalentes.
- `frontend/src/pages/settings/Settings.css` - classes CSS equivalentes.

Likely tests:

- `frontend/src/tests/inline-style-policy.test.ts` - couverture principale.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- inline-style
rg -n "style=" src -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-029-encadrer-styles-inline-statiques-frontend/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-029-encadrer-styles-inline-statiques-frontend/00-story.md
```

## 22. Regression Risks

- Risk: la garde bloque un cas dynamique legitime.
  - Guardrail: allowlist exacte avec cle style et raison.
- Risk: une migration CSS change le layout.
  - Guardrail: tests composants existants et lint frontend.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Put static styling in CSS files only.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-004` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-004` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
