# Story CS-040 aligner-registre-markdown-allowlist-fallbacks-css: Aligner le registre markdown et l'allowlist executable des fallbacks CSS

Status: done

## 1. Objective

Aligner le registre markdown et `CSS_FALLBACK_EXCEPTIONS`.
Le resultat doit etre un contrat exact, verifie et maintenable pour les fallbacks CSS autorises.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1748/03-story-candidates.md#SC-001`
- Reason for change: le finding `F-002` indique que le registre markdown annonce une allowlist exacte.
  Il ne documente que 7 lignes alors que l'allowlist executable contient 165 exceptions.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Choisir et appliquer une source canonique unique pour les exceptions de fallbacks CSS.
  - Aligner les 165 exceptions executables avec le registre markdown, ou generer les deux depuis une donnee commune.
  - Ajouter une garde de parite qui echoue si markdown et allowlist executable divergent.
  - Exiger statut, raison et condition de sortie pour chaque fallback conserve.
- Out of scope:
  - Reduire le nombre de fallbacks CSS au-dela des corrections necessaires a la parite.
  - Convertir les styles inline TSX.
  - Migrer les valeurs visuelles hardcodees hors fallback.
  - Modifier les tokens globaux sans decision explicite.
- Explicit non-goals:
  - Ne pas affaiblir `RG-044`, `RG-048` ou `RG-050`.
  - Ne pas creer une deuxieme source de verite d'exceptions.
  - Ne pas accepter d'entree wildcard ou par dossier.
  - Ne pas masquer une divergence par un test qui ignore des lignes documentaires.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: registry-catalog-refactor
- Archetype reason: la story converge un registre documentaire et un catalogue executable vers un contrat unique.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les fallbacks deja autorises peuvent rester autorises uniquement s'ils sont documentes et testes exactement.
  - Aucune exception implicite ou non documentee ne doit rester active.
  - Aucun changement visuel n'est recherche.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le choix de source canonique impose un format durable non couvert par les fichiers existants.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La suite Vitest design-system est la source observable du contrat executable. |
| Baseline Snapshot | yes | Le nombre et l'identite des exceptions doivent etre compares avant/apres. |
| Ownership Routing | yes | La story doit declarer quel fichier ou artefact devient proprietaire canonique. |
| Allowlist Exception | yes | Chaque fallback conserve est une exception exacte. |
| Contract Shape | no | Aucun contrat API, DTO, payload ou type public n'est modifie. |
| Batch Migration | yes | Les entrees markdown et TypeScript doivent converger en un lot complet. |
| Reintroduction Guard | yes | La divergence documentaire/executable ne doit pas revenir. |
| Persistent Evidence | yes | La parite et l'inventaire des exceptions doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/css-fallback-policy.test.ts`.
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`.
- Secondary evidence:
  - `frontend/src/tests/design-system-allowlist.ts`.
  - `frontend/src/styles/css-fallback-allowlist.md`.
  - Scan `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," frontend/src -g "*.css"`.
- Static scans alone are not sufficient for this story because:
  - La correction vise la parite entre contrat documentaire et contrat executable, pas seulement le comptage de fallbacks.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-040-aligner-registre-markdown-allowlist-fallbacks-css/css-fallback-contract-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-040-aligner-registre-markdown-allowlist-fallbacks-css/css-fallback-contract-after.md`
- Expected invariant:
  - Chaque fallback executable conserve a une ligne documentaire equivalente avec statut, raison et condition de sortie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Fallback CSS documente | `frontend/src/styles/css-fallback-allowlist.md` ou source commune explicite | entree implicite dans CSS |
| Fallback CSS executable | `frontend/src/tests/design-system-allowlist.ts` ou artefact genere depuis la source commune | allowlist parallele |
| Garde de parite | `frontend/src/tests/css-fallback-policy.test.ts` ou `frontend/src/tests/design-system-guards.test.ts` | verification manuelle non testee |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/css-fallback-allowlist.md` | chaque fallback conserve | Exception documentee. | Condition de sortie obligatoire. |
| `frontend/src/tests/design-system-allowlist.ts` | `CSS_FALLBACK_EXCEPTIONS` | Exception executable exacte. | Doit etre en parite avec le registre. |

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
| Parity | registre + allowlist | source unique | guards | `npm run test -- css-fallback` | diff | format ambigu |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before parity inventory | `css-fallback-contract-before.md` | Capturer markdown, executable et delta initial. |
| After parity inventory | `css-fallback-contract-after.md` | Prouver la parite complete. |
| Markdown registry | `frontend/src/styles/css-fallback-allowlist.md` | Documenter statut, raison et sortie de chaque exception. |
| Executable allowlist | `frontend/src/tests/design-system-allowlist.ts` | Alimenter les guards deterministes. |

## 4i. Reintroduction Guard

