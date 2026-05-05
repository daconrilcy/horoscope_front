# Story CS-046 migrer-cluster-visuel-typographique-prioritaire: Migrer le cluster visuel et typographique prioritaire

Status: ready-to-dev

## 1. Objective

Migrer a 100% le cluster prioritaire de valeurs visuelles et typographiques hardcodees identifie par l'audit `2026-05-05-1831`.
Le lot couvre `App.css`, `AdminPromptsPage.css`, `HelpPage.css`, `Settings.css` et `AstrologerProfilePage.css`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1831/03-story-candidates.md#SC-003`
- Reason for change: le finding `F-004` mesure une dette large dans 109 fichiers et recommande de poursuivre par clusters de plus forte densite.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src`
- In scope:
  - Traiter le cluster exact: `App.css`, `AdminPromptsPage.css`, `HelpPage.css`, `Settings.css`, `AstrologerProfilePage.css`.
  - Capturer les compteurs before/after pour couleurs, typographie, spacing, radius et shadow dans ces fichiers.
  - Remplacer les repetitions par tokens ou roles existants lorsque le mapping est clair.
  - Documenter toute extension semantique durable dans `token-namespace-registry.md` ou `typography-roles.md`.
- Out of scope:
  - Les autres fichiers F-004 non inclus dans le cluster.
  - Styles inline TSX traites par `CS-045`.
  - Fallbacks CSS traites par `CS-044`.
  - Refonte UX ou changement de contenu.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-046` ou `RG-050`.
  - Ne pas creer de token pour une valeur unique.
  - Ne pas remplacer par un token near-equivalent sans justification explicite.
  - Ne pas corriger du style hors cluster.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un cluster borne de declarations hardcodees vers les owners canoniques du design-system.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit rester equivalent ou differer uniquement par convergence documentee vers un token/role semantique.
  - Aucune API React, route, contenu ou logique produit ne doit changer.
  - Toute extension semantique doit etre reutilisable et documentee.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: plusieurs tokens possibles peuvent remplacer une valeur sans signal clair du registre.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards design-system/theme-tokens valident les regles de tokens et exceptions. |
| Baseline Snapshot | yes | Les compteurs du cluster doivent etre compares before/after. |
| Ownership Routing | yes | Les decisions visuelles doivent revenir aux tokens, roles et registres canoniques. |
| Allowlist Exception | yes | Les valeurs conservees hors token doivent etre exactes et justifiees. |
| Contract Shape | no | Aucun API, DTO, schema ou type public n'est modifie. |
| Batch Migration | yes | Le scope est un cluster multi-fichiers. |
| Reintroduction Guard | yes | Les literals migres ne doivent pas revenir dans le cluster. |
| Persistent Evidence | yes | Les compteurs before/after et decisions doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`
  - AST guard Vitest: `frontend/src/tests/theme-tokens.test.ts`
- Secondary evidence:
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - Scans cibles des couleurs, tailles, poids, line-height, spacing, radius et shadows dans le cluster.
- Static scans alone are not sufficient for this story because:
  - Ils detectent les literals mais ne prouvent pas que le remplacement respecte le proprietaire canonique.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-046-migrer-cluster-visuel-typographique-prioritaire/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-046-migrer-cluster-visuel-typographique-prioritaire/hardcoded-values-after.md`
- Expected invariant:
  - Les compteurs du cluster diminuent et chaque literal conserve est justifie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Couleurs recurrentes | `design-tokens.css` + `token-namespace-registry.md` | literal repete non classe |
| Typographie recurrente | `typography-roles.md` + tokens associes | declarations repetees implicites |
| Exceptions conservees | artefacts before/after de la story | exception implicite dans CSS |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `hardcoded-values-after.md` | literals conserves du cluster | Valeur unique, contrainte externe ou blocker. | Sortie ou permanence documentee. |
| `frontend/src/styles/token-namespace-registry.md` | nouveau token ou namespace | Extension semantique durable. | Permanent only if reusable and classified. |
| `frontend/src/styles/typography-roles.md` | nouveau role typographique | Role durable. | Permanent only if reusable and classified. |

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
| Priority visual cluster | repeated CSS literals | tokens, roles, or exception | 5 CSS files | token tests | counts + scans | ambiguous mapping |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before count | `_condamad/stories/CS-046-migrer-cluster-visuel-typographique-prioritaire/hardcoded-values-before.md` | Capturer compteurs, valeurs repetees et mapping propose. |
| After count | `hardcoded-values-after.md` | Prouver reduction et exceptions finales. |
| Token registry | `frontend/src/styles/token-namespace-registry.md` | Documenter toute extension semantique durable. |
| Typography registry | `frontend/src/styles/typography-roles.md` | Documenter tout role typographique durable. |

## 4i. Reintroduction Guard

- Guard target: literals migres dans les cinq fichiers du cluster et namespaces non classes.
- Architecture guard against reintroduction required: les tests design-system/theme-tokens doivent echouer si un literal migre revient sans classification.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- design-system theme-tokens` plus scans cibles.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1831/02-finding-register.md#F-004` - hardcoded colors, spacing, radius, shadows et typographie restent larges.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1831/00-audit-report.md` - liste exhaustive des fichiers candidats F-004.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-05-1831/03-story-candidates.md#SC-003` - cluster prioritaire.
- Evidence 4: `frontend/src/styles/token-namespace-registry.md` - registre de namespaces tokens.
- Evidence 5: `frontend/src/styles/typography-roles.md` - registre des roles typographiques.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les cinq fichiers du cluster contiennent moins de valeurs visuelles et typographiques hardcodees.
- Les repetitions migrent vers tokens ou roles existants quand le mapping est clair.
- Les exceptions restantes sont auditees avec raison et condition de sortie.
- Les registries restent synchronises avec toute extension semantique.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens frontend doivent rester classes.
  - `RG-045` - les valeurs migrees ne doivent pas revenir dans les fichiers du lot.
  - `RG-046` - les roles typographiques semantiques sont canoniques pour les repetitions.
  - `RG-050` - les guards design-system doivent rester executables.
