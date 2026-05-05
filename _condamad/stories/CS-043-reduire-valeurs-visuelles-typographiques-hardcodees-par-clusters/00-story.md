# Story CS-043 reduire-valeurs-visuelles-typographiques-hardcodees-par-clusters: Reduire les valeurs visuelles et typographiques hardcodees par clusters

Status: done

## 1. Objective

Migrer les valeurs visuelles et typographiques hardcodees dans des clusters CSS fortement repetes.
La convergence doit utiliser les tokens et roles existants sans creer de namespaces non classes.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1748/03-story-candidates.md#SC-004`
- Reason for change: le finding `F-005` indique encore 1671 hits color-like, 1570 declarations typographiques et 2653 declarations spacing/radius/shadow dans `frontend/src`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src`
- In scope:
  - Capturer les compteurs before des valeurs visuelles et typographiques du lot selectionne.
  - Selectionner un ou plusieurs clusters coherents et bornes depuis la liste F-005.
  - Remplacer les repetitions par des tokens/roles semantiques existants.
  - Documenter toute nouvelle extension semantique durable dans le registre de namespaces ou de typographie.
  - Prouver la reduction par compteurs after et tests design-system.
- Out of scope:
  - Migration exhaustive de tous les fichiers F-005 si elle depasse le lot borne.
  - Conversion des styles inline, sauf si un fichier du lot contient aussi une dette inline deja couverte par `CS-041`.
  - Reduction des fallbacks CSS `var(--token, value)` couverte par `CS-042`.
  - Changement de layout ou refonte visuelle.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-046` ou `RG-050`.
  - Ne pas creer de token opportuniste pour une valeur unique.
  - Ne pas remplacer une valeur par un token near-equivalent sans justification.
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne de declarations CSS hardcodees vers des tokens/roles canoniques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit rester equivalent ou differer uniquement par convergence documentee vers un token semantique.
  - Toute nouvelle extension semantique doit etre documentee et gardee.
  - Aucun changement d'API React, contenu ou navigation n'est autorise.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: plusieurs tokens near-equivalents peuvent remplacer une meme valeur sans signal clair du registre.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards design-system et theme-tokens sont la source executable des regles statiques. |
| Baseline Snapshot | yes | Les compteurs de literals du lot doivent etre compares avant/apres. |
| Ownership Routing | yes | Les decisions visuelles doivent revenir aux tokens, roles et registres canoniques. |
| Allowlist Exception | yes | Les valeurs conservees hors token doivent etre exactes et justifiees. |
| Contract Shape | no | Aucun contrat API, DTO, payload, export ou type public n'est modifie. |
| Batch Migration | yes | Le scope est un lot par clusters CSS. |
| Reintroduction Guard | yes | Les valeurs migrees ne doivent pas revenir dans les fichiers du lot. |
| Persistent Evidence | yes | Les compteurs before/after et decisions doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`.
  - AST guard Vitest: `frontend/src/tests/theme-token-policy.test.ts` ou test theme-token existant equivalent.
- Secondary evidence:
  - `frontend/src/styles/token-namespace-registry.md`.
  - `frontend/src/styles/typography-roles.md`.
  - Scans cibles des couleurs, tailles typographiques, spacing, radius et shadows dans les fichiers du lot.
- Static scans alone are not sufficient for this story because:
  - Les scans detectent les literals mais ne prouvent pas que les remplacements respectent les owners canoniques.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-043-reduire-valeurs-visuelles-typographiques-hardcodees-par-clusters/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-043-reduire-valeurs-visuelles-typographiques-hardcodees-par-clusters/hardcoded-values-after.md`
- Expected invariant:
  - Les compteurs du lot diminuent sans expansion de namespaces non classes ni regression des roles typographiques.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Couleurs globales et surfaces recurrentes | `frontend/src/styles/design-tokens.css` et `token-namespace-registry.md` | literal CSS repete non classe |
| Typographie semantique | `frontend/src/styles/typography-roles.md` et tokens associes | declarations typographiques repetees |
| Exceptions visuelles conservees | registre/story evidence du lot | exception implicite dans CSS |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `hardcoded-values-after.md` | literals conserves du lot | Exception auditee ou valeur unique. | Sortie ou permanence documentee. |
| `frontend/src/styles/token-namespace-registry.md` | nouveau token ou namespace | Extension semantique durable. | Permanent only if reusable and classified. |
| `frontend/src/styles/typography-roles.md` | nouveau role typographique | Role semantique durable. | Permanent only if reusable and classified. |

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
| Visual cluster | repeated literals | token, role, or extension | CSS lot | `npm run test -- theme-tokens` | count + scan | ambiguity |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before count | `hardcoded-values-before.md` | Capturer fichiers, compteurs et clusters. |
| After count | `hardcoded-values-after.md` | Prouver la reduction et les exceptions. |
| Token registry | `frontend/src/styles/token-namespace-registry.md` | Documenter toute extension semantique durable. |
| Typography registry | `frontend/src/styles/typography-roles.md` | Documenter tout role typographique durable. |

## 4i. Reintroduction Guard

