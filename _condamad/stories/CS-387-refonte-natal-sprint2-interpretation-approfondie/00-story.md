# Story CS-387 refonte-natal-sprint2-interpretation-approfondie: Refonte /natal Sprint 2 — Interprétation approfondie

Status: ready-to-dev

## Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-29 — plan refonte `/natal` (couche 2)
- Selected mode: Repo-informed story
- Reason for change: après la couche 1 (CS-386), la page doit exploiter les maisons
  et signaux interprétatifs via domaines de vie, forces, défis et aspects majeurs
  scorés — sans réexposer le bruit technique.
- Source-alignment evidence: le brief Sprint 2 exige cartes par sujet de vie, lectures
  forces/défis reliées aux placements, et top 10 aspects avec niveaux d'impact.

## Objective

Ajouter à `/natal` la couche 2 « interprétation approfondie » : section « Les grands
domaines de vie », sections « Forces » et « Défis », et « Aspects majeurs » limités aux
10 plus importants avec fiches enrichies — en consommant le payload public et
l'interprétation existante, sans recalcul astrologique frontend.

## Domain Boundary

- Domain: frontend-natal-page
- In scope:
  - Composants `NatalLifeDomains`, `NatalStrengths`, `NatalChallenges`, `NatalMajorAspects`.
  - Consommation de `interpretation_adapter`, `planet_condition_signals`, `houses`,
    `planet_positions`, `chart_balance.dominant_aspects`.
  - Extension types frontend pour `chart_balance` / aspects dominants publics.
  - i18n, CSS, tests Vitest des nouvelles sections.
- Out of scope:
  - Hero, synthèse IA, ADN astrologique (CS-386).
  - Signature karmique et potentiels (CS-388).
  - Mode astrologue et bascule technique (CS-389).
  - Nouveaux endpoints backend, prompts LLM, moteurs de scoring.
- Explicit non-goals:
  - Pas d'affichage de tous les aspects bruts avec orbes/scores techniques.
  - Pas de génération locale de texte interprétatif si absent du payload/LLM.
  - Pas de modification du moteur `PlanetDominanceEngine` ou `InterpretationAdapterEngine`.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: sections UX frontend consommant contrats JSON publics déjà calculés.
- Behavior change allowed: constrained
- Behavior change constraints:
  - S'appuyer sur CS-386 pour l'ordre de page; insérer sections après ADN/synthèse.
  - Top 10 aspects depuis `chart_balance.dominant_aspects`; absence de ranking public = blocker.
  - Texte forces/défis depuis signaux/thèmes API ou paragraphes interprétation LLM.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le payload public ne fournit pas de ranking aspects exploitable.
- Additional validation rules:
  - Vitest prouve six domaines, forces, défis et limite dix aspects majeurs.
  - Scan `rg` interdit orbes techniques et rescoring local des aspects.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest prouve rendu des 6 domaines et limite à 10 aspects. |
| Baseline Snapshot | yes | Snapshots/tests before-after sur structure sections Sprint 2. |
| Ownership Routing | yes | Nouveaux owners feature `natal-chart/**`. |
| Allowlist Exception | no | Pas d'allowlist pour inférer forces/défis localement. |
| Contract Shape | yes | Types `chart_balance`, `dominant_aspects` alignés payload public. |
| Batch Migration | no | Pas de migration backend. |
| Reintroduction Guard | yes | Interdire retour liste complète aspects bruts en vue principale. |
| Persistent Evidence | yes | Artefacts validation Sprint 2. |

## Runtime Source of Truth

- Primary source of truth:
  - Vitest/Testing Library sur composants Sprint 2 et `NatalChartPage`.
  - `AST guard` via tests d'architecture natal-chart si présents.
- Secondary evidence:
  - `pnpm --dir frontend build` pour types `chart_balance`; scans `rg` anti-rescoring.
- Static scans alone are not sufficient for this story because:
  - Le top 10 aspects et les six domaines doivent être prouvés au rendu.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-387-refonte-natal-sprint2-interpretation-approfondie/evidence/before-sprint2-sections.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-387-refonte-natal-sprint2-interpretation-approfondie/evidence/after-sprint2-sections.txt`
- Expected invariant:
  - Seules les sections Sprint 2 s'ajoutent; contrat JSON public natal inchangé.
  - CS-386 est deja implemente dans la branche; sinon cette story doit rester bloquee.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Domaines, forces, défis, aspects UI | `frontend/src/features/natal-chart/` | logique inline page |
| Ranking aspects dominants | payload `chart_balance` backend | tri React arbitraire |
| Signaux interprétatifs | `interpretation_adapter` public | mappings locaux de thèmes |

## Contract Shape

- Contract type:
  - Types frontend `chart_balance.dominant_aspects` depuis payload public.
- Fields:
  - `dominant_aspects[].rank`: entier positif depuis payload public.
  - `dominant_aspects[].dominance_score`: score normalisé depuis payload public.
- Required fields:
  - aucun nouveau champ backend; extension types frontend uniquement.
- Optional fields:
  - `chart_balance` absent sur charts legacy avec état dégradé UI.
- Status codes:
  - non applicable; pas de nouvelle route HTTP.
- Serialization names:
  - noms JSON backend conservés depuis `json_builder.py`.
- Frontend type impact:
  - extension `frontend/src/api/natal-chart/index.ts`.
- Generated contract impact:
  - none.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-387-refonte-natal-sprint2-interpretation-approfondie/evidence/validation.txt` | Preuve commandes frontend passées. |
