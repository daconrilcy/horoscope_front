# Story CS-056 reduire-fallbacks-css-restants-apres-refactor: Reduire les fallbacks CSS restants apres refactor

Status: ready-to-dev

## 1. Objective

Reduire un lot borne de fallbacks CSS `var(--token, literal)` parmi les 24 exceptions restantes.
Le lot commence par `PeriodCard.css`, `NatalInterpretation.css`, `KeyPointCard.css` et `NatalChartPage.css`.
Chaque suppression doit prouver que le token canonique est garanti en app et en test.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-001`
- Reason for change: `F-002` indique que la dette fallback CSS reste active avec 24 exceptions exactes et 23 lignes sources dans 10 fichiers.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Capturer les compteurs before/after des fallbacks CSS du lot.
  - Traiter prioritairement `PeriodCard.css`, `NatalInterpretation.css`, `KeyPointCard.css` et `NatalChartPage.css`.
  - Supprimer uniquement les fallbacks dont le token canonique est garanti par les fichiers de tokens charges en app et en test.
  - Synchroniser `frontend/src/styles/css-fallback-allowlist.md` et `frontend/src/tests/design-system-allowlist.ts`.
- Out of scope:
  - Migration globale des 10 fichiers fallback si elle depasse le lot borne.
  - Creation d'un nouveau theme premium sans decision produit.
  - Conversion des styles inline, hardcoded values hors fallback ou selectors legacy.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-048` ou `RG-050`.
  - Ne pas remplacer un fallback literal par un autre fallback literal.
  - Ne pas traiter les aliases premium `needs-user-decision` sans decision utilisateur explicite.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: legacy-facade-removal
- Archetype reason: la story retire des surfaces de compatibilite fallback classees, avec delete-only pour les fallbacks devenus inutiles.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit rester equivalent lorsque la valeur vient deja du token canonique.
  - Toute difference visible admise doit etre documentee comme convergence vers token canonique.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un fallback premium, theme ou compatibility compense un token absent ou une valeur produit non tranchee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards `css-fallback`, `design-system` et `theme-tokens` prouvent l'etat executable. |
| Baseline Snapshot | yes | Les compteurs before/after sont requis pour le lot. |
| Ownership Routing | yes | Les valeurs doivent appartenir aux tokens ou aux registres d'exception canoniques. |
| Allowlist Exception | yes | Les exceptions restantes doivent rester exactes dans markdown et TS. |
| Contract Shape | no | Aucun contrat API, DTO, route ou type public n'est modifie. |
| Batch Migration | yes | Plusieurs fichiers CSS peuvent etre touches dans un batch explicite. |
| Reintroduction Guard | yes | Les fallbacks retires ne doivent pas revenir non classes. |
| Persistent Evidence | yes | Les inventories before/after doivent rester dans le dossier story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/premium-theme.css`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/tests/design-system-allowlist.ts`
- Secondary evidence:
  - `npm run test -- css-fallback design-system theme-tokens`
  - `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - Un scan ne prouve pas que le token canonique est garanti dans le runtime et les tests.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-056-reduire-fallbacks-css-restants-apres-refactor/css-fallbacks-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-056-reduire-fallbacks-css-restants-apres-refactor/css-fallbacks-after.md`
- Expected invariant:
  - Le nombre d'exceptions du lot diminue ou chaque blocage restant est classe `needs-user-decision`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Token global garanti | `design-tokens.css` ou `theme.css` | fallback literal local |
