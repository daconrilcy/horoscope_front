# Story CS-058 migrer-cluster-coherent-valeurs-visuelles-hardcodees: Migrer un cluster coherent de valeurs visuelles hardcodees

Status: ready-to-dev

## 1. Objective

Migrer un seul cluster produit coherent de valeurs visuelles ou typographiques hardcodees.
Le cluster doit converger vers les tokens, roles typographiques ou utilitaires existants.
La story exclut tout refactor global des 116 fichiers signales.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-003`
- Reason for change: `F-004` indique 116 fichiers avec signaux visuels ou typographiques hardcodes qui concurrencent encore les tokens semantiques.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components`
- In scope:
  - Choisir un cluster borne: prediction cards, natal interpretation, chat shell, ou admin prompt surfaces.
  - Utiliser les tokens, roles typographiques et utilitaires existants avant toute creation.
  - Capturer les compteurs before/after pour les fichiers du cluster choisi.
  - Mettre a jour `token-namespace-registry.md` ou `typography-roles.md` seulement si un token ou role durable est introduit.
- Out of scope:
  - Migration de tous les 116 fichiers.
  - Refonte visuelle produit.
  - Migration des fallbacks CSS ou styles inline sauf lorsqu'un fichier du cluster impose une classification explicite.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-046` ou `RG-050`.
  - Ne pas creer de token synonyme pour contourner une valeur locale.
  - Ne pas changer de surface produit en cours de story.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un batch de valeurs locales dans un cluster nomme avec preuves before/after.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit converger vers des tokens existants sans degradation fonctionnelle.
  - Une difference visuelle n'est admise que si elle est documentee comme alignement token/role.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: deux valeurs proches portent une intention produit differente ou si un nouveau token semantique durable est necessaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests `design-system`, `theme-tokens` et `visual-smoke` valident le comportement executable. |
| Baseline Snapshot | yes | Les compteurs before/after du cluster sont obligatoires. |
| Ownership Routing | yes | Les decisions visuelles doivent appartenir aux tokens, roles ou utilitaires canoniques. |
| Allowlist Exception | no | La story ne doit pas ajouter d'exception durable sans autre registre exact. |
| Contract Shape | no | Aucun contrat API ou type public n'est modifie. |
| Batch Migration | yes | Le cluster contient plusieurs declarations/fichiers. |
| Reintroduction Guard | yes | Les valeurs migrees ne doivent pas revenir non classees. |
| Persistent Evidence | yes | Les inventories du cluster doivent rester auditables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - tests `design-system`, `theme-tokens` et `visual-smoke`.
- Secondary evidence:
  - scan cible des literals dans le cluster choisi.
- Static scans alone are not sufficient for this story because:
  - Une valeur hardcodee peut etre valide si elle est une donnee locale non design-system; la classification du cluster est requise.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-058-migrer-cluster-coherent-valeurs-visuelles-hardcodees/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-058-migrer-cluster-coherent-valeurs-visuelles-hardcodees/hardcoded-values-after.md`
- Expected invariant:
  - Les valeurs design-system du cluster diminuent ou sont classees avec decision explicite.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Couleur, spacing, radius, shadow repetes | token existant ou utilitaire existant | literal local repete |
| Taille/poids/line-height typographique | `typography-roles.md` et roles CSS existants | declaration typographique locale repetee |
| Nouveau token durable | `design-tokens.css` plus registre namespace | token non documente |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: the selected archetype does not require an exception allowlist.
  Any retained literal must be documented in the before/after artifacts.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Selected cluster | hardcoded declarations | existing tokens and roles | selected files | design-system tests | inventory diff | product decision |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `hardcoded-values-before.md` | Capturer cluster, fichiers et compteurs initiaux. |
| After inventory | `hardcoded-values-after.md` | Prouver valeurs migrees, restants et differences admises. |

## 4i. Reintroduction Guard

- Guard target: valeurs migrees du cluster et registres tokens/typographie.
- Architecture guard against reintroduction required: `npm run test -- design-system theme-tokens visual-smoke`.
- Guard evidence: Evidence profile: `reintroduction_guard`; tests plus scan cible des valeurs migrees.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0016/00-audit-report.md#F-004` - 116 fichiers contiennent encore des signaux hardcodes.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-003` - demande un cluster coherent et des compteurs before/after.
- Evidence 3: `frontend/src/styles/token-namespace-registry.md` - registre des namespaces de tokens.
- Evidence 4: `frontend/src/styles/typography-roles.md` - roles typographiques canoniques.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Un cluster produit unique est choisi et documente.
- Les literals remplacables du cluster utilisent des tokens, roles ou utilitaires existants.
- Toute creation durable de token ou role est inscrite dans le registre approprie.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens restent classes.
  - `RG-045` - les valeurs migrees ne doivent pas revenir non classees.
  - `RG-046` - les roles typographiques sont la voie canonique.
  - `RG-050` - les guards design-system restent executables.
- Non-applicable invariants:
  - `RG-047` - les styles inline ne sont pas le scope principal.
  - `RG-048` - les fallbacks CSS ne sont pas le scope principal.
  - `RG-049` - les selectors legacy ne sont pas le scope principal.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens visual-smoke`
  - `npm run lint`
  - inventories before/after.
