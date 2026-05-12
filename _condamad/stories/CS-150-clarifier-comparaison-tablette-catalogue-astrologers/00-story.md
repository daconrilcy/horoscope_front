# Story CS-150 clarifier-comparaison-tablette-catalogue-astrologers: Clarifier la comparaison tablette du catalogue /astrologers

Status: done

## 1. Objective

Corriger la page `/astrologers` pour rendre la comparaison plus immédiate sans
refonte. La grille tablette doit afficher deux cartes comparables au lieu d'une
seule carte très large, sans ajouter de liste de critères redondante au header.

## 2. Trigger / Source

- Source type: audit
- Source reference: `.codex-artifacts/astrologers-audit-2026-05-12/before-metrics.json`
- Reason for change: l'audit rendu montre `columnsFirstRow: 1` a `768x1024`
  avec des cartes de `686px`, ce qui ralentit la comparaison.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-astrologers-catalog`
- In scope:
  - Grille catalogue dans `frontend/src/styles/app/cards.css`.
  - Tests catalogue et guards CSS existants.
- Out of scope:
  - Backend, API, authentification, route `/astrologers/:id`, `App.css`, `RootLayout`, `PageLayout`, nouvelles dependances.
- Explicit non-goals:
  - Ne pas changer l'ordre de rotation des astrologues.
  - Ne pas reintroduire `.astrologer-*`, `person-card--featured`, hauteur fixe fragile ou styles inline.
  - Ne pas ajouter de quatrieme colonne desktop autour de `1440px`.
  - Ne pas modifier les styles globaux dans `frontend/src/App.css`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: correction UX/UI frontend locale sans archetype backend/API applicable.
- Additional validation rules:
  - Playwright doit mesurer le DOM charge de `/astrologers` aux viewports `390x844`, `768x1024` et `1440x1000`.
  - Les tests Vitest doivent couvrir le contrat CSS de grille.
  - Les scans negatifs doivent rester zero-hit sur les surfaces interdites par RG-079/RG-089/RG-090.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Passer la grille catalogue a deux colonnes tablette et trois colonnes desktop, avec une colonne mobile.
  - Preserver la carte bouton unique, le CTA non imbrique, les etats loading/error/empty et la navigation vers profil.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: la correction exige une nouvelle promesse marketing, un nouveau tunnel de conversion ou une dependance.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le rendu navigateur de `/astrologers` est la source de verite pour le nombre de colonnes et l'absence d'overflow. |
| Baseline Snapshot | yes | L'audit a produit un baseline before et l'implementation doit produire un after comparable. |
| Ownership Routing | yes | Les responsabilites doivent rester dans la route, l'i18n et les CSS owners existants du catalogue. |
| Allowlist Exception | no | Aucune nouvelle exception ou allowlist n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO ou type externe n'est modifie. |
| Batch Migration | no | La correction touche une seule surface locale. |
| Reintroduction Guard | yes | Les guards existants RG-079/RG-089/RG-090 doivent continuer a bloquer les regressions catalogue. |
| Persistent Evidence | yes | Les captures/mesures before-after doivent rester dans les artefacts de story ou d'audit. |

## 4b. Runtime Source of Truth

- Runtime source of truth: active
- Primary source of truth: Playwright DOM runtime measurement of loaded `/astrologers` with controlled `/v1/astrologers`, `/v1/auth/me`, and `/v1/users/me/settings` responses.
- Secondary evidence: Vitest DOM/CSS guards and persisted screenshots in `.codex-artifacts/astrologers-audit-2026-05-12/`.
- Static scans alone are not sufficient: column count and overflow must be measured from the browser layout engine.
- Runtime artifact: generated manifest `.codex-artifacts/astrologers-audit-2026-05-12/after-metrics.json` generated from browser `getBoundingClientRect()` results.
- Required evidence:
  - `390x844`: une colonne, pas d'overflow horizontal.
  - `768x1024`: deux colonnes sur la premiere ligne.
  - `1440x1000`: trois colonnes sur la premiere ligne.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `.codex-artifacts/astrologers-audit-2026-05-12/before-metrics.json`
  - `.codex-artifacts/astrologers-audit-2026-05-12/before-*.png`
- Comparison after implementation:
  - `.codex-artifacts/astrologers-audit-2026-05-12/after-metrics.json`
  - `.codex-artifacts/astrologers-audit-2026-05-12/after-*.png`
- Expected invariant:
  - Aucune regression des guards catalogue et aucune nouvelle surface de style globale.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Grille catalogue | `frontend/src/styles/app/cards.css` | Style inline ou `App.css` |
| Tests catalogue | Tests existants `AstrologersPage`, `design-system`, `visual-smoke` | Nouvelle suite parallele inutile |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before runtime metrics | `.codex-artifacts/astrologers-audit-2026-05-12/before-metrics.json` | Prouver les constats d'audit. |
| After runtime metrics | `.codex-artifacts/astrologers-audit-2026-05-12/after-metrics.json` | Prouver la fermeture des constats. |
| Story evidence | `_condamad/stories/CS-150-clarifier-comparaison-tablette-catalogue-astrologers/validation-evidence.md` | Regrouper commandes, scans et resultat audit final. |

## 4i. Reintroduction Guard

The implementation must add or update a guard that fails if the protected catalogue behavior regresses.

Required forbidden examples:

- `.astrologer-*`
- `person-card--featured`
- `featured={index === 0}`
- `style=` in the touched route/components
- `people-page` or `person-card` in `frontend/src/App.css`

Guard evidence:

- Evidence profile: `reintroduction_guard`; `npm run test -- AstrologersPage design-system visual-smoke` checks catalogue DOM/CSS.
- Evidence profile: `negative_scan`; targeted `rg` scans check forbidden symbols.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `.codex-artifacts/astrologers-audit-2026-05-12/before-metrics.json#tablet-one-column`
- Closure proof required: after metrics show two columns at `768x1024`, three at `1440x1000`, one at `390x844`, guards/tests/scans pass.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/styles/app/cards.css` - `.people-page .person-grid`
  utilise `repeat(auto-fit, minmax(min(100%, 340px), 1fr))`, ce qui produit une
  seule colonne a `768x1024`.
- Evidence 2: `.codex-artifacts/astrologers-audit-2026-05-12/before-metrics.json` - `columnsFirstRow` vaut `1` a `768x1024` et `3` a `1440x1000`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- La grille affiche une colonne mobile, deux colonnes tablette, trois colonnes desktop.
- Les cartes conservent leur hierarchie identity-first, CTA non imbrique et surface token-backed.
- Les artefacts after prouvent que l'audit n'a plus de constat in-domain sur `/astrologers`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-079` - la page `/astrologers` garde son relief compact token-backed hors `App.css`.
  - `RG-089` - le catalogue reste responsive, sans featured span fragile ni styles inline.
  - `RG-090` - la hierarchie identity-first, le CTA non imbrique et la grille desktop non etroite restent proteges.