| Token premium garanti | `premium-theme.css` et registre token | alias implicite non classe |
| Exception fallback conservee | `css-fallback-allowlist.md` et `design-system-allowlist.ts` | exception implicite en CSS |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/css-fallback-allowlist.md` | fallbacks restants du lot | Registre lisible des exceptions. | Doit diminuer ou documenter une sortie. |
| `frontend/src/tests/design-system-allowlist.ts` | `CSS_FALLBACK_EXCEPTIONS` | Source executable des guards. | Doit correspondre au markdown. |

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
| Fallback batch | listed fallback CSS files | guaranteed CSS tokens | selected CSS declarations | allowlist guards | fallback scan | token absent or premium ambiguity |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-056-reduire-fallbacks-css-restants-apres-refactor/css-fallbacks-before.md` | Capturer hits, compteurs et classifications initiales. |
| After inventory | `css-fallbacks-after.md` | Prouver suppressions, exceptions restantes et synchronisation. |

## 4i. Reintroduction Guard

- Guard target: fallbacks supprimes du lot et synchronisation des registres.
- Architecture guard against reintroduction required: `npm run test -- css-fallback design-system theme-tokens`.
- Reintroduced forbidden symbols source: `var(--token, literal)` entries in CSS plus `CSS_FALLBACK_EXCEPTIONS`.
- Guard evidence: Evidence profile: `reintroduction_guard`; command `npm run test -- css-fallback design-system theme-tokens`.
- Forbidden symbols scan: `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0016/00-audit-report.md#F-002` - 24 exceptions exactes et clusters principaux nommes.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-001` - impose before/after, fichiers de depart et registres a synchroniser.
- Evidence 3: `frontend/src/styles/css-fallback-allowlist.md` - registre markdown des fallbacks.
- Evidence 4: `frontend/src/tests/design-system-allowlist.ts` - allowlist executable design-system.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Le lot prioritaire a un inventaire before/after persistant.
- Les fallbacks garantis sont supprimes du CSS et des registres.
- Les exceptions restantes sont exactes, justifiees et couvertes par les guards.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens restent classes.
  - `RG-048` - les fallbacks CSS doivent rester exacts et classes.
  - `RG-050` - les guards anti-drift design-system restent executables.
- Non-applicable invariants:
  - `RG-047` - les styles inline TSX sont hors scope.
  - `RG-049` - les selectors legacy ne sont pas modifies.
- Required regression evidence:
  - `npm run test -- css-fallback design-system theme-tokens`
  - scan fallback final
  - artefacts before/after persistants
- Allowed differences:
  - Diminution des entrees allowlistees et suppression des fallbacks garantis.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline couvre les fallbacks du lot. | Evidence profile: `baseline_before_after_diff`; `rg -n "var\\(" src -g "*.css"`. |
| AC2 | Chaque fallback supprime a une preuve de token garanti. | Evidence profile: `ast_architecture_guard`; `npm run test -- theme-tokens`. |
| AC3 | Les registres fallback restent synchronises. | Evidence profile: `allowlist_register_validated`; `npm run test -- css-fallback design-system`. |
| AC4 | Les aliases premium ambigus restent bloques. | Evidence profile: `external_usage_blocker`; `rg -n "needs-user-decision|premium" _condamad/stories/CS-056*`. |
| AC5 | Aucun nouveau fallback non classe n'est introduit. | Evidence profile: `repo_wide_negative_scan`; `rg -n "var\\(" src -g "*.css"`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et le compteur initial du lot prioritaire (AC: AC1)
- [ ] Task 2 - Classer chaque fallback du lot comme `delete`, `keep`, ou `needs-user-decision` (AC: AC2, AC4)
- [ ] Task 3 - Supprimer uniquement les fallbacks classes `delete` (AC: AC2, AC5)
- [ ] Task 4 - Mettre a jour `css-fallback-allowlist.md` et `design-system-allowlist.ts` dans le meme changement (AC: AC3)
- [ ] Task 5 - Capturer l'after et executer les validations frontend et story (AC: AC1, AC3, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css`, `frontend/src/styles/theme.css`, `frontend/src/styles/premium-theme.css`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/tests/design-system-allowlist.ts`
- Do not recreate:
  - Registre parallele de fallbacks.
  - Alias premium ou fallback literal de remplacement.
  - Token nouveau sans classification.
- Shared abstraction allowed only if:
  - Elle supprime une duplication prouvee du lot et reste documentee dans les registres existants.

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

- Nouveau `var(--token, literal)` non classe.
- Entree markdown sans entree executable correspondante.
- Entree executable sans justification markdown.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: fallback still required because the token is not guaranteed.
- `external-active`: fallback documented as needed by external theme, premium surface, or audit evidence.
- `historical-facade`: fallback only preserves a compatibility visual surface after canonical token ownership exists.
- `dead`: fallback removable because the token is guaranteed.
- `needs-user-decision`: product, premium theme, or compatibility ambiguity remains.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must remain registered. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `replace-consumer`, `needs-user-decision` | Must migrate consumers then delete; must not be repointed. |
| `dead` | `delete` | Must be deleted from CSS and registries. |
| `needs-user-decision` | `needs-user-decision` | Must block deletion for that item. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions for the audit: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path when applicable:

- `_condamad/stories/CS-056-reduire-fallbacks-css-restants-apres-refactor/css-fallbacks-before.md`
- `_condamad/stories/CS-056-reduire-fallbacks-css-restants-apres-refactor/css-fallbacks-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Tokens disponibles | `design-tokens.css`, `theme.css`, `premium-theme.css` | fallback literal dans CSS |
| Exceptions fallback | `css-fallback-allowlist.md` et `design-system-allowlist.ts` | exception implicite |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving a wrapper
- preserving through re-export
- replacing one fallback literal with another
- preserving an unregistered compatibility alias
- keeping a removed fallback in any allowlist

