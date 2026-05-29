# Story CS-388 refonte-natal-sprint3-expertise-karmique: Refonte /natal Sprint 3 — Expertise karmique et potentiels

Status: ready-to-dev

## Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-29 — plan refonte `/natal` (couche 3)
- Selected mode: Repo-informed story
- Reason for change: le brief Sprint 3 ajoute forte valeur marketing via signature
  karmique et lectures de potentiels — toujours en narration avant technique.
- Source-alignment evidence: couvre « Votre trajectoire d'évolution », talents cachés,
  potentiel relationnel et professionnel à partir de Nœuds, Saturne, Pluton et signaux API.

## Objective

Ajouter à `/natal` la couche 3 « expertise astrologique accessible » : section « Votre
trajectoire d'évolution » (signature karmique) et sections potentiels (talents cachés,
relationnel, professionnel) — en combinant payload public (points astraux, placements,
signaux) et contenu interprétatif LLM existant, sans nouveau moteur backend.

## Domain Boundary

- Domain: frontend-natal-page
- In scope:
  - Composants `NatalKarmicSignature`, `NatalHiddenTalents`, `NatalRelationshipPotential`,
    `NatalCareerPotential`.
  - Consommation `astral_points` / `planet_positions` pour Nœud N/S, Saturne, Pluton.
  - Réutilisation interprétation LLM complète ou signaux `interpretation_adapter`.
  - i18n, CSS, tests Vitest, intégration ordre page post Sprint 2.
- Out of scope:
  - Couches 1 et 2 (CS-386, CS-387).
  - Mode astrologue premium et données techniques (CS-389).
  - Nouveau use case LLM backend, tables DB, recalcul points astraux.
  - Export PDF refonte.
- Explicit non-goals:
  - Pas de texte karmique inventé côté React sans source LLM/signaux.
  - Pas d'affichage technique des variantes de nœuds/Lilith en vue principale.
  - Pas de contournement RG-150 pour rejets LLM.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: sections narratives frontend consommant faits et interprétation existants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Placer sections après domaines/aspects Sprint 2.
  - Nœuds via points astraux publics; fallback dégradé si points absents.
  - Potentiels ancrés MC, VII, X, dominantes et paragraphes LLM acceptés.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: produit exige nouveau prompt LLM dédié karmique backend.
- Additional validation rules:
  - Vitest prouve sections karmiques, potentiels et états dégradés sans invention locale.
  - Scan `rg` interdit constantes locales de nœuds et dumps JSON.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest prouve rendu karmique et états dégradés. |
| Baseline Snapshot | yes | Evidence before/after sections Sprint 3. |
| Ownership Routing | yes | Owners feature `natal-chart/**`. |
| Allowlist Exception | no | Pas d'invention narrative locale allowlistée. |
| Contract Shape | yes | Types points astraux publics consommés sans orphan. |
| Batch Migration | no | Pas de migration. |
| Reintroduction Guard | yes | Pas de dump JSON points astraux en vue principale. |
| Persistent Evidence | yes | Artefacts validation Sprint 3. |

## Runtime Source of Truth

- Primary source of truth:
  - Vitest/Testing Library sur composants karmiques Sprint 3.
  - `AST guard` via tests d'architecture natal-chart si présents.
- Secondary evidence:
  - `pnpm --dir frontend build` pour types points astraux; scans `rg` anti-constantes locales.
- Static scans alone are not sufficient for this story because:
  - Les sections karmiques doivent être prouvées au rendu avec payload complet et partiel.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-388-refonte-natal-sprint3-expertise-karmique/evidence/before-sprint3-sections.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-388-refonte-natal-sprint3-expertise-karmique/evidence/after-sprint3-sections.txt`
- Expected invariant:
  - Seules les sections Sprint 3 s'ajoutent; contrat public natal inchangé.
  - CS-386 et CS-387 sont deja implementes dans la branche; sinon cette story doit rester bloquee.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| UI karmique et potentiels | `frontend/src/features/natal-chart/` | page monolithique |
| Points astraux factuels | payload public backend | calcul React |
| Texte narratif karmique | interprétation LLM acceptée | invention UI |

## Contract Shape

- Contract type:
  - Types frontend pour points astraux publics dans `NatalResult`.
- Fields:
  - Nœud Nord/Sud depuis `astral_points` publics.
  - Saturne et Pluton depuis `planet_positions` publics.
- Required fields:
  - aucun nouveau champ backend.
- Optional fields:
  - points astraux partiels avec état dégradé UI documenté.
- Status codes:
  - non applicable.
- Serialization names:
  - codes points astraux backend conservés tels quels.
- Frontend type impact:
  - extension `frontend/src/api/natal-chart/index.ts` quand types absents avant implémentation.
- Generated contract impact:
  - none.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-388-refonte-natal-sprint3-expertise-karmique/evidence/validation.txt` | Preuve commandes frontend passées. |