- Non-applicable invariants:
  - `RG-080` - la story ne touche pas `/astrologers/:id`.
  - `RG-088` - la story ne touche pas la landing.
- Required regression evidence:
  - `npm run test -- AstrologersPage design-system visual-smoke`
  - `npm run lint`
  - scans zero-hit de `App.css`, `.astrologer-*`, `style=`, `featured={index === 0}`, `person-card--featured`, hauteurs fixes fragiles.
  - after metrics navigateur.
- Allowed differences:
- Grille tablette a deux colonnes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La grille affiche deux colonnes tablette. | Evidence profile: `runtime_source_of_truth`; after metrics + `rg -n "tablet" after-metrics.json`. |
| AC2 | La grille affiche trois colonnes desktop. | Evidence profile: `runtime_source_of_truth`; after metrics + `rg -n "desktop" after-metrics.json`. |
| AC3 | La grille mobile reste une colonne sans overflow. | Evidence profile: `runtime_source_of_truth`; after metrics + `rg -n "mobile" after-metrics.json`. |
| AC4 | Les invariants RG-079/RG-089/RG-090 restent satisfaits. | Evidence profile: `reintroduction_guard`; `npm run test -- AstrologersPage design-system visual-smoke`. |
| AC5 | Aucun style catalogue n'est ajoute dans `App.css`. | Evidence profile: `negative_scan`; `rg -n "people-page|person-card" src/App.css`. |

## 8. Implementation Tasks