- Non-applicable invariants:
  - `RG-047` - les styles inline TSX ne sont pas le domaine principal.
  - `RG-048` - les fallbacks CSS sont traites par `CS-044`.
  - `RG-049` - aucun selecteur legacy n'est cree.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens`, scans before/after, `npm run lint`.
- Allowed differences:
  - Convergence documentee vers des tokens ou roles semantiques.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Baseline par fichier des compteurs visuels du cluster. | Evidence: `rg -n "App.css|AdminPromptsPage.css" hardcoded-values-before.md`. |
| AC2 | Chaque literal repete a une decision finale. | Evidence: `rg -n "unclassified|TODO|TBD" hardcoded-values-after.md` zero-hit. |
| AC3 | Les mappings clairs migrent vers tokens ou roles canoniques. | Evidence: batch scan `rg -n "#|font-size|box-shadow" src -g "*.css"`. |
| AC4 | Toute extension de token ou role est documentee dans le registre approprie. | Evidence profile: `architecture_guard`; `npm run test -- theme-tokens design-system`. |
| AC5 | Le cluster preserve la logique produit. | Evidence: AST guard `design-system-guards.test.ts`; `npm run test -- design-system`. |
| AC6 | Le frontend reste buildable. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run build`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer les compteurs before pour les cinq fichiers du cluster (AC: AC1)
- [ ] Task 2 - Classer chaque literal repete avec mapping canonique ou exception/blocker (AC: AC2)
- [ ] Task 3 - Migrer les valeurs avec mapping clair vers tokens ou roles existants (AC: AC3)
- [ ] Task 4 - Documenter toute extension semantique durable et les exceptions finales (AC: AC2, AC4)
- [ ] Task 5 - Capturer les compteurs after et scans cibles de non-retour (AC: AC1, AC2, AC3)
- [ ] Task 6 - Executer lint, build et guards frontend (AC: AC4, AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - Variables CSS locales deja presentes dans les fichiers du cluster.
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
- Do not recreate:
  - Token pour une valeur unique.
  - Role typographique duplicatif.
  - Palette parallele dans un CSS de page.
  - Utility globale pour un cas strictement local.
- Shared abstraction allowed only if:
  - Elle supprime une repetition mesurable dans le cluster et son owner est documente.

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

- Nouveau namespace token absent de `token-namespace-registry.md`.
- Nouveau role absent de `typography-roles.md`.
- Literal migre qui revient dans le cluster sans justification.
- Remplacement near-equivalent non documente.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Couleurs et effets reutilisables | `design-tokens.css` + `token-namespace-registry.md` | literals repetes |
| Typographie reutilisable | `typography-roles.md` + tokens associes | declarations repetees |
| Exceptions du cluster | `hardcoded-values-after.md` | exception implicite dans CSS |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/App.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/AstrologerProfilePage.css`
- `_condamad/audits/frontend-design-system/2026-05-05-1831/00-audit-report.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - migration des literals repetes du cluster.
- `frontend/src/pages/admin/AdminPromptsPage.css` - migration des literals repetes du cluster.
- `frontend/src/pages/HelpPage.css` - migration des literals repetes du cluster.
- `frontend/src/pages/settings/Settings.css` - migration des literals repetes du cluster.
- `frontend/src/pages/AstrologerProfilePage.css` - migration des literals repetes du cluster.
- `frontend/src/styles/token-namespace-registry.md` - uniquement si une extension semantique durable est introduite.
- `frontend/src/styles/typography-roles.md` - uniquement si un role durable est introduit.
- `_condamad/stories/CS-046-migrer-cluster-visuel-typographique-prioritaire/hardcoded-values-before.md` - baseline.
- `_condamad/stories/CS-046-migrer-cluster-visuel-typographique-prioritaire/hardcoded-values-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - garde design-system.
- `frontend/src/tests/theme-tokens.test.ts` - garde tokens.
- Tests pages existants si les classes visibles changent.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/tests/inline-style-allowlist.ts` - hors scope.
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
npm run build
$files = @("src/App.css", "src/pages/admin/AdminPromptsPage.css", "src/pages/HelpPage.css")
$files += @("src/pages/settings/Settings.css", "src/pages/AstrologerProfilePage.css")
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\\(|font-size:|box-shadow:|border-radius:" $files
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-046-migrer-cluster-visuel-typographique-prioritaire/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-046-migrer-cluster-visuel-typographique-prioritaire/00-story.md
```

## 22. Regression Risks

- Risk: un token near-equivalent modifie subtilement le rendu.
  - Guardrail: blocker si le mapping n'est pas clair.
- Risk: un nouveau namespace ou role n'est pas documente.
  - Guardrail: `npm run test -- theme-tokens design-system`.
- Risk: le cluster est traite partiellement.
  - Guardrail: AC1 et AC2 exigent les cinq fichiers et zero item non classe.

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

- `_condamad/audits/frontend-design-system/2026-05-05-1831/03-story-candidates.md#SC-003` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1831/02-finding-register.md#F-004` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1831/00-audit-report.md` - liste exhaustive des fichiers candidats.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
