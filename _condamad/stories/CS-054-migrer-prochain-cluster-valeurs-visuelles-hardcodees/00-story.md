# Story CS-054 migrer-prochain-cluster-valeurs-visuelles-hardcodees: Migrer le prochain cluster de valeurs visuelles hardcodees

Status: ready-to-dev

## 1. Objective

Migrer un cluster produit coherent parmi les 106 fichiers avec valeurs visuelles ou typographiques hardcodees.
Le dev agent choisit un seul cluster, reutilise les tokens/roles existants, capture les compteurs, et documente les exceptions.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-003`
- Reason for change: `F-004` montre que 106 fichiers applicatifs contiennent encore des signaux visuels ou typographiques hardcodes.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src`
- In scope:
  - Choisir un cluster unique, de preference `NatalChartPage`, cartes de prediction, ou shell chat legacy.
  - Capturer les valeurs du cluster avant/apres avec compteurs.
  - Remplacer les valeurs migrables par tokens, roles typographiques ou variables existantes.
  - Mettre a jour `token-namespace-registry.md` ou `typography-roles.md` seulement si une extension durable est creee.
- Out of scope:
  - Traiter les 106 fichiers.
  - Changer UX, contenu, routes, API ou logique React.
  - Reduire les fallbacks CSS ou styles inline sauf s'ils font partie directe du cluster choisi.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-045`, `RG-046` ou `RG-050`.
  - Ne pas creer de token pour une valeur unique.
  - Ne pas masquer une decision produit ambigue par un token near-equivalent.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot multi-fichiers de literals vers owners canoniques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit rester equivalent ou converger explicitement vers un token/role documente.
  - Aucune logique produit, route, API ou comportement React ne change.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une valeur a plusieurs mappings plausibles ou encode une decision produit/design non documentee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les guards `design-system` et `theme-tokens` valident les owners canoniques. |
| Baseline Snapshot | yes | Les compteurs du cluster sont obligatoires. |
| Ownership Routing | yes | Les decisions visuelles doivent appartenir aux tokens, roles ou exceptions documentees. |
| Allowlist Exception | yes | Les exceptions restantes doivent etre explicites dans l'artefact after. |
| Contract Shape | no | Aucun contrat API, DTO, schema ou type public n'est modifie. |
| Batch Migration | yes | Le scope est un cluster coherent potentiellement multi-fichiers. |
| Reintroduction Guard | yes | Les literals migres ne doivent pas revenir non classes. |
| Persistent Evidence | yes | Les compteurs et mappings doivent rester auditables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - `frontend/src/tests/theme-tokens.test.ts`
- Secondary evidence:
  - Scans cibles du cluster pour couleurs, dimensions, shadows, radius, spacing et typographie.
