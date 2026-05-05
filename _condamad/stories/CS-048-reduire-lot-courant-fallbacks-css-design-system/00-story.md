# Story CS-048 reduire-lot-courant-fallbacks-css-design-system: Reduire le lot courant de fallbacks CSS design-system

Status: ready-to-dev

## 1. Objective

Reduire a 100% un lot borne et coherent de fallbacks CSS `var(--token, literal)`.
Seuls les fallbacks dont le token canonique est garanti sont supprimes.
Le registre markdown et l'allowlist executable doivent rester synchronises.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-002`
- Reason for change: 68 fallbacks restent actifs dans 14 fichiers CSS et conservent des decisions visuelles alternatives a cote des tokens canoniques.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Choisir et documenter un seul lot de surface parmi les fichiers F-003.
  - Par defaut, traiter `App.css`, `AdminPromptsPage.css`, `Settings.css`, `BirthProfilePage.css`.
  - Capturer les compteurs before/after du lot choisi.
  - Supprimer les fallbacks dont le token existe dans les sources chargees par l'application.
  - Mettre a jour `css-fallback-allowlist.md` et `design-system-allowlist.ts` dans la meme modification.
- Out of scope:
  - Traiter les 14 fichiers si cela depasse le lot choisi.
  - Modifier la palette, la hierarchie typographique ou les styles inline.
  - Ajouter de nouveaux tokens pour eviter une decision produit.
- Explicit non-goals:
  - Ne pas affaiblir `RG-048` ou `RG-050`.
  - Ne pas conserver un fallback supprime dans une allowlist.
  - Ne pas remplacer un fallback literal par un autre fallback local.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story reduit une dette CSS par lot borne avec before/after et registre.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit rester equivalent quand le token canonique a la meme valeur de reference.
  - Toute difference doit etre documentee comme convergence vers token canonique.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un fallback semble compenser l'absence d'un token charge, un theme externe, ou une valeur produit non canonique.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests css-fallback/design-system prouvent l'etat executable des exceptions. |
| Baseline Snapshot | yes | Les compteurs before/after du lot choisi sont obligatoires. |
| Ownership Routing | yes | La decision visuelle doit revenir aux tokens et registres canoniques. |
| Allowlist Exception | yes | Les exceptions restantes doivent rester exactes dans deux registres. |
| Contract Shape | no | Aucun contrat API ou type public n'est modifie. |
| Batch Migration | yes | Le scope est un lot multi-fichiers. |
| Reintroduction Guard | yes | Les fallbacks supprimes ne doivent pas revenir hors classification. |
| Persistent Evidence | yes | Les compteurs et decisions du lot doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
  - `frontend/src/styles/css-fallback-allowlist.md`
- Secondary evidence:
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/theme.css`
  - Scan `rg -n "var\\(--[^,)]+,\\s*[^)]+\\)" src -g "*.css"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - Le registre executable et le registre markdown doivent rester exacts, pas seulement diminuer en volume.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-048-reduire-lot-courant-fallbacks-css-design-system/css-fallbacks-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-048-reduire-lot-courant-fallbacks-css-design-system/css-fallbacks-after.md`
- Expected invariant:
  - Le nombre de fallbacks du lot choisi diminue; toute entree restante a une justification et une condition de sortie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Token CSS garanti | `design-tokens.css` ou `theme.css` | fallback literal local |
| Exception de fallback conservee | `css-fallback-allowlist.md` + `design-system-allowlist.ts` | exception implicite dans CSS |
| Decision visuelle durable | registre de tokens | valeur literal non classee |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/css-fallback-allowlist.md` | fallbacks restants du lot | Exception CSS exacte. | Doit diminuer ou rester justifiee avec sortie. |
| `frontend/src/tests/design-system-allowlist.ts` | meme inventaire executable | Guard Vitest. | Doit correspondre au markdown. |

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
| F-003 priority batch | selected CSS fallbacks | guaranteed tokens | chosen CSS files | allowlist guards | before/after scans | token not guaranteed |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `css-fallbacks-before.md` | Capturer le lot, les compteurs et les decisions proposees. |
| After inventory | `css-fallbacks-after.md` | Prouver les suppressions, les exceptions restantes et les compteurs finaux. |

## 4i. Reintroduction Guard

- Guard target: fallbacks supprimes du lot et synchronisation markdown/allowlist executable.
- Architecture guard against reintroduction required: `npm run test -- css-fallback design-system` must fail if unclassified fallbacks return.
- Guard evidence: Evidence profile: `reintroduction_guard`; tests plus scan cible `rg`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md#F-003` - 68 fallback exceptions across 14 CSS files.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-002` - bounded batch reduction required.
- Evidence 3: `frontend/src/styles/css-fallback-allowlist.md` - markdown registry to keep exact.
- Evidence 4: `frontend/src/tests/design-system-allowlist.ts` - executable allowlist to keep exact.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consulted before cadrage.

## 6. Target State