- Allowed differences:
  - Diminution des literals du cluster ou remplacement par tokens/roles documentes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le cluster choisi est borne. | Evidence profile: `baseline_before_after_diff`; `rg -n "#[0-9A-Fa-f]{3,8}|px|rem" frontend/src`. |
| AC2 | Les valeurs remplacees reutilisent les tokens existants. | Evidence profile: `ast_architecture_guard`; `npm run test -- design-system theme-tokens`. |
| AC3 | Tout token ou role durable est registre ou bloque. | Evidence profile: `allowlist_register_validated`; `npm run test -- theme-tokens design-system`. |
| AC4 | Le compteur du cluster diminue ou reste justifie. | Evidence profile: `baseline_before_after_diff`; `rg -n "#[0-9A-Fa-f]{3,8}|px|rem" frontend/src`. |
| AC5 | Les validations frontend ciblees passent. | Evidence profile: `frontend_quality`; `npm run test -- design-system theme-tokens visual-smoke` et `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Choisir et documenter un cluster unique avant edition (AC: AC1)
- [ ] Task 2 - Capturer les compteurs et valeurs initiales du cluster (AC: AC1, AC4)
- [ ] Task 3 - Remplacer les valeurs eligibles par tokens, roles ou utilitaires existants (AC: AC2)
- [ ] Task 4 - Mettre a jour les registres uniquement si un token ou role durable est ajoute (AC: AC3)
- [ ] Task 5 - Capturer l'after et executer les validations (AC: AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/utilities.css`
  - `frontend/src/styles/typography-roles.md`
  - `frontend/src/styles/token-namespace-registry.md`
- Do not recreate:
  - token synonyme d'une valeur existante.
  - classe utilitaire locale si une utilite globale existe deja.
  - second registre de valeurs hardcodees.
- Shared abstraction allowed only if:
  - Elle reduit une repetition observee dans le cluster choisi et son owner est clair.

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

- Nouveau token non classe.
- Literal repete remplace par un autre literal equivalent.
- Migration opportuniste hors cluster choisi.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Tokens globaux | `design-tokens.css` et `theme.css` | literals locaux repetes |
| Roles typographiques | `typography-roles.md` | declarations typographiques dupliquees |
| Classification namespace | `token-namespace-registry.md` | token implicite |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/utilities.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/NatalInterpretation.css`
- `frontend/src/features/chat/components/ChatWindow.css`
- `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/components/prediction/PeriodCard.css` - possible cluster prediction cards.
- `frontend/src/components/prediction/KeyPointCard.css` - possible cluster prediction cards.
- `frontend/src/components/NatalInterpretation.css` - possible cluster natal.
- `frontend/src/features/chat/components/ChatWindow.css` - possible cluster chat shell.
- `frontend/src/styles/token-namespace-registry.md` - seulement si token durable ajoute.
- `frontend/src/styles/typography-roles.md` - seulement si role durable ajoute.
- `_condamad/stories/CS-058-migrer-cluster-coherent-valeurs-visuelles-hardcodees/hardcoded-values-before.md` - baseline.
- `_condamad/stories/CS-058-migrer-cluster-coherent-valeurs-visuelles-hardcodees/hardcoded-values-after.md` - evidence finale.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`

Files not expected to change:

- `backend/` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/tests/inline-style-allowlist.ts` - hors scope sauf si le cluster choisi contient une exception inline explicitement classifiee.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens visual-smoke
npm run lint
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-058-migrer-cluster-coherent-valeurs-visuelles-hardcodees/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-058-migrer-cluster-coherent-valeurs-visuelles-hardcodees/00-story.md
```

## 22. Regression Risks

- Risk: creation de tokens synonymes.
  - Guardrail: AC2 impose reuse avant creation.
- Risk: refactor trop large.
  - Guardrail: AC1 borne un seul cluster.
- Risk: changement visuel non documente.
  - Guardrail: AC4 exige before/after et differences admises.

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

- `_condamad/audits/frontend-design-system/2026-05-06-0016/03-story-candidates.md#SC-003` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-06-0016/02-finding-register.md#F-004` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-06-0016/00-audit-report.md#F-004` - broad file list.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