| Before sections | `_condamad/stories/CS-387-refonte-natal-sprint2-interpretation-approfondie/evidence/before-sprint2-sections.txt` | Baseline sections Sprint 2. |
| After sections | `_condamad/stories/CS-387-refonte-natal-sprint2-interpretation-approfondie/evidence/after-sprint2-sections.txt` | Comparaison sections Sprint 2. |
| Review output | `_condamad/stories/CS-387-refonte-natal-sprint2-interpretation-approfondie/generated/11-code-review.md` | Revue automatique séparée. |

## Current State Evidence

- Evidence 1: `frontend/src/pages/NatalChartPage.tsx` - liste complète aspects avec orbes.
- Evidence 2: `backend/app/services/chart/json_builder.py` - projection `dominant_aspects`.
- Evidence 3: `frontend/src/api/natal-chart/index.ts` - absence de type `chart_balance`.
- Evidence 4: `backend/app/domain/astrology/runtime/dominant_aspect_runtime_data.py` - contrat rank/score.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - registre consulté pour RG-129.
- Evidence 6: `_condamad/stories/story-status.md` - tracker consulté pour numéro CS-387.

## Target State

- Section « Les grands domaines de vie » avec 6 cartes : Personnalité, Émotions,
  Relations, Carrière, Argent, Spiritualité — chaque carte cite placements publics
  (Soleil, Lune, MC, maisons VII, X, II et XII).
- Section « Forces » avec 3 items minimum, reliés à placements/signaux visibles.
- Section « Défis » avec 3 items minimum, reliés à placements/signaux visibles.
- Section « Aspects majeurs » : max 10 aspects, triés par score/rang API, badges
  Impact majeur / fort / secondaire; fiche avec signification, manifestation, positif,
  point d'attention — sans orbe effective ni raw score en vue principale.
- Tests Vitest couvrant rendu vide, dégradé et payload complet.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Scope vector:
  - Operation: update
  - Domain: frontend-natal-page
  - Surfaces: `frontend/src/features/natal-chart/**`, tests page
- Applicable invariants:
  - `RG-129` — tri/groupement aspects et domaines depuis payload public uniquement.
  - `RG-123` — signaux/thèmes depuis `interpretation_adapter`; pas de règles locales.
  - `RG-047`, `RG-052` — CSS tokenisé sans inline statique.
  - `RG-071`, `RG-073` — ownership feature natal-chart préservé.
  - `RG-150` — paragraphes LLM forces/défis depuis interprétations acceptées seulement.
- Needs-investigation invariants:
  - `RG-121` — vérifier que le frontend ne re-score pas les dominantes/aspects.
- Non-applicable examples:
  - `RG-124` — contrat secte chart-level; non requis pour cartes domaines de vie.
  - `RG-018` — prompts LLM non modifiés si réutilisation interprétation existante.
- Required regression evidence:
  - `pnpm --dir frontend test -- NatalLifeDomains NatalMajorAspects NatalChartPage`
  - `pnpm --dir frontend lint`
  - `rg -n "orb_used|raw_score|weighted_score|centrality" frontend/src/features/natal-chart`