- Guard target: divergence entre `css-fallback-allowlist.md` et `CSS_FALLBACK_EXCEPTIONS`.
- Architecture guard required: un test Vitest doit echouer si une entree existe dans une surface sans l'autre, ou si une entree manque de statut, raison ou condition de sortie.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- css-fallback design-system` verifie la parite.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1748/02-finding-register.md#F-002` - le registre markdown et l'allowlist executable ont diverge.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1748/00-audit-report.md` -
  le markdown documente 7 lignes alors que `CSS_FALLBACK_EXCEPTIONS` contient 165 exceptions.
- Evidence 3: `frontend/src/styles/css-fallback-allowlist.md` - registre documentaire a aligner.
- Evidence 4: `frontend/src/tests/design-system-allowlist.ts` - allowlist executable a aligner.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Le registre markdown et l'allowlist executable representent exactement le meme ensemble d'exceptions.
- La parite est testee automatiquement.
- Chaque exception conservee indique statut, raison et condition de sortie.
- Aucun fallback CSS non classe ne peut etre ajoute sans echec de test.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens frontend doivent rester classes.
  - `RG-048` - aucun fallback CSS non classe ne doit etre ajoute.
  - `RG-050` - les exceptions design-system doivent rester exactes et verifiees.
- Non-applicable invariants:
  - `RG-045` - aucune migration de valeurs hardcodees hors fallback n'est incluse.
  - `RG-046` - la hierarchie typographique n'est pas touchee.
  - `RG-047` - les styles inline ne sont pas touches.
  - `RG-049` - les selecteurs legacy ne sont pas touches.
- Required regression evidence:
  - `npm run test -- css-fallback design-system`, `npm run lint`, scan fallback cible.
- Allowed differences:
  - Changement de format du registre si la source canonique reste unique, testee et documentee.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | L'inventaire before liste le delta. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "delta" css-fallback-contract-before.md`. |
| AC2 | Le contrat final contient les exceptions executables sans orpheline. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- css-fallback`. |
| AC3 | Chaque exception finale a une sortie. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- css-fallback`. |
| AC4 | La garde de parite echoue en cas de divergence. | Evidence profile: `reintroduction_guard`; `npm run test -- css-fallback design-system`. |
| AC5 | Aucun nouveau fallback CSS non classe n'est introduit. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `rg -n "var\\(" src -g "*.css"`. |
| AC6 | La validation frontend reste verte. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint` et `npm run test -- css-fallback design-system`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'inventaire before markdown/executable/fallback scan (AC: AC1)
- [ ] Task 2 - Choisir la source canonique minimale sans creer de source concurrente (AC: AC2, AC3)
- [ ] Task 3 - Aligner `css-fallback-allowlist.md` et `CSS_FALLBACK_EXCEPTIONS` sur le meme ensemble exact (AC: AC2, AC3)
- [ ] Task 4 - Ajouter ou durcir la garde de parite (AC: AC4, AC5)
- [ ] Task 5 - Capturer l'inventaire after et le delta final (AC: AC1, AC2)
- [ ] Task 6 - Executer lint et tests design-system cibles (AC: AC4, AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/css-fallback-allowlist.md`.
  - `frontend/src/tests/design-system-allowlist.ts`.
  - `frontend/src/tests/css-fallback-policy.test.ts`.
  - `frontend/src/tests/design-system-guards.test.ts`.
- Do not recreate:
  - Une allowlist secondaire de fallbacks.
  - Un parser markdown ad hoc duplique si un helper de test existant couvre deja le besoin.
  - Des exceptions implicites dans les fichiers CSS.
- Shared abstraction allowed only if:
  - Elle remplace une duplication reelle entre le registre et les guards et reste locale aux tests/design-system.

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

- `CSS_FALLBACK_EXCEPTIONS` avec entree absente du registre final.
- Ligne markdown sans entree executable correspondante.
- Exception fallback sans statut, raison ou condition de sortie.
- Wildcard ou exception par dossier.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Contrat fallback CSS | Source canonique choisie dans cette story | duplication markdown/TypeScript divergente |
| Validation parite | Tests design-system existants | revue manuelle |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-policy.ts`
- `_condamad/audits/frontend-design-system/2026-05-05-1748/02-finding-register.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/css-fallback-allowlist.md` - alignement exact ou sortie generee.
- `frontend/src/tests/design-system-allowlist.ts` - source executable ou consommation de la source canonique.
- `frontend/src/tests/css-fallback-policy.test.ts` - garde de parite.
- `frontend/src/tests/design-system-guards.test.ts` - garde anti-drift si c'est le meilleur emplacement.
- `frontend/src/tests/design-system-policy.ts` - helper partage si le code existant le demande.
- `_condamad/stories/CS-040-aligner-registre-markdown-allowlist-fallbacks-css/css-fallback-contract-before.md` - baseline.
- `_condamad/stories/CS-040-aligner-registre-markdown-allowlist-fallbacks-css/css-fallback-contract-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/css-fallback-policy.test.ts` - validation du contrat fallback.
- `frontend/src/tests/design-system-guards.test.ts` - validation de parite design-system.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/**/*.tsx` - hors scope.
- `frontend/src/**/*.css` hors registre - aucune migration de fallback attendue.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- css-fallback design-system
rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-040-aligner-registre-markdown-allowlist-fallbacks-css/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-040-aligner-registre-markdown-allowlist-fallbacks-css/00-story.md
```

## 22. Regression Risks

- Risk: le registre et l'allowlist divergent a nouveau apres une reduction future.
  - Guardrail: test de parite obligatoire et `RG-050`.
- Risk: une exception reste documentee mais non executable.
  - Guardrail: AC2 et AC3 bloquent toute entree orpheline.
- Risk: un fallback non classe est ajoute pendant l'alignement.
  - Guardrail: `RG-048` et guard CSS fallback.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Ne pas traiter cette story comme une reduction generale des 165 fallbacks; l'objectif prioritaire est la parite contractuelle complete.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1748/03-story-candidates.md#SC-001` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1748/02-finding-register.md#F-002` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1748/00-audit-report.md` - preuve du drift.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