| Before sections | `_condamad/stories/CS-388-refonte-natal-sprint3-expertise-karmique/evidence/before-sprint3-sections.txt` | Baseline Sprint 3. |
| After sections | `_condamad/stories/CS-388-refonte-natal-sprint3-expertise-karmique/evidence/after-sprint3-sections.txt` | Comparaison Sprint 3. |
| Review output | `_condamad/stories/CS-388-refonte-natal-sprint3-expertise-karmique/generated/11-code-review.md` | Revue automatique séparée. |

## Current State Evidence

- Evidence 1: `backend/app/services/chart/json_builder.py` - projection points astraux publics.
- Evidence 2: `frontend/src/api/natal-chart/index.ts` - types points astraux à confirmer.
- Evidence 3: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - flux LLM existant.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - registre consulté pour RG-115.
- Evidence 5: `_condamad/stories/story-status.md` - tracker consulté pour numéro CS-388.

## Target State

- Section « Votre trajectoire d'évolution » construite avec Nœud Nord, Nœud Sud,
  Saturne, Pluton — narration principale + rappel placement symbolique concis.
- Section « Talents cachés » avec items reliés signaux ou placements (XII, Neptune).
- Section « Potentiel relationnel » (Vénus, VII, signaux relationnels API).
- Section « Potentiel professionnel » (MC, X, planètes culminantes API).
- États loading/empty/upsell alignés entitlement existant; pas de variante technique visible.
- Tests couvrant payload complet, points astraux partiels, utilisateur free.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-115` — points astraux lus depuis payload; pas de constantes locales nœuds/Lilith.
  - `RG-116` — pas de mélange interprétation points dans calculateur; UI consomme vue publique.
  - `RG-129` — pas de dérivation karmique locale depuis longitudes.
  - `RG-150` — contenu LLM depuis interprétations acceptées uniquement.
  - `RG-047`, `RG-052` — styling tokenisé.
  - `RG-071`, `RG-073` — ownership feature préservé.
- Needs-investigation invariants:
  - Vérifier types frontend `astral_points` vs contrat public actuel avant implémentation.
- Non-applicable examples:
  - `RG-122` — hayz/rejoicing; réservé CS-389 mode astrologue.
  - `RG-018` — pas de nouveau prompt fallback sans story backend dédiée.
- Required regression evidence:
  - `pnpm --dir frontend test -- NatalKarmicSignature NatalCareerPotential NatalChartPage`
  - `pnpm --dir frontend lint`
  - `rg -n "TRUE_NODE|MEAN_NODE|LILITH_VARIANTS|NODE_VARIANTS" frontend/src/features/natal-chart`
- Allowed differences: copy marketing i18n si placements source identiques.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Section karmique titrée « Votre trajectoire d'évolution ». | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalKarmicSignature`. |
| AC2 | Les corps karmiques attendus sont cités depuis le payload. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalKarmicSignature`. |
| AC3 | Talents cachés affichent items ancrés signaux ou placements. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalHiddenTalents`. |
| AC4 | Potentiel relationnel cite Vénus. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalRelationshipPotential`. |
| AC5 | Potentiel professionnel cite le MC. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalCareerPotential`. |
| AC6 | Aucun dump JSON points astraux en vue principale. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "JSON.stringify" frontend/src/features/natal-chart`. |
| AC7 | Rejets LLM ne sont pas rendus comme contenu valide. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalInterpretation`. |
| AC8 | Build TypeScript passe avec types points astraux. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend build`. |
| AC9 | Dossier evidence present. | Evidence profile: baseline_before_after_diff; `rg --files _condamad/stories/CS-388*/evidence`. |

## Implementation Tasks

- [ ] Task 1: Confirmer et typer points astraux publics frontend. (AC: AC2, AC8)
- [ ] Task 2: Implémenter `NatalKarmicSignature`. (AC: AC1, AC2)
- [ ] Task 3: Implémenter potentiels talents/relations/carrière. (AC: AC3, AC4, AC5)
  - [ ] Subtask 3.1: Brancher texte LLM accepté ou signaux `interpretation_adapter`.
- [ ] Task 4: Intégrer page, i18n, upsell, tests, evidence. (AC: AC6, AC7, AC9)

## Mandatory Reuse / DRY Constraints

- Reuse:
  - Patterns cartes Sprint 2; hooks interprétation et labels astrologiques.
  - Points astraux et placements depuis `LatestNatalChart.result`.
- Do not recreate:
  - Calculateur variantes nœuds; repository points astraux côté frontend.
  - Nouveau flux génération LLM sans story backend.

## No Legacy / Forbidden Paths

- Forbidden unless explicitly approved:
  - legacy constantes locales `NODE_VARIANTS`, `LILITH_VARIANTS`, `ASTRAL_POINTS`
  - compatibility alias réaffichant dumps JSON expert
  - silent fallback narrative karmique sans source
- Specific forbidden symbols / paths:
  - `style=` inline statique
  - désérialisation frontend de payloads `status="rejected"`

## Removal Classification Rules

- Removal classification: not applicable

## Removal Audit Format

- Removal audit: not applicable

## Delete-Only Rule

- Delete-only rule: not applicable

## External Usage Blocker

- External usage blocker:
  - CS-386 ou CS-387 non implemente dans la branche cible.

## Generated Contract Check

- Generated contract check: not applicable
- Reason: pas de changement contrat API public.

## Files to Inspect First

- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `backend/app/services/chart/json_builder.py`
- `_condamad/stories/CS-387-refonte-natal-sprint2-interpretation-approfondie/00-story.md`

## Expected Files to Modify

Likely files:

- `frontend/src/features/natal-chart/NatalKarmicSignature.tsx` — implementation-created path.
- `frontend/src/features/natal-chart/NatalHiddenTalents.tsx` — implementation-created path.
- `frontend/src/features/natal-chart/NatalRelationshipPotential.tsx` — implementation-created path.
- `frontend/src/features/natal-chart/NatalCareerPotential.tsx` — implementation-created path.
- `frontend/src/pages/NatalChartPage.tsx` — composition Sprint 3.
- `frontend/src/i18n/natalChart.ts` — libellés karmiques et potentiels.

Likely tests:

- `frontend/src/tests/NatalKarmicSignature.test.tsx` — implementation-created path.
- `frontend/src/tests/NatalChartPage.test.tsx` — ordre sections Sprint 3.

Files not expected to change:

- `backend/app/domain/astrology/**`
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx` — contenu expert Sprint 4.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

```powershell
pnpm --dir frontend test -- NatalKarmicSignature NatalHiddenTalents NatalRelationshipPotential NatalCareerPotential NatalChartPage natalInterpretation
pnpm --dir frontend lint
pnpm --dir frontend build
rg -n "NODE_VARIANTS|LILITH_VARIANTS|ASTRAL_POINTS\\s*=" frontend/src/features/natal-chart
Manual check: /natal affiche trajectoire karmique et trois potentiels sans JSON brut.
```

## Regression Risks

- Risk: points astraux absents sur charts legacy → section vide.
  - Guardrail: état dégradé testé; copy explicite sans invention.
- Risk: contenu karmique dupliqué avec interprétation complète.
  - Guardrail: extraire sous-sections structurées; DRY avec `NatalThemeSynthesis`.
- Risk: violation RG-150 via cache rejeté.
  - Guardrail: réutiliser garde-fous `NatalInterpretation` existants.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## References

- Brief utilisateur 2026-05-29 — section 7 signature karmique et Sprint 3 backlog.
- CS-386, CS-387 — prérequis couches 1 et 2.
- CS-389 — mode astrologue Sprint 4.
