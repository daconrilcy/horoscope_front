# Story CS-386 refonte-natal-sprint1-comprehension-immediate: Refonte /natal Sprint 1 — Compréhension immédiate

Status: ready-to-dev

## Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-29 — plan de refonte page `/natal` (couche 1)
- Selected mode: Repo-informed story
- Reason for change: la page `/natal` expose trop de données techniques avant toute
  narration; le gain perçu exige hero narratif, synthèse IA visible, ADN astrologique
  et masquage du bruit expert par défaut.
- Source-alignment evidence: le brief exige diagnostic avant donnée; Sprint 1 couvre
  hero, synthèse, dominantes et retrait du bruit technique de la vue principale.

## Objective

Refondre la vue principale de `/natal` pour une couche 1 « compréhension immédiate » :
hero triptyque Soleil/Lune/Ascendant, section « Ce que votre thème raconte », cartes
« ADN astrologique » alimentées par le payload public existant, et retrait du bruit
technique ainsi que du panneau expert de la vue par défaut.

## Domain Boundary

- Domain: frontend-natal-page
- In scope:
  - `NatalChartPage` layout, ordre des sections et copy principale.
  - Nouveaux composants presentational sous `frontend/src/features/natal-chart/**`.
  - Consommation frontend de `dominant_planets`, `interpretation_adapter`,
    `chart_signature` et Lune via `planet_positions` / `astro_profile`.
  - Promotion visuelle de la synthèse IA via la feature d'interprétation existante.
  - Masquage par défaut de `NatalExpertPanel` et des dumps techniques listés au brief.
  - i18n `natalChart.ts`, CSS page-scoped, tests Vitest page/feature.
- Out of scope:
  - Domaines de vie, forces, défis, aspects enrichis (CS-387).
  - Signature karmique et potentiels (CS-388).
  - Mode astrologue premium et bascule technique complète (CS-389).
  - Changements backend API, prompts LLM, schémas Pydantic, migrations DB.
- Explicit non-goals:
  - Pas de recalcul astrologique côté React (RG-129).
  - Pas de redesign du panneau expert ni de nouvelle famille LLM.
  - Pas de suppression définitive des données techniques (repositionnement Sprint 4).

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: refonte UX frontend multi-section sans changement de contrat API public.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Réorganiser `/natal` sans casser génération, entitlement, historique interprétation.
  - Conserver les hooks API existants; extraire le rendu en composants dédiés.
  - Types frontend étendus uniquement pour lire des champs déjà projetés par le backend.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le produit refuse de masquer le panneau expert avant CS-389.
- Additional validation rules:
  - Vitest doit prouver hero, synthèse, ADN et absence du bruit technique par défaut.
  - Scan `rg` interdit recalcul astrologique et styles inline statiques.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest/Testing Library prouvent l'ordre des sections et le masquage par défaut. |
| Baseline Snapshot | yes | Captures/tests avant-après prouvent le retrait du bruit technique visible. |
| Ownership Routing | yes | Orchestration sous `features/natal-chart/**`; page allégée. |
| Allowlist Exception | no | Aucune allowlist autorisée pour recalcul astrologique frontend. |
| Contract Shape | yes | Extension des types `LatestNatalChart` pour champs publics déjà émis. |
| Batch Migration | no | Pas de migration multi-fichiers backend. |
| Reintroduction Guard | yes | Interdire réintroduction du bruit technique et du recalcul React. |
| Persistent Evidence | yes | Artefacts story pour revue et non-régression visuelle ciblée. |

## Runtime Source of Truth

- Primary source of truth:
  - Vitest/Testing Library sur `NatalChartPage` et composants feature natal.
  - `AST guard` via tests d'architecture composants natal-chart si présents.
- Secondary evidence:
  - `pnpm --dir frontend build` pour types `chart_signature`; scans `rg` anti-recalcul.
- Static scans alone are not sufficient for this story because:
  - L'ordre des sections et le masquage par défaut doivent être prouvés au rendu.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-386-refonte-natal-sprint1-comprehension-immediate/evidence/before-natal-page-structure.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-386-refonte-natal-sprint1-comprehension-immediate/evidence/after-natal-page-structure.txt`
