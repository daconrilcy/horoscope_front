# Story CS-044 reduire-fallbacks-css-layout-shell-pages: Reduire les fallbacks CSS du layout, shell et pages prioritaires

Status: ready-to-dev

## 1. Objective

Reduire a 100% le lot choisi de fallbacks CSS `var(--token, value)` dans les surfaces layout, shell et pages prioritaires.
Chaque fallback du lot doit migrer vers un token canonique ou rester comme exception exacte avec raison, owner et condition de sortie.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1831/03-story-candidates.md#SC-001`
- Reason for change: le finding `F-002` mesure 117 fallbacks CSS actifs dans 19 fichiers; la story doit reduire un lot borne sans laisser de dette implicite.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src`
- In scope:
  - Traiter entierement le lot `App.css`, `Header.css`, `Sidebar.css`, `HelpPage.css`, `Settings.css`, `glass.css`, `utilities.css`.
  - Capturer les inventaires before/after des fallbacks du lot.
  - Migrer les fallbacks migration-only vers `var(--token)` ou vers un token semantique deja classe.
  - Synchroniser `frontend/src/styles/css-fallback-allowlist.md` et `frontend/src/tests/design-system-allowlist.ts`.
- Out of scope:
  - Les 12 autres fichiers F-002 non listes dans le lot.
  - Styles inline TSX.
  - Migration generale des valeurs hardcodees hors fallback.
  - Refonte visuelle ou changement d'API React.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-048` ou `RG-050`.
  - Ne pas creer d'exception wildcard, par dossier, ou sans condition de sortie.
  - Ne pas ajouter de nouveau fallback literal pour compenser un token manquant.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot multi-fichiers de fallbacks allowlistes vers tokens canoniques ou exceptions exactes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit rester equivalent lorsque les tokens globaux sont charges.
  - Toute difference visuelle doit etre documentee comme convergence vers un token semantique existant.
  - Aucun contrat de composant React ne doit changer.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un fallback semble necessaire pour un mode d'isolation sans source de tokens globale.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards Vitest design-system et css-fallback valident les exceptions actives. |