- Un lot explicite de fallbacks est reduit avec compteurs before/after.
- Les fichiers CSS du lot ne conservent que des fallbacks justifies.
- Le registre markdown et l'allowlist executable ont le meme inventaire final.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les tokens utilises doivent rester classes.
  - `RG-048` - les fallbacks CSS doivent rester classes et exacts.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-047` - styles inline hors scope.
  - `RG-049` - legacy selectors hors scope sauf si un fichier commun est touche sans modification legacy.
- Required regression evidence:
  - `npm run test -- css-fallback design-system`, scan fallback, artefacts before/after.
- Allowed differences:
  - Diminution des entrees allowlistees et retrait des fallbacks garantis.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le lot traite couvre 100% des fallbacks des fichiers choisis. | Evidence profile: `baseline_snapshot`; `rg -n "var\\(--" selected files`. |
| AC2 | Chaque fallback supprime correspond a un token garanti. | Evidence profile: `architecture_guard`; `npm run test -- css-fallback design-system`. |
| AC3 | Le registre markdown correspond au scan final. | Evidence profile: `allowlist_guard`; `npm run test -- css-fallback design-system`. |
| AC4 | L'allowlist executable correspond au scan final. | Evidence profile: `allowlist_guard`; `npm run test -- css-fallback design-system`. |
| AC5 | Aucun nouveau fallback non classe n'est introduit dans le lot. | Evidence profile: `negative_scan`; `rg -n "var\\(--" selected files`. |
| AC6 | Le frontend reste valide apres reduction. | Evidence profile: `frontend_quality`; `npm run test -- css-fallback design-system` and `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Choisir le lot prioritaire et capturer l'inventaire before exhaustif (AC: AC1)
- [ ] Task 2 - Verifier pour chaque fallback si le token canonique est garanti (AC: AC2)
- [ ] Task 3 - Supprimer uniquement les fallbacks garantis et ne pas toucher les autres (AC: AC2, AC4)
- [ ] Task 4 - Synchroniser markdown et allowlist executable avec l'etat final (AC: AC3, AC4)
- [ ] Task 5 - Capturer l'inventaire after et executer les validations (AC: AC1, AC3, AC4, AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/tests/design-system-allowlist.ts`
- Do not recreate:
  - Registre parallele de fallbacks.
  - Token nouveau sans classification.
  - Fallback literal alternatif.
- Shared abstraction allowed only if:
  - Elle supprime une duplication reelle dans le lot et reste documentee.

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

- Nouveau `var(--token, literal)` non present dans le registre final.
- Entree markdown sans entree executable correspondante.
- Entree executable sans justification markdown.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: fallback required because token is not guaranteed in the active runtime.
- `dead`: fallback removable because token is guaranteed.
- `needs-user-decision`: fallback may encode product/theming behavior that cannot be inferred.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must remain registered. |
| `dead` | `delete` | Must be deleted from CSS and registries. |
| `needs-user-decision` | `needs-user-decision` | Must block deletion for that entry. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/CS-048-reduire-lot-courant-fallbacks-css-design-system/css-fallbacks-before.md`
- `_condamad/stories/CS-048-reduire-lot-courant-fallbacks-css-design-system/css-fallbacks-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Fallbacks CSS restants | `css-fallback-allowlist.md` + `design-system-allowlist.ts` | fallback implicite |
| Tokens disponibles | `design-tokens.css` + `theme.css` | literal dans `var()` |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- replacing one fallback literal with another
- preserving a compatibility alias
- keeping an unregistered fallback active

## 15. External Usage Blocker

If an item is classified as `needs-user-decision`, it must not be deleted. The dev agent must stop for that item or record explicit user decision with evidence.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/App.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/BirthProfilePage.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - remove guaranteed fallbacks if included in selected batch.
- `frontend/src/pages/admin/AdminPromptsPage.css` - remove guaranteed fallbacks if included in selected batch.
- `frontend/src/pages/settings/Settings.css` - remove guaranteed fallbacks if included in selected batch.
- `frontend/src/pages/BirthProfilePage.css` - remove guaranteed fallbacks if included in selected batch.
- `frontend/src/styles/css-fallback-allowlist.md` - synchronize remaining exceptions.
- `frontend/src/tests/design-system-allowlist.ts` - synchronize executable allowlist.
- `_condamad/stories/CS-048-reduire-lot-courant-fallbacks-css-design-system/css-fallbacks-before.md` - baseline.
- `_condamad/stories/CS-048-reduire-lot-courant-fallbacks-css-design-system/css-fallbacks-after.md` - final evidence.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`

Files not expected to change:

- `backend/` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/tests/inline-style-allowlist.ts` - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- css-fallback design-system
npm run lint
rg -n "var\(--[^,)]+,\s*[^)]+\)" src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-048-reduire-lot-courant-fallbacks-css-design-system/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-048-reduire-lot-courant-fallbacks-css-design-system/00-story.md
```

## 22. Regression Risks

- Risk: suppression d'un fallback encore necessaire a un theme.
  - Guardrail: classification `needs-user-decision` bloque la suppression.
- Risk: registres desynchronises.
  - Guardrail: AC3 exige le passage de `npm run test -- css-fallback design-system`.
- Risk: scope trop large et incomplet.
  - Guardrail: AC1 exige un lot nomme et 100% des hits du lot.

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

- `_condamad/audits/frontend-design-system/2026-05-05-1942/03-story-candidates.md#SC-002` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1942/02-finding-register.md#F-003` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1942/00-audit-report.md#F-003` - file list and current count.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