- Guard target: valeurs hardcodees migrees dans les fichiers du lot et namespaces non classes.
- Architecture guard required: les guards design-system/theme-tokens doivent echouer si un literal migre revient sans classification ou si un namespace non classe est ajoute.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- design-system theme-tokens` plus scans cibles du lot.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1748/02-finding-register.md#F-005` - les valeurs visuelles et typographiques hardcodees restent larges.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1748/00-audit-report.md` -
  liste exhaustive des fichiers candidats pour `F-005`.
- Evidence 3: `frontend/src/styles/token-namespace-registry.md` - registre des namespaces de tokens.
- Evidence 4: `frontend/src/styles/typography-roles.md` - registre des roles typographiques.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Le lot selectionne contient moins de literals visuels et typographiques repetes.
- Les remplacements reutilisent les tokens/roles existants lorsque possible.
- Les nouvelles extensions semantiques sont documentees et testees.
- Les exceptions restantes sont listees avec raison et condition de sortie.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens frontend doivent rester classes.
  - `RG-045` - les valeurs migrees ne doivent pas revenir dans les fichiers du lot.
  - `RG-046` - les roles typographiques semantiques sont canoniques pour les repetitions.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-047` - les styles inline ne sont pas le domaine principal.
  - `RG-048` - les fallbacks CSS sont traites par `CS-042`.
  - `RG-049` - les surfaces legacy CSS ne sont pas le domaine principal.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens`, scans cibles before/after, `npm run lint`.
- Allowed differences:
  - Convergence visuelle documentee vers un token ou role semantique existant.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les compteurs before sont captures. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "cluster|count" hardcoded-values-before.md`. |
| AC2 | Les literals repetes migrent vers les tokens clairs. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `rg -n "#[0-9A-Fa-f]{3,8}" src -g "*.css"`. |
| AC3 | Toute valeur conservee hors token est justifiee. | Evidence profile: `allowlist_register_validated`; command: `rg -n "Reason|Exit" hardcoded-values-after.md`. |
| AC4 | Aucun namespace de token ou role typographique non classe n'est introduit. | Evidence profile: `architecture_guard`; `npm run test -- design-system theme-tokens`. |
| AC5 | Les surfaces touchees gardent un rendu fonctionnel. | Evidence profile: `component_behavior_test`; command: `npm run test -- design-system theme-tokens`. |
| AC6 | Le frontend reste lintable. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer les compteurs before et choisir un cluster borne (AC: AC1)
- [ ] Task 2 - Mapper les literals repetes vers tokens/roles existants ou blocker si ambigu (AC: AC2, AC4)
- [ ] Task 3 - Modifier les CSS du lot sans changer l'API React ni le contenu (AC: AC2, AC5)
- [ ] Task 4 - Documenter les exceptions et toute extension semantique durable (AC: AC3, AC4)
- [ ] Task 5 - Capturer les compteurs after et les scans de non-retour (AC: AC1, AC2, AC3)
- [ ] Task 6 - Executer lint, guards et tests cibles (AC: AC4, AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css`.
  - `frontend/src/styles/token-namespace-registry.md`.
  - `frontend/src/styles/typography-roles.md`.
  - Variables CSS deja presentes dans les feuilles de style locales.
  - Tests `design-system` et `theme-tokens` existants.
- Do not recreate:
  - Token pour une valeur unique sans reutilisation.
  - Role typographique duplicatif.
  - Classe utilitaire globale pour un cas local.
  - Palette parallele dans un fichier CSS.
- Shared abstraction allowed only if:
  - Elle supprime une repetition mesurable et elle est documentee dans le registre approprie.

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

- Nouveau token ou namespace absent de `token-namespace-registry.md`.
- Nouveau role absent de `typography-roles.md`.
- Literal migre qui revient dans un fichier du lot.
- Valeur near-equivalent remplacee sans justification.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Couleurs et effets reutilisables | `design-tokens.css` + `token-namespace-registry.md` | literals repetes |
| Typographie reutilisable | `typography-roles.md` + tokens associes | declarations repetees |
| Exceptions du lot | artefacts before/after de cette story | exception implicite dans CSS |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/index.css`
- `frontend/src/App.css`
- `frontend/src/layouts/AuthLayout.css`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/WizardLayout.css`
- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Card/Card.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/landing/LandingPage.css`
- `_condamad/audits/frontend-design-system/2026-05-05-1748/00-audit-report.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- CSS du cluster selectionne depuis `00-audit-report.md#F-005---Hardcoded-Visual--Typography-Files-Outside-Token-Sources` - migration de literals.
- `frontend/src/styles/token-namespace-registry.md` - uniquement si un token/namespace durable est introduit.
- `frontend/src/styles/typography-roles.md` - uniquement si un role typographique durable est introduit.
- `_condamad/stories/CS-043-reduire-valeurs-visuelles-typographiques-hardcodees-par-clusters/hardcoded-values-before.md` - baseline.
- `_condamad/stories/CS-043-reduire-valeurs-visuelles-typographiques-hardcodees-par-clusters/hardcoded-values-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - garde design-system.
- Test theme-token existant sous `frontend/src/tests` - validation des tokens.
- Tests composants/pages touches quand disponibles.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/tests/design-system-allowlist.ts` - hors scope sauf si une exception design-system existante doit rester synchronisee.
- `frontend/src/styles/css-fallback-allowlist.md` - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- design-system theme-tokens
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\\(|hsla?\\(|font-size:|font-weight:|line-height:|letter-spacing:|box-shadow:|border-radius:|margin:|padding:" src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-043-reduire-valeurs-visuelles-typographiques-hardcodees-par-clusters/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: un token near-equivalent modifie subtilement le rendu.
  - Guardrail: blocker utilisateur si le mapping n'est pas clair.
- Risk: un nouveau namespace non classe apparait.
  - Guardrail: `RG-044` et tests theme-tokens.
- Risk: un literal migre revient dans le meme cluster.
  - Guardrail: inventaire after et scan cible.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Ne pas utiliser cette story pour une refonte visuelle; elle vise une migration mesurable vers les owners canoniques.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1748/03-story-candidates.md#SC-004` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1748/02-finding-register.md#F-005` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1748/00-audit-report.md` - liste exhaustive des fichiers candidats.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