| Baseline Snapshot | yes | Le lot doit avoir un compte before/after prouvant la reduction. |
| Ownership Routing | yes | Les tokens requis et exceptions fallback ont des owners distincts. |
| Allowlist Exception | yes | Chaque fallback restant doit etre une exception exacte. |
| Contract Shape | no | Aucun API, DTO, schema ou type public n'est modifie. |
| Batch Migration | yes | Le scope est un lot borne de fichiers CSS. |
| Reintroduction Guard | yes | Les fallbacks retires ou non classes ne doivent pas revenir. |
| Persistent Evidence | yes | Les inventaires before/after doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/css-fallback-policy.test.ts`
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`
- Secondary evidence:
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/tests/design-system-allowlist.ts`
  - Scan `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - Ils comptent les fallbacks mais ne prouvent pas leur classification exacte.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-044-reduire-fallbacks-css-layout-shell-pages/css-fallbacks-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-044-reduire-fallbacks-css-layout-shell-pages/css-fallbacks-after.md`
- Expected invariant:
  - Tous les fallbacks du lot sont traites; aucun fallback non classe n'est ajoute hors lot.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Token global requis | `frontend/src/styles/design-tokens.css` et `token-namespace-registry.md` | fallback literal local |
| Exception fallback | `css-fallback-allowlist.md` + `CSS_FALLBACK_EXCEPTIONS` | exception implicite |
| Validation executable | `css-fallback-policy.test.ts` et `design-system-guards.test.ts` | verification manuelle seule |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/css-fallback-allowlist.md` | fallbacks restants du lot | Exception documentee. | Exit condition required. |
| `frontend/src/tests/design-system-allowlist.ts` | `CSS_FALLBACK_EXCEPTIONS` | Exception executable exacte. | Must match documented retained exceptions. |

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
| Layout shell pages | selected CSS fallbacks | token or exact exception | selected CSS | fallback tests | scan + diff | missing owner |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-044-reduire-fallbacks-css-layout-shell-pages/css-fallbacks-before.md` | Capturer chaque fallback du lot avant edition. |
| After inventory | `_condamad/stories/CS-044-reduire-fallbacks-css-layout-shell-pages/css-fallbacks-after.md` | Prouver le traitement complet du lot. |
| Fallback registry | `frontend/src/styles/css-fallback-allowlist.md` | Documenter les exceptions restantes. |
| Executable allowlist | `frontend/src/tests/design-system-allowlist.ts` | Garder la preuve executable exacte. |

## 4i. Reintroduction Guard

- Guard target: fallback CSS migre ou fallback non present dans l'allowlist exacte.
- Architecture guard against reintroduction required: `frontend/src/tests/css-fallback-policy.test.ts` doit echouer pour tout fallback non classe.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- css-fallback design-system`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1831/02-finding-register.md#F-002` - 117 fallbacks CSS restent dans 19 fichiers.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1831/00-audit-report.md#F-002---CSS-Fallback-Debt-19-Files` - liste exhaustive des fichiers candidats.
- Evidence 3: `frontend/src/styles/css-fallback-allowlist.md` - registre des exceptions CSS fallback.
- Evidence 4: `frontend/src/tests/design-system-allowlist.ts` - allowlist executable des exceptions.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Chaque fallback du lot est traite, sans reste ambigu.
- Les fallbacks migres consomment les tokens canoniques sans valeur locale de secours.
- Les exceptions restantes ont owner, raison et condition de sortie synchronises markdown/executable.
- Les guards prouvent que le lot est complet et que la dette ne croit pas ailleurs.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens frontend doivent rester classes.
  - `RG-048` - aucun fallback CSS non classe ne doit etre ajoute.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-045` - les hardcoded values hors fallback ne sont pas le domaine principal.
  - `RG-046` - la typographie n'est pas le domaine principal.
  - `RG-047` - les styles inline ne sont pas touches.
  - `RG-049` - aucun selecteur legacy n'est cree.
- Required regression evidence:
  - `npm run test -- css-fallback design-system`, scan fallback cible, `npm run lint`.
- Allowed differences:
  - Suppression de fallbacks et conservation d'exceptions exactes documentees.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Baseline exhaustif des 7 fichiers du lot. | Evidence: `rg -n "App.css|Header.css|Sidebar.css" css-fallbacks-before.md`. |
| AC2 | Chaque fallback du lot a une decision finale. | Evidence: `rg -n "unclassified|TODO|TBD" css-fallbacks-after.md` zero-hit. |
| AC3 | Les decisions `migrate-token` utilisent le token sans fallback literal. | Evidence: batch scan `rg -n "var\\(" src -g "*.css"`. |
| AC4 | Les exceptions restantes sont synchronisees markdown/executable. | Evidence profile: `allowlist_register_validated`; `npm run test -- css-fallback design-system`. |
| AC5 | Aucun fallback CSS non classe n'est introduit hors lot. | Evidence: AST guard `css-fallback-policy.test.ts`; `npm run test -- css-fallback`. |
| AC6 | Le frontend reste valide apres migration. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`; `npm run test -- css-fallback design-system`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline exhaustif du lot selectionne (AC: AC1)
- [ ] Task 2 - Classer chaque fallback du lot avec owner, decision et justification (AC: AC2)
- [ ] Task 3 - Migrer tous les fallbacks `migrate-token` vers la consommation canonique du token (AC: AC3)
- [ ] Task 4 - Mettre a jour le registre markdown et l'allowlist executable pour les exceptions conservees (AC: AC4)
- [ ] Task 5 - Capturer l'inventaire after et les scans zero-hit attendus (AC: AC2, AC3, AC5)
- [ ] Task 6 - Executer lint et guards frontend cibles (AC: AC4, AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/tests/design-system-allowlist.ts`
- Do not recreate:
  - Une deuxieme allowlist fallback.
  - Des tokens locaux non classes.
  - Des fallbacks de secours silencieux dans les fichiers touches.
- Shared abstraction allowed only if:
  - Elle supprime une repetition mesurable et elle est documentee dans le registre de namespaces.

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

- `var(--token, value)` conserve dans le lot sans ligne markdown et allowlist executable.
- Entree `CSS_FALLBACK_EXCEPTIONS` sans equivalent dans `css-fallback-allowlist.md`.
- Exception wildcard ou par dossier.
- Nouveau token absent de `token-namespace-registry.md`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Token requis | `frontend/src/styles/design-tokens.css` + `token-namespace-registry.md` | fallback literal local |
| Exception fallback | `css-fallback-allowlist.md` + `CSS_FALLBACK_EXCEPTIONS` | CSS implicite |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/App.css`
- `frontend/src/components/layout/Header.css`
- `frontend/src/components/layout/Sidebar.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/styles/glass.css`
- `frontend/src/styles/utilities.css`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - suppression ou classification des fallbacks du lot.
- `frontend/src/components/layout/Header.css` - suppression ou classification des fallbacks du lot.
- `frontend/src/components/layout/Sidebar.css` - suppression ou classification des fallbacks du lot.
- `frontend/src/pages/HelpPage.css` - suppression ou classification des fallbacks du lot.
- `frontend/src/pages/settings/Settings.css` - suppression ou classification des fallbacks du lot.
- `frontend/src/styles/glass.css` - suppression ou classification des fallbacks du lot.
- `frontend/src/styles/utilities.css` - suppression ou classification des fallbacks du lot.
- `frontend/src/styles/css-fallback-allowlist.md` - synchronisation des exceptions.
- `frontend/src/tests/design-system-allowlist.ts` - synchronisation executable.
- `_condamad/stories/CS-044-reduire-fallbacks-css-layout-shell-pages/css-fallbacks-before.md` - baseline.
- `_condamad/stories/CS-044-reduire-fallbacks-css-layout-shell-pages/css-fallbacks-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/css-fallback-policy.test.ts` - garde principale.
- `frontend/src/tests/design-system-guards.test.ts` - garde design-system.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/**/*.tsx` - hors scope de cette story.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- css-fallback design-system
$files = @("src/App.css", "src/components/layout/Header.css", "src/components/layout/Sidebar.css")
$files += @("src/pages/HelpPage.css", "src/pages/settings/Settings.css", "src/styles/glass.css", "src/styles/utilities.css")
rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," $files
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-044-reduire-fallbacks-css-layout-shell-pages/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-044-reduire-fallbacks-css-layout-shell-pages/00-story.md
```

## 22. Regression Risks

- Risk: un fallback necessaire en contexte isole est migre a tort.
  - Guardrail: decision `blocker` obligatoire si l'owner token global n'est pas garanti.
- Risk: le registre markdown et l'allowlist executable divergent.
  - Guardrail: `npm run test -- css-fallback design-system`.
- Risk: le lot est seulement partiellement traite.
  - Guardrail: AC1 et AC2 exigent 100% des fichiers et zero item non classe.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Ne pas declarer la story terminee tant que chaque fallback du lot n'a pas une decision prouvee.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1831/03-story-candidates.md#SC-001` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1831/02-finding-register.md#F-002` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1831/00-audit-report.md` - liste exhaustive des fichiers candidats.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