- Allowed differences: libellés i18n des bandes d'impact si seuils API inchangés.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Six cartes domaines de vie sont rendues avec titres canoniques. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalLifeDomains`. |
| AC2 | Chaque carte domaine cite des placements issus du payload. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalLifeDomains`. |
| AC3 | La section Forces affiche au moins trois items ancrés payload. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalStrengths`. |
| AC4 | La section Défis affiche au moins trois items ancrés payload. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalChallenges`. |
| AC5 | Aspects majeurs limités à dix entrées triées par rang public. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalMajorAspects`. |
| AC6 | Bandes Impact majeur/fort/secondaire visibles sans raw score. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalMajorAspects`. |
| AC7 | Orbes détaillés absents des aspects majeurs. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "orb_used|effective" frontend/src/features/natal-chart`. |
| AC8 | Types `chart_balance` compilent sans orphan types. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend build`. |
| AC9 | Dossier evidence present. | Evidence profile: baseline_before_after_diff; `rg --files _condamad/stories/CS-387*/evidence`. |

## Implementation Tasks

- [ ] Task 1: Étendre types API pour `chart_balance` et aspects dominants. (AC: AC5, AC8)
  - [ ] Subtask 1.1: Mapper champs `dominant_aspects`, `rank`, `dominance_score`, `reasons`.
- [ ] Task 2: Implémenter `NatalLifeDomains` (6 cartes). (AC: AC1, AC2)
  - [ ] Subtask 2.1: Mapper Personnalité, Émotions, Relations, Carrière, Argent, Spiritualité.
- [ ] Task 3: Implémenter `NatalStrengths` et `NatalChallenges`. (AC: AC3, AC4)
  - [ ] Subtask 3.1: Source signaux `interpretation_adapter` ou contenu LLM accepté.
- [ ] Task 4: Implémenter `NatalMajorAspects` top 10 enrichi. (AC: AC5, AC6, AC7)
  - [ ] Subtask 4.1: Bandes d'impact depuis seuils documentés du payload.
- [ ] Task 5: Intégrer sections dans page, i18n, tests, evidence. (AC: AC9)
  - [ ] Subtask 5.1: Mettre à jour `NatalChartPage.test.tsx` pour ordre Sprint 2.

## Mandatory Reuse / DRY Constraints

- Reuse:
  - `useAstrologyLabels`, helpers formatage degrés existants si affichage symbolique.
  - `interpretation_adapter`, `dominant_planets`, hooks interprétation pour texte enrichi.
  - Carte UI pattern introduit par CS-386 (`NatalAstrologicalDna`).
- Do not recreate:
  - Moteur de ranking aspects; tri, seuils ou rescoring local interdits.
  - Nouvelle API REST pour domaines de vie.
- Shared abstraction allowed only if:
  - `NatalInsightCard` générique props-driven sans logique doctrinale.

## No Legacy / Forbidden Paths

- Forbidden unless explicitly approved:
  - compatibility wrappers réaffichant la liste complète aspects CS-386 masquée
  - legacy imports depuis l'ancienne liste aspects inline page
  - duplicate scoring local `weighted_score`, `centrality`, `house_rulership_load`
  - silent fallback inventant forces/défis sans source payload/LLM
- Specific forbidden symbols / paths:
  - recalcul `AspectEvaluator` côté frontend
  - `style=` inline statique

## Removal Classification Rules

- Removal classification: not applicable

## Removal Audit Format

- Removal audit: not applicable

## Delete-Only Rule

- Delete-only rule: not applicable

## External Usage Blocker

- External usage blocker:
  - CS-386 non implemente dans la branche cible.
  - Payload public sans `chart_balance.dominant_aspects` exploitable.

## Generated Contract Check

- Generated contract check: not applicable
- Reason: consommation de champs JSON publics existants; pas de changement OpenAPI.

## Files to Inspect First

- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `backend/app/services/chart/json_builder.py`
- `backend/app/domain/astrology/runtime/dominant_aspect_runtime_data.py`
- `_condamad/stories/CS-386-refonte-natal-sprint1-comprehension-immediate/00-story.md`

## Expected Files to Modify

Likely files:

- `frontend/src/features/natal-chart/NatalLifeDomains.tsx` — implementation-created path.
- `frontend/src/features/natal-chart/NatalStrengths.tsx` — implementation-created path.
- `frontend/src/features/natal-chart/NatalChallenges.tsx` — implementation-created path.
- `frontend/src/features/natal-chart/NatalMajorAspects.tsx` — implementation-created path.
- `frontend/src/pages/NatalChartPage.tsx` — composition sections Sprint 2.
- `frontend/src/api/natal-chart/index.ts` — types `chart_balance`.
- `frontend/src/i18n/natalChart.ts` — libellés domaines, forces, aspects.

Likely tests:

- `frontend/src/tests/NatalLifeDomains.test.tsx` — implementation-created path.
- `frontend/src/tests/NatalMajorAspects.test.tsx` — implementation-created path.
- `frontend/src/tests/NatalChartPage.test.tsx` — ordre et limite 10 aspects.

Files not expected to change:

- `backend/app/domain/astrology/**` — hors scope.
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx` — Sprint 4.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

```powershell
pnpm --dir frontend test -- NatalLifeDomains NatalMajorAspects NatalStrengths NatalChallenges NatalChartPage
pnpm --dir frontend lint
pnpm --dir frontend build
rg -n "orb_used|raw_score|weighted_score|aspect_centrality" frontend/src/features/natal-chart
Manual check: /natal affiche 6 domaines, forces, défis et max 10 aspects sans orbes techniques.
```

## Regression Risks

- Risk: absence de ranking aspects public bloque le top 10 sans rescoring local.
  - Guardrail: test imposant source `chart_balance.dominant_aspects`; blocker produit si absent.
- Risk: forces/défis génériques non ancrés placements.
  - Guardrail: AC3/AC4 exigent citation placement/signal dans tests.
- Risk: duplication avec interprétation LLM longue.
  - Guardrail: réutiliser extraits structurés; pas de second flux génération.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## References

- Brief utilisateur 2026-05-29 — sections 3 à 6 du plan architecture page.
- CS-386 — prérequis couche 1.
- CS-388, CS-389 — stories suivantes.