- Expected invariant:
  - Seule la vue principale `/natal` change; contrat API public natal inchangé.
  - Les futures couches CS-387 a CS-389 doivent s'inserer apres les sections Sprint 1,
    sans reexposer le bruit technique par defaut.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Hero, synthèse, ADN UI | `frontend/src/features/natal-chart/` | logique inline page monolithique |
| Orchestration interprétation | `NatalInterpretation.tsx` | nouveau wrapper API sous `components/` |
| Faits dominantes/signatures | payload `LatestNatalChart.result` | calcul React local |

## Contract Shape

- Contract type:
  - Types frontend `LatestNatalChart.result` pour champs JSON publics existants.
- Fields:
  - `chart_signature.primary_element`: string optionnelle depuis payload public.
  - `chart_signature.primary_modality`: string optionnelle depuis payload public.
  - `chart_signature.primary_polarity`: string optionnelle depuis payload public.
- Required fields:
  - aucun nouveau champ backend; extension types frontend uniquement.
- Optional fields:
  - `chart_balance`, `chart_signature` quand absents sur charts legacy.
- Status codes:
  - non applicable; pas de nouvelle route API.
- Serialization names:
  - noms JSON backend conservés tels quels dans `json_builder.py`.
- Frontend type impact:
  - extension `frontend/src/api/natal-chart/index.ts`.
