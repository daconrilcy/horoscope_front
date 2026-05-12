# Story CS-151 corriger-libelle-guide-par-defaut-astrologers: Corriger le libelle du guide par defaut /astrologers

Status: done

## 1. Objective

Corriger le libelle francais du badge de guide par defaut dans les surfaces
astrologues. Le texte actuel `Votre défaut` est ambigu et peut se lire comme
un defaut personnel; il doit devenir un libelle clair de selection par defaut.

## 2. Trigger / Source

- Source type: audit
- Source reference: nouvel audit UX/UI Codex du 2026-05-12 sur `/astrologers`
- Reason for change: le rendu catalogue avec `default_astrologer_id` affiche
  `Votre défaut`, microcopy contradictoire avec l'intention de confiance.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-astrologers-copy`
- In scope:
  - Libelle `your_default` dans `frontend/src/i18n/astrologers.ts`.
  - Tests existants qui verifient le badge par defaut.
- Out of scope:
  - Layout, grille, cartes, API, backend, profil `/astrologers/:id`.
- Explicit non-goals:
  - Ne pas modifier la logique `defaultAstrologerId`.
  - Ne pas modifier `AstrologerCard.tsx` sauf si un test revele une issue.
  - Ne pas ajouter de style, de dependance, de fallback ou de doublon i18n.
  - Ne pas changer les invariants `RG-079`, `RG-089`, `RG-090`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: correction microcopy frontend locale sans archetype API.
- Additional validation rules:
  - Les tests doivent prouver que l'ancien libelle francais n'est plus rendu.
  - Les scans catalogue doivent rester zero-hit sur les surfaces interdites.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Seul le texte visible du badge de guide par defaut peut changer.
  - La structure DOM, les routes et les comportements de selection restent inchanges.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: le libelle implique une decision de marque plus large.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le changement est un libelle i18n rendu dans le DOM de `/astrologers`. |
| Baseline Snapshot | no | Les tests texte suffisent pour cette microcopy locale. |
| Ownership Routing | yes | Le libelle doit rester dans l'owner i18n existant. |
| Allowlist Exception | no | Aucune exception n'est autorisee. |
| Contract Shape | no | Aucun contrat API ou type externe n'est modifie. |
| Batch Migration | no | Une seule cle i18n est concernee. |
| Reintroduction Guard | yes | L'ancien libelle ne doit pas revenir dans les tests/sources actives. |
| Persistent Evidence | yes | La story doit conserver les preuves de validation. |

## 4b. Runtime Source of Truth

- Runtime source of truth: active
- Primary source of truth: rendered DOM of `AstrologersPage` with a configured
  `default_astrologer_id`.
- Secondary evidence: source scan of `frontend/src` and i18n owner diff.
- Static scans alone are not sufficient: the badge text must be asserted in the
  rendered component state where the default astrologer exists.
- Runtime artifact: generated manifest `frontend/logs/vite/vitest-report.json`
  from `npm run test -- AstrologersPage`.

## 4c. Baseline / Before-After Rule

- Baseline / before-after: not applicable
- Reason: correction de libelle couverte par tests DOM et scan source.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Libelles astrologues | `frontend/src/i18n/astrologers.ts` | Texte duplique en composant |
| Badge rendu | `AstrologerCard` via `tAstrologers` | Nouvelle logique locale |
| Tests catalogue | `frontend/src/tests/AstrologersPage.test.tsx` | Nouvelle suite parallele |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated
  client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-151-corriger-libelle-guide-par-defaut-astrologers/validation-evidence.md` | Prouver tests, scans et revue. |

## 4i. Reintroduction Guard

The implementation must add or update a guard that fails if the old copy returns.

Required forbidden examples:

- `Votre défaut`
- `Su defecto`

Guard evidence:

- Evidence profile: `component_test`; `npm run test -- AstrologersPage`.
- Evidence profile: `negative_scan`; `rg -n "Votre défaut|Su defecto" frontend/src`.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: audit UX/UI `/astrologers` 2026-05-12#default-badge-copy
- Closure proof required: tests updated, old copy zero-hit, story evidence.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/i18n/astrologers.ts` - `your_default.fr` vaut
  `Votre défaut`.
- Evidence 2: `frontend/src/tests/AstrologersPage.test.tsx` - deux tests
  attendent explicitement `Votre défaut`.
