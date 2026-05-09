# Story CS-126 migrer-ou-garder-explicitement-precision-evidence: Migrer ou garder explicitement les familles precision et evidence

Status: done

## 1. Objective

Fermer `F-002` en statuant sans ambiguite les classes precision et evidence encore definies dans `frontend/src/App.css`.
Les sorties admises sont: migration vers primitives App ou owners feature-scoped explicites, ou conservation documentee comme contrat CSS public exact avec garde et sortie.
La story doit durcir CS-124 pour que `precision/evidence` ne restent jamais des residus non classes.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/03-story-candidates.md#SC-002`
- Reason for change: `F-002` montre que CS-124 ne bloque pas `precision/evidence`.
  Les familles precision badge, evidence tags et evidence pill restent actives dans `App.css` et trois consommateurs TSX.

## 3. Domain Boundary

- Domain: frontend-app-css-standardization
- In scope:
  - `frontend/src/App.css`
  - `frontend/src/features/consultations/components/ConsultationSummaryStep.tsx`
  - `frontend/src/features/consultations/components/DataCollectionStep.tsx`
  - `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
- Out of scope:
  - logique metier consultations ou natal interpretation
  - architecture des composants hors changement de `className`
  - CSS page-scoped sans lien direct avec ces classes
  - backend
- Explicit non-goals:
  - ne pas changer les statuts metier de precision ou les donnees d'evidence
  - ne pas recreer les anciens noms sous forme d'alias
  - ne pas affaiblir `RG-044` a `RG-050`, `RG-059`, `RG-061`, `RG-075`
  - ne pas laisser `precision/evidence` comme exception implicite ou wildcard

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story ferme une lacune de garde et impose une decision exacte pour deux familles visuelles residuelles.
- Behavior change allowed: no
- Behavior change constraints:
  - rendu visuel equivalent attendu pour badges precision et pills evidence
  - seuls noms CSS, owners et guards peuvent changer
  - la migration vers des primitives existantes est autorisee; conserver l'ancienne surface comme remplacement ne l'est pas
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: `precision-badge` ou `evidence-pill/evidence-tags` doit rester une API CSS publique permanente sous `App.css`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde Vitest design-system doit prouver la decision `precision/evidence`. |
| Baseline Snapshot | yes | Les hits actuels `precision/evidence` doivent etre compares avant/apres. |
| Ownership Routing | yes | Chaque famille doit avoir owner App generique, owner feature, ou blocker public contract. |
| Allowlist Exception | yes | Toute conservation doit etre exacte, source-backed et expiree/permanente decidee. |
| Contract Shape | no | Aucun contrat API, DTO, route, schema ou client genere n'est touche. |
| Batch Migration | yes | Precision et evidence ont consommateurs distincts et preuves separees. |
| Reintroduction Guard | yes | La story doit bloquer le retour de `precision/evidence` non classes dans `App.css`. |
| Persistent Evidence | yes | La decision et les scans doivent etre conserves dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard: `frontend/src/tests/design-system-guards.test.ts` validant l'absence ou l'allowlist exacte de `precision/evidence` dans `App.css`.
- Secondary evidence:
  - scans `rg -n "precision-|evidence-" src/App.css src -g "*.tsx"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - la lacune source est une garde partielle; la fermeture doit etre executable par Vitest.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/precision-evidence-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/precision-evidence-after.md`
- Expected invariant:
  - `precision/evidence` sont zero-hit dans `App.css` ou listés comme exceptions exactes avec owner, justification, guard et sortie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Precision badge global | App primitive or documented public App CSS contract | unclassified `.precision-badge*` in `App.css` |
| Consultation-specific precision UI | `frontend/src/features/consultations/**` stylesheet if feature-owned | alias retained in `App.css` |
| Natal evidence pills/tags | natal feature/component stylesheet if feature-owned | broad App namespace without source-backed contract |
| Guard exceptions | `frontend/src/tests/design-system-allowlist.ts` exact entries | wildcard `precision-*` or `evidence-*` exception |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | exact precision/evidence class names if retained | public CSS contract | permanence decision or dated exit condition |
| `frontend/src/styles/token-namespace-registry.md` | exact precision/evidence App variables if retained | source-backed App extension | dated exit condition or permanence |

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
| precision badges | precision badge CSS | App or consultation owner | two TSX files | consultation tests | zero-hit or exact allowlist | public API decision |
| evidence tags/pills | evidence CSS | App primitive or natal owner | `NatalInterpretationEvidence.tsx` | natal tests | zero-hit or exact allowlist | public CSS API decision |
| guard closure | precision/evidence in `App.css` | exact design-system guard | none unless class names change | design-system tests | no wildcard | unclassified hit |

Closure map:

- Total affected surface: exact active consumers and CSS families listed above.
- Batches included in this story: precision, evidence, guard closure.
- Batches intentionally deferred: none.
- Stop condition for the source finding: `F-002` closed by zero-hit or exact source-backed allowlist; no follow-up story required for `precision/evidence`.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before scan | `_condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/precision-evidence-before.md` | record current hits from E-014 and active consumers |
| after decision | `_condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/precision-evidence-after.md` | prove zero-hit or exact allowlist with owner |
| final evidence | `_condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/generated/10-final-evidence.md` | preserve test, lint and scan results |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- `.precision-badge`, `.precision-badge--high`, `.precision-badge--medium`, `.precision-badge--limited`, `.precision-badge--blocked` in `frontend/src/App.css` when migrated
- evidence tag and pill selectors in `frontend/src/App.css` when migrated
- `--app-precision-*` or `--app-evidence-*` without exact allowlist entry

Guard evidence:

- Evidence profile: `reintroduction_guard`.
  `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` checks the no-wildcard policy.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/02-finding-register.md#F-002`
- Closure proof required: before/after `precision/evidence` scan, exact owner decision, guard update, targeted consumer tests.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

- Evidence 1: audit E-014 - precision and evidence families remain active in `App.css` and TSX consumers.
- Evidence 2: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/02-finding-register.md#F-002` - CS-124 guard does not cover `precision/evidence`.
- Evidence 3: `frontend/src/features/consultations/components/ConsultationSummaryStep.tsx` - active precision class consumer per audit.
- Evidence 4: `frontend/src/features/consultations/components/DataCollectionStep.tsx` - active precision class consumer per audit.
- Evidence 5: `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx` - active evidence class consumer per audit.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

- Precision badges are either migrated out of `App.css` or explicitly kept as exact App CSS contract with owner and guard.
- Evidence tags/pills are either migrated out of `App.css` or explicitly kept as exact App CSS contract with owner and guard.
- No wildcard `precision-*` or `evidence-*` allowlist exists.
- The guard fails on future unclassified `precision/evidence` hits in `App.css`.
- Consumer TSX files use only the final canonical class names.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - namespace CSS frontend remains classified.
  - `RG-047` - TSX changes must not introduce static inline styles.
  - `RG-048` - CSS fallbacks remain classified.
  - `RG-049` - no legacy style surface stays unclassified.
  - `RG-050` - design-system guards stay exact and executable.
  - `RG-061` - `App.css` declarations remain guarded and tokenized.
  - `RG-075` - App specificity guard remains active.
  - `RG-077` - this story establishes the exact `precision/evidence` residual policy.
- Non-applicable invariants:
  - `RG-064` - page architecture is not changed.
  - `RG-073` - natal feature ownership is only touched for CSS class ownership, not API orchestration.
- Required regression evidence:
  - before/after scans, exact allowlist or zero-hit proof, targeted consumer tests, design-system guard suite.
- Allowed differences:
  - CSS class/variable names and owner stylesheet location only; user-visible behavior must not change.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Baseline records precision/evidence inventory. | Baseline profile; `precision-evidence-before.md`; `rg -n "precision-|evidence-" src/App.css src`. |
| AC2 | Precision badge family has an explicit final decision. | Batch mapping; `precision-evidence-after.md`; `npm run test -- ConsultationWizardPage`. |
| AC3 | Evidence tags/pills family has an explicit final decision. | Batch mapping; `precision-evidence-after.md`; `npm run test -- natalInterpretation`. |
| AC4 | Guard blocks unclassified `precision/evidence` in `App.css`. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system theme-tokens`. |
| AC5 | No forbidden CSS governance vocabulary is introduced. | Forbidden scan; `rg -n "OLD|legacy|alias|compat|shim" src/App.css`. |
| AC6 | Frontend validation remains green after class/owner changes. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`, `npm run build`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture the precision/evidence baseline. (AC: AC1)
  - [ ] Write `precision-evidence-before.md` with CSS hits, variables, selectors and TSX consumers.

- [ ] Task 2 - Decide and implement the precision batch. (AC: AC2, AC5)
  - [ ] Choose migrate-to-primitives, migrate-to-consultation-owner, or exact public App contract.
  - [ ] Update `ConsultationSummaryStep.tsx` and `DataCollectionStep.tsx` only when class names change.
  - [ ] Remove old names from `App.css` unless they are exact documented public contract entries.

- [ ] Task 3 - Decide and implement the evidence batch. (AC: AC3, AC5)
  - [ ] Choose migrate-to-primitives, migrate-to-natal-owner, or exact public App contract.
  - [ ] Update `NatalInterpretationEvidence.tsx` only when class names change.
  - [ ] Remove old names from `App.css` unless they are exact documented public contract entries.

- [ ] Task 4 - Harden guards and allowlists. (AC: AC4, AC5)
  - [ ] Update `design-system-guards.test.ts` for `precision/evidence`.
  - [ ] Add allowlist entries only if exact, source-backed and with permanence/expiry.

- [ ] Task 5 - Persist after evidence and validate. (AC: AC1, AC4, AC6)
  - [ ] Write `precision-evidence-after.md` and `generated/10-final-evidence.md`.
  - [ ] Run targeted tests, design-system suite, lint, build and negative scans.

## 9. Mandatory Reuse / DRY Constraints

- Reuse existing App primitives before creating new CSS families.
- Reuse existing owner stylesheets if a family is feature-owned; do not create a parallel global CSS surface.
- Reuse `design-system-guards.test.ts` and `design-system-allowlist.ts` for guard policy.
- Do not duplicate precision/evidence styles under both `App.css` and feature CSS.
- Shared abstraction allowed only if both precision and evidence genuinely share a presentation primitive without semantic leakage.

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

- wildcard `precision-*` or `evidence-*` allowlist
- `.precision-badge*` alias selectors after migration
- `.evidence-*` alias selectors after migration
- `--app-precision-*` or `--app-evidence-*` without registry decision
- `PASS with limitation`
- `OLD`, `legacy`, `alias`, `compat`, `compatibility`, `shim`, `migration-only`

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: class or variable is referenced by first-party production code and is the canonical owner.
- `external-active`: class or variable is referenced by public docs, generated links, analytics, or explicit audit evidence.
- `historical-facade`: class or variable exists only to preserve an older CSS surface.
- `dead`: class or variable has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

## 12. Removal Audit Format

Required audit table in `precision-evidence-after.md`:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/precision-evidence-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Precision badge presentation | App primitive, consultation owner, or exact public App contract | unclassified `.precision-badge*` in `App.css` |
| Evidence tag/pill presentation | App primitive, natal owner, or exact public App contract | unclassified `.evidence-*` in `App.css` |
| Precision/evidence guard | `frontend/src/tests/design-system-guards.test.ts` | manual scan only |
| Exceptions | `frontend/src/tests/design-system-allowlist.ts` | wildcard entries |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving old class names as aliases
- keeping old variables as compatibility layer
- duplicating active styles in `App.css` and feature CSS
- replacing deletion with a hidden fallback selector

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/00-audit-report.md`
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/01-evidence-log.md`
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/02-finding-register.md`
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/03-story-candidates.md`
- `_condamad/stories/CS-123-migrer-cartes-listes-badges-modales-vers-primitives-css/00-story.md`
- `_condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/App.css`
- `frontend/src/features/consultations/components/ConsultationSummaryStep.tsx`
- `frontend/src/features/consultations/components/DataCollectionStep.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/App.css` - remove, replace, or explicitly retain exact `precision/evidence` families.
- `frontend/src/features/consultations/components/ConsultationSummaryStep.tsx` - update precision class names if migrated.
- `frontend/src/features/consultations/components/DataCollectionStep.tsx` - update precision class names if migrated.
- `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx` - update evidence class names if migrated.
- `frontend/src/tests/design-system-guards.test.ts` - close `precision/evidence` guard gap.
- `frontend/src/tests/design-system-allowlist.ts` - exact exceptions only if retained.
- `frontend/src/styles/token-namespace-registry.md` - retained `--app-precision-*` / `--app-evidence-*` only if public App contract.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- existing ConsultationWizardPage / ConsultationMigration tests located by `rg --files frontend/src -g "*test*"`
- existing natalInterpretation tests located by `rg --files frontend/src -g "*test*"`

Files not expected to change:

- `backend/**` - outside domain.
- `frontend/package.json` - no dependency change.
- unrelated page CSS not owning extracted precision/evidence selectors.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

```powershell
Push-Location frontend
npm run test -- ConsultationWizardPage ConsultationMigration natalInterpretation design-system visual-smoke
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke
npm run lint
npm run build
rg -n "precision-|evidence-" src/App.css src -g "*.tsx"
rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css src/tests/design-system-allowlist.ts
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/00-story.md
```

The `precision-|evidence-` scan may return TSX or CSS hits only when they match the exact canonical decision.
Unclassified `App.css` hits fail the story.

## 22. Regression Risks

- Risk: visual state mapping for high/medium/limited/blocked changes.
  - Guardrail: targeted consultation tests and before/after screenshot or CSS evidence in final artifact.
- Risk: evidence tags lose planet/aspect/angle differentiation.
  - Guardrail: natalInterpretation tests and exact class mapping in after artifact.
- Risk: allowlist hides future residuals.
  - Guardrail: no wildcard, exact entries only, guard fails unknown `precision/evidence` names.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions, unclassified fallback, compatibility, legacy, shim, alias, TODO, or hidden residual work.

## 24. References

- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/03-story-candidates.md#SC-002` - source candidate.
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/02-finding-register.md#F-002` - source finding.
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753/01-evidence-log.md#E-014` - precision/evidence evidence.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