- Generated contract impact:
  - none.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-386-refonte-natal-sprint1-comprehension-immediate/evidence/validation.txt` | Preuve commandes frontend passées. |
| Before structure | `_condamad/stories/CS-386-refonte-natal-sprint1-comprehension-immediate/evidence/before-natal-page-structure.txt` | Baseline ordre sections avant refonte. |
| After structure | `_condamad/stories/CS-386-refonte-natal-sprint1-comprehension-immediate/evidence/after-natal-page-structure.txt` | Comparaison ordre sections après refonte. |
| Review output | `_condamad/stories/CS-386-refonte-natal-sprint1-comprehension-immediate/generated/11-code-review.md` | Revue automatique séparée. |

## Current State Evidence

- Evidence 1: `frontend/src/pages/NatalChartPage.tsx` - listes planètes avec longitudes visibles.
- Evidence 2: `frontend/src/features/natal-chart/NatalExpertPanel.tsx` - panneau expert rendu inline.
- Evidence 3: `frontend/src/api/natal-chart/index.ts` - types sans `chart_signature`.
- Evidence 4: `backend/app/services/chart/json_builder.py` - projection `chart_signature` publique.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - registre consulté pour RG-129.
- Evidence 6: `_condamad/stories/story-status.md` - tracker consulté pour numéro CS-386.

## Target State

- En-tête « Votre profil astrologique » avec triptyque ☉ Soleil, ☽ Lune, ↑ Ascendant
  et ligne de traits synthétiques (depuis sign profiles / `interpretation_adapter`).
- Section « Ce que votre thème raconte » placée avant les données brutes; 5 à 10
  paragraphes via interprétation courte existante ou état loading/upsell cohérent.
- Section « ADN astrologique » avec cartes : dominante planétaire, maître du thème,
  planète culminante, élément/modalité/polarité dominants — texte « Pourquoi ? » depuis
  `explanation_facts` / signaux API, sans inférence locale.
- Vue principale sans longitudes brutes, orbes détaillés, scores techniques, dumps JSON
  ni `NatalExpertPanel` visible par défaut.
- `NatalChartPage.tsx` allégé; nouveaux owners `NatalProfileHero`, `NatalThemeSynthesis`,
  `NatalAstrologicalDna` sous `features/natal-chart/`.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Scope vector:
  - Operation: update
  - Domain: frontend-natal-page
  - Surfaces: `frontend/src/pages/NatalChartPage.tsx`, `frontend/src/features/natal-chart/**`
  - Out-of-scope: backend API, DB, auth billing, migrations
- Applicable invariants:
  - `RG-047` — pas de styles inline statiques sur les nouvelles surfaces.
  - `RG-052` — tokens CSS canoniques pour hero et cartes ADN.
  - `RG-071` — `NatalInterpretation.tsx` reste décomposé; pas de monolithe.
  - `RG-073` — orchestration feature sous `features/natal-chart/**`.
  - `RG-129` — affichage depuis payload public uniquement; pas de règles locales.
  - `RG-150` — rejets LLM jamais rendus comme interprétation valide.
- Needs-investigation invariants:
  - Registry gap: invariant route `/natal` dédié absent; couvert par tests page Vitest.
- Non-applicable examples:
  - `RG-121` — moteur dominantes backend hors scope frontend.
  - `RG-002` — routeurs API backend non touchés.
  - `RG-018` — gouvernance prompts LLM non modifiée.
- Required regression evidence:
  - `pnpm --dir frontend test -- NatalChartPage NatalProfileHero NatalAstrologicalDna`
  - `pnpm --dir frontend lint`
  - `rg -n "style=" frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx`
  - `rg -n "DIURNAL_PLANETS|DOMINANCE_WEIGHTS|HAYZ_RULES" frontend/src/features/natal-chart`
- Allowed differences: copy i18n FR/EN; ordre visuel des cartes ADN si contenu identique.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le hero affiche un triptyque Soleil/Lune/Ascendant. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalChartPage`. |
| AC2 | Le titre « Thème natal de base » n'est plus le titre principal. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalChartPage`. |
| AC3 | « Ce que votre thème raconte » précède planètes/maisons brutes. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalChartPage`. |
| AC4 | Les cartes ADN consomment `dominant_planets` sans recalcul React. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm --dir frontend test -- NatalAstrologicalDna`. |
| AC5 | Élément/modalité/polarité lisent `chart_signature` typé. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend build`. |
| AC6 | Longitudes brutes absentes de la vue principale. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalChartPage`. |
| AC7 | `NatalExpertPanel` est masqué par défaut. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalChartPage`. |
| AC8 | Pas de style inline statique. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "style=" frontend/src/features/natal-chart`. |
| AC9 | Dossier evidence present. | Evidence profile: baseline_before_after_diff; `rg --files _condamad/stories/CS-386*/evidence`. |

## Implementation Tasks

- [ ] Task 1: Extraire `NatalProfileHero` avec triptyque et traits synthétiques. (AC: AC1, AC2)
  - [ ] Subtask 1.1: Lire Lune depuis `planet_positions` et signes depuis labels i18n.
  - [ ] Subtask 1.2: Ajouter CSS hero dans `NatalChartPage.css` ou fichier feature dédié.
- [ ] Task 2: Créer `NatalThemeSynthesis` et repositionner l'interprétation courte. (AC: AC3)
  - [ ] Subtask 2.1: Réutiliser hooks `useNatalInterpretation` sans dupliquer orchestration.
  - [ ] Subtask 2.2: Gérer loading, upsell free et quota inchangés fonctionnellement.
- [ ] Task 3: Créer `NatalAstrologicalDna` depuis payload public. (AC: AC4, AC5)
  - [ ] Subtask 3.1: Étendre types `natal-chart/index.ts` pour `chart_signature`.
  - [ ] Subtask 3.2: Rendre cartes dominante, maître, culminante, balance avec « Pourquoi ? ».
- [ ] Task 4: Retirer le bruit technique de la vue principale. (AC: AC6, AC7)
  - [ ] Subtask 4.1: Déplacer listes planètes/maisons/aspects brutes hors rendu default.
  - [ ] Subtask 4.2: Retirer rendu inline de `NatalExpertPanel` de la vue principale.
- [ ] Task 5: Tests, i18n, evidence et garde-fous. (AC: AC8, AC9)
  - [ ] Subtask 5.1: Mettre à jour `NatalChartPage.test.tsx` et tests feature dédiés.
  - [ ] Subtask 5.2: Persister `evidence/validation.txt` et snapshot before/after si utile.

## Mandatory Reuse / DRY Constraints

- Reuse:
  - `NatalInterpretation` / hooks `useNatalInterpretation*` pour la synthèse IA.
  - `useAstrologyLabels`, `natalChartTranslations`, tokens CSS `natal-page-*`.
  - Types et helpers existants `DominantPlanetsResult`, `InterpretationAdapterResult`.
- Do not recreate:
  - Nouvelle couche API, nouveau endpoint, nouveau calcul de dominantes frontend.
  - Second panneau expert ou duplicate de `NatalExpertPanel`.
- Shared abstraction allowed only if:
  - Carte ADN générique paramétrée par props API; pas de helper astrologique local.

## No Legacy / Forbidden Paths

- Forbidden unless explicitly approved:
  - compatibility wrappers around old page sections
  - transitional aliases for removed visible blocks
  - legacy imports from `components/NatalInterpretation`
  - duplicate active implementations of interpretation orchestration
  - silent fallback behavior inventing traits or dominants
  - preserving old technical lists visible by default
- Specific forbidden symbols / paths:
  - `frontend/src/components/NatalInterpretation.tsx`
  - constantes doctrinales `DIURNAL_PLANETS`, `DOMINANCE_WEIGHTS`, `HAYZ_RULES`
  - `style=` inline statique dans les nouveaux TSX

## Removal Classification Rules

- Removal classification: not applicable

## Removal Audit Format

- Removal audit: not applicable

## Delete-Only Rule

- Delete-only rule: not applicable

## External Usage Blocker

- External usage blocker: not applicable

## Generated Contract Check

- Generated contract check: not applicable
- Reason: extension de types frontend pour champs JSON déjà émis; pas de changement OpenAPI.

## Files to Inspect First

- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `backend/app/services/chart/json_builder.py` (lecture seule — forme payload)

## Expected Files to Modify

Likely files:

- `frontend/src/pages/NatalChartPage.tsx` — nouvel ordre de sections et composition.
- `frontend/src/pages/NatalChartPage.css` — layout hero et ADN.
- `frontend/src/features/natal-chart/NatalProfileHero.tsx` — implementation-created path.
- `frontend/src/features/natal-chart/NatalThemeSynthesis.tsx` — implementation-created path.
- `frontend/src/features/natal-chart/NatalAstrologicalDna.tsx` — implementation-created path.
- `frontend/src/api/natal-chart/index.ts` — types `chart_signature`, `chart_balance`.
- `frontend/src/i18n/natalChart.ts` — libellés hero, synthèse, ADN.

Likely tests:

- `frontend/src/tests/NatalChartPage.test.tsx` — ordre sections et masquage expert.
- `frontend/src/tests/NatalAstrologicalDna.test.tsx` — implementation-created path.

Files not expected to change:

- `backend/app/**` — hors scope Sprint 1.
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx` — contenu inchangé; masqué seulement.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

```powershell
pnpm --dir frontend test -- NatalChartPage NatalAstrologicalDna natalInterpretation
pnpm --dir frontend lint
pnpm --dir frontend build
rg -n "style=" frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx
rg -n "DIURNAL_PLANETS|DOMINANCE_WEIGHTS|HAYZ_RULES|SECT_PLANETS" frontend/src/features/natal-chart
Manual check: ouvrir /natal avec utilisateur test; hero, synthèse et ADN visibles sans longitudes brutes ni panneau expert.
```

## Regression Risks

- Risk: régression entitlement/upsell interprétation lors du repositionnement.
  - Guardrail: conserver tests `natalInterpretation.test.tsx` verts; RG-150.
- Risk: dérive vers recalcul astrologique pour traits ou dominantes.
  - Guardrail: RG-129 + scans `rg` interdits + tests ADN avec payload mocké.
- Risk: `NatalChartPage.tsx` redevient monolithique.
  - Guardrail: RG-071/RG-073 + limite de taille composants extraits.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not preserve legacy visible technical lists for convenience.

## References

- Brief utilisateur 2026-05-29 — vision 3 couches et backlog Sprint 1.
- `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/00-story.md`
- `_condamad/stories/CS-385-corriger-faux-degrade-projections-natal-persiste/00-story.md`
- Stories suivantes: CS-387, CS-388, CS-389.