- [x] Task 1 - Corriger la grille responsive catalogue (AC: AC1, AC2, AC3)
  - [x] Subtask 2.1 - Ajuster `cards.css` avec une colonne mobile, deux tablette, trois desktop.
  - [x] Subtask 2.2 - Garder les tokens et selectors owners existants.

- [x] Task 2 - Adapter les tests et guards (AC: AC4, AC5)
  - [x] Subtask 3.1 - Mettre a jour `AstrologersPage.test.tsx`.
  - [x] Subtask 3.2 - Mettre a jour les guards CSS qui verifient le contrat de grille.

- [x] Task 3 - Valider et documenter la fermeture (AC: AC1, AC2, AC3, AC4, AC5)
  - [x] Subtask 4.1 - Produire les after metrics/captures.
  - [x] Subtask 4.2 - Ajouter `validation-evidence.md`.
  - [x] Subtask 4.3 - Mettre la story et `story-status.md` au statut approprie apres implementation.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `people-page-header`, `person-grid` et `person-card` owners existants.
  - Tests `AstrologersPage`, `design-system-guards` et `visual-smoke`.
- Do not recreate:
  - Nouveau composant catalogue parallele.
  - Nouveau systeme de grille.
  - Nouvelle source de traductions.
- Shared abstraction allowed only if:
  - N/A - la correction locale ne justifie pas de nouvelle abstraction.

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

- `frontend/src/App.css` pour `people-page` ou `person-card`.
- `.astrologer-*`
- `person-card--featured`
- `featured={index === 0}`
- `style=` dans `frontend/src/pages/AstrologersPage.tsx` ou `frontend/src/features/astrologers`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Route catalogue astrologues | `frontend/src/pages/AstrologersPage.tsx` | Nouveau route component parallele |
| Composants cartes/grille | `frontend/src/features/astrologers/components/**` | Duplicats sous `pages` |
| Styles catalogue | `frontend/src/styles/app/cards.css` | `frontend/src/App.css`, inline styles |
| Tokens catalogue existants | `frontend/src/styles/app/tokens.css` | Valeurs hardcodees hors owner |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/styles/app/cards.css`
- `frontend/src/styles/app/media.css`
- `frontend/src/styles/app/tokens.css`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/app/cards.css` - ajuster la grille responsive.
- `frontend/src/tests/AstrologersPage.test.tsx` - couvrir le header.
- `frontend/src/tests/design-system-guards.test.ts` - garder le contrat de grille.
- `frontend/src/tests/visual-smoke.test.tsx` - synchroniser le smoke CSS.
- `_condamad/stories/CS-150-clarifier-comparaison-tablette-catalogue-astrologers/validation-evidence.md` - preuve de validation.
- `_condamad/stories/story-status.md` - statut de la story.

Likely tests:

- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`

Files not expected to change:

- `frontend/src/App.css` - surface globale interdite pour le catalogue.
- `backend/**` - aucun contrat backend touche.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- AstrologersPage design-system visual-smoke
npm run lint
rg -n "people-page|person-card" src/App.css
rg -n "astrologer-" src/styles/app src/features/astrologers
rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers
rg -n "featured=\{index === 0\}|person-card--featured|height:\s*24[0-9]px|height:\s*25[0-9]px" src/features/astrologers src/styles/app src/tests
```

Story validation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-150-clarifier-comparaison-tablette-catalogue-astrologers/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-150-clarifier-comparaison-tablette-catalogue-astrologers/00-story.md
```

Runtime/manual evidence:

- Playwright local sur `/astrologers` a `390x844`, `768x1024`, `1440x1000`.

## 22. Regression Risks

- Risk: une grille tablette a deux colonnes pourrait casser le mobile etroit.
  - Guardrail: after metrics `390x844` + `RG-089`.
- Risk: le header pourrait redevenir textuel sans aide de choix.
  - Guardrail: test DOM `AstrologersPage`.
- Risk: la correction pourrait recreer des styles catalogue dans `App.css`.
  - Guardrail: scans zero-hit + `RG-079`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 24. References

- `_condamad/stories/regression-guardrails.md` - invariants RG-079/RG-089/RG-090.
- `_condamad/stories/CS-149-optimiser-hierarchie-premium-catalogue-astrologers/00-story.md` - contrat precedent de hierarchie premium catalogue.
- `.codex-artifacts/astrologers-audit-2026-05-12/before-metrics.json` - preuve de l'audit initial.