- Evidence 3: `frontend/src/features/astrologers/components/AstrologerCard.tsx`
  consomme deja `t("your_default", lang)`, donc aucun nouveau mecanisme n'est requis.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants
  consultes avant cadrage.

## 6. Target State

After implementation:

- Le badge francais indique clairement que le guide est le choix par defaut.
- Les traductions anglaise et espagnole ne portent pas de formulation maladroite.
- Les tests prouvent que l'ancien libelle francais n'est plus rendu.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-079` - le badge reste dans le catalogue sans style global.
  - `RG-089` - la carte garde ses badges de choix et son CTA non imbrique.
  - `RG-090` - la hierarchie de carte reste identity-first.
- Non-applicable invariants:
  - `RG-080` - la story ne modifie pas le profil astrologue.
- Required regression evidence:
  - `npm run test -- AstrologersPage design-system visual-smoke`
  - `npm run lint`
  - scans zero-hit des anciens libelles et des surfaces interdites.
- Allowed differences:
  - Libelle `your_default` remplace par une formulation claire.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le badge francais affiche `Guide par défaut`. | Evidence profile: `component_test`; `npm run test -- AstrologersPage`. |
| AC2 | L'ancien libelle francais ne reste pas actif. | Evidence profile: `negative_scan`; `rg -n "Votre défaut" frontend/src`. |
| AC3 | Les guards catalogue restent satisfaits. | Evidence profile: `reintroduction_guard`; `npm run test -- AstrologersPage design-system visual-smoke`. |
| AC4 | Le lint frontend reste vert. | Evidence profile: `lint`; `npm run lint`. |

## 8. Implementation Tasks

- [x] Task 1 - Corriger la traduction i18n (AC: AC1, AC2)
  - [x] Subtask 1.1 - Remplacer les libelles `your_default` ambigus.
  - [x] Subtask 1.2 - Ne pas modifier la structure de carte.

- [x] Task 2 - Mettre a jour les tests (AC: AC1, AC2, AC3)
  - [x] Subtask 2.1 - Remplacer les attentes `Votre défaut`.
  - [x] Subtask 2.2 - Verifier que l'ancien libelle n'est plus attendu.

- [x] Task 3 - Valider et documenter (AC: AC2, AC3, AC4)
  - [x] Subtask 3.1 - Executer tests, lint et scans.
  - [x] Subtask 3.2 - Ajouter `validation-evidence.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `tAstrologers` et la cle `your_default`.
  - Tests `AstrologersPage` existants.
- Do not recreate:
  - Nouvelle cle parallele pour le meme badge.
  - Texte hardcode dans `AstrologerCard.tsx`.
- Shared abstraction allowed only if:
  - N/A - une correction de libelle ne justifie pas d'abstraction.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `Votre défaut`
- `Su defecto`
- `style=` dans `frontend/src/pages/AstrologersPage.tsx`
- `people-page` ou `person-card` dans `frontend/src/App.css`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Libelles astrologues | `frontend/src/i18n/astrologers.ts` | Texte inline en composant |
| Rendu badge defaut | `frontend/src/features/astrologers/components/AstrologerCard.tsx` | Nouvelle carte parallele |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or
  generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/i18n/astrologers.ts`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/i18n/astrologers.ts` - corriger `your_default`.
- `frontend/src/tests/AstrologersPage.test.tsx` - mettre a jour les attentes.
- `_condamad/stories/CS-151-corriger-libelle-guide-par-defaut-astrologers/validation-evidence.md` - preuve.
- `_condamad/stories/story-status.md` - statut.

Likely tests:

- `frontend/src/tests/AstrologersPage.test.tsx`

Files not expected to change:

- `frontend/src/App.css` - styles globaux interdits.
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
rg -n "Votre défaut|Su defecto" src
rg -n "people-page|person-card" src/App.css
rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers
```

Story validation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-151-corriger-libelle-guide-par-defaut-astrologers/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-151-corriger-libelle-guide-par-defaut-astrologers/00-story.md
```

## 22. Regression Risks

- Risk: un test peut continuer a documenter l'ancien libelle.
  - Guardrail: scan zero-hit `Votre défaut`.
- Risk: correction trop large hors microcopy.
  - Guardrail: revue diff et scope files.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 24. References

- `_condamad/stories/regression-guardrails.md` - invariants catalogue.
- `frontend/src/i18n/astrologers.ts` - owner i18n du libelle.