- Static scans alone are not sufficient for this story because:
  - Ils ne prouvent pas que la valeur a ete routee vers le bon owner canonique.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-054-migrer-prochain-cluster-valeurs-visuelles-hardcodees/hardcoded-values-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-054-migrer-prochain-cluster-valeurs-visuelles-hardcodees/hardcoded-values-after.md`
- Expected invariant:
  - Le cluster choisi diminue ses literals hardcodes; chaque valeur restante a une classification et une condition de sortie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Couleur reusable | `design-tokens.css` + `token-namespace-registry.md` | literal local repete |
| Typographie reusable | `typography-roles.md` | declarations typographiques dupliquees |
| Spacing/radius/shadow recurrent | tokens/variables existants | valeur magique locale |
| Exception unique | `hardcoded-values-after.md` | exception implicite |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `hardcoded-values-after.md` | literals conserves du cluster | Valeur unique, blocker, ou decision produit. | Must include exit condition or permanence decision. |
| `frontend/src/styles/token-namespace-registry.md` | nouveau token si cree | Ownership semantique durable. | Permanent only if reusable. |
| `frontend/src/styles/typography-roles.md` | nouveau role si cree | Role typographique durable. | Permanent only if reusable. |

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
| Chosen F-004 cluster | hardcoded values | tokens, roles, variables, or exception | selected files | design/theme guards | counts | ambiguous mapping |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before count | `hardcoded-values-before.md` | Capturer cluster, compteurs, valeurs et mapping propose. |
| After count | `hardcoded-values-after.md` | Prouver reduction, mappings effectifs et exceptions finales. |

## 4i. Reintroduction Guard

- Guard target: valeurs migrees du cluster, namespaces token et roles typographiques.
- Architecture guard against reintroduction required: `npm run test -- design-system theme-tokens`.
- Guard evidence: Evidence profile: `reintroduction_guard`; tests plus scans cibles du cluster.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md#F-004` - 106 fichiers applicatifs avec signaux hardcodes.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-003` - migration par cluster produit borne demandee.
- Evidence 3: `frontend/src/styles/token-namespace-registry.md` - registre des namespaces tokens.
- Evidence 4: `frontend/src/styles/typography-roles.md` - registre des roles typographiques.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Un cluster nomme est traite avec decisions finales pour 100% de ses valeurs.
- Les valeurs migrables utilisent des owners existants ou une extension documentee.
- Les exceptions restantes sont explicites et testees.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens restent classes.
  - `RG-045` - les valeurs migrees ne reviennent pas non classees.
  - `RG-046` - les roles typographiques sont la voie canonique pour les repetitions.
  - `RG-050` - les guards anti-drift restent executables.
- Non-applicable invariants:
  - `RG-047` - styles inline hors scope sauf si le cluster en contient directement.
  - `RG-048` - fallbacks CSS hors scope sauf si le cluster en contient directement.
  - `RG-049` - legacy selectors hors scope sauf cluster chat legacy explicitement choisi.
- Required regression evidence:
  - `npm run test -- design-system theme-tokens`, `npm run lint`, scans cibles et artefacts before/after.
- Allowed differences:
  - Convergence documentee vers tokens/roles semantiques et baisse des compteurs du cluster.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le cluster choisi est explicite. | Evidence profile: `scope_guard`; `rg -n "Cluster|Files" hardcoded-values-before.md`. |
| AC2 | 100% des valeurs du cluster ont une decision finale. | Evidence profile: `baseline_snapshot`; `rg -n "TODO|TBD|unclassified" hardcoded-values-after.md`. |
| AC3 | Les valeurs avec mapping clair migrent vers tokens/roles/variables existants. | Evidence profile: `architecture_guard`; `npm run test -- design-system theme-tokens`. |
| AC4 | Toute extension semantique durable est documentee dans le registre approprie. | Evidence profile: `registry_guard`; `npm run test -- theme-tokens design-system`. |
| AC5 | Les compteurs du cluster diminuent ou les blockers sont justifies. | Evidence profile: `before_after`; `rg -n "Total|before|after" hardcoded-values-*.md`. |
| AC6 | Le frontend reste valide. | Evidence profile: `frontend_quality`; `npm run lint` et tests cibles existants. |

## 8. Implementation Tasks

- [ ] Task 1 - Selectionner un seul cluster et capturer le baseline exhaustif (AC: AC1, AC2)
- [ ] Task 2 - Mapper chaque valeur vers owner canonique, exception ou blocker (AC: AC2, AC3)
- [ ] Task 3 - Migrer les mappings clairs vers tokens/roles/variables existants (AC: AC3)
- [ ] Task 4 - Documenter extensions et exceptions finales (AC: AC4, AC5)
- [ ] Task 5 - Executer les guards, lint et tests cibles (AC: AC3, AC4, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - Variables locales deja presentes dans le cluster.
- Do not recreate:
  - Token pour une valeur unique.
  - Role typographique duplicatif.
  - Utility globale speculative.
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

- Nouveau namespace token absent du registre.
- Nouveau role absent de `typography-roles.md`.
- Literal migre qui reste ou revient sans justification.

## 11. Removal Classification Rules

Classification must be deterministic:

- `migrate`: clear canonical token, role, or variable exists.
- `keep-classified`: unique or externally constrained literal with reason.
- `needs-user-decision`: ambiguous product/design decision.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `migrate` | `replace` | Must use canonical owner. |
| `keep-classified` | `keep` | Must be documented in after artifact. |
| `needs-user-decision` | `needs-user-decision` | Must block that item. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/CS-054-migrer-prochain-cluster-valeurs-visuelles-hardcodees/hardcoded-values-before.md`
- `_condamad/stories/CS-054-migrer-prochain-cluster-valeurs-visuelles-hardcodees/hardcoded-values-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Tokens frontend | `design-tokens.css` + `token-namespace-registry.md` | repeated literals |
| Typography roles | `typography-roles.md` | repeated font declarations |
| Remaining exceptions | `hardcoded-values-after.md` | implicit local values |

## 14. Delete-Only Rule

Items classified as `migrate` must be replaced by canonical owner, not kept as parallel literal.

Forbidden:

- keeping the literal and adding a token beside it
- near-equivalent token without documented mapping
- compatibility alias to preserve a hardcoded value

## 15. External Usage Blocker

If a literal is tied to external branding, third-party visual contract, or product decision, classify it `needs-user-decision` or `keep-classified` with proof before changing it.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/App.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `unknown until repo inspection` plus assumption risk: exact CSS/TSX files depend on selected single cluster.
- `frontend/src/styles/token-namespace-registry.md` - only if a reusable token namespace extension is introduced.
- `frontend/src/styles/typography-roles.md` - only if a reusable typography role is introduced.
- `_condamad/stories/CS-054-migrer-prochain-cluster-valeurs-visuelles-hardcodees/hardcoded-values-before.md` - baseline.
- `_condamad/stories/CS-054-migrer-prochain-cluster-valeurs-visuelles-hardcodees/hardcoded-values-after.md` - final evidence.

Likely tests:

- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- Existing component/page tests for the chosen cluster when present.

Files not expected to change:

- `backend/` - hors scope.
- `frontend/package.json` - aucune dependance.
- Fichiers hors cluster choisi - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens
npm run lint
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|font-size:|font-weight:|box-shadow:|border-radius:" selected-cluster-files
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-054-migrer-prochain-cluster-valeurs-visuelles-hardcodees/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-054-migrer-prochain-cluster-valeurs-visuelles-hardcodees/00-story.md
```

## 22. Regression Risks

- Risk: cluster trop large et inacheve.
  - Guardrail: AC1 limite a un cluster unique et AC2 exige 100% des decisions.
- Risk: mapping near-equivalent modifie le rendu.
  - Guardrail: decision utilisateur requise en cas d'ambiguite.
- Risk: dette de tokens supplementaire.
  - Guardrail: AC4 et `RG-044` imposent registre canonique.

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

- `_condamad/audits/frontend-design-system/2026-05-05-2053/03-story-candidates.md#SC-003` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-2053/02-finding-register.md#F-004` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-2053/00-audit-report.md#F-004` - current broad count and recommendations.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