## 15. External Usage Blocker

If an item is classified as `external-active` or `needs-user-decision`, it must not be deleted.
The dev agent must stop for that item or record explicit user decision with evidence and risk.

## 17. Generated Contract Check

- Generated contract check: no generated frontend/API artifact is expected to expose these CSS fallback entries.
- Required generated-contract evidence:
  - OpenAPI path absence: unchanged because CSS files are not API routes.
  - generated client/schema absence: unchanged because no generated client consumes CSS fallback entries.
  - generated manifest absence: `npm run test -- css-fallback design-system` remains the executable manifest guard.

## 18. Files to Inspect First

- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/NatalInterpretation.css`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/components/prediction/PeriodCard.css` - supprimer les fallbacks garantis du cluster.
- `frontend/src/components/NatalInterpretation.css` - supprimer les fallbacks garantis du cluster.
- `frontend/src/components/prediction/KeyPointCard.css` - supprimer les fallbacks garantis du cluster.
- `frontend/src/pages/NatalChartPage.css` - supprimer les fallbacks garantis non ambigus.
- `frontend/src/styles/css-fallback-allowlist.md` - synchroniser les exceptions.
- `frontend/src/tests/design-system-allowlist.ts` - synchroniser l'allowlist executable.
- `_condamad/stories/CS-056-reduire-fallbacks-css-restants-apres-refactor/css-fallbacks-before.md` - baseline.
- `_condamad/stories/CS-056-reduire-fallbacks-css-restants-apres-refactor/css-fallbacks-after.md` - evidence finale.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`

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
npm run test -- css-fallback design-system theme-tokens
npm run lint
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-056-reduire-fallbacks-css-restants-apres-refactor/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-056-reduire-fallbacks-css-restants-apres-refactor/00-story.md
```

## 22. Regression Risks

- Risk: suppression d'un fallback encore utile dans le theme premium.
  - Guardrail: classification `needs-user-decision` bloque la suppression.
- Risk: registres desynchronises.
  - Guardrail: AC3 exige les guards `css-fallback` et `design-system`.
- Risk: migration trop large.
  - Guardrail: le lot prioritaire est borne aux fichiers listes.

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

- `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-001` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-06-0016/02-finding-register.md#F-002` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-06-0016/00-audit-report.md#F-002` - current count and file list.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
